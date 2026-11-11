# Progress

Final state after the hardening iteration (details and evidence: `HARDENING.md`).

## What works

- `data/articulated_objects.py` generates two-state observations (20 posed 48x48 RGB views + an independent, noisy, visible-surface point cloud per state) of procedural articulated objects; 18 train scenes with visible answers and 26 test scenes (inputs in `data/scenes/test/inputs`, answers only in `eval/test/gt`).
- `method/splart.py` implements SPLART's Stages 1, 2a, 2b, 3a, 3b and 3c with a differentiable splatting renderer and the upstream constants and schedule.
- `baseline/static_baseline.py` (nothing moves) and `baseline/icp_articulation.py` (displacement split + multi-start ICP).
- `eval/train/evaluate.py` and the hidden `eval/test/evaluate.py` score every method directory under `checkpoints/` (articulation_estimation, part_reconstruction) with strict validation and worst values for failures.

## Results (hidden test, 26 scenes)

| Method | success | PSNR | mIoU |
|---|---:|---:|---:|
| SPLART reference | 0.808 | 31.9 | 0.690 |
| ICP baseline | 0.038 | 10.6 | 0.029 |
| static baseline | 0 | 10.0 | 0 |

Train slice: SPLART 0.889 success, PSNR 34.4.

## Known issues

- Skipping Stage 2a beats the full reference (0.885 success); the paper reports the opposite (small) effect.
- GPU nondeterminism: reruns of the identical configuration differ by up to R* 0.24.
- Procedural data, low resolution and isotropic Gaussians instead of the paper's PartNet-Mobility renders and full 3DGS; PARIS / DTA are not reproduced (paper numbers kept under `_paper_reported`).
