"""No-motion baseline: the whole object is static and the joint does not move.

Writes one prediction per scene in the artifact format of briefing/evaluation.md:
state-0 input points become static Gaussians, the mobile set is empty and the
motion amount is zero.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def knn_scale(points: np.ndarray, k: int = 3) -> np.ndarray:
    out = np.empty(len(points))
    for s in range(0, len(points), 1024):
        x = points[s : s + 1024]
        d2 = ((x[:, None, :] - points[None, :, :]) ** 2).sum(-1)
        d2.sort(axis=1)
        out[s : s + 1024] = np.sqrt(d2[:, 1 : k + 1].mean(1))
    return np.clip(out, 0.004, 0.05)


def empty_set():
    return np.zeros((0, 3), np.float32), np.zeros(0, np.float32), np.zeros((0, 3), np.float32), np.zeros(0, np.float32)


def write_prediction(path: Path, axis, pivot, amount, static, mobile) -> None:
    out = {"axis": np.asarray(axis, np.float64), "pivot": np.asarray(pivot, np.float64), "amount": np.array(float(amount))}
    for name, (m, s, c, o) in (("static", static), ("mobile", mobile)):
        out[f"{name}_means"] = np.asarray(m, np.float32).reshape(-1, 3)
        out[f"{name}_scales"] = np.asarray(s, np.float32).reshape(-1)
        out[f"{name}_colors"] = np.clip(np.asarray(c, np.float32).reshape(-1, 3), 0, 1)
        out[f"{name}_opacities"] = np.clip(np.asarray(o, np.float32).reshape(-1), 0, 1)
    np.savez(path, **out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", default=["data/scenes/train/inputs", "data/scenes/test/inputs"])
    parser.add_argument("--out", default="checkpoints/static_baseline")
    args = parser.parse_args()
    pred_dir = Path(args.out) / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for path in sorted(p for d in args.inputs for p in Path(d).glob("*.npz")):
        with np.load(path, allow_pickle=False) as d:
            pts = d["points0"].astype(np.float64)
            cols = d["colors0"].astype(np.float64)
        static = (pts, knn_scale(pts), cols, np.full(len(pts), 0.9))
        write_prediction(pred_dir / f"{path.stem}.npz", [0.0, 0.0, 1.0], [0.0, 0.0, 0.0], 0.0, static, empty_set())
        n += 1
    print(f"[static_baseline] wrote {n} predictions to {pred_dir}")


if __name__ == "__main__":
    main()
