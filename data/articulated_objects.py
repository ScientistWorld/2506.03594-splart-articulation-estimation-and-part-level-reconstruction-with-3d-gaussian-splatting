"""Procedural two-part articulated objects observed at two articulation states.

Each scene is a small articulated object (cabinet door, drawer, laptop lid,
scissors, telescoping tube, ...) built from textured box / cylinder surfaces.
The object is observed at two end states of a revolute or prismatic joint.
For each state the observations are

* posed RGB images rendered with an alpha-compositing Gaussian splatting model
  from the dense ground-truth surface, from cameras on the upper hemisphere,
* a sparse, noisy, coloured point cloud of the *visible* surface (what an SfM /
  MVS pre-process would hand to a 3D Gaussian Splatting reconstruction),
  sampled independently for each state (no point correspondence, different
  point counts, a few floaters, random order).

Ground truth (never part of the observations): per-point part labels, the
articulation (axis, pivot, motion amount from state 0 to state 1) and dense
noise-free samples of the visible static / mobile surfaces used to score
part-level geometry.

This module is the visible copy of the generator; the visible train scenes
listed in ``TRAIN_SCENES`` are produced with it.  ``python
data/articulated_objects.py --out DIR`` writes them (inputs and ground truth in
separate files) for development.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

TEMPLATES_REVOLUTE = ("cabinet_door", "laptop", "lidded_box", "scissors", "lever")
TEMPLATES_PRISMATIC = ("drawer", "slider", "telescope", "sliding_panel")
TEMPLATES = TEMPLATES_REVOLUTE + TEMPLATES_PRISMATIC

IMAGE_SIZE = 48
NUM_VIEWS = 20
FOV_DEG = 42.0
GT_GAUSSIAN_SCALE = 0.016
GT_OPACITY = 0.95
BACKGROUND = np.ones(3)
N_DENSE = 3500
N_CANDIDATES = 2400
OBJECT_RADIUS = 0.62
VIS_TOL = 0.03

# Visible train scenes: (seed, template).  Two per template.
TRAIN_SCENES = tuple((1000 + i, t) for i, t in enumerate(TEMPLATES + TEMPLATES))


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------


def rotation_matrix(axis, angle: float) -> np.ndarray:
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s = np.cos(angle), np.sin(angle)
    C = 1.0 - c
    return np.array(
        [
            [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C],
        ]
    )


def _box(center, half, part, color, open_faces=(), R=None, tex=None) -> dict:
    return {
        "kind": "box",
        "center": np.asarray(center, dtype=np.float64),
        "R": np.eye(3) if R is None else np.asarray(R, dtype=np.float64),
        "half": np.asarray(half, dtype=np.float64),
        "open": tuple(open_faces),
        "part": int(part),
        "color": np.asarray(color, dtype=np.float64),
        "tex": tex,
    }


def _cyl(center, radius, half_h, part, color, caps=(True, True), R=None, tex=None) -> dict:
    return {
        "kind": "cyl",
        "center": np.asarray(center, dtype=np.float64),
        "R": np.eye(3) if R is None else np.asarray(R, dtype=np.float64),
        "radius": float(radius),
        "half_h": float(half_h),
        "caps": (bool(caps[0]), bool(caps[1])),
        "part": int(part),
        "color": np.asarray(color, dtype=np.float64),
        "tex": tex,
    }


_FACES = (("+x", 0, 1.0), ("-x", 0, -1.0), ("+y", 1, 1.0), ("-y", 1, -1.0), ("+z", 2, 1.0), ("-z", 2, -1.0))


def _box_faces(prim: dict) -> list:
    h = prim["half"]
    out = []
    for name, ax, sign in _FACES:
        if name in prim["open"]:
            continue
        a1, a2 = [i for i in range(3) if i != ax]
        out.append((ax, sign, a1, a2, 4.0 * h[a1] * h[a2]))
    return out


def prim_area(prim: dict) -> float:
    if prim["kind"] == "box":
        return float(sum(f[4] for f in _box_faces(prim)))
    r, hh = prim["radius"], prim["half_h"]
    return float(2.0 * np.pi * r * 2.0 * hh + np.pi * r * r * sum(prim["caps"]))


def sample_local(prim: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    if n <= 0:
        return np.zeros((0, 3))
    if prim["kind"] == "box":
        faces = _box_faces(prim)
        areas = np.array([f[4] for f in faces])
        idx = rng.choice(len(faces), size=n, p=areas / areas.sum())
        u = rng.uniform(-1.0, 1.0, size=(n, 2))
        h = prim["half"]
        pts = np.zeros((n, 3))
        for k, (ax, sign, a1, a2, _) in enumerate(faces):
            sel = idx == k
            pts[sel, ax] = sign * h[ax]
            pts[sel, a1] = u[sel, 0] * h[a1]
            pts[sel, a2] = u[sel, 1] * h[a2]
        return pts
    r, hh = prim["radius"], prim["half_h"]
    comps = np.array(
        [
            2.0 * np.pi * r * 2.0 * hh,
            np.pi * r * r if prim["caps"][0] else 0.0,
            np.pi * r * r if prim["caps"][1] else 0.0,
        ]
    )
    idx = rng.choice(3, size=n, p=comps / comps.sum())
    phi = rng.uniform(0.0, 2.0 * np.pi, size=n)
    zz = rng.uniform(-hh, hh, size=n)
    rad = r * np.sqrt(rng.uniform(0.0, 1.0, size=n))
    pts = np.zeros((n, 3))
    lat = idx == 0
    pts[lat, 0] = r * np.cos(phi[lat])
    pts[lat, 1] = r * np.sin(phi[lat])
    pts[lat, 2] = zz[lat]
    for k, zc in ((1, -hh), (2, hh)):
        sel = idx == k
        pts[sel, 0] = rad[sel] * np.cos(phi[sel])
        pts[sel, 1] = rad[sel] * np.sin(phi[sel])
        pts[sel, 2] = zc
    return pts


def prim_colors(prim: dict, local: np.ndarray) -> np.ndarray:
    base = prim["color"]
    tex = prim["tex"]
    n = len(local)
    if tex is None or n == 0:
        return np.repeat(base[None], n, axis=0)
    f, ph = tex["freq"], tex["phase"]
    if tex["kind"] == "stripes":
        s = np.sign(np.sin(2.0 * np.pi * f * local[:, tex["axes"][0]] + ph))
    else:
        a, b = tex["axes"]
        s = np.sign(np.sin(2.0 * np.pi * f * local[:, a] + ph) * np.sin(2.0 * np.pi * f * local[:, b] + ph))
    return np.clip(base[None] + tex["amp"] * s[:, None] * tex["dir"][None], 0.02, 0.98)


def to_world(prim: dict, local: np.ndarray) -> np.ndarray:
    return local @ prim["R"].T + prim["center"]


def move_prim(prim: dict, Rm: np.ndarray, tm: np.ndarray) -> dict:
    out = dict(prim)
    out["center"] = Rm @ prim["center"] + tm
    out["R"] = Rm @ prim["R"]
    return out


# ---------------------------------------------------------------------------
# templates (canonical frame, z up)
# ---------------------------------------------------------------------------


def _rand_color(rng):
    return rng.uniform(0.12, 0.88, size=3)


def _near_color(rng, c, d=0.08):
    return np.clip(c + rng.uniform(-d, d, size=3), 0.05, 0.95)


def _rand_tex(rng):
    kind = rng.choice(["stripes", "checker", "none"], p=[0.45, 0.35, 0.2])
    if kind == "none":
        return None
    axes = tuple(int(a) for a in rng.choice(3, size=2, replace=False))
    direction = rng.normal(size=3)
    direction = 0.6 * direction / np.linalg.norm(direction) + 0.4 * np.ones(3) / np.sqrt(3.0)
    return {
        "kind": str(kind),
        "axes": axes,
        "freq": float(rng.uniform(3.0, 9.0)),
        "phase": float(rng.uniform(0.0, 2.0 * np.pi)),
        "amp": float(rng.uniform(0.08, 0.16)),
        "dir": direction / np.linalg.norm(direction),
    }


def _part_color(rng, static_color, similar_prob=0.35):
    if rng.random() < similar_prob:
        return _near_color(rng, static_color, 0.1)
    return _rand_color(rng)


def _t_cabinet_door(rng):
    W, D, H = rng.uniform(0.55, 0.9), rng.uniform(0.3, 0.55), rng.uniform(0.5, 0.95)
    cb = _rand_color(rng)
    prims = [_box((0, 0, 0), (W / 2, D / 2, H / 2), 0, cb, open_faces=("-y",), tex=_rand_tex(rng))]
    if rng.random() < 0.6:
        prims.append(
            _box((0, 0, rng.uniform(-0.2, 0.2) * H), (W / 2 * 0.97, D / 2 * 0.95, 0.01), 0, _rand_color(rng))
        )
    s = float(rng.choice([-1.0, 1.0]))
    t = 0.013
    yd = -D / 2 - t - 0.002
    prims.append(_box((0, yd, 0), (W / 2, t, H / 2), 1, _part_color(rng, cb), tex=_rand_tex(rng)))
    prims.append(_box((-s * W * 0.38, yd - t - 0.02, 0), (0.025, 0.02, 0.045), 1, _rand_color(rng)))
    joint = {"type": "revolute", "axis": np.array([0.0, 0.0, s]), "pivot": np.array([s * W / 2, yd, 0.0])}
    qa = rng.uniform(0.0, np.deg2rad(8.0))
    qb = qa + rng.uniform(np.deg2rad(25.0), np.deg2rad(100.0))
    return prims, joint, (qa, qb)


def _t_drawer(rng):
    W, D, H = rng.uniform(0.5, 0.85), rng.uniform(0.4, 0.65), rng.uniform(0.25, 0.5)
    cb = _rand_color(rng)
    prims = [_box((0, 0, 0), (W / 2, D / 2, H / 2), 0, cb, open_faces=("-y",), tex=_rand_tex(rng))]
    t = 0.013
    yf = -D / 2 - t - 0.002
    prims.append(_box((0, yf, 0), (W / 2 * 0.95, t, H / 2 * 0.92), 1, _part_color(rng, cb), tex=_rand_tex(rng)))
    prims.append(
        _box((0, -0.02, -H * 0.04), (W / 2 * 0.88, D / 2 * 0.9, H / 2 * 0.78), 1, _rand_color(rng), open_faces=("+z", "-y"))
    )
    prims.append(_box((0, yf - t - 0.02, H * 0.12), (min(0.12, W * 0.2), 0.018, 0.018), 1, _rand_color(rng)))
    joint = {"type": "prismatic", "axis": np.array([0.0, -1.0, 0.0]), "pivot": np.zeros(3)}
    qa = rng.uniform(0.0, 0.03)
    qb = qa + rng.uniform(0.35, 0.8) * D
    return prims, joint, (qa, qb)


def _t_laptop(rng):
    W, D = rng.uniform(0.6, 0.95), rng.uniform(0.4, 0.62)
    tb, tl = 0.022, 0.012
    cb = _rand_color(rng)
    prims = [
        _box((0, 0, 0), (W / 2, D / 2, tb), 0, cb, tex=_rand_tex(rng)),
        _box((0, -D * 0.06, tb + 0.002), (W / 2 * 0.85, D / 2 * 0.55, 0.002), 0, _rand_color(rng)),
        _box((0, 0, tb + 0.006 + tl), (W / 2, D / 2, tl), 1, _part_color(rng, cb), tex=_rand_tex(rng)),
    ]
    joint = {"type": "revolute", "axis": np.array([-1.0, 0.0, 0.0]), "pivot": np.array([0.0, D / 2, tb + 0.006])}
    qa = rng.uniform(np.deg2rad(15.0), np.deg2rad(60.0))
    qb = min(qa + rng.uniform(np.deg2rad(25.0), np.deg2rad(75.0)), np.deg2rad(140.0))
    return prims, joint, (qa, qb)


def _t_lidded_box(rng):
    W, D, H = rng.uniform(0.45, 0.8), rng.uniform(0.35, 0.6), rng.uniform(0.25, 0.5)
    cb = _rand_color(rng)
    prims = [
        _box((0, 0, 0), (W / 2, D / 2, H / 2), 0, cb, open_faces=("+z",), tex=_rand_tex(rng)),
        _box((0, 0, H / 2 + 0.014), (W / 2 + 0.012, D / 2 + 0.012, 0.012), 1, _part_color(rng, cb), tex=_rand_tex(rng)),
    ]
    joint = {"type": "revolute", "axis": np.array([-1.0, 0.0, 0.0]), "pivot": np.array([0.0, D / 2 + 0.012, H / 2 + 0.002])}
    qa = rng.uniform(0.0, np.deg2rad(10.0))
    qb = qa + rng.uniform(np.deg2rad(30.0), np.deg2rad(110.0))
    return prims, joint, (qa, qb)


def _t_scissors(rng):
    L = rng.uniform(0.7, 1.0)
    w = rng.uniform(0.05, 0.08)
    th = 0.012
    beta = rng.uniform(np.deg2rad(10.0), np.deg2rad(25.0))
    ca = _rand_color(rng)
    cb = _part_color(rng, ca, similar_prob=0.5)
    prims = []
    for part, ang, z, col in ((0, beta, 0.0, ca), (1, -beta, 2.2 * th, cb)):
        Rz = rotation_matrix([0, 0, 1], ang)
        prims.append(_box(Rz @ np.array([0.1 * L, 0.0, z]), (L / 2, w / 2, th), part, col, R=Rz, tex=_rand_tex(rng)))
        prims.append(_box(Rz @ np.array([-0.42 * L, 0.0, z]), (0.08, 0.06, th), part, _near_color(rng, col, 0.15), R=Rz))
    joint = {"type": "revolute", "axis": np.array([0.0, 0.0, 1.0]), "pivot": np.array([0.0, 0.0, th])}
    qa = 0.0
    qb = float(rng.choice([-1.0, 1.0])) * rng.uniform(np.deg2rad(15.0), np.deg2rad(50.0))
    return prims, joint, (qa, qb)


def _t_lever(rng):
    W, D, H = rng.uniform(0.35, 0.55), rng.uniform(0.3, 0.45), rng.uniform(0.15, 0.3)
    cb = _rand_color(rng)
    L = rng.uniform(0.35, 0.55)
    zp = H / 2 + 0.16
    prims = [
        _box((0, 0, 0), (W / 2, D / 2, H / 2), 0, cb, tex=_rand_tex(rng)),
        _box((0, 0, H / 2 + 0.08), (0.03, 0.03, 0.08), 0, _rand_color(rng)),
        _box((L / 2 - 0.04, 0, zp), (L / 2, 0.025, 0.025), 1, _part_color(rng, cb), tex=_rand_tex(rng)),
        _box((L - 0.04, 0, zp), (0.04, 0.04, 0.04), 1, _rand_color(rng)),
    ]
    joint = {"type": "revolute", "axis": np.array([0.0, 1.0, 0.0]), "pivot": np.array([0.0, 0.0, zp])}
    qa = rng.uniform(np.deg2rad(-40.0), np.deg2rad(10.0))
    qb = qa - rng.uniform(np.deg2rad(20.0), np.deg2rad(60.0))
    return prims, joint, (qa, qb)


def _t_slider(rng):
    L = rng.uniform(0.8, 1.1)
    cr = _rand_color(rng)
    prims = [
        _box((0, 0, 0), (L / 2, 0.09, 0.03), 0, cr, tex=_rand_tex(rng)),
        _box((L / 2 - 0.02, 0, 0.06), (0.02, 0.09, 0.03), 0, _rand_color(rng)),
        _box((-L / 2 + 0.02, 0, 0.06), (0.02, 0.09, 0.03), 0, _rand_color(rng)),
    ]
    flat = rng.random() < 0.5
    bh = 0.02 if flat else rng.uniform(0.04, 0.07)
    bw = rng.uniform(0.07, 0.11)
    travel = rng.uniform(0.15, 0.45)
    lo, hi = -L / 2 + 0.05 + bw, L / 2 - 0.05 - bw - travel
    x0 = rng.uniform(lo, max(lo, hi))
    color = _near_color(rng, cr, 0.06) if flat else _rand_color(rng)
    prims.append(_box((x0, 0, 0.03 + bh + 0.002), (bw, 0.075, bh), 1, color, tex=_rand_tex(rng)))
    joint = {"type": "prismatic", "axis": np.array([1.0, 0.0, 0.0]), "pivot": np.zeros(3)}
    return prims, joint, (0.0, travel)


def _t_telescope(rng):
    R = rng.uniform(0.08, 0.13)
    Lo = rng.uniform(0.3, 0.45)
    Li = rng.uniform(0.7, 0.9) * Lo
    s0 = rng.uniform(0.02, 0.08)
    Ry = rotation_matrix([0, 1, 0], np.pi / 2)  # local z -> world x
    co = _rand_color(rng)
    prims = [
        _cyl((0, 0, 0), R, Lo, 0, co, caps=(True, False), R=Ry, tex=_rand_tex(rng)),
        _box((-0.1 * Lo, 0, R + 0.014), (Lo * 0.5, 0.015, 0.012), 0, _rand_color(rng)),
        _cyl((Lo + s0 - Li, 0, 0), 0.72 * R, Li, 1, _part_color(rng, co), caps=(True, True), R=Ry, tex=_rand_tex(rng)),
    ]
    travel = rng.uniform(0.15, min(0.4, Li - s0 - 0.05))
    joint = {"type": "prismatic", "axis": np.array([1.0, 0.0, 0.0]), "pivot": np.zeros(3)}
    return prims, joint, (0.0, travel)


def _t_sliding_panel(rng):
    W, H = rng.uniform(0.7, 1.0), rng.uniform(0.5, 0.8)
    cb = _rand_color(rng)
    prims = [
        _box((0, 0.03, 0), (W / 2, 0.012, H / 2), 0, cb, tex=_rand_tex(rng)),
        _box((0, -0.01, H / 2 + 0.015), (W / 2, 0.03, 0.015), 0, _rand_color(rng)),
        _box((0, -0.01, -H / 2 - 0.015), (W / 2, 0.03, 0.015), 0, _rand_color(rng)),
    ]
    pw = W / 2 * rng.uniform(0.45, 0.55)
    prims.append(_box((-W / 2 + pw, -0.02, 0), (pw, 0.01, H / 2 * 0.97), 1, _part_color(rng, cb), tex=_rand_tex(rng)))
    prims.append(_box((-W / 2 + 2 * pw - 0.05, -0.042, 0), (0.015, 0.012, 0.06), 1, _rand_color(rng)))
    travel = rng.uniform(0.35, 0.95) * (W - 2 * pw)
    joint = {"type": "prismatic", "axis": np.array([1.0, 0.0, 0.0]), "pivot": np.zeros(3)}
    return prims, joint, (0.0, travel)


_BUILDERS = {
    "cabinet_door": _t_cabinet_door,
    "laptop": _t_laptop,
    "lidded_box": _t_lidded_box,
    "scissors": _t_scissors,
    "lever": _t_lever,
    "drawer": _t_drawer,
    "slider": _t_slider,
    "telescope": _t_telescope,
    "sliding_panel": _t_sliding_panel,
}


# ---------------------------------------------------------------------------
# cameras and rendering
# ---------------------------------------------------------------------------


def look_at(position: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """World-to-camera rotation/translation (OpenCV: x right, y down, z forward)."""
    f = target - position
    f = f / np.linalg.norm(f)
    r = np.cross(f, np.array([0.0, 0.0, 1.0]))
    if np.linalg.norm(r) < 1e-6:
        r = np.cross(f, np.array([0.0, 1.0, 0.0]))
    r = r / np.linalg.norm(r)
    d = np.cross(f, r)
    R = np.stack([r, d, f])
    return R, -R @ position


def sample_cameras(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    Rs, ts = [], []
    for _ in range(n):
        elev = np.deg2rad(rng.uniform(12.0, 65.0))
        az = rng.uniform(0.0, 2.0 * np.pi)
        dist = rng.uniform(2.4, 2.9)
        pos = dist * np.array([np.cos(elev) * np.cos(az), np.cos(elev) * np.sin(az), np.sin(elev)])
        R, t = look_at(pos, rng.uniform(-0.03, 0.03, size=3))
        Rs.append(R)
        ts.append(t)
    return np.stack(Rs), np.stack(ts)


def intrinsics(size: int = IMAGE_SIZE, fov_deg: float = FOV_DEG) -> np.ndarray:
    f = 0.5 * size / np.tan(np.deg2rad(fov_deg) / 2.0)
    return np.array([f, f, size / 2.0, size / 2.0])


def render_gaussians(means, scales, colors, opacities, R, t, intr, size, background, chunk=768):
    """Alpha-composited isotropic Gaussian splatting (front-to-back by depth).

    Pixel (i, j) has centre (u, v) = (j + 0.5, i + 0.5).  A Gaussian with world
    standard deviation s at depth z has image variance (fx s / z)^2 + 0.3.
    Returns rgb (H, W, 3), expected depth (H, W) and accumulated alpha (H, W).
    """
    pc = means @ R.T + t
    keep = pc[:, 2] > 0.05
    pc, scales, colors, opacities = pc[keep], scales[keep], colors[keep], opacities[keep]
    fx, fy, cx, cy = intr
    z = pc[:, 2]
    u = fx * pc[:, 0] / z + cx
    v = fy * pc[:, 1] / z + cy
    var = (fx * scales / z) ** 2 + 0.3
    order = np.argsort(z, kind="stable")
    u, v, var, colors, opacities, z = u[order], v[order], var[order], colors[order], opacities[order], z[order]
    ys, xs = np.mgrid[0:size, 0:size]
    pu = xs.ravel() + 0.5
    pv = ys.ravel() + 0.5
    P = size * size
    rgb = np.empty((P, 3))
    depth = np.empty(P)
    acc = np.empty(P)
    for s in range(0, P, chunk):
        e = min(P, s + chunk)
        du = pu[None, s:e] - u[:, None]
        dv = pv[None, s:e] - v[:, None]
        alpha = np.minimum(0.99, opacities[:, None] * np.exp(-0.5 * (du * du + dv * dv) / var[:, None]))
        T = np.cumprod(1.0 - alpha, axis=0)
        Tex = np.concatenate([np.ones((1, e - s)), T[:-1]], axis=0)
        w = alpha * Tex
        a = w.sum(axis=0)
        rgb[s:e] = w.T @ colors + (1.0 - a)[:, None] * background[None]
        depth[s:e] = (w.T @ z) / np.maximum(a, 1e-6)
        acc[s:e] = a
    return rgb.reshape(size, size, 3), depth.reshape(size, size), acc.reshape(size, size)


def visible_mask(points, Rs, ts, intr, depths, accs, size, tol=VIS_TOL, min_views=2) -> np.ndarray:
    fx, fy, cx, cy = intr
    count = np.zeros(len(points), dtype=np.int64)
    for R, t, D, A in zip(Rs, ts, depths, accs):
        pc = points @ R.T + t
        z = pc[:, 2]
        zs = np.where(z > 0.05, z, 1.0)
        iu = np.floor(fx * pc[:, 0] / zs + cx).astype(np.int64)
        iv = np.floor(fy * pc[:, 1] / zs + cy).astype(np.int64)
        inside = (z > 0.05) & (iu >= 0) & (iu < size) & (iv >= 0) & (iv < size)
        idx = np.where(inside)[0]
        d = D[iv[idx], iu[idx]]
        a = A[iv[idx], iu[idx]]
        ok = (a > 0.5) & (np.abs(z[idx] - d) < tol)
        count[idx[ok]] += 1
    return count >= min_views


# ---------------------------------------------------------------------------
# scene generation
# ---------------------------------------------------------------------------


def _allocate(total: int, areas, minimum: int) -> np.ndarray:
    areas = np.asarray(areas, dtype=np.float64)
    counts = np.maximum(minimum, np.round(total * areas / areas.sum())).astype(np.int64)
    return counts


def _random_pose(rng) -> np.ndarray:
    yaw = rotation_matrix([0, 0, 1], rng.uniform(0.0, 2.0 * np.pi))
    phi = rng.uniform(0.0, 2.0 * np.pi)
    tilt = rotation_matrix([np.cos(phi), np.sin(phi), 0.0], np.deg2rad(rng.uniform(0.0, 20.0)))
    return tilt @ yaw


def generate_scene(seed: int, template: str) -> tuple[dict, dict]:
    """Return (inputs, ground_truth) for one scene."""
    rng = np.random.default_rng(int(seed))
    prims, joint, (qa, qb) = _BUILDERS[template](rng)
    if rng.random() < 0.5:
        qa, qb = qb, qa
    jtype = joint["type"]
    axis_c = joint["axis"] / np.linalg.norm(joint["axis"])
    pivot_c = np.asarray(joint["pivot"], dtype=np.float64)

    def motion(q):
        if jtype == "revolute":
            Rm = rotation_matrix(axis_c, q)
            return Rm, pivot_c - Rm @ pivot_c
        return np.eye(3), q * axis_c

    states_prims = []
    for q in (qa, qb):
        Rm, tm = motion(q)
        states_prims.append([move_prim(p, Rm, tm) if p["part"] == 1 else p for p in prims])

    # dense ground-truth surface samples (shared local coordinates across states)
    counts = _allocate(N_DENSE, [prim_area(p) for p in prims], 24)
    local = [sample_local(p, int(n), rng) for p, n in zip(prims, counts)]
    dense = [np.concatenate([to_world(sp, lc) for sp, lc in zip(states_prims[l], local)]) for l in (0, 1)]
    dense_col = np.concatenate([prim_colors(p, lc) for p, lc in zip(prims, local)])
    dense_part = np.concatenate([np.full(len(lc), p["part"], dtype=np.int64) for p, lc in zip(prims, local)])

    allpts = np.concatenate(dense)
    center = allpts.mean(axis=0)
    radius = float(np.linalg.norm(allpts - center, axis=1).max())
    scale = OBJECT_RADIUS / radius * rng.uniform(0.9, 1.05)
    G = _random_pose(rng)
    shift = rng.uniform(-0.04, 0.04, size=3)

    def world(x):
        return scale * (np.asarray(x) - center) @ G.T + shift

    dense_w = [world(d) for d in dense]
    axis_w = G @ axis_c
    pivot_w = world(pivot_c[None])[0]
    amount = float(qb - qa) if jtype == "revolute" else float(scale * (qb - qa))

    intr = intrinsics()
    cams = [sample_cameras(rng, NUM_VIEWS) for _ in (0, 1)]
    n_dense = len(dense_part)
    g_scales = np.full(n_dense, GT_GAUSSIAN_SCALE)
    g_opac = np.full(n_dense, GT_OPACITY)
    images, depths, accs = [], [], []
    for l in (0, 1):
        im_l, d_l, a_l = [], [], []
        for R, t in zip(*cams[l]):
            rgb, dep, acc = render_gaussians(dense_w[l], g_scales, dense_col, g_opac, R, t, intr, IMAGE_SIZE, BACKGROUND)
            im_l.append(rgb)
            d_l.append(dep)
            a_l.append(acc)
        images.append(np.stack(im_l))
        depths.append(np.stack(d_l))
        accs.append(np.stack(a_l))

    vis = [visible_mask(dense_w[l], cams[l][0], cams[l][1], intr, depths[l], accs[l], IMAGE_SIZE) for l in (0, 1)]
    seen = vis[0] | vis[1]
    gt_static = dense_w[0][(dense_part == 0) & seen]
    gt_mobile0 = dense_w[0][(dense_part == 1) & seen]

    noise = rng.uniform(0.003, 0.010)
    floater_frac = rng.uniform(0.0, 0.05)
    lo = allpts.min(axis=0)
    bb_w = world(np.stack([allpts.min(axis=0), allpts.max(axis=0)]))
    bb_lo, bb_hi = bb_w.min(axis=0) - 0.1, bb_w.max(axis=0) + 0.1
    del lo

    points, colors, labels = [], [], []
    ccounts = _allocate(N_CANDIDATES, [prim_area(p) for p in prims], 16)
    for l in (0, 1):
        cl = [sample_local(p, int(n), rng) for p, n in zip(prims, ccounts)]
        cand = world(np.concatenate([to_world(sp, lc) for sp, lc in zip(states_prims[l], cl)]))
        ccol = np.concatenate([prim_colors(p, lc) for p, lc in zip(prims, cl)])
        cpart = np.concatenate([np.full(len(lc), p["part"], dtype=np.int64) for p, lc in zip(prims, cl)])
        cvis = np.where(visible_mask(cand, cams[l][0], cams[l][1], intr, depths[l], accs[l], IMAGE_SIZE))[0]
        n_target = int(rng.integers(380, 601))
        if len(cvis) > n_target:
            cvis = rng.choice(cvis, size=n_target, replace=False)
        pts = cand[cvis] + rng.normal(0.0, noise, size=(len(cvis), 3))
        col = np.clip(ccol[cvis] + rng.normal(0.0, 0.03, size=(len(cvis), 3)), 0.0, 1.0)
        lab = cpart[cvis]
        n_f = int(rng.binomial(len(cvis), floater_frac))
        if n_f > 0:
            pts = np.concatenate([pts, rng.uniform(bb_lo, bb_hi, size=(n_f, 3))])
            col = np.concatenate([col, rng.uniform(0.0, 1.0, size=(n_f, 3))])
            lab = np.concatenate([lab, np.full(n_f, -1, dtype=np.int64)])
        perm = rng.permutation(len(pts))
        points.append(pts[perm])
        colors.append(col[perm])
        labels.append(lab[perm])

    inputs = {
        "articulation_type": np.array(jtype),
        "points0": points[0].astype(np.float32),
        "colors0": colors[0].astype(np.float32),
        "points1": points[1].astype(np.float32),
        "colors1": colors[1].astype(np.float32),
        "images0": np.round(np.clip(images[0], 0, 1) * 255).astype(np.uint8),
        "images1": np.round(np.clip(images[1], 0, 1) * 255).astype(np.uint8),
        "cams0_R": cams[0][0].astype(np.float32),
        "cams0_t": cams[0][1].astype(np.float32),
        "cams1_R": cams[1][0].astype(np.float32),
        "cams1_t": cams[1][1].astype(np.float32),
        "intrinsics": intr.astype(np.float32),
        "image_size": np.array(IMAGE_SIZE),
        "background": BACKGROUND.astype(np.float32),
    }
    gt = {
        "template": np.array(template),
        "articulation_type": np.array(jtype),
        "labels0": labels[0].astype(np.int64),
        "labels1": labels[1].astype(np.int64),
        "axis": axis_w.astype(np.float64),
        "pivot": pivot_w.astype(np.float64),
        "amount": np.array(amount, dtype=np.float64),
        "gt_static": gt_static.astype(np.float64),
        "gt_mobile0": gt_mobile0.astype(np.float64),
        "noise": np.array(noise),
        "floater_frac": np.array(floater_frac),
    }
    return inputs, gt


def write_scenes(out_dir: str | Path, scenes=TRAIN_SCENES) -> None:
    out = Path(out_dir)
    (out / "inputs").mkdir(parents=True, exist_ok=True)
    (out / "gt").mkdir(parents=True, exist_ok=True)
    for i, (seed, template) in enumerate(scenes):
        inputs, gt = generate_scene(seed, template)
        name = f"train_{i:03d}"
        np.savez(out / "inputs" / f"{name}.npz", **inputs)
        np.savez(out / "gt" / f"{name}.npz", **gt)
        print(f"wrote {name} ({template}, seed {seed})", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/downloads/train_scenes")
    args = parser.parse_args()
    write_scenes(args.out)
