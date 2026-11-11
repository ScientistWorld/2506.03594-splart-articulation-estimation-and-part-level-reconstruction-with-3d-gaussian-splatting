# Evaluation Targets

All targets are scored on the 26 held-out test scenes (also reported on the 18 train scenes) from `checkpoints/<method>/predictions/`; train with `bash scripts/evaluate_train.sh`, test with the hidden `scripts/evaluate_test.sh`. Reference values are the final reference runs in `scoring/scores_test.json`.

## Primary: articulation_estimation — success_rate (higher is better)

Fraction of scenes whose joint estimate meets the paper's thresholds. Reference SPLART 0.808 (train 0.889); ICP baseline 0.038; static baseline 0.

Supporting metrics in the same experiment (lower is better, truncated at the success thresholds): `axis_error_deg` (reference 1.26), `pivot_error` (0.0005), `rotation_error_deg` (2.30), `translation_error` (0.011).

## Primary: part_reconstruction — psnr (higher is better)

PSNR of renders at held-out views and articulation states, worst value for scenes whose joint fails. Reference 31.9 dB (train 34.4); ICP baseline 10.6; static baseline 10.0.

## Constraint: part_reconstruction — part_miou, depth_mae, cd_static, cd_mobile, cd_whole

A better joint must not come from giving up the part-level reconstruction: static/mobile segmentation of the held-out renders (reference mIoU 0.690), depth (MAE 0.216) and part geometry (Chamfer 0.092 / 0.124 / 0.083) are scored with the same per-scene gating.

## Constraint: validity of the submission

Every value must lie in its documented range and every directory under `checkpoints/` is scored. An invalid file fails the whole run (worst value of every metric of both experiments), and a missing scene gets worst values. Recorded in `scoring/scores_test.json` under `_meta.status`.
