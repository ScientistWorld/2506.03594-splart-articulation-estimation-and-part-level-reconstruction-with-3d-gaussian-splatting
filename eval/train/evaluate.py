"""Train-slice evaluator for articulated Gaussian prediction artifacts.

This is intentionally self-contained inside eval/train/. It scores the visible
development slice only and never imports from method/ or eval/test/.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


SLICE = "train"
SLICE_SCENES = ("revolute_hinge", "prismatic_diagonal")


def _normalize(v: np.ndarray) -> np.ndarray:
    return v / max(float(np.linalg.norm(v)), 1e-12)


def _rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = _normalize(axis)
    x, y, z = axis
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1.0 - c
    return np.array(
        [
            [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C],
        ],
        dtype=np.float64,
    )


def _transform(points: np.ndarray, articulation_type: str, axis: np.ndarray, pivot: np.ndarray, amount: float) -> np.ndarray:
    axis = _normalize(axis)
    if articulation_type == "revolute":
        return (points - pivot) @ _rotation_matrix(axis, amount).T + pivot
    if articulation_type == "prismatic":
        return points + axis * amount
    raise ValueError(f"Unknown articulation_type: {articulation_type}")


def _weighted_chamfer(x: np.ndarray, wx: np.ndarray, y: np.ndarray, wy: np.ndarray) -> float:
    d2 = ((x[:, None, :] - y[None, :, :]) ** 2).sum(axis=-1)
    wx = np.clip(wx.astype(np.float64), 1e-8, None)
    wy = np.clip(wy.astype(np.float64), 1e-8, None)
    wx = wx / wx.sum()
    wy = wy / wy.sum()
    return float((wx * d2.min(axis=1)).sum() + (wy * d2.min(axis=0)).sum())


def _cross_mobile_sets(
    x0: np.ndarray,
    x1: np.ndarray,
    opacity: np.ndarray,
    m0: np.ndarray,
    m1: np.ndarray,
    articulation_type: str,
    axis: np.ndarray,
    pivot: np.ndarray,
    amount: float,
    state: int,
) -> tuple[np.ndarray, np.ndarray]:
    static_x = np.concatenate([x0, x1], axis=0)
    static_w = np.concatenate([opacity * (1.0 - m0), opacity * (1.0 - m1)], axis=0)
    if state == 0:
        mobile_x = np.concatenate([x0, _transform(x1, articulation_type, axis, pivot, -amount)], axis=0)
    else:
        mobile_x = np.concatenate([x1, _transform(x0, articulation_type, axis, pivot, amount)], axis=0)
    mobile_w = np.concatenate([opacity * m0, opacity * m1], axis=0)
    return np.concatenate([static_x, mobile_x], axis=0), np.concatenate([static_w, mobile_w], axis=0)


def _part_iou(pred: np.ndarray, labels: np.ndarray) -> tuple[float, float, float]:
    pred = pred.astype(bool)
    labels = labels.astype(bool)
    tp = np.logical_and(pred, labels).sum()
    fp = np.logical_and(pred, ~labels).sum()
    fn = np.logical_and(~pred, labels).sum()
    mobile_iou = float(tp / max(tp + fp + fn, 1))
    static_pred = ~pred
    static = ~labels
    tp_s = np.logical_and(static_pred, static).sum()
    fp_s = np.logical_and(static_pred, ~static).sum()
    fn_s = np.logical_and(~static_pred, static).sum()
    static_iou = float(tp_s / max(tp_s + fp_s + fn_s, 1))
    return mobile_iou, static_iou, (mobile_iou + static_iou) / 2.0


def _score_scene(prediction: dict, data: np.lib.npyio.NpzFile) -> dict[str, float]:
    articulation_type = str(data["articulation_type"])
    axis = _normalize(np.asarray(prediction["axis"], dtype=np.float64))
    pivot = np.asarray(prediction.get("pivot", [0.0, 0.0, 0.0]), dtype=np.float64)
    amount = float(prediction["amount"])
    gt_axis = _normalize(np.asarray(data["axis"], dtype=np.float64))
    gt_amount = float(data["amount"])

    if float(np.dot(axis, gt_axis)) < 0.0:
        axis = -axis
        amount = -amount

    axis_error_deg = float(np.degrees(np.arccos(np.clip(np.dot(axis, gt_axis), -1.0, 1.0))))
    if articulation_type == "prismatic":
        amount_error = float(np.linalg.norm(axis * amount - gt_axis * gt_amount))
        pivot_error = 0.0
    else:
        amount_error = abs(amount - gt_amount)
        pivot_gt = np.asarray(data["pivot"], dtype=np.float64)
        pivot_error = float(np.linalg.norm(np.cross(pivot - pivot_gt, gt_axis)))

    m0 = np.asarray(prediction["mobility_state0"], dtype=np.float64)
    m1 = np.asarray(prediction["mobility_state1"], dtype=np.float64)
    mobility = (m0 + m1) / 2.0
    mobile_iou, static_iou, mean_part_iou = _part_iou(mobility >= 0.5, np.asarray(data["labels"], dtype=np.int64))

    x0 = np.asarray(data["state0"], dtype=np.float64)
    x1 = np.asarray(data["state1"], dtype=np.float64)
    opacity = np.asarray(data["opacities"], dtype=np.float64)
    cm0_x, cm0_w = _cross_mobile_sets(x0, x1, opacity, m0, m1, articulation_type, axis, pivot, amount, 0)
    cm1_x, cm1_w = _cross_mobile_sets(x0, x1, opacity, m0, m1, articulation_type, axis, pivot, amount, 1)
    reconstruction_chamfer = _weighted_chamfer(cm0_x, cm0_w, x0, opacity)
    reconstruction_chamfer += _weighted_chamfer(cm1_x, cm1_w, x1, opacity)

    success = (
        axis_error_deg < 5.0
        and amount_error < 0.05
        and pivot_error < 0.05
        and mean_part_iou > 0.75
        and reconstruction_chamfer < 0.01
    )
    return {
        "axis_error_deg": axis_error_deg,
        "amount_error": amount_error,
        "pivot_error": pivot_error,
        "mobile_iou": mobile_iou,
        "static_iou": static_iou,
        "mean_part_iou": mean_part_iou,
        "reconstruction_chamfer": reconstruction_chamfer,
        "success": float(success),
    }


def _discover_artifacts(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("*/results.json") if path.is_file())


def _resolve_artifacts(cli_artifacts: list[str], discover_root: Path) -> list[Path]:
    artifacts = [Path(path) for path in cli_artifacts] if cli_artifacts else _discover_artifacts(discover_root)
    if not artifacts:
        raise FileNotFoundError(f"No result artifacts found under {discover_root}")
    return artifacts


def aggregate(paths: list[Path], data_dir: Path) -> tuple[dict, dict]:
    scene_set = set(SLICE_SCENES)
    scenes = {path.stem: path for path in data_dir.glob("*.npz") if path.stem in scene_set}
    missing_data = sorted(scene_set.difference(scenes))
    if missing_data:
        raise FileNotFoundError(f"Missing {SLICE} data scenes: {missing_data}")

    grouped = defaultdict(list)
    seen_scenes = defaultdict(set)
    per_scene = defaultdict(dict)
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {path}")
        artifact = json.loads(path.read_text())
        method = artifact["method"]
        for prediction in artifact["results"]:
            scene = prediction["scene"]
            if scene not in scene_set:
                continue
            with np.load(scenes[scene]) as data:
                score = _score_scene(prediction, data)
                grouped[method].append(score)
                seen_scenes[method].add(scene)
                per_scene[method][scene] = {"slice": SLICE, **score}

    for method, found in seen_scenes.items():
        missing = sorted(scene_set.difference(found))
        if missing:
            raise KeyError(f"Artifact set for method '{method}' is missing {SLICE} scenes: {missing}")
    if not grouped:
        raise ValueError(f"No predictions matched {SLICE} scenes: {sorted(scene_set)}")

    out = {"experiments": {"synthetic_articulated_gaussians": {"results": {}}}}
    for method, rows in grouped.items():
        keys = sorted(rows[0])
        out["experiments"]["synthetic_articulated_gaussians"]["results"][method] = {
            key: float(sum(row[key] for row in rows) / len(rows)) for key in keys
        }
    return out, {"slice": SLICE, "scenes": list(SLICE_SCENES), "synthetic_articulated_gaussians": dict(per_scene)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="*")
    parser.add_argument("--data-dir", default="data/synthetic_splart")
    parser.add_argument("--discover-root", default="checkpoints")
    parser.add_argument("--output", default="scoring/scores_train.json")
    parser.add_argument("--per-scene-output", default="scoring/per_scene_train.json")
    args = parser.parse_args()

    artifacts = _resolve_artifacts(args.artifacts, Path(args.discover_root))
    scores, per_scene = aggregate(artifacts, Path(args.data_dir))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(scores, indent=2))
    Path(args.per_scene_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.per_scene_output).write_text(json.dumps(per_scene, indent=2))
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
