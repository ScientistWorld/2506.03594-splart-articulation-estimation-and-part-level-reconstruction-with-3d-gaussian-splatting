"""Baseline that treats the whole object as static."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/synthetic_splart")
    parser.add_argument("--output", default="checkpoints/static_baseline/results.json")
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(Path(args.data_dir).glob("*.npz")):
        data = np.load(path)
        labels = data["labels"].astype(bool)
        pred = np.zeros_like(labels, dtype=bool)
        tp = np.logical_and(pred, labels).sum()
        fp = np.logical_and(pred, ~labels).sum()
        fn = np.logical_and(~pred, labels).sum()
        mobile_iou = float(tp / max(tp + fp + fn, 1))
        static = ~labels
        static_iou = float(np.logical_and(~pred, static).sum() / static.sum())
        recon_chamfer = float(np.mean(np.sum((data["state0"] - data["state1"]) ** 2, axis=1)))
        results.append(
            {
                "scene": path.stem,
                "articulation_type": str(data["articulation_type"]),
                "metrics": {
                    "axis_error_deg": 90.0,
                    "amount_error": abs(float(data["amount"])),
                    "pivot_error": 0.0,
                    "mobile_iou": mobile_iou,
                    "static_iou": static_iou,
                    "mean_part_iou": (mobile_iou + static_iou) / 2,
                    "reconstruction_chamfer": recon_chamfer,
                },
            }
        )
    out.write_text(json.dumps({"method": "static_baseline", "results": results}, indent=2))
    print(json.dumps({"wrote": str(out), "num_scenes": len(results)}, indent=2))


if __name__ == "__main__":
    main()
