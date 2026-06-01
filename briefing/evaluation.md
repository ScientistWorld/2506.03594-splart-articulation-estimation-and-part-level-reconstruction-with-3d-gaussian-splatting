# Evaluation

## Metrics

The scored task measures whether a method can recover a two-state articulated object from provided observations. Articulation quality is measured by axis angular error, motion amount error, and pivot-line error for revolute joints. Part decomposition quality is measured with mobile/static/mean IoU, worst-part IoU, mobility Brier score, and state-mobility disagreement. Geometric consistency is measured with opacity-weighted reconstruction Chamfer between the predicted two-state representation and the observed states.

The aggregate `quality_score` combines articulation accuracy, part decomposition, and reconstruction consistency; higher is better. A scene-level `success` flag is 1 only when all required articulation, decomposition, calibration, and geometry thresholds are met.

## Baselines and Targets

The included baseline treats all elements as static and estimates no meaningful articulation. The target is to recover both the moving part and articulation parameters from two-state observations, with high success and low geometric error.

## Evaluation Protocol

Standalone evaluation is available through `scripts/evaluate.sh`, which reads prediction artifacts and never imports from `method/`. `scripts/reproduce.sh` demonstrates the packaged end-to-end flow and writes `scoring/scores.json`. Future methods must emit the same JSON artifact format with per-scene predicted axis, pivot, motion amount, and per-state part-mobility values; all ground-truth-aware metrics are computed inside `eval/`.
