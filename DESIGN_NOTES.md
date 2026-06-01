# Train/Test Evaluation Design Notes

## Checked

- Read `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh` side by side. The train script calls `eval/train/` and writes `scoring/scores_train.json`; the test script calls `eval/test/` and writes `scoring/scores_test.json`.
- Checked train/test evaluators for cross-imports and method detachment. Both slices are self-contained and read method artifacts from `checkpoints/*/results.json` or explicit artifact paths.
- Grepped for hardcoded method defaults, paper-agreement metric names, train/test cross-imports, and hardware-dependent runtime metrics. No forbidden metric names or runtime metrics are used.
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` are absent.
- Ran `bash -n scripts/evaluate_train.sh` and `bash -n scripts/evaluate_test.sh`.

## Changed

- Added three anti-shortcut metrics to both train and test evaluators:
  - `worst_part_iou`, which penalizes methods that solve only the static or only the mobile class while hiding behind mean IoU.
  - `mobility_brier`, which scores soft mobility probabilities and makes threshold-only mask gaming visible.
  - `state_mobility_disagreement`, which penalizes inconsistent state-specific mobility predictions for the same Gaussian.
- Tightened the binary `success` condition to require both adequate worst-class IoU and low mobility Brier score, so success now reflects decomposition quality rather than only average mask quality.
- Clipped mobility predictions to `[0, 1]` after checking shape and finiteness. This prevents negative or over-one mask values from manipulating weighted Chamfer terms.
- Fixed a test-slice resolver issue: explicit artifact paths are now authoritative. A stale `scoring/scores_train.json` can no longer override an explicitly requested test artifact.
- Tightened aggregation so every submitted method must include every scene in the requested slice. Previously, an artifact with no matching slice scenes could be silently ignored when another method had valid scenes.
- Updated `scoring/reference.json` with descriptions for all metrics and schema entries for the new anti-shortcut metrics.

## Runtime Concerns For Next Iteration

- I did not run the Python evaluators or compute new numbers, per the design-only instruction. The runner should verify that existing `checkpoints/lightweight_splart/results.json` remains comfortably below the stricter `mobility_brier < 0.08` and `worst_part_iou > 0.70` success thresholds on both slices.
- The split still has only two scenes per slice. The new metrics triangulate more behavior from each scene, but the next runner should watch for saturation by the lightweight method and for high variance from any method that specializes by articulation type.
- `scoring/reference.json` now defines train/test metrics that the split evaluators compute. The legacy top-level `scripts/evaluate.sh` still uses `eval/evaluate_synthetic.py`; this pass did not modify that off-scope path.

## Runtime Pass

- Submitted CPU job `6cb2c8b2-e30` with `scripts/run.sh` running `scripts/evaluate_train.sh` followed by `scripts/evaluate_test.sh`; exit code was 0.
- Generated `scoring/scores_train.json`, `scoring/scores_test.json`, `scoring/per_scene_train.json`, and `scoring/per_scene_test.json` from the checkpoint artifacts rather than hand-filled values.
- Train and test method sets match exactly: `splart_lightweight` and `static_baseline`.
- The score files are not byte-identical. Train uses `revolute_hinge` and `prismatic_diagonal`; test uses `revolute_tilted_axis` and `prismatic_slider`. Articulation and reconstruction metrics move between slices.
- `splart_lightweight` succeeds on both slices and remains comfortably inside the stricter thresholds. Its continuous metrics leave room for improvement: train/test axis error is `0.5035/0.7875` degrees, amount error is `0.0091/0.0182`, pivot error is `0.0004/0.0095`, and mobility Brier is `0.0029/0.0007`.
- Segmentation IoU for `splart_lightweight` is near-perfect and reaches `1.0` on the test slice. This is a caveat for the part-IoU metrics, but the split still has non-saturated geometric and soft-mask quantities, while the static baseline remains separated on mobile IoU, Brier score, and success.

## Validation Fix

- Stage-3 validation rejected binary `success` as the primary metric because it is identical across train and test for every method (`splart_lightweight` succeeds on both, `static_baseline` fails on both).
- Replaced the ranked primary metric with continuous `quality_score`, which combines articulation error, motion amount error, pivot error, part IoU, and reconstruction Chamfer. Binary `success` remains reported as a threshold summary.
- `quality_score` is intentionally computed from scientific quantities already used by the evaluator, not from agreement with paper numbers, so it gives future agents a non-saturated train signal and a held-out test comparison.
