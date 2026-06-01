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
