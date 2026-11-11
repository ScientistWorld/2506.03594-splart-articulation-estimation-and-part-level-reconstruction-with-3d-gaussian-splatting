"""Correspondence-free geometric baseline: displacement split + multi-start ICP.

1. Remove isolated points (floaters) from each state's point cloud.
2. Points of one state farther than tau from every point of the other state are
   labelled mobile (they moved); the rest are static.
3. Register the state-0 mobile points onto the state-1 mobile points with
   trimmed ICP from many random initial rotations (translation-only for
   prismatic joints) and keep the lowest trimmed residual.
4. Convert the rigid motion to the known joint type (revolute: axis, angle and
   least-squares pivot; prismatic: direction and distance).

With ``--restarts`` large this enumerates initial rotations exhaustively, which
is the brute-force alternative to gradient-based articulation search.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from static_baseline import knn_scale, write_prediction  # noqa: E402


def nn(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Nearest neighbour of each row of a in b: (distance, index)."""
    dist = np.empty(len(a))
    idx = np.empty(len(a), dtype=np.int64)
    bb = (b * b).sum(1)
    for s in range(0, len(a), 1024):
        x = a[s : s + 1024]
        d2 = (x * x).sum(1)[:, None] + bb[None, :] - 2.0 * x @ b.T
        j = d2.argmin(1)
        idx[s : s + 1024] = j
        dist[s : s + 1024] = np.sqrt(np.maximum(d2[np.arange(len(x)), j], 0.0))
    return dist, idx


def remove_outliers(p: np.ndarray, c: np.ndarray, k: int = 8):
    d2 = ((p[:, None, :] - p[None, :, :]) ** 2).sum(-1)
    d2.sort(axis=1)
    md = np.sqrt(d2[:, 1 : k + 1]).mean(1)
    keep = md <= np.median(md) + 3.0 * np.median(np.abs(md - np.median(md))) + 1e-9
    return p[keep], c[keep]


def kabsch(a: np.ndarray, b: np.ndarray):
    ca, cb = a.mean(0), b.mean(0)
    H = (a - ca).T @ (b - cb)
    U, _, Vt = np.linalg.svd(H)
    D = np.diag([1.0, 1.0, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, cb - R @ ca


def icp(src, dst, R, t, translation_only: bool, iters: int = 40, trim: float = 0.8):
    for _ in range(iters):
        moved = src @ R.T + t
        d, j = nn(moved, dst)
        keep = d <= np.quantile(d, trim)
        if translation_only:
            t = t + (dst[j[keep]] - moved[keep]).mean(0)
        else:
            R, t = kabsch(src[keep], dst[j[keep]])
    d, _ = nn(src @ R.T + t, dst)
    return R, t, float(np.sort(d)[: max(1, int(trim * len(d)))].mean())


def random_rotation(rng) -> np.ndarray:
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    w, x, y, z = q
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def to_joint(R, t, jtype):
    if jtype == "prismatic":
        d = float(np.linalg.norm(t))
        axis = t / d if d > 1e-9 else np.array([1.0, 0.0, 0.0])
        return axis, np.zeros(3), d
    angle = float(np.arccos(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)))
    w = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    if np.linalg.norm(w) < 1e-9:
        return np.array([0.0, 0.0, 1.0]), np.zeros(3), 0.0
    axis = w / np.linalg.norm(w)
    pivot = np.linalg.lstsq(np.eye(3) - R, t, rcond=None)[0]
    pivot = pivot - axis * float(pivot @ axis)
    return axis, pivot, angle


def solve(inp: dict, restarts: int, seed: int):
    jtype = str(inp["articulation_type"])
    p0, c0 = remove_outliers(inp["points0"].astype(np.float64), inp["colors0"].astype(np.float64))
    p1, _ = remove_outliers(inp["points1"].astype(np.float64), inp["colors1"].astype(np.float64))
    spacing = float(np.median(nn(p0[: len(p0) // 2], p0[len(p0) // 2 :])[0]))
    tau = max(3.0 * spacing, 0.03)
    d01, _ = nn(p0, p1)
    d10, _ = nn(p1, p0)
    mob0, mob1 = d01 > tau, d10 > tau
    axis, pivot, amount = np.array([0.0, 0.0, 1.0]), np.zeros(3), 0.0
    if mob0.sum() >= 10 and mob1.sum() >= 10:
        a, b = p0[mob0], p1[mob1]
        rng = np.random.default_rng(seed)
        best = None
        for k in range(restarts):
            R0 = np.eye(3) if (k == 0 or jtype == "prismatic") else random_rotation(rng)
            t0 = b.mean(0) - R0 @ a.mean(0)
            R, t, res = icp(a, b, R0, t0, translation_only=(jtype == "prismatic"))
            if best is None or res < best[0]:
                best = (res, R, t)
            if jtype == "prismatic":
                break
        axis, pivot, amount = to_joint(best[1], best[2], jtype)
    scale = knn_scale(p0)
    static = (p0[~mob0], scale[~mob0], c0[~mob0], np.full((~mob0).sum(), 0.9))
    mobile = (p0[mob0], scale[mob0], c0[mob0], np.full(mob0.sum(), 0.9))
    return axis, pivot, amount, static, mobile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", default=["data/scenes/train/inputs", "data/scenes/test/inputs"])
    parser.add_argument("--out", default="checkpoints/icp_baseline")
    parser.add_argument("--restarts", type=int, default=24)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    pred_dir = Path(args.out) / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for d in args.inputs for p in Path(d).glob("*.npz"))
    for path in paths:
        with np.load(path, allow_pickle=False) as d:
            inp = {k: np.asarray(d[k]) for k in ("articulation_type", "points0", "colors0", "points1", "colors1")}
        axis, pivot, amount, static, mobile = solve(inp, args.restarts, args.seed)
        write_prediction(pred_dir / f"{path.stem}.npz", axis, pivot, amount, static, mobile)
        print(f"[icp_baseline] {path.stem}: amount={amount:.3f}", flush=True)
    print(f"[icp_baseline] wrote {len(paths)} predictions to {pred_dir}")


if __name__ == "__main__":
    main()
