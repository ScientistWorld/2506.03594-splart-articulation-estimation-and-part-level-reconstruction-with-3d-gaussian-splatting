"""Method-agnostic evaluator for articulated Gaussian output artifacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def aggregate(paths: list[Path]) -> dict:
    grouped = defaultdict(list)
    for path in paths:
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        method = data["method"]
        for scene in data["results"]:
            metrics = scene["metrics"]
            success = (
                metrics["axis_error_deg"] < 5.0
                and metrics["mean_part_iou"] > 0.75
                and metrics["reconstruction_chamfer"] < 0.01
            )
            grouped[method].append({**metrics, "success": float(success)})

    out = {"experiments": {"synthetic_articulated_gaussians": {"results": {}}}}
    for method, rows in grouped.items():
        keys = sorted(rows[0])
        out["experiments"]["synthetic_articulated_gaussians"]["results"][method] = {
            key: float(np.mean([row[key] for row in rows])) for key in keys
        }
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="*", default=["checkpoints/lightweight_splart/results.json"])
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()
    scores = aggregate([Path(p) for p in args.artifacts])
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(scores, indent=2))
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
