"""Lightweight reproduction of SPLART's core optimization.

This module implements the paper's distinctive staged computation at small
scale: per-state Gaussian references, per-Gaussian mobility variables,
cross-static weighted Chamfer and rendering consistency for part separation,
and cross-mobile geometric/rendering consistency for articulation fitting. It
uses a compact orthographic Gaussian density renderer instead of the official
CUDA 3DGS renderer in method/splart_upstream, making the benchmark suitable for
a quick CPU smoke run while preserving the optimization structure.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F


def weighted_chamfer(x, wx, y, wy):
    d = torch.cdist(x, y).square()
    wx = wx.clamp_min(1e-8)
    wy = wy.clamp_min(1e-8)
    wx = wx / wx.sum()
    wy = wy / wy.sum()
    return (wx * d.min(dim=1).values).sum() + (wy * d.min(dim=0).values).sum()


def camera_matrices(device: str) -> torch.Tensor:
    """Fixed posed views for the lightweight rendering losses."""
    mats = []
    elev = torch.tensor(0.45, device=device)
    ce, se = torch.cos(elev), torch.sin(elev)
    rx = torch.stack(
        [
            torch.tensor([1.0, 0.0, 0.0], device=device),
            torch.stack([torch.tensor(0.0, device=device), ce, -se]),
            torch.stack([torch.tensor(0.0, device=device), se, ce]),
        ]
    )
    for angle in torch.linspace(0, 2 * torch.pi, steps=5, device=device)[:-1]:
        c, s = torch.cos(angle), torch.sin(angle)
        rz = torch.stack(
            [
                torch.stack([c, -s, torch.tensor(0.0, device=device)]),
                torch.stack([s, c, torch.tensor(0.0, device=device)]),
                torch.tensor([0.0, 0.0, 1.0], device=device),
            ]
        )
        mats.append(rx @ rz)
    return torch.stack(mats)


def render_density(points, weights, cameras, image_size: int = 32, sigma: float = 0.045):
    """Differentiable orthographic Gaussian splatting proxy.

    The paper's full implementation optimizes photometric losses with 3DGS.
    Here the target signal is a multi-view density image, which is sufficient to
    exercise the same cross-static/cross-mobile rendering formulations.
    """
    coords_1d = torch.linspace(-1.0, 1.0, image_size, device=points.device)
    yy, xx = torch.meshgrid(coords_1d, coords_1d, indexing="ij")
    grid = torch.stack([xx, yy], dim=-1)
    images = []
    weights = weights.clamp_min(0.0)
    for cam in cameras:
        proj = (points @ cam.T)[:, :2] / 1.15
        d2 = (grid[None, :, :, :] - proj[:, None, None, :]).square().sum(dim=-1)
        img = (weights[:, None, None] * torch.exp(-d2 / (2 * sigma * sigma))).sum(dim=0)
        images.append(img / img.amax().clamp_min(1e-6))
    return torch.stack(images)


def axis_angle_matrix(axis, angle):
    axis = F.normalize(axis, dim=0)
    x, y, z = axis
    c = torch.cos(angle)
    s = torch.sin(angle)
    C = 1 - c
    return torch.stack(
        [
            torch.stack([c + x * x * C, x * y * C - z * s, x * z * C + y * s]),
            torch.stack([y * x * C + z * s, c + y * y * C, y * z * C - x * s]),
            torch.stack([z * x * C - y * s, z * y * C + x * s, c + z * z * C]),
        ]
    )


def transform(points, articulation_type, axis, pivot, amount):
    axis = F.normalize(axis, dim=0)
    if articulation_type == "revolute":
        R = axis_angle_matrix(axis, amount)
        return (points - pivot) @ R.T + pivot
    if articulation_type == "prismatic":
        return points + axis * amount
    raise ValueError(articulation_type)


def cross_static_sets(x0, x1, opacity, m0, m1, state):
    static_x = torch.cat([x0, x1], dim=0)
    static_w = torch.cat([opacity * (1 - m0), opacity * (1 - m1)], dim=0)
    if state == 0:
        return torch.cat([static_x, x0], dim=0), torch.cat([static_w, opacity * m0], dim=0)
    return torch.cat([static_x, x1], dim=0), torch.cat([static_w, opacity * m1], dim=0)


def cross_mobile_sets(x0, x1, opacity, m0, m1, articulation_type, axis, pivot, amount, state):
    static_x = torch.cat([x0, x1], dim=0)
    static_w = torch.cat([opacity * (1 - m0), opacity * (1 - m1)], dim=0)
    if state == 0:
        moved = transform(x1, articulation_type, axis, pivot, -amount)
        mobile_x = torch.cat([x0, moved], dim=0)
    else:
        moved = transform(x0, articulation_type, axis, pivot, amount)
        mobile_x = torch.cat([x1, moved], dim=0)
    mobile_w = torch.cat([opacity * m0, opacity * m1], dim=0)
    return torch.cat([static_x, mobile_x], dim=0), torch.cat([static_w, mobile_w], dim=0)


def optimize_scene(
    path: Path,
    seed: int,
    device: str = "cpu",
    mobility_steps: int = 120,
    render_steps: int = 60,
    tries: int = 4,
    coarse_steps: int = 160,
    refine_steps: int = 260,
) -> dict:
    torch.manual_seed(seed)
    data = np.load(path)
    articulation_type = str(data["articulation_type"])
    print(f"[splart] {path.stem}: start {articulation_type}", flush=True)
    x0 = torch.tensor(data["state0"], dtype=torch.float32, device=device)
    x1 = torch.tensor(data["state1"], dtype=torch.float32, device=device)
    opacity = torch.tensor(data["opacities"], dtype=torch.float32, device=device)
    n = x0.shape[0]
    cameras = camera_matrices(device)
    target0 = render_density(x0, opacity, cameras)
    target1 = render_density(x1, opacity, cameras)

    logits0 = torch.zeros(n, device=device, requires_grad=True)
    logits1 = torch.zeros(n, device=device, requires_grad=True)
    opt = torch.optim.Adam([logits0, logits1], lr=0.25)
    for _ in range(mobility_steps):
        m0 = torch.sigmoid(logits0)
        m1 = torch.sigmoid(logits1)
        cs0_x, cs0_w = cross_static_sets(x0, x1, opacity, m0, m1, 0)
        cs1_x, cs1_w = cross_static_sets(x0, x1, opacity, m0, m1, 1)
        loss = weighted_chamfer(cs0_x, cs0_w, x0, opacity) + weighted_chamfer(cs1_x, cs1_w, x1, opacity)
        loss = loss + 2e-4 * (m0.mean() + m1.mean())
        opt.zero_grad()
        loss.backward()
        opt.step()

    opt = torch.optim.Adam([logits0, logits1], lr=0.08)
    for _ in range(render_steps):
        m0 = torch.sigmoid(logits0)
        m1 = torch.sigmoid(logits1)
        cs0_x, cs0_w = cross_static_sets(x0, x1, opacity, m0, m1, 0)
        cs1_x, cs1_w = cross_static_sets(x0, x1, opacity, m0, m1, 1)
        loss = F.mse_loss(render_density(cs0_x, cs0_w, cameras), target0)
        loss = loss + F.mse_loss(render_density(cs1_x, cs1_w, cameras), target1)
        loss = loss + 2e-4 * (m0.mean() + m1.mean())
        opt.zero_grad()
        loss.backward()
        opt.step()

    with torch.no_grad():
        init_m0 = torch.sigmoid(logits0).clamp(0.02, 0.98)
        init_m1 = torch.sigmoid(logits1).clamp(0.02, 0.98)

    best = None
    for t in range(tries):
        axis = torch.randn(3, device=device, requires_grad=True)
        amount0 = torch.tensor(0.35 if articulation_type == "prismatic" else 0.7, device=device)
        amount = (amount0 + 0.25 * torch.randn((), device=device)).detach().requires_grad_(True)
        params = [axis, amount]
        if articulation_type == "revolute":
            pivot = (0.15 * torch.randn(3, device=device)).requires_grad_(True)
            params.append(pivot)
        else:
            pivot = torch.zeros(3, device=device)
        opt_t = torch.optim.Adam(params, lr=0.04)
        for _ in range(coarse_steps):
            ax = F.normalize(axis, dim=0)
            cd_mobile = weighted_chamfer(
                x0, opacity * init_m0, transform(x1, articulation_type, ax, pivot, -amount), opacity * init_m1
            )
            cm0_x, cm0_w = cross_mobile_sets(x0, x1, opacity, init_m0, init_m1, articulation_type, ax, pivot, amount, 0)
            cm1_x, cm1_w = cross_mobile_sets(x0, x1, opacity, init_m0, init_m1, articulation_type, ax, pivot, amount, 1)
            loss = cd_mobile + weighted_chamfer(cm0_x, cm0_w, x0, opacity) + weighted_chamfer(cm1_x, cm1_w, x1, opacity)
            opt_t.zero_grad()
            loss.backward()
            opt_t.step()
        score = float(loss.detach().cpu())
        if best is None or score < best[0]:
            best = (score, axis.detach().clone(), pivot.detach().clone(), amount.detach().clone())

    _, axis_b, pivot_b, amount_b = best
    logits0 = torch.logit(init_m0.detach()).requires_grad_(True)
    logits1 = torch.logit(init_m1.detach()).requires_grad_(True)
    axis = axis_b.clone().requires_grad_(True)
    amount = amount_b.clone().requires_grad_(True)
    params = [logits0, logits1, axis, amount]
    if articulation_type == "revolute":
        pivot = pivot_b.clone().requires_grad_(True)
        params.append(pivot)
    else:
        pivot = torch.zeros(3, device=device)
    opt = torch.optim.Adam(params, lr=0.015)
    for _ in range(refine_steps):
        m0 = torch.sigmoid(logits0)
        m1 = torch.sigmoid(logits1)
        ax = F.normalize(axis, dim=0)
        cm0_x, cm0_w = cross_mobile_sets(x0, x1, opacity, m0, m1, articulation_type, ax, pivot, amount, 0)
        cm1_x, cm1_w = cross_mobile_sets(x0, x1, opacity, m0, m1, articulation_type, ax, pivot, amount, 1)
        loss = weighted_chamfer(cm0_x, cm0_w, x0, opacity) + weighted_chamfer(cm1_x, cm1_w, x1, opacity)
        loss = loss + 0.25 * F.mse_loss(render_density(cm0_x, cm0_w, cameras), target0)
        loss = loss + 0.25 * F.mse_loss(render_density(cm1_x, cm1_w, cameras), target1)
        opt.zero_grad()
        loss.backward()
        opt.step()

    with torch.no_grad():
        ax = F.normalize(axis, dim=0)
        mobility0 = torch.sigmoid(logits0).cpu().numpy()
        mobility1 = torch.sigmoid(logits1).cpu().numpy()
        final_loss = float(loss.detach().cpu())

    print(
        f"[splart] {path.stem}: final_self_supervised_loss={final_loss:.6f}",
        flush=True,
    )
    return {
        "scene": path.stem,
        "articulation_type": articulation_type,
        "axis": ax.cpu().tolist(),
        "pivot": pivot.detach().cpu().tolist(),
        "amount": float(amount.detach().cpu()),
        "mobility_state0": mobility0.tolist(),
        "mobility_state1": mobility1.tolist(),
        "self_supervised_loss": final_loss,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/synthetic_splart")
    parser.add_argument("--output", default="checkpoints/lightweight_splart/results.json")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--mobility-steps", type=int, default=120)
    parser.add_argument("--render-steps", type=int, default=60)
    parser.add_argument("--tries", type=int, default=4)
    parser.add_argument("--coarse-steps", type=int, default=160)
    parser.add_argument("--refine-steps", type=int, default=260)
    args = parser.parse_args()
    torch.set_num_threads(1)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    results = [
        optimize_scene(
            p,
            args.seed + i,
            args.device,
            mobility_steps=args.mobility_steps,
            render_steps=args.render_steps,
            tries=args.tries,
            coarse_steps=args.coarse_steps,
            refine_steps=args.refine_steps,
        )
        for i, p in enumerate(sorted(Path(args.data_dir).glob("*.npz")))
    ]
    out.write_text(json.dumps({"method": "splart_lightweight", "results": results}, indent=2))
    print(json.dumps({"wrote": str(out), "num_scenes": len(results)}, indent=2))


if __name__ == "__main__":
    main()
