# Evaluation

## Metrics

The paper reports articulation quality with axis angular error, pivot-line error for revolute joints, rotation-angle error for revolute joints, translation-distance error for prismatic joints, and an articulation success rate. Paper success is based on articulation thresholds: axis error below 5 degrees, pivot-line error below 0.05 for revolute scenes, rotation error below 10 degrees for revolute scenes, and translation error below 0.05 for prismatic scenes.

The paper also evaluates reconstruction and rendering with static/mobile/whole mesh Chamfer distance, PSNR, depth MAE, and part-segmentation mIoU. The lightweight benchmark in this workspace keeps the same two-state articulated-object goal but uses Gaussian point sets instead of full RGB 3DGS scenes. Its stricter success gate includes the paper-like articulation thresholds plus part IoU, mobility calibration, state-consistency, and weighted Chamfer checks so a method cannot pass by fitting motion while ignoring the static/mobile decomposition.

## Baselines and Targets

The included baseline treats all elements as static and estimates no meaningful articulation. The target is to recover both the moving part and articulation parameters from two-state observations, with high success and low geometric error.

## Evaluation Protocol

Run `scripts/reproduce.sh` to generate the benchmark data, run the baseline, run the reference reproduction, and write `scoring/scores.json`. Standalone evaluation is available through `scripts/evaluate.sh`, which reads prediction artifacts and never imports from `method/`. Future methods must emit the same JSON artifact format with per-scene predicted axis, pivot, motion amount, and per-state part-mobility values; all ground-truth-aware metrics are computed inside `eval/`.
