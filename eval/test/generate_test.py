"""Generate the held-out test scenes (hidden; run once by the gym builder).

The visible inputs go to ``data/scenes/test/inputs`` (what a method sees); the
answers go to ``eval/test/gt`` only.  Test scenes use secret 62-bit seeds drawn
once with ``secrets`` and stored in ``eval/test/test_scenes.json``, and mix the
visible object families with four held-out families defined only here, so the
answers cannot be regenerated from the visible generator.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import secrets
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def _load_generator():
    spec = importlib.util.spec_from_file_location("articulated_objects", ROOT / "data" / "articulated_objects.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["articulated_objects"] = mod
    spec.loader.exec_module(mod)
    return mod


ao = _load_generator()


def _t_round_bin_lid(rng):
    R = rng.uniform(0.2, 0.32)
    Hh = rng.uniform(0.2, 0.35)
    cb = ao._rand_color(rng)
    lt = 0.012
    prims = [
        ao._cyl((0, 0, 0), R, Hh, 0, cb, caps=(True, False), tex=ao._rand_tex(rng)),
        ao._box((R + 0.04, 0, -Hh + 0.02), (0.05, 0.06, 0.012), 0, ao._rand_color(rng)),
        ao._cyl((0, 0, Hh + lt + 0.002), R + 0.01, lt, 1, ao._part_color(rng, cb), caps=(True, True), tex=ao._rand_tex(rng)),
        ao._box((R * 0.55, 0, Hh + 2 * lt + 0.018), (0.035, 0.03, 0.016), 1, ao._rand_color(rng)),
    ]
    joint = {"type": "revolute", "axis": np.array([0.0, -1.0, 0.0]), "pivot": np.array([-(R + 0.01), 0.0, Hh + 0.002])}
    qa = rng.uniform(0.0, np.deg2rad(8.0))
    qb = qa + rng.uniform(np.deg2rad(30.0), np.deg2rad(100.0))
    return prims, joint, (qa, qb)


def _t_faucet(rng):
    W, D, H = rng.uniform(0.3, 0.5), rng.uniform(0.25, 0.4), rng.uniform(0.06, 0.12)
    cb = ao._rand_color(rng)
    pr = rng.uniform(0.035, 0.05)
    ph = rng.uniform(0.12, 0.2)
    prims = [
        ao._box((0, 0, 0), (W / 2, D / 2, H / 2), 0, cb, tex=ao._rand_tex(rng)),
        ao._cyl((0, 0, H / 2 + ph), pr, ph, 0, ao._near_color(rng, cb, 0.15), caps=(False, True)),
        ao._box((0, -0.12, H / 2 + 2 * ph - 0.03), (0.025, 0.12, 0.02), 0, ao._rand_color(rng)),
    ]
    L = rng.uniform(0.2, 0.32)
    zt = H / 2 + 2 * ph + 0.03
    ch = ao._part_color(rng, cb)
    prims.append(ao._cyl((0, 0, zt), pr * 0.9, 0.025, 1, ch, caps=(True, True)))
    prims.append(ao._box((L / 2, 0, zt + 0.01), (L / 2, 0.02, 0.012), 1, ch, tex=ao._rand_tex(rng)))
    joint = {"type": "revolute", "axis": np.array([0.0, 0.0, 1.0]), "pivot": np.array([0.0, 0.0, zt])}
    qa = rng.uniform(np.deg2rad(-30.0), np.deg2rad(30.0))
    qb = qa + float(rng.choice([-1.0, 1.0])) * rng.uniform(np.deg2rad(30.0), np.deg2rad(90.0))
    return prims, joint, (qa, qb)


def _t_piston(rng):
    W, D, H = rng.uniform(0.3, 0.5), rng.uniform(0.3, 0.5), rng.uniform(0.25, 0.45)
    cb = ao._rand_color(rng)
    r = rng.uniform(0.05, 0.09)
    hp = rng.uniform(0.12, 0.2)
    x0, y0 = rng.uniform(-0.25, 0.25) * W, rng.uniform(-0.25, 0.25) * D
    ins = 0.5 * hp
    cp = ao._part_color(rng, cb)
    prims = [
        ao._box((0, 0, 0), (W / 2, D / 2, H / 2), 0, cb, tex=ao._rand_tex(rng)),
        ao._cyl((x0, y0, H / 2 + hp - ins), r, hp, 1, cp, caps=(False, True), tex=ao._rand_tex(rng)),
        ao._cyl((x0, y0, H / 2 + 2 * hp - ins + 0.012), r * 1.5, 0.012, 1, ao._rand_color(rng), caps=(True, True)),
    ]
    joint = {"type": "prismatic", "axis": np.array([0.0, 0.0, 1.0]), "pivot": np.zeros(3)}
    qa = rng.uniform(0.0, 0.03)
    qb = qa + rng.uniform(0.12, 0.3)
    return prims, joint, (qa, qb)


def _t_window_sash(rng):
    W, H = rng.uniform(0.6, 0.9), rng.uniform(0.7, 1.0)
    fw = 0.03
    cf = ao._rand_color(rng)
    prims = [
        ao._box((W / 2 - fw / 2, 0, 0), (fw / 2, 0.03, H / 2), 0, cf, tex=ao._rand_tex(rng)),
        ao._box((-W / 2 + fw / 2, 0, 0), (fw / 2, 0.03, H / 2), 0, cf),
        ao._box((0, 0, H / 2 - fw / 2), (W / 2, 0.03, fw / 2), 0, cf),
        ao._box((0, 0, -H / 2 + fw / 2), (W / 2, 0.03, fw / 2), 0, cf),
        ao._box((0, 0.012, H / 4), (W / 2 - fw, 0.008, H / 4 - fw / 2), 0, ao._rand_color(rng), tex=ao._rand_tex(rng)),
    ]
    cs = ao._part_color(rng, cf)
    prims.append(ao._box((0, -0.012, -H / 4 + fw / 4), (W / 2 - fw, 0.008, H / 4 - fw / 2), 1, cs, tex=ao._rand_tex(rng)))
    prims.append(ao._box((0, -0.03, -H / 2 + fw + 0.04), (0.06, 0.012, 0.012), 1, ao._rand_color(rng)))
    joint = {"type": "prismatic", "axis": np.array([0.0, 0.0, 1.0]), "pivot": np.zeros(3)}
    travel = rng.uniform(0.25, 0.8) * (H / 2 - fw)
    return prims, joint, (0.0, travel)


HELDOUT = {
    "round_bin_lid": _t_round_bin_lid,
    "faucet": _t_faucet,
    "piston": _t_piston,
    "window_sash": _t_window_sash,
}


def scene_list(path: Path) -> list:
    if path.exists():
        return [tuple(x) for x in json.loads(path.read_text())["scenes"]]
    templates = list(ao.TEMPLATES) * 2 + list(HELDOUT) * 2
    order = list(range(len(templates)))
    rnd = secrets.SystemRandom()
    rnd.shuffle(order)
    scenes = [(secrets.randbits(62), templates[i]) for i in order]
    path.write_text(json.dumps({"scenes": scenes}, indent=1))
    return scenes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs-out", default=str(ROOT / "data" / "scenes" / "test" / "inputs"))
    parser.add_argument("--gt-out", default=str(HERE / "gt"))
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    ao.BUILDERS.update(HELDOUT)
    scenes = scene_list(HERE / "test_scenes.json")
    ao.write_scenes(args.inputs_out, args.gt_out, scenes, "test", workers=args.workers)


if __name__ == "__main__":
    main()
