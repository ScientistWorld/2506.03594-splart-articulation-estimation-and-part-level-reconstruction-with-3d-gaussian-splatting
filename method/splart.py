"""SPLART (Lin et al., 2025) reproduced at reduced scale.

Implements the paper's decoupled multi-stage optimisation on each scene:

Stage 1   per-state 3DGS reconstruction from the posed RGB images (photometric
          L1 + D-SSIM loss), initialised from the state's point cloud.
Stage 2a  duplicate G_ref -> G_tgt, add a mobility m in [0, 1] (init 0.5) per
          Gaussian and fit the mobilities with the cross-static weighted
          Chamfer consistency (Eq. 6) + lambda_geom * mean(m).
Stage 2b  cross-static rendering (Eq. 7): render G_l (full) + G_{1-l}*(1-M_{1-l})
          against state-l images, jointly optimising Gaussians and mobilities
          with lambda_photo * mean(M_{1-l}).
Stage 3a  articulation estimation by geometric consistency: K_m randomised
          tries of the mobile-only consistency (Eq. 11/12), one cross-mobile
          try continued from the best of them plus K_cm randomised cross-mobile
          tries (Eq. 13), then a final joint articulation + mobility run (Eq. 10).
Stage 3b  cross-mobile rendering (Eq. 14): joint optimisation of Gaussians,
          mobilities and articulation with the photometric loss.
Stage 3c  mobility correction with the cross-mobile geometric consistency (Eq. 15).

Constants follow the official implementation (method/splart_upstream): Chamfer
targets restricted to weights > 0.1, lambda_geom = 1e-4, lambda_photo = 5e-3,
K_m = K_cm = 3, articulation randomisation and learning rates, and the
convergence rule of the geometric stages.  Reduced-scale choices: isotropic
Gaussians with view-independent colour, no densification (pruning only), and
fewer photometric iterations (images are 48x48).

Inputs: ``data/scenes/<split>/inputs/<scene>.npz``.  Output per scene:
``<out>/predictions/<scene>.npz`` in the artifact format of briefing/evaluation.md.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import traceback
import zlib
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

CULL_ALPHA = 0.1
LAMBDA_M_GEOM = 1e-4
LAMBDA_M_PHOTO = 5e-3
LAMBDA_OPACITY = 1e-5
SSIM_LAMBDA = 0.2
PRUNE_OPACITY = 0.05
GEOM_LRS = {"axis": 3e-2, "pivot": 3e-2, "dist": 1e-2, "angle": 1e-1}
PHOTO_ART_LRS = {"axis": 1e-4, "pivot": 1e-4, "dist": 3e-5, "angle": 3e-4}


# --------------------------------------------------------------------------- rendering


class Renderer:
    """Differentiable copy of data/articulated_objects.render_gaussians (rgb only)."""

    def __init__(self, intr, size: int, background, device):
        self.fx, self.fy, self.cx, self.cy = [float(v) for v in intr]
        ar = torch.arange(size, device=device, dtype=torch.float32)
        ys, xs = torch.meshgrid(ar, ar, indexing="ij")
        self.pu = xs.reshape(-1) + 0.5
        self.pv = ys.reshape(-1) + 0.5
        self.size = size
        self.bg = torch.as_tensor(np.asarray(background), dtype=torch.float32, device=device)

    def __call__(self, means, scales, colors, opac, R, t):
        V = R.shape[0]
        pc = torch.einsum("vij,nj->vni", R, means) + t[:, None, :]
        z = pc[..., 2]
        ok = z > 0.05
        okf = ok.to(means.dtype)
        zs = torch.where(ok, z, torch.ones_like(z))
        u = self.fx * pc[..., 0] / zs + self.cx
        v = self.fy * pc[..., 1] / zs + self.cy
        var = (self.fx * scales[None, :] / zs) ** 2 + 0.3
        order = torch.argsort(z.detach(), dim=1, stable=True)
        u = u.gather(1, order)
        v = v.gather(1, order)
        var = var.gather(1, order)
        op = opac[order] * okf.gather(1, order)
        col = colors[order]
        d2 = (self.pu[None, None, :] - u[..., None]) ** 2 + (self.pv[None, None, :] - v[..., None]) ** 2
        alpha = torch.clamp(op[..., None] * torch.exp(-0.5 * d2 / var[..., None]), max=0.99)
        T = torch.cumprod(1.0 - alpha, dim=1)
        w = alpha * torch.cat([torch.ones_like(T[:, :1]), T[:, :-1]], dim=1)
        a = w.sum(1)
        rgb = torch.einsum("vnp,vnc->vpc", w, col) + (1.0 - a)[..., None] * self.bg
        return rgb.reshape(V, self.size, self.size, 3)


def _ssim_window(device):
    x = torch.arange(11, dtype=torch.float32, device=device) - 5
    g = torch.exp(-(x**2) / (2 * 1.5**2))
    g = g / g.sum()
    return (g[:, None] * g[None, :])[None, None].repeat(3, 1, 1, 1)


def ssim(x, y, win):
    c1, c2 = 0.01**2, 0.03**2
    mx = F.conv2d(x, win, padding=5, groups=3)
    my = F.conv2d(y, win, padding=5, groups=3)
    sxx = F.conv2d(x * x, win, padding=5, groups=3) - mx * mx
    syy = F.conv2d(y * y, win, padding=5, groups=3) - my * my
    sxy = F.conv2d(x * y, win, padding=5, groups=3) - mx * my
    s = ((2 * mx * my + c1) * (2 * sxy + c2)) / ((mx * mx + my * my + c1) * (sxx + syy + c2))
    return s.mean()


def photo_loss(pred, gt, win):
    l1 = (pred - gt).abs().mean()
    s = ssim(pred.permute(0, 3, 1, 2), gt.permute(0, 3, 1, 2), win)
    return (1.0 - SSIM_LAMBDA) * l1 + SSIM_LAMBDA * (1.0 - s)


# --------------------------------------------------------------------------- Gaussians


def init_gaussians(points: np.ndarray, colors: np.ndarray, device) -> dict:
    x = torch.as_tensor(points, dtype=torch.float32, device=device)
    d = torch.cdist(x, x)
    d.fill_diagonal_(float("inf"))
    k = min(3, max(1, x.shape[0] - 1))
    knn = d.topk(k, dim=1, largest=False).values
    s = knn.square().mean(1).sqrt().clamp(0.004, 0.05)
    c = torch.as_tensor(colors, dtype=torch.float32, device=device).clamp(0.02, 0.98)
    return {
        "means": x.clone(),
        "log_scales": s.log(),
        "color_logits": torch.logit(c),
        "opac_logits": torch.full((x.shape[0],), 0.0, device=device),
    }


def activated(g: dict):
    return g["means"], g["log_scales"].exp(), torch.sigmoid(g["color_logits"]), torch.sigmoid(g["opac_logits"])


def gaussian_param_groups(g: dict, scale: float = 1.0):
    return [
        {"params": [g["means"]], "lr": 5e-4 * scale, "name": "means"},
        {"params": [g["log_scales"]], "lr": 5e-3 * scale, "name": "log_scales"},
        {"params": [g["color_logits"]], "lr": 1e-2 * scale, "name": "color_logits"},
        {"params": [g["opac_logits"]], "lr": 5e-2 * scale, "name": "opac_logits"},
    ]


def require_grad(g: dict) -> dict:
    return {k: v.detach().clone().requires_grad_(True) for k, v in g.items()}


def clamp_scales(*gs):
    with torch.no_grad():
        for g in gs:
            g["log_scales"].clamp_(math.log(1e-3), math.log(0.1))


# --------------------------------------------------------------------------- articulation


def rodrigues(a, th):
    zero = torch.zeros_like(a[0])
    K = torch.stack(
        [
            torch.stack([zero, -a[2], a[1]]),
            torch.stack([a[2], zero, -a[0]]),
            torch.stack([-a[1], a[0], zero]),
        ]
    )
    eye = torch.eye(3, device=a.device, dtype=a.dtype)
    return eye + torch.sin(th) * K + (1.0 - torch.cos(th)) * (K @ K)


def transform(x, art: dict, jtype: str, direction: float):
    """Apply the motion state0 -> state1 (direction=+1) or its inverse (-1)."""
    a = F.normalize(art["axis"], dim=0)
    if jtype == "revolute":
        R = rodrigues(a, art["angle"] * direction)
        return (x - art["pivot"]) @ R.T + art["pivot"]
    return x + a * (art["dist"] * direction)


def random_articulation(jtype: str, gen: torch.Generator, device) -> dict:
    """Upstream ArticulationParams.randomize()."""
    axis = torch.randn(3, generator=gen)
    axis = axis / axis.norm()
    art = {
        "axis": axis,
        "pivot": torch.randn(3, generator=gen) * 0.3 if jtype == "revolute" else torch.zeros(3),
        "angle": (torch.rand((), generator=gen) * 2 - 1) * math.pi,
        "dist": torch.randn((), generator=gen) * 0.1,
    }
    return {k: v.to(device) for k, v in art.items()}


def art_keys(jtype: str):
    return ("axis", "pivot", "angle") if jtype == "revolute" else ("axis", "dist")


def art_param_groups(art: dict, jtype: str, lrs: dict, scale: float = 1.0):
    return [{"params": [art[k]], "lr": lrs[k] * scale} for k in art_keys(jtype)]


def art_requires_grad(art: dict, jtype: str) -> dict:
    out = {k: v.detach().clone() for k, v in art.items()}
    for k in art_keys(jtype):
        out[k].requires_grad_(True)
    return out


def canonical_articulation(art: dict, jtype: str) -> dict:
    """Upstream angle regularisation: angle in [0, pi] by flipping the axis."""
    out = {k: v.detach().clone() for k, v in art.items()}
    out["axis"] = F.normalize(out["axis"], dim=0)
    if jtype == "revolute":
        ang = float(out["angle"]) % (2 * math.pi)
        if ang > math.pi:
            ang = 2 * math.pi - ang
            out["axis"] = -out["axis"]
        out["angle"] = torch.tensor(ang, device=out["axis"].device)
    return out


# --------------------------------------------------------------------------- geometric consistency


def weighted_chamfer(x, wx, y, wy, tau=CULL_ALPHA):
    """Eq. 5 with the upstream restriction of nearest-neighbour targets to weights > tau."""
    my = wy > tau
    mx = wx > tau
    if int(my.sum()) == 0:
        my = torch.ones_like(my)
    if int(mx.sum()) == 0:
        mx = torch.ones_like(mx)
    d1 = torch.cdist(x, y[my]).square().min(dim=1).values
    d2 = torch.cdist(y, x[mx]).square().min(dim=1).values
    return (d1 * wx).sum() / wx.sum().clamp_min(1e-8) + (d2 * wy).sum() / wy.sum().clamp_min(1e-8)


class GeomContext:
    """Fixed tensors for the geometric stages (G_ref and detached G_tgt)."""

    def __init__(self, ref, tgt, jtype: str, color_weight: float = 0.0):
        self.jtype = jtype
        self.cw = color_weight
        self.ref = [self._feat(*activated(g)) for g in ref]
        self.tgt = [self._feat(*activated(g)) for g in tgt]

    def _feat(self, means, scales, colors, opac):
        means, colors, opac = means.detach(), colors.detach(), opac.detach()
        return {"x": means, "c": colors, "o": opac}

    def _pts(self, x, c):
        if self.cw > 0:
            return torch.cat([x, self.cw * c], dim=1)
        return x

    def loss(self, mode: str, m0, m1, art=None):
        t0, t1 = self.tgt
        x0, x1, o0, o1 = t0["x"], t1["x"], t0["o"], t1["o"]
        if mode in ("m", "cm"):
            x01 = transform(x0, art, self.jtype, +1.0)
            x10 = transform(x1, art, self.jtype, -1.0)
        if mode == "m":
            return weighted_chamfer(self._pts(x0, t0["c"]), o0 * m0, self._pts(x10, t1["c"]), o1 * m1)
        tx0 = [self._pts(x0, t0["c"]), self._pts(x1, t1["c"])]
        tw0 = [o0, o1 * (1 - m1)]
        tx1 = [self._pts(x1, t1["c"]), self._pts(x0, t0["c"])]
        tw1 = [o1, o0 * (1 - m0)]
        if mode == "cm":
            tx0.append(self._pts(x10, t1["c"]))
            tw0.append(o1 * m1)
            tx1.append(self._pts(x01, t0["c"]))
            tw1.append(o0 * m0)
        r0, r1 = self.ref
        return weighted_chamfer(self._pts(r0["x"], r0["c"]), r0["o"], torch.cat(tx0), torch.cat(tw0)) + weighted_chamfer(
            self._pts(r1["x"], r1["c"]), r1["o"], torch.cat(tx1), torch.cat(tw1)
        )


def run_until_converged(loss_fn, groups, r_th=1e-3, max_iters=3000, min_iters=20, window=10):
    """Upstream SplartModel._optimize: stop when the relative change vs a running mean < r_th."""
    opt = torch.optim.Adam(groups, eps=1e-15)
    avg = None
    value = float("nan")
    it = 0
    for it in range(1, max_iters + 1):
        opt.zero_grad(set_to_none=True)
        loss = loss_fn()
        loss.backward()
        opt.step()
        value = float(loss.detach())
        if avg is None:
            r, avg = 1.0, value
        else:
            r = 1.0 - value / avg if avg != 0 else 0.0
            avg = ((window - 1) * avg + value) / window
        if it >= min_iters and abs(r) < r_th:
            break
    return value, it


# --------------------------------------------------------------------------- the pipeline


class Scene:
    def __init__(self, path: Path, device):
        with np.load(path, allow_pickle=False) as d:
            self.name = path.stem
            self.jtype = str(d["articulation_type"])
            self.points = [d["points0"], d["points1"]]
            self.colors = [d["colors0"], d["colors1"]]
            self.images = [torch.as_tensor(d[f"images{l}"], device=device).float() / 255.0 for l in (0, 1)]
            self.R = [torch.as_tensor(d[f"cams{l}_R"], dtype=torch.float32, device=device) for l in (0, 1)]
            self.t = [torch.as_tensor(d[f"cams{l}_t"], dtype=torch.float32, device=device) for l in (0, 1)]
            self.intr = d["intrinsics"].astype(np.float64)
            self.size = int(d["image_size"])
            self.background = d["background"].astype(np.float64)


def _views(scene: Scene, l: int, gen: torch.Generator, batch: int):
    n = scene.images[l].shape[0]
    idx = torch.randperm(n, generator=gen)[:batch].to(scene.images[l].device)
    return scene.R[l][idx], scene.t[l][idx], scene.images[l][idx]


def _lr_decay(opt, name, start, end, it, total):
    frac = it / max(total - 1, 1)
    for gr in opt.param_groups:
        if gr.get("name") == name:
            gr["lr"] = start * (end / start) ** frac


def stage1(scene, render, win, gen, cfg, log):
    gs = []
    for l in (0, 1):
        g = require_grad(init_gaussians(scene.points[l], scene.colors[l], scene.images[l].device))
        gs.append(g)
    opts = [torch.optim.Adam(gaussian_param_groups(g), eps=1e-15) for g in gs]
    iters = cfg["s1_iters"]
    prune_at = {iters // 3, (2 * iters) // 3}
    for it in range(iters):
        for l in (0, 1):
            g, opt = gs[l], opts[l]
            _lr_decay(opt, "means", 5e-4, 5e-5, it, iters)
            R, t, gt = _views(scene, l, gen, cfg["batch"])
            means, scales, colors, opac = activated(g)
            loss = photo_loss(render(means, scales, colors, opac, R, t), gt, win) + LAMBDA_OPACITY * opac.mean()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            clamp_scales(g)
        if it in prune_at:
            for l in (0, 1):
                gs[l] = _prune(gs[l])
                opts[l] = torch.optim.Adam(gaussian_param_groups(gs[l]), eps=1e-15)
                _lr_decay(opts[l], "means", 5e-4, 5e-5, it, iters)
    gs = [_prune(g) for g in gs]
    log["stage1_counts"] = [int(g["means"].shape[0]) for g in gs]
    log["stage1_last_loss"] = float(loss.detach())
    return [{k: v.detach() for k, v in g.items()} for g in gs]


def _prune(g):
    with torch.no_grad():
        keep = torch.sigmoid(g["opac_logits"]) >= PRUNE_OPACITY
        if int(keep.sum()) < 8:
            keep = torch.sigmoid(g["opac_logits"]).argsort(descending=True)[:8]
        return {k: v.detach()[keep].clone().requires_grad_(True) for k, v in g.items()}


def stage2a(ctx: GeomContext, mlog, cfg, log):
    def fn():
        m0, m1 = torch.sigmoid(mlog[0]), torch.sigmoid(mlog[1])
        return ctx.loss("cs", m0, m1) + LAMBDA_M_GEOM * torch.cat([m0, m1]).mean()

    v, n = run_until_converged(fn, [{"params": mlog, "lr": 3.0}], r_th=1e-3, max_iters=cfg["geom_max_iters"])
    log["stage2a"] = {"loss": v, "iters": n}


def stage2b(scene, render, win, gen, tgt, mlog, cfg, log):
    groups = gaussian_param_groups(tgt[0]) + gaussian_param_groups(tgt[1])
    groups.append({"params": mlog, "lr": 1e-1})
    opt = torch.optim.Adam(groups, eps=1e-15)
    iters = cfg["s2b_iters"]
    for it in range(iters):
        l = it % 2
        o = 1 - l
        R, t, gt = _views(scene, l, gen, cfg["batch"])
        xl, sl, cl, ol = activated(tgt[l])
        xo, so, co, oo = activated(tgt[o])
        mo = torch.sigmoid(mlog[o])
        pred = render(torch.cat([xl, xo]), torch.cat([sl, so]), torch.cat([cl, co]), torch.cat([ol, oo * (1 - mo)]), R, t)
        loss = photo_loss(pred, gt, win) + LAMBDA_M_PHOTO * mo.mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        clamp_scales(*tgt)
    log["stage2b_last_loss"] = float(loss.detach())


def stage3a(ctx: GeomContext, mlog, jtype, gen, device, cfg, log):
    m0f, m1f = torch.sigmoid(mlog[0]).detach(), torch.sigmoid(mlog[1]).detach()
    tries = []
    best_m = None
    for k in range(cfg["k_m"]):
        art = art_requires_grad(random_articulation(jtype, gen, device), jtype)
        v, n = run_until_converged(
            lambda: ctx.loss("m", m0f, m1f, art), art_param_groups(art, jtype, GEOM_LRS), max_iters=cfg["geom_max_iters"]
        )
        tries.append({"mode": "m", "loss": v, "iters": n})
        if best_m is None or v < best_m[0]:
            best_m = (v, {k2: x.detach().clone() for k2, x in art.items()})
    best_cm = None
    inits = []
    if best_m is not None:
        inits.append(("continued", best_m[1], 0.1))
    for k in range(cfg["k_cm"]):
        inits.append(("random", random_articulation(jtype, gen, device), 1.0))
    for kind, init, lr_scale in inits:
        art = art_requires_grad(init, jtype)
        v, n = run_until_converged(
            lambda: ctx.loss("cm", m0f, m1f, art),
            art_param_groups(art, jtype, GEOM_LRS, lr_scale),
            max_iters=cfg["geom_max_iters"],
        )
        tries.append({"mode": "cm", "init": kind, "loss": v, "iters": n})
        if best_cm is None or v < best_cm[0]:
            best_cm = (v, {k2: x.detach().clone() for k2, x in art.items()}, lr_scale)
    # final joint articulation + mobility refinement (Eq. 10a)
    art = art_requires_grad(best_cm[1], jtype)

    def fn():
        return ctx.loss("cm", torch.sigmoid(mlog[0]), torch.sigmoid(mlog[1]), art)

    groups = art_param_groups(art, jtype, GEOM_LRS, best_cm[2]) + [{"params": mlog, "lr": 1.0}]
    v, n = run_until_converged(fn, groups, r_th=1e-4, max_iters=cfg["geom_max_iters"])
    tries.append({"mode": "cm_joint", "loss": v, "iters": n})
    log["stage3a"] = tries
    return canonical_articulation(art, jtype)


def stage3b(scene, render, win, gen, tgt, mlog, art, jtype, cfg, log):
    art = art_requires_grad(art, jtype)
    groups = gaussian_param_groups(tgt[0]) + gaussian_param_groups(tgt[1])
    groups.append({"params": mlog, "lr": 3e-3})
    groups += art_param_groups(art, jtype, PHOTO_ART_LRS)
    opt = torch.optim.Adam(groups, eps=1e-15)
    iters = cfg["s3b_iters"]
    for it in range(iters):
        l = it % 2
        o = 1 - l
        direction = 1.0 if o == 0 else -1.0
        R, t, gt = _views(scene, l, gen, cfg["batch"])
        xl, sl, cl, ol = activated(tgt[l])
        xo, so, co, oo = activated(tgt[o])
        mo = torch.sigmoid(mlog[o])
        xm = transform(xo, art, jtype, direction)
        pred = render(
            torch.cat([xl, xo, xm]),
            torch.cat([sl, so, so]),
            torch.cat([cl, co, co]),
            torch.cat([ol, oo * (1 - mo), oo * mo]),
            R,
            t,
        )
        loss = photo_loss(pred, gt, win)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        clamp_scales(*tgt)
    log["stage3b_last_loss"] = float(loss.detach())
    return canonical_articulation(art, jtype)


def stage3c(ctx: GeomContext, mlog, art, cfg, log):
    art = {k: v.detach() for k, v in art.items()}

    def fn():
        return ctx.loss("cm", torch.sigmoid(mlog[0]), torch.sigmoid(mlog[1]), art)

    v, n = run_until_converged(fn, [{"params": mlog, "lr": 0.3}], r_th=1e-3, max_iters=cfg["geom_max_iters"])
    log["stage3c"] = {"loss": v, "iters": n}


def export(tgt, mlog, art, jtype) -> dict:
    with torch.no_grad():
        x0, s0, c0, o0 = activated(tgt[0])
        x1, s1, c1, o1 = activated(tgt[1])
        m0, m1 = torch.sigmoid(mlog[0]), torch.sigmoid(mlog[1])
        x10 = transform(x1, art, jtype, -1.0)
        out = {}
        for name, xs, ss, cs, os_ in (
            ("static", [x0, x1], [s0, s1], [c0, c1], [o0 * (1 - m0), o1 * (1 - m1)]),
            ("mobile", [x0, x10], [s0, s1], [c0, c1], [o0 * m0, o1 * m1]),
        ):
            x, s, c, o = torch.cat(xs), torch.cat(ss), torch.cat(cs), torch.cat(os_)
            keep = o > 0.005
            out[f"{name}_means"] = x[keep].cpu().numpy().astype(np.float32)
            out[f"{name}_scales"] = s[keep].cpu().numpy().astype(np.float32)
            out[f"{name}_colors"] = c[keep].clamp(0, 1).cpu().numpy().astype(np.float32)
            out[f"{name}_opacities"] = o[keep].clamp(0, 1).cpu().numpy().astype(np.float32)
        a = F.normalize(art["axis"], dim=0)
        out["axis"] = a.cpu().numpy().astype(np.float64)
        if jtype == "revolute":
            out["pivot"] = art["pivot"].cpu().numpy().astype(np.float64)
            out["amount"] = np.array(float(art["angle"]), dtype=np.float64)
        else:
            out["pivot"] = np.zeros(3)
            out["amount"] = np.array(float(art["dist"]), dtype=np.float64)
    return out


def run_scene(path: Path, cfg: dict, device, seed: int) -> tuple[dict, dict]:
    scene_seed = (zlib.crc32(path.stem.encode()) + 7919 * seed) % (2**31 - 1)
    torch.manual_seed(scene_seed)
    gen = torch.Generator().manual_seed(scene_seed)
    scene = Scene(path, device)
    render = Renderer(scene.intr, scene.size, scene.background, device)
    win = _ssim_window(device)
    log = {"scene": scene.name, "type": scene.jtype, "seed": scene_seed, "config": cfg}
    t0 = time.time()
    ref = stage1(scene, render, win, gen, cfg, log)
    tgt = [require_grad(g) for g in ref]
    mlog = [torch.zeros(g["means"].shape[0], device=device, requires_grad=True) for g in tgt]
    log["t_stage1"] = time.time() - t0
    if not cfg["skip_2a"]:
        stage2a(GeomContext(ref, tgt, scene.jtype, cfg["color_weight"]), mlog, cfg, log)
    if not cfg["skip_2b"]:
        stage2b(scene, render, win, gen, tgt, mlog, cfg, log)
    log["t_stage2"] = time.time() - t0
    ctx = GeomContext(ref, tgt, scene.jtype, cfg["color_weight"])
    if cfg["skip_3a"]:
        art = canonical_articulation(random_articulation(scene.jtype, gen, device), scene.jtype)
    else:
        art = stage3a(ctx, mlog, scene.jtype, gen, device, cfg, log)
    log["after_3a"] = {k: v.cpu().tolist() for k, v in art.items()}
    if not cfg["skip_3b"]:
        art = stage3b(scene, render, win, gen, tgt, mlog, art, scene.jtype, cfg, log)
    ctx = GeomContext(ref, tgt, scene.jtype, cfg["color_weight"])
    stage3c(ctx, mlog, art, cfg, log)
    log["t_total"] = time.time() - t0
    log["final"] = {k: v.cpu().tolist() for k, v in art.items()}
    return export(tgt, mlog, art, scene.jtype), log


def pick_device(spec: str, shard: int):
    if spec != "auto":
        return torch.device(spec)
    if torch.cuda.is_available():
        try:
            n = torch.cuda.device_count()
            dev = torch.device(f"cuda:{shard % n}")
            torch.zeros(1, device=dev).sum().item()
            return dev
        except Exception as exc:  # pragma: no cover - driver problems fall back to CPU
            print(f"[splart] CUDA unusable ({exc}); using CPU", flush=True)
    return torch.device("cpu")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inputs", nargs="+", default=["data/scenes/train/inputs", "data/scenes/test/inputs"])
    ap.add_argument("--out", default="checkpoints/splart")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--scenes", nargs="*", default=None, help="optional subset of scene names")
    ap.add_argument("--batch", type=int, default=4, help="views per photometric step")
    ap.add_argument("--s1-iters", type=int, default=2000)
    ap.add_argument("--s2b-iters", type=int, default=1000)
    ap.add_argument("--s3b-iters", type=int, default=2000)
    ap.add_argument("--geom-max-iters", type=int, default=3000)
    ap.add_argument("--k-m", type=int, default=3)
    ap.add_argument("--k-cm", type=int, default=3)
    ap.add_argument("--color-weight", type=float, default=0.0, help="0 = paper (xyz-only Chamfer)")
    ap.add_argument("--skip-2a", action="store_true")
    ap.add_argument("--skip-2b", action="store_true")
    ap.add_argument("--skip-3a", action="store_true")
    ap.add_argument("--skip-3b", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    torch.set_num_threads(max(1, args.threads))
    device = pick_device(args.device, args.shard)
    cfg = {
        "batch": args.batch,
        "s1_iters": args.s1_iters,
        "s2b_iters": args.s2b_iters,
        "s3b_iters": args.s3b_iters,
        "geom_max_iters": args.geom_max_iters,
        "k_m": args.k_m,
        "k_cm": args.k_cm,
        "color_weight": args.color_weight,
        "skip_2a": args.skip_2a,
        "skip_2b": args.skip_2b,
        "skip_3a": args.skip_3a,
        "skip_3b": args.skip_3b,
    }
    paths = sorted(f for d in args.inputs for f in Path(d).glob("*.npz"))
    if args.scenes:
        wanted = set(args.scenes)
        paths = [f for f in paths if f.stem in wanted]
    paths = paths[args.shard :: args.num_shards]
    out = Path(args.out)
    (out / "predictions").mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    print(f"[splart] shard {args.shard}/{args.num_shards}: {len(paths)} scenes on {device}", flush=True)
    for path in paths:
        dest = out / "predictions" / f"{path.stem}.npz"
        if dest.exists() and not args.overwrite:
            continue
        try:
            pred, log = run_scene(path, cfg, device, args.seed)
        except Exception:
            print(f"[splart] {path.stem} FAILED\n{traceback.format_exc()}", flush=True)
            continue
        tmp = dest.with_suffix(".tmp.npz")
        np.savez(tmp, **pred)
        tmp.replace(dest)
        (out / "logs" / f"{path.stem}.json").write_text(json.dumps(log, indent=1, default=float))
        print(f"[splart] {path.stem} ({log['type']}) done in {log['t_total']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
