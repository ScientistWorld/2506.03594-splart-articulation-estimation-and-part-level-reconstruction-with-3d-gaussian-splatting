"""Build shortcut submissions from saved reference / baseline predictions.

Each shortcut is a method directory under tmp/hardening/shortcuts/ that the
unchanged test evaluator scores with ``--root tmp/hardening/shortcuts``.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "checkpoints/splart/predictions"
STATIC = ROOT / "checkpoints/static_baseline/predictions"
OUT = ROOT / "tmp/hardening/shortcuts"
SCENES = sorted(p.stem for p in (ROOT / "data/scenes/test/inputs").glob("*.npz"))


def load(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as d:
        return {k: np.asarray(d[k]) for k in d.files}


def put(name: str, scene: str, pred: dict, fname: str | None = None) -> None:
    d = OUT / name / "predictions"
    d.mkdir(parents=True, exist_ok=True)
    np.savez(d / (fname or f"{scene}.npz"), **pred)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    ref = {s: load(REF / f"{s}.npz") for s in SCENES if (REF / f"{s}.npz").exists()}
    static = {s: load(STATIC / f"{s}.npz") for s in SCENES}
    first = SCENES[0]

    (OUT / "empty_method_dir").mkdir()  # a failed method left on disk
    for i, s in enumerate(SCENES):
        if s in ref and i % 2 == 0:
            put("missing_half_scenes", s, ref[s])
    for s, p in ref.items():
        q = dict(p)
        if s == first:
            q["axis"] = np.array([np.nan, 0.0, 1.0])
        put("nan_axis_one_scene", s, q)
        q = dict(p)
        if s == first:
            q["static_opacities"] = q["static_opacities"] * 1e100
        put("impossible_opacity_one_scene", s, q)
        put("duplicate_files", s, p)
        put("duplicate_files", s, p, fname=f"{s}_copy.npz")
        put("duplicate_files", s, p, fname=f"{s}.dup.npz")
        q = dict(p)
        for k in ("means", "scales", "colors", "opacities"):
            q[f"static_{k}"] = np.concatenate([p[f"static_{k}"], p[f"mobile_{k}"]])
            q[f"mobile_{k}"] = p[f"mobile_{k}"][:0]
        put("all_static_masks", s, q)
        q = dict(p)
        lo = np.concatenate([p["static_means"], p["mobile_means"]]).min(0) - 0.05
        hi = np.concatenate([p["static_means"], p["mobile_means"]]).max(0) + 0.05
        n_have = len(p["static_means"]) + len(p["mobile_means"])
        k = max(0, min(6000, 20000 - n_have))
        g = np.random.default_rng(0).uniform(lo, hi, size=(k, 3)).astype(np.float32)
        q["static_means"] = np.concatenate([p["static_means"], g])
        q["static_scales"] = np.concatenate([p["static_scales"], np.full(k, 0.02, np.float32)])
        q["static_colors"] = np.concatenate([p["static_colors"], np.ones((k, 3), np.float32)])
        q["static_opacities"] = np.concatenate([p["static_opacities"], np.full(k, 0.1, np.float32)])
        put("faint_gaussian_grid", s, q)
        q = dict(p)
        extra = 20001
        q["static_means"] = np.concatenate([p["static_means"], np.zeros((extra, 3), np.float32)])
        q["static_scales"] = np.concatenate([p["static_scales"], np.full(extra, 0.01, np.float32)])
        q["static_colors"] = np.concatenate([p["static_colors"], np.ones((extra, 3), np.float32)])
        q["static_opacities"] = np.concatenate([p["static_opacities"], np.zeros(extra, np.float32)])
        put("too_many_gaussians", s, q)
    # pickled object array in one file -> must be rejected, never unpickled
    for s, p in ref.items():
        q = dict(p)
        if s == first:
            q["axis"] = np.array([{"x": 1}], dtype=object)
        d = OUT / "pickled_payload" / "predictions"
        d.mkdir(parents=True, exist_ok=True)
        np.savez(d / f"{s}.npz", **q)
    # forged score files next to static-baseline predictions
    for s, p in static.items():
        put("forged_score_files", s, p)
    perfect = {"success_rate": 1.0, "axis_error_deg": 0.0, "psnr": 99.0, "part_miou": 1.0}
    for f in ("scores_test.json", "metrics.json", "predictions/scores.json"):
        (OUT / "forged_score_files" / f).write_text(json.dumps(perfect))
    print(f"[shortcuts] built {sorted(p.name for p in OUT.iterdir())}")


if __name__ == "__main__":
    main()
