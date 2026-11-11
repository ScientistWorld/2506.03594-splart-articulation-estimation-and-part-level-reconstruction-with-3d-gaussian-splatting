"""Held-out test-slice evaluator for two-state articulated-object reconstructions.

Self-contained (numpy only).  Never imports from method/ or eval/train/.  The
answers live in eval/test/gt/; methods only see data/scenes/test/inputs/.

Every directory under the method root (default checkpoints/) is a method and is
scored; its predictions are read from ``<root>/<method>/predictions/<scene>.npz``.
Every number is recomputed from the raw prediction arrays:

* articulation_estimation: paper metrics (axis angle error, pivot line distance,
  rotation geodesic error, translation error) and the paper's success rule
  (axis < 5 deg; revolute: pivot < 0.05 and rotation < 10 deg; prismatic:
  translation < 0.05).  Errors are truncated at those thresholds per scene, so
  a failed scene counts as the threshold value and cannot be hidden.
* part_reconstruction: the predicted static + mobile Gaussians are rendered at
  held-out cameras and articulation states (mobile part moved by fraction q of
  the predicted motion) and compared with ground-truth images (PSNR), composited
  depth (MAE) and static/mobile/background segmentation (mIoU); part geometry is
  compared with dense ground-truth surfaces (Chamfer, static / mobile / whole).
  A scene whose articulation fails gets the worst reconstruction values.

A missing scene gets the worst value of every metric.  A run with any invalid
prediction (unreadable file, wrong shape, non-finite number, opacity or colour
outside [0, 1], non-positive scale, too many Gaussians, zero axis, ...) or with
no predictions at all is a failed run: every metric of every experiment gets its
worst value.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

SLICE = "test"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GT_DIR = HERE / "gt"
EXPECTED_SCENES = 26
DEFAULT_METHOD_ROOT = ROOT / "checkpoints"

MAX_GAUSSIANS = 20000
CD_MIN_OPACITY = 0.1
ART = "articulation_estimation"
REC = "part_reconstruction"
THRESH = {"axis_error_deg": 5.0, "pivot_error": 0.05, "rotation_error_deg": 10.0, "translation_error": 0.05}
WORST = {
    ART: {
        "success_rate": 0.0,
        "axis_error_deg": THRESH["axis_error_deg"],
        "pivot_error": THRESH["pivot_error"],
        "rotation_error_deg": THRESH["rotation_error_deg"],
        "translation_error": THRESH["translation_error"],
    },
    REC: {"psnr": 10.0, "depth_mae": 1.0, "part_miou": 0.0, "cd_static": 0.2, "cd_mobile": 0.2, "cd_whole": 0.2},
}
HIGHER_IS_BETTER = {"success_rate", "psnr", "part_miou"}
SET_KEYS = ("means", "scales", "colors", "opacities")


class InvalidPrediction(Exception):
    pass


# --------------------------------------------------------------------------- validation


def _numeric(name: str, arr: np.ndarray, shape: tuple) -> np.ndarray:
    if arr.dtype == object or not (np.issubdtype(arr.dtype, np.floating) or np.issubdtype(arr.dtype, np.integer)):
        raise InvalidPrediction(f"{name}: non-numeric dtype {arr.dtype}")
    if len(shape) != arr.ndim or any(s is not None and s != a for s, a in zip(shape, arr.shape)):
        raise InvalidPrediction(f"{name}: shape {arr.shape}, expected {shape}")
    out = arr.astype(np.float64)
    if not np.isfinite(out).all():
        raise InvalidPrediction(f"{name}: non-finite values")
    return out


def _unit_range(name: str, arr: np.ndarray) -> np.ndarray:
    if arr.size and (arr.min() < -1e-6 or arr.max() > 1.0 + 1e-6):
        raise InvalidPrediction(f"{name}: values outside [0, 1]")
    return np.clip(arr, 0.0, 1.0)


def load_prediction(path: Path, jtype: str) -> dict:
    try:
        with np.load(path, allow_pickle=False) as d:
            raw = {k: np.asarray(d[k]) for k in d.files}
    except Exception as exc:  # unreadable / pickled / not an npz
        raise InvalidPrediction(f"unreadable prediction file: {type(exc).__name__}")
    need = ["axis", "pivot", "amount"] + [f"{s}_{k}" for s in ("static", "mobile") for k in SET_KEYS]
    missing = [k for k in need if k not in raw]
    if missing:
        raise InvalidPrediction(f"missing keys {missing}")
    pred = {
        "axis": _numeric("axis", raw["axis"], (3,)),
        "pivot": _numeric("pivot", raw["pivot"], (3,)),
        "amount": float(_numeric("amount", raw["amount"].reshape(-1), (1,))[0]),
    }
    norm = float(np.linalg.norm(pred["axis"]))
    if norm < 1e-6:
        raise InvalidPrediction("axis has zero length")
    pred["axis"] = pred["axis"] / norm
    if np.abs(pred["pivot"]).max() > 1e3:
        raise InvalidPrediction("pivot coordinate beyond 1e3")
    limit = 2.0 * math.pi if jtype == "revolute" else 5.0
    if abs(pred["amount"]) > limit + 1e-9:
        raise InvalidPrediction(f"motion amount {pred['amount']} outside [-{limit}, {limit}]")
    total = 0
    for s in ("static", "mobile"):
        means = _numeric(f"{s}_means", raw[f"{s}_means"], (None, 3))
        n = means.shape[0]
        scales = _numeric(f"{s}_scales", raw[f"{s}_scales"], (n,))
        colors = _unit_range(f"{s}_colors", _numeric(f"{s}_colors", raw[f"{s}_colors"], (n, 3)))
        opac = _unit_range(f"{s}_opacities", _numeric(f"{s}_opacities", raw[f"{s}_opacities"], (n,)))
        if n and (scales.min() <= 0.0 or scales.max() > 1.0):
            raise InvalidPrediction(f"{s}_scales outside (0, 1]")
        if n and np.abs(means).max() > 1e3:
            raise InvalidPrediction(f"{s}_means coordinate beyond 1e3")
        pred[s] = (means, scales, colors, opac)
        total += n
    if total == 0:
        raise InvalidPrediction("no Gaussians")
    if total > MAX_GAUSSIANS:
        raise InvalidPrediction(f"{total} Gaussians > limit {MAX_GAUSSIANS}")
    return pred


# --------------------------------------------------------------------------- geometry


def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = axis / np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    C = 1.0 - c
    return np.array(
        [
            [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C],
        ]
    )


def articulate(points, jtype, axis, pivot, amount, frac):
    if jtype == "revolute":
        R = rotation_matrix(axis, frac * amount)
        return (points - pivot) @ R.T + pivot
    return points + (frac * amount) * axis


def line_distance(p1, a1, p2, a2) -> float:
    n = np.cross(a1, a2)
    nn = float(np.linalg.norm(n))
    w = p1 - p2
    if nn < 1e-6:
        return float(np.linalg.norm(np.cross(w, a2)))
    return abs(float(w @ n)) / nn


def articulation_errors(pred: dict, gt: dict, jtype: str) -> dict:
    a_p, a_g = pred["axis"], gt["axis"] / np.linalg.norm(gt["axis"])
    out = {"axis_error_deg": math.degrees(math.acos(min(1.0, abs(float(a_p @ a_g)))))}
    if jtype == "revolute":
        Rp = rotation_matrix(a_p, pred["amount"])
        Rg = rotation_matrix(a_g, float(gt["amount"]))
        cos = (np.trace(Rp.T @ Rg) - 1.0) / 2.0
        out["rotation_error_deg"] = math.degrees(math.acos(float(np.clip(cos, -1.0, 1.0))))
        out["pivot_error"] = line_distance(pred["pivot"], a_p, gt["pivot"], a_g)
        ok = (
            out["axis_error_deg"] < THRESH["axis_error_deg"]
            and out["pivot_error"] < THRESH["pivot_error"]
            and out["rotation_error_deg"] < THRESH["rotation_error_deg"]
        )
    else:
        out["translation_error"] = float(np.linalg.norm(a_p * pred["amount"] - a_g * float(gt["amount"])))
        ok = out["axis_error_deg"] < THRESH["axis_error_deg"] and out["translation_error"] < THRESH["translation_error"]
    out["success"] = bool(ok)
    return out


# --------------------------------------------------------------------------- rendering


def render(means, scales, colors, opac, mobile, R, t, intr, size, depth_bg, chunk=256):
    """Same splatting model as the observations (see data/articulated_objects.py)."""
    pc = means @ R.T + t
    keep = pc[:, 2] > 0.05
    pc, scales, colors, opac, mobile = pc[keep], scales[keep], colors[keep], opac[keep], mobile[keep]
    fx, fy, cx, cy = intr
    z = pc[:, 2]
    u = fx * pc[:, 0] / z + cx
    v = fy * pc[:, 1] / z + cy
    var = (fx * scales / z) ** 2 + 0.3
    order = np.argsort(z, kind="stable")
    u, v, var, colors, opac, mobile, z = u[order], v[order], var[order], colors[order], opac[order], mobile[order], z[order]
    ys, xs = np.mgrid[0:size, 0:size]
    pu = xs.ravel() + 0.5
    pv = ys.ravel() + 0.5
    P = size * size
    rgb = np.ones((P, 3))
    acc = np.zeros(P)
    dep = np.full(P, depth_bg)
    mob = np.zeros(P)
    if len(z) == 0:
        return rgb, acc, dep, mob
    for s in range(0, P, chunk):
        e = min(P, s + chunk)
        du = pu[None, s:e] - u[:, None]
        dv = pv[None, s:e] - v[:, None]
        alpha = np.minimum(0.99, opac[:, None] * np.exp(-0.5 * (du * du + dv * dv) / var[:, None]))
        T = np.cumprod(1.0 - alpha, axis=0)
        w = alpha * np.concatenate([np.ones((1, e - s)), T[:-1]], axis=0)
        a = w.sum(axis=0)
        rgb[s:e] = w.T @ colors + (1.0 - a)[:, None]
        acc[s:e] = a
        dep[s:e] = w.T @ z + (1.0 - a) * depth_bg
        mob[s:e] = w.T @ mobile
    return rgb, acc, dep, mob


def _nn_dist(a: np.ndarray, b: np.ndarray, chunk: int = 2048) -> np.ndarray:
    out = np.empty(len(a))
    bb = (b * b).sum(1)
    for s in range(0, len(a), chunk):
        x = a[s : s + chunk]
        d2 = (x * x).sum(1)[:, None] + bb[None, :] - 2.0 * x @ b.T
        out[s : s + chunk] = np.sqrt(np.maximum(d2.min(axis=1), 0.0))
    return out


def chamfer(pred: np.ndarray, gt: np.ndarray, cap: float) -> float:
    if len(pred) == 0 or len(gt) == 0:
        return cap
    return float(min(cap, _nn_dist(pred, gt).mean() + _nn_dist(gt, pred).mean()))


def reconstruction_metrics(pred: dict, gt: dict, jtype: str) -> dict:
    intr = gt["intrinsics"].astype(np.float64)
    size = int(gt["image_size"])
    depth_bg = float(gt["depth_background"])
    sm, ss, sc, so = pred["static"]
    mm, ms, mc, mo = pred["mobile"]
    flags = np.concatenate([np.zeros(len(sm)), np.ones(len(mm))])
    psnrs, derr = [], []
    inter, union = np.zeros(3), np.zeros(3)
    for R, t, q, g_rgb, g_dep, g_alpha, g_seg in zip(
        gt["heldout_R"], gt["heldout_t"], gt["heldout_q"], gt["heldout_rgb"], gt["heldout_depth"], gt["heldout_alpha"], gt["heldout_seg"]
    ):
        moved = articulate(mm, jtype, pred["axis"], pred["pivot"], pred["amount"], float(q))
        rgb, acc, dep, mob = render(
            np.concatenate([sm, moved]), np.concatenate([ss, ms]), np.concatenate([sc, mc]), np.concatenate([so, mo]),
            flags, R.astype(np.float64), t.astype(np.float64), intr, size, depth_bg,
        )
        gt_rgb = g_rgb.reshape(-1, 3).astype(np.float64) / 255.0
        mse = float(np.mean((rgb - gt_rgb) ** 2))
        psnrs.append(-10.0 * math.log10(max(mse, 1e-10)))
        g_alpha = g_alpha.reshape(-1)
        fg = (g_alpha > 0.5) | (acc > 0.5)
        derr.append(np.minimum(np.abs(dep - g_dep.reshape(-1).astype(np.float64)), WORST[REC]["depth_mae"])[fg])
        seg = np.where(acc < 0.5, 0, np.where(mob > 0.5 * acc, 2, 1))
        g_seg = g_seg.reshape(-1)
        for c in range(3):
            inter[c] += np.sum((seg == c) & (g_seg == c))
            union[c] += np.sum((seg == c) | (g_seg == c))
    derr = np.concatenate(derr)
    iou = np.where(union > 0, inter / np.maximum(union, 1), 1.0)
    cap = WORST[REC]["cd_whole"]
    ps = sm[so >= CD_MIN_OPACITY]
    pm = mm[mo >= CD_MIN_OPACITY]
    gs, gm = gt["gt_static"].astype(np.float64), gt["gt_mobile0"].astype(np.float64)
    return {
        "psnr": max(WORST[REC]["psnr"], float(np.mean(psnrs))),
        "depth_mae": float(derr.mean()) if derr.size else WORST[REC]["depth_mae"],
        "part_miou": float(iou.mean()),
        "cd_static": chamfer(ps, gs, cap),
        "cd_mobile": chamfer(pm, gm, cap),
        "cd_whole": chamfer(np.concatenate([ps, pm]), np.concatenate([gs, gm]), cap),
    }


# --------------------------------------------------------------------------- scoring


def load_ground_truth() -> dict:
    files = sorted(GT_DIR.glob(f"{SLICE}_*.npz"))
    if len(files) != EXPECTED_SCENES:
        raise RuntimeError(f"expected {EXPECTED_SCENES} ground-truth scenes in {GT_DIR}, found {len(files)}")
    gts = {}
    for f in files:
        with np.load(f, allow_pickle=False) as d:
            gts[f.stem] = {k: np.asarray(d[k]) for k in d.files}
    return gts


def score_scene(pred: dict | None, gt: dict) -> dict:
    jtype = str(gt["articulation_type"])
    row = {"type": jtype, "present": pred is not None}
    if pred is None:
        row.update({"success": False})
        return row
    row.update(articulation_errors(pred, gt, jtype))
    rec = reconstruction_metrics(pred, gt, jtype)
    row.update({f"raw_{k}": v for k, v in rec.items()})
    return row


def aggregate(rows: dict) -> dict:
    out = {ART: {}, REC: {}}
    vals = list(rows.values())
    out[ART]["success_rate"] = float(np.mean([1.0 if r.get("success") else 0.0 for r in vals]))
    for key, types in (
        ("axis_error_deg", ("revolute", "prismatic")),
        ("pivot_error", ("revolute",)),
        ("rotation_error_deg", ("revolute",)),
        ("translation_error", ("prismatic",)),
    ):
        sel = [min(r.get(key, THRESH[key]), THRESH[key]) for r in vals if r["type"] in types]
        out[ART][key] = float(np.mean(sel)) if sel else WORST[ART][key]
    for key in WORST[REC]:
        out[REC][key] = float(np.mean([r[f"raw_{key}"] if r.get("success") else WORST[REC][key] for r in vals]))
    for exp in out:
        for key, value in out[exp].items():
            if not math.isfinite(value):
                out[exp][key] = WORST[exp][key]
    return out


def score_method(method_dir: Path, gts: dict) -> tuple[str, dict, dict]:
    pred_dir = method_dir / "predictions"
    rows = {}
    present = 0
    try:
        for scene, gt in gts.items():
            path = pred_dir / f"{scene}.npz"
            if path.is_file():
                rows[scene] = score_scene(load_prediction(path, str(gt["articulation_type"])), gt)
                present += 1
            else:
                rows[scene] = score_scene(None, gt)
    except InvalidPrediction as exc:
        return f"failed: {scene}: {exc}", {e: dict(v) for e, v in WORST.items()}, {}
    except Exception as exc:  # any other malformed content counts as a failed run
        return f"failed: {scene}: {type(exc).__name__}: {exc}", {e: dict(v) for e, v in WORST.items()}, {}
    if present == 0:
        return "failed: no predictions for this slice", {e: dict(v) for e, v in WORST.items()}, {}
    status = "ok" if present == len(gts) else f"incomplete: {len(gts) - present} scenes missing"
    return status, aggregate(rows), rows


def discover(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))


def main() -> None:
    parser = argparse.ArgumentParser(description="Score every method directory on the hidden test slice.")
    parser.add_argument("--root", default=str(DEFAULT_METHOD_ROOT), help="directory holding one sub-directory per method")
    parser.add_argument("--output", default=str(ROOT / "scoring" / "scores_test.json"))
    parser.add_argument("--per-scene-output", default=None)
    args = parser.parse_args()

    gts = load_ground_truth()
    result = {"experiments": {ART: {"results": {}}, REC: {"results": {}}}, "_meta": {"slice": SLICE, "num_scenes": len(gts), "status": {}}}
    per_scene = {}
    for method_dir in discover(Path(args.root)):
        name = method_dir.name
        status, metrics, rows = score_method(method_dir, gts)
        for exp in (ART, REC):
            result["experiments"][exp]["results"][name] = metrics[exp]
        result["_meta"]["status"][name] = status
        per_scene[name] = rows
        print(f"[{SLICE}] {name}: {status}", flush=True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False))
    if args.per_scene_output:
        Path(args.per_scene_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.per_scene_output).write_text(json.dumps(per_scene, indent=1, default=float))
    print(json.dumps(result["experiments"], indent=2))


if __name__ == "__main__":
    main()
