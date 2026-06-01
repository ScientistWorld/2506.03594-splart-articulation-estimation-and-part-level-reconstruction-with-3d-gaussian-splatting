"""Synthetic articulated Gaussian benchmark data.

The generated scenes provide two observed articulation states with ground-truth
static/mobile labels and articulation parameters. This is a lightweight
substitute for the paper datasets, but it preserves the two-rigid-part,
two-state articulated object problem used by SPLART.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class SceneSpec:
    name: str
    articulation_type: str
    seed: int


DEFAULT_SCENES = (
    SceneSpec("revolute_hinge", "revolute", 13),
    SceneSpec("prismatic_slider", "prismatic", 29),
)


def _rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
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
        dtype=np.float32,
    )


def transform_points(
    points: np.ndarray,
    articulation_type: str,
    axis: np.ndarray,
    pivot: np.ndarray,
    amount: float,
) -> np.ndarray:
    if articulation_type == "revolute":
        R = _rotation_matrix(axis, amount)
        return (points - pivot) @ R.T + pivot
    if articulation_type == "prismatic":
        return points + axis / np.linalg.norm(axis) * amount
    raise ValueError(f"Unknown articulation_type: {articulation_type}")


def generate_scene(spec: SceneSpec) -> dict:
    rng = np.random.default_rng(spec.seed)
    n_static = 80
    n_mobile = 60

    static = rng.normal(loc=(-0.25, 0.0, 0.0), scale=(0.18, 0.16, 0.12), size=(n_static, 3)).astype(np.float32)
    mobile_base = rng.normal(loc=(0.35, 0.05, 0.0), scale=(0.15, 0.13, 0.10), size=(n_mobile, 3)).astype(np.float32)

    if spec.articulation_type == "revolute":
        axis = np.array([0.05, 0.0, 1.0], dtype=np.float32)
        axis /= np.linalg.norm(axis)
        pivot = np.array([0.05, -0.05, 0.0], dtype=np.float32)
        amount = np.float32(np.deg2rad(42.0))
    else:
        axis = np.array([1.0, 0.15, 0.05], dtype=np.float32)
        axis /= np.linalg.norm(axis)
        pivot = np.zeros(3, dtype=np.float32)
        amount = np.float32(0.38)

    mobile_moved = transform_points(mobile_base, spec.articulation_type, axis, pivot, float(amount))
    noise0 = rng.normal(scale=0.006, size=(n_static + n_mobile, 3)).astype(np.float32)
    noise1 = rng.normal(scale=0.006, size=(n_static + n_mobile, 3)).astype(np.float32)

    state0 = np.concatenate([static, mobile_base], axis=0) + noise0
    state1 = np.concatenate([static, mobile_moved], axis=0) + noise1
    labels = np.concatenate([np.zeros(n_static, dtype=np.int64), np.ones(n_mobile, dtype=np.int64)])
    opacities = np.concatenate(
        [
            rng.uniform(0.7, 1.0, size=n_static),
            rng.uniform(0.55, 0.9, size=n_mobile),
        ]
    ).astype(np.float32)

    return {
        "name": spec.name,
        "articulation_type": spec.articulation_type,
        "state0": state0,
        "state1": state1,
        "labels": labels,
        "opacities": opacities,
        "axis": axis.astype(np.float32),
        "pivot": pivot.astype(np.float32),
        "amount": np.asarray(amount, dtype=np.float32),
    }


def write_default_dataset(out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for spec in DEFAULT_SCENES:
        scene = generate_scene(spec)
        np.savez_compressed(out / f"{spec.name}.npz", **scene)


if __name__ == "__main__":
    write_default_dataset(Path(__file__).parent / "synthetic_splart")
