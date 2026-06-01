# Evaluation

## Metrics

Articulation quality is measured by axis angular error in degrees, motion amount error, and pivot-line error for revolute scenes. Part decomposition is measured with static, mobile, and mean part IoU. Geometry consistency is measured with weighted Chamfer distance between the reconstructed articulated Gaussian sets and the observed state sets. The benchmark also reports a success rate: a scene succeeds when the axis error is below 5 degrees, motion amount error is below 0.05, pivot-line error is below 0.05 for revolute scenes, mean part IoU is above 0.75, and reconstruction Chamfer is below 0.01.

## Baselines and Targets

The included baseline treats all points as static and estimates no meaningful articulation. The target is to recover both the moving part and articulation parameters from two-state observations, with high success and low geometric error.

## Evaluation Protocol

Run `scripts/reproduce.sh` to generate the benchmark data, run the baseline, run the proposed method, and write `scoring/scores.json`. Standalone evaluation is available through `scripts/evaluate.sh`, which reads prediction artifacts and never imports from `method/`. Future methods must emit the same JSON artifact format with per-scene predicted axis, pivot, motion amount, and per-state mobility values; all ground-truth-aware metrics are computed inside `eval/`.
