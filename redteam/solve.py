"""Audit methods using only the scientist-visible observations and generator.

Anything named shortcut is deliberately an audit shortcut, never a claimed
improvement to the paper. No evaluator imports or process/environment changes.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def leaked_predictions(rebuild=False):
    """Shortcut: copy answers from public NPZs or reconstruct their generator."""
    if rebuild:
        from data.articulated_gaussians import DEFAULT_SCENES, generate_scene
        scenes = [(spec.name, generate_scene(spec)) for spec in DEFAULT_SCENES]
    else:
        scenes = [(p.stem, dict(np.load(p))) for p in sorted((ROOT / 'data/synthetic_splart').glob('*.npz'))]
    rows = []
    for name, d in scenes:
        labels = np.asarray(d['labels'], dtype=float).tolist()
        rows.append(dict(scene=name, articulation_type=str(d['articulation_type']),
                         axis=np.asarray(d['axis']).tolist(), pivot=np.asarray(d['pivot']).tolist(),
                         amount=float(d['amount']), mobility_state0=labels, mobility_state1=labels))
    return rows


def rigid_fit(x, y):
    """Kabsch fit, including batch dimensions. Row-vector convention."""
    cx, cy = x.mean(axis=-2), y.mean(axis=-2)
    cov = np.swapaxes(x-cx[..., None, :], -1, -2) @ (y-cy[..., None, :])
    u, _, vt = np.linalg.svd(cov)
    correction = np.broadcast_to(np.eye(3), cov.shape).copy()
    correction[..., 2, 2] = np.linalg.det(u @ vt)
    rotation = u @ correction @ vt
    translation = cy - np.einsum('...i,...ij->...j', cx, rotation)
    return rotation, translation


def brute_force_predictions(enumerate_triples=True):
    """Shortcut: exhaust every observed moving-point triple, then rigid refit.

    Only state0/state1 and known joint type are read. Corresponding row order
    makes the benchmark much simpler than independent RGB reconstructions.
    This is an honest alternative on the reduced task, a shortcut relative to
    the intended research problem. No labels, seeds or articulation GT used.
    """
    rows, diagnostics = [], {}
    for path in sorted((ROOT / 'data/synthetic_splart').glob('*.npz')):
        start = time.monotonic()
        with np.load(path) as d:
            x, y = d['state0'].astype(float), d['state1'].astype(float)
            kind = str(d['articulation_type'])
        mobile = np.linalg.norm(y-x, axis=1) > 0.06
        xm, ym = x[mobile], y[mobile]
        candidates = 0
        if kind == 'prismatic':
            # Exhaust each matched displacement candidate, then least squares.
            shifts = ym-xm
            errors = ((shifts[:, None, :] - shifts[None, :, :])**2).sum(-1).mean(-1)
            best_shift = shifts[int(errors.argmin())]
            inliers = np.linalg.norm(shifts-best_shift, axis=1) < 0.05
            shift = shifts[inliers].mean(axis=0)
            amount = np.linalg.norm(shift)
            axis, pivot = shift/amount, np.zeros(3)
            candidates = len(shifts)
        elif not enumerate_triples:
            rotation, translation = rigid_fit(xm, ym)
            r = rotation.T
            amount = np.arccos(np.clip((np.trace(r)-1)/2, -1, 1))
            axis = np.array([r[2,1]-r[1,2], r[0,2]-r[2,0], r[1,0]-r[0,1]])
            axis /= np.linalg.norm(axis)
            pivot = np.linalg.lstsq(np.eye(3)-r, translation, rcond=1e-8)[0]
            candidates = 1
        else:
            best_error, best = float('inf'), None
            iterator = itertools.combinations(range(len(xm)), 3)
            while True:
                triples = list(itertools.islice(iterator, 1024))
                if not triples:
                    break
                inds = np.asarray(triples)
                rotation, translation = rigid_fit(xm[inds], ym[inds])
                predicted = np.einsum('ni,bij->bnj', xm, rotation) + translation[:, None, :]
                errors = np.mean(np.minimum(((predicted-ym)**2).sum(-1), 0.05**2), axis=1)
                k = int(errors.argmin())
                if errors[k] < best_error:
                    best_error, best = errors[k], (rotation[k], translation[k])
                candidates += len(inds)
            rotation, translation = best
            inliers = np.linalg.norm(xm @ rotation + translation - ym, axis=1) < 0.05
            rotation, translation = rigid_fit(xm[inliers], ym[inliers])
            r = rotation.T
            amount = np.arccos(np.clip((np.trace(r)-1)/2, -1, 1))
            axis = np.array([r[2,1]-r[1,2], r[0,2]-r[2,0], r[1,0]-r[0,1]])
            axis /= np.linalg.norm(axis)
            pivot = np.linalg.lstsq(np.eye(3)-r, translation, rcond=1e-8)[0]
        mask = mobile.astype(float).tolist()
        rows.append(dict(scene=path.stem, articulation_type=kind, axis=axis.tolist(),
                         pivot=pivot.tolist(), amount=float(amount),
                         mobility_state0=mask, mobility_state1=mask))
        diagnostics[path.stem] = dict(candidates=candidates, moving_points=int(mobile.sum()),
                                      seconds=time.monotonic()-start)
    return rows, diagnostics


if __name__ == '__main__':
    name, output = sys.argv[1:3]
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    if name in ['shortcut_brute_force', 'shortcut_correspondence_baseline']:
        rows, diagnostic = brute_force_predictions(name == 'shortcut_brute_force')
        Path(output).with_name('brute_force_diagnostics.json').write_text(json.dumps(diagnostic, indent=2))
    else:
        rows = leaked_predictions(name == 'shortcut_generator_answers')
    Path(output).write_text(json.dumps(dict(method=name, results=rows), indent=2))
