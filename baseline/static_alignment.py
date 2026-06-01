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
        n = int(data["state0"].shape[0])
        results.append(
            {
                "scene": path.stem,
                "articulation_type": str(data["articulation_type"]),
                "axis": [1.0, 0.0, 0.0],
                "pivot": [0.0, 0.0, 0.0],
                "amount": 0.0,
                "mobility_state0": [0.0] * n,
                "mobility_state1": [0.0] * n,
            }
        )
    out.write_text(json.dumps({"method": "static_baseline", "results": results}, indent=2))
    print(json.dumps({"wrote": str(out), "num_scenes": len(results)}, indent=2))


if __name__ == "__main__":
    main()
