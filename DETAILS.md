# Overview

- **Paper:** SPLART: Articulation Estimation and Part-Level Reconstruction with 3D Gaussian Splatting (arXiv 2506.03594).
- **Task:** from posed RGB images (and a sparse visible-surface point cloud) of a two-part articulated object at two end states, recover which parts move, the joint (revolute or prismatic, type known) and a part-level reconstruction that renders at new views and new articulation states.
- **Benchmark here:** procedural articulated objects (13 families: cabinet doors, drawers, laptops, lidded boxes, scissors, levers, sliders, telescopes, sliding panels, and four families only in the hidden test), 18 visible train scenes and 26 held-out test scenes; 20 posed 48x48 views and one independently sampled noisy point cloud per state.
- **Scored experiments:** `articulation_estimation` (paper success rule and errors) and `part_reconstruction` (held-out-view PSNR, part-segmentation mIoU, depth MAE, part Chamfer), see `briefing/evaluation.md`.
- **Reference:** `method/splart.py` (all six SPLART stages); baselines `static_baseline` (nothing moves) and `icp_baseline` (displacement split + multi-start ICP).
- **Paper's reported numbers** (PARIS-PMS / SPLART-PMS) are kept under `_paper_reported` in `scoring/reference.json`; they are on a different scale and are not targets.

---

# Problem Definition

## Research Question

Reconstruct a two-part articulated object (a static parent and one moving child part) and estimate its joint from observations of the object at two end states of its motion, without 3D labels, part annotations or category priors. The joint type (revolute or prismatic) is known. A solution must say which parts of the reconstruction are static and which move, estimate the joint (axis, pivot for revolute joints, and the motion amount from state 0 to state 1), and produce a part-level reconstruction that renders correctly at new viewpoints and at new articulation states between, and slightly beyond, the two observed ones.

## Why It Matters

Articulated digital twins (doors, drawers, lids, levers, sliders) are needed for robot manipulation and AR/VR. Capturing an object twice with a camera is cheap; annotating parts and joints, or scanning with 3D sensors, is not.

## Observations Per Scene

For each of the two states, independently:

- 20 posed RGB images (48 x 48, white background) with known intrinsics and world-to-camera extrinsics; each state has its own cameras on the upper hemisphere;
- a sparse, noisy, coloured point cloud of the visible surface (380 to 600 points plus a few floaters), sampled independently per state: there is no point correspondence between the states, point order is random and the counts differ.

Objects come in many shapes and random poses, colours and textures; some families appear only in the held-out test scenes. Ground-truth answers for the train scenes are visible; those of the test scenes are not.

## Success Criteria

A good method recovers the joint accurately on most scenes (axis within 5 degrees; revolute: pivot line within 0.05 and rotation within 10 degrees; prismatic: translation within 0.05, in scene units where objects have radius about 0.6), and its static/mobile reconstruction renders the object correctly at unseen views and articulation states, with correct part segmentation and part geometry.

---

# Paper Method (SPLART) and Its Reproduction

SPLART (Lin et al., 2025, arXiv 2506.03594) reconstructs a two-part articulated object from posed RGB images of two articulation states with 3D Gaussian Splatting, gives every Gaussian a differentiable mobility m in [0, 1] (static component opacity sigma(1-m), mobile component sigma*m), and runs a decoupled multi-stage optimisation:

1. **Stage 1** — a separate 3DGS per state from that state's images (photometric L1 + D-SSIM).
2. **Stage 2a** — duplicate the per-state models (G_ref -> G_tgt) and fit mobilities with the cross-static weighted Chamfer consistency: the static components of both states plus the current state's mobile components must match that state's reference (Eq. 3-6), with a small mobility regulariser.
3. **Stage 2b** — cross-static rendering: render G_l plus the static component of G_{1-l} against state-l images, jointly refining Gaussians and mobilities (Eq. 7).
4. **Stage 3a** — articulation by geometric consistency: K_m randomised tries of the mobile-only Chamfer (Eq. 11-12), then a cross-mobile try continued from the best of them and K_cm randomised cross-mobile tries (Eq. 13), then a final joint articulation + mobility run (Eq. 10).
5. **Stage 3b** — cross-mobile rendering: the other state's mobile component is moved by the estimated joint; Gaussians, mobilities and joint are refined photometrically (Eq. 14).
6. **Stage 3c** — mobility correction with the cross-mobile Chamfer (Eq. 15).

## Reproduction (`method/splart.py`)

All six stages are implemented in PyTorch with a differentiable copy of the benchmark's splatting model. Constants follow the official implementation (`method/splart_upstream`): Chamfer nearest-neighbour targets restricted to weights > 0.1, lambda_geom = 1e-4, lambda_photo = 5e-3, articulation randomisation (pivot ~ N(0, 0.3^2), axis ~ uniform, angle ~ U(-pi, pi), distance ~ N(0, 0.1^2)), per-stage learning rates, the convergence rule of the geometric stages (relative change against a running mean), and one view per photometric step with 10000 / 5000 / 10000 steps for Stages 1 / 2b / 3b.

Scaled-down or adapted parts:

- isotropic Gaussians with view-independent colour, 48 x 48 images, initialised from the sparse input point clouds; no densification (low-opacity pruning only);
- mobility logits bounded to [-8, 8] so that Stage 2b can still revise Stage 2a estimates (with the Stage-2a learning rate of 3 the logits otherwise saturate);
- 6 + 6 randomised tries instead of 3 + 3.

`bash scripts/method.sh` runs it on every scene (writes `checkpoints/splart`). Flags reproduce the paper's ablations (`--skip-2a/--skip-2b/--skip-3a/--skip-3b`).

---

# Evaluation

## Data

- `data/scenes/train/inputs/train_XXX.npz` (18 scenes) and `data/scenes/train/gt/train_XXX.npz` (their answers) — the visible development slice, generated by `data/articulated_objects.py`.
- `data/scenes/test/inputs/test_XXX.npz` (26 scenes) — inputs of the held-out slice. Their answers are hidden; the test slice also contains object families that never occur in train.

Input keys: `articulation_type` (`"revolute"` / `"prismatic"`), `points{l}` (N_l x 3), `colors{l}` (N_l x 3, in [0, 1]), `images{l}` (20 x 48 x 48 x 3 uint8), `cams{l}_R` (20 x 3 x 3) and `cams{l}_t` (20 x 3) world-to-camera (OpenCV convention: x right, y down, z forward), `intrinsics` (fx, fy, cx, cy), `image_size`, `background` (white), for states l = 0, 1.

Image formation: `render_gaussians` in `data/articulated_objects.py` — isotropic Gaussians alpha-composited front to back by camera depth; a Gaussian with world standard deviation s at depth z has image variance (fx s / z)^2 + 0.3 and pixel alpha min(0.99, opacity * exp(-d^2 / 2 variance)); pixel centres at integer + 0.5. The same model renders submitted reconstructions.

## What A Method Submits

One directory per method: `checkpoints/<method>/predictions/<scene>.npz`, one file per train and test scene, with numeric arrays only:

| key | shape | meaning |
|---|---|---|
| `axis` | (3,) | joint axis (any non-zero length) |
| `pivot` | (3,) | a point on the rotation axis (ignored for prismatic) |
| `amount` | () | motion from state 0 to state 1: rotation angle in radians about `axis` (right-hand rule, |amount| <= 2 pi) or translation distance along `axis` (|amount| <= 5) |
| `static_means`, `static_scales`, `static_colors`, `static_opacities` | (Ns,3), (Ns,), (Ns,3), (Ns,) | Gaussians of the static part |
| `mobile_means`, `mobile_scales`, `mobile_colors`, `mobile_opacities` | (Nm,3), (Nm,), (Nm,3), (Nm,) | Gaussians of the moving part, placed at their state-0 pose |

Scales are world standard deviations in (0, 1]; colours and opacities lie in [0, 1]; Ns + Nm is between 1 and 20000.

At articulation fraction q (q = 0 is state 0, q = 1 is state 1) the object is the static Gaussians plus the mobile Gaussians moved by fraction q of the predicted motion (rotation by q * amount about the axis line through `pivot`, or translation by q * amount along `axis`).

## Metrics

Experiment `articulation_estimation` (weight 0.6), per scene, then averaged:

- `success_rate` — fraction of scenes with axis error < 5 deg and, for revolute joints, pivot error < 0.05 and rotation error < 10 deg, for prismatic joints translation error < 0.05.
- `axis_error_deg` — angle between predicted and true axis lines (sign-invariant), all scenes.
- `pivot_error` — closest distance between the predicted and true rotation axis lines, revolute scenes.
- `rotation_error_deg` — geodesic distance between predicted and true rotations of the motion, revolute scenes.
- `translation_error` — distance between predicted and true translation vectors, prismatic scenes.

Each error is truncated at its success threshold before averaging, so a failed scene counts as the threshold value.

Experiment `part_reconstruction` (weight 0.4): each scene has 8 hidden cameras at articulation fractions q in [-0.1, 1.1] (two of them at q = 0 and q = 1). The submitted Gaussians are rendered at those cameras and states and compared with the ground truth:

- `psnr` — RGB PSNR (dB) averaged over the views (floored at 10).
- `part_miou` — mean IoU of the background / static / mobile pixel labelling (a pixel is foreground if accumulated alpha >= 0.5 and mobile if the mobile Gaussians contribute more than half of its alpha).
- `depth_mae` — mean absolute error of composited depth (expected depth with background depth 4.0) over pixels that are foreground in either image, per-pixel error capped at 1.
- `cd_static`, `cd_mobile`, `cd_whole` — symmetric Chamfer distance (mean nearest-neighbour distance in both directions) between the centres of submitted Gaussians with opacity >= 0.1 and dense samples of the true observed static surface / mobile surface in its state-0 pose / whole object; capped at 0.2.

A scene whose articulation is not successful gets the worst reconstruction values (psnr 10, part_miou 0, depth_mae 1, Chamfer 0.2).

## Failures

- A missing scene file gets the worst value of every metric for that scene.
- Any invalid file (unreadable or pickled content, missing key, wrong shape, non-finite number, colour or opacity outside [0, 1], non-positive or > 1 scale, zero axis, out-of-range amount, too many Gaussians) makes the whole run failed: every metric of both experiments gets its worst value.
- Every directory under `checkpoints/` is scored; one without valid test predictions is a failed run. Files other than the expected `predictions/<scene>.npz` are ignored, including any score files a method writes.

## Protocol

- `bash scripts/evaluate_train.sh` scores every method on the train slice (`scoring/scores_train.json`, per-scene details in `scoring/per_scene_train.json`); `bash scripts/evaluate.sh` writes the same numbers to `scoring/scores.json`.
- The held-out slice is scored by a separate hidden evaluator in the same way and writes `scoring/scores_test.json`.
- The evaluators only read prediction files; they never import or run method code, and every number is recomputed from the submitted arrays.
- Reference points: `checkpoints/static_baseline` (nothing moves) and `checkpoints/icp_baseline` (displacement-based part split + multi-start ICP), produced by `bash scripts/baseline.sh`.

---

# Reproduction Log

### Iteration 1: gpt-5.5
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 7m | **GPU**: 0.0h
- **Jobs**: 1 total (1 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 16:34] - none
- Read the SPLART paper and identified the core multi-stage algorithm: per-state 3DGS reconstruction, per-Gaussian mobility, cross-static mobility estimation, and cross-mobile articulation optimization.
- Vendored the official SPLART code release into `method/splart_upstream`.
- Implemented a lightweight Gaussian-mean reproduction of the core SPLART mobility and articulation optimization for a first CPU smoke job.
- Added method-agnostic evaluation, a static baseline, scripts, environment setup, and scoring reference structure.

### [2026-06-01 16:42] - core_claim
- CPU smoke job completed successfully with `scripts/reproduce.sh` and `python validate.py --compare`.
- The lightweight SPLART reproduction achieved `success=1.0`, `axis_error_deg=0.5531`, `mean_part_iou=0.8420`, and `reconstruction_chamfer=0.00609` on the two-state articulated Gaussian benchmark.
- The static baseline scored `success=0.0`, `axis_error_deg=90.0`, `mobile_iou=0.0`, and `reconstruction_chamfer=0.04559`, confirming the benchmark distinguishes articulation recovery from static alignment.

</details>

### Iteration 2: gpt-5.5
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h
- **Jobs**: 3 total (2 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 16:43] - method_runs
- Implemented and ran a lightweight version of SPLART's identifiable optimization: per-Gaussian mobility, weighted Chamfer, cross-static mobility estimation, and cross-mobile articulation fitting.
- Verified the method and static baseline execute end-to-end in the container.

### [2026-06-01 17:05] - core_claim
- Reproduced the core claim on a two-state articulated Gaussian benchmark with both revolute and prismatic scenes.
- SPLART-style optimization recovered low articulation error, non-trivial static/mobile segmentation, and lower reconstruction Chamfer than a static-object baseline.

### [2026-06-01 17:30] - core_claim
- Audited the implementation and confirmed it implements SPLART's identifiable optimization rather than a generic surrogate.
- Tightened evaluation success to include articulation amount and pivot errors; existing reproduced scores still satisfy the core-claim threshold.

### [2026-06-01 17:33] - core_claim
- Fixed the one-CPU verification stall by reducing the lightweight optimizer budget and adding flushed per-scene method progress.
- Re-ran the full reproducible pipeline in job `16b3c3d5-445`; it completed with exit code 0, regenerated baseline and method artifacts, and passed `validate.py --compare`.

</details>

### Iteration 3: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 13m | **GPU**: 0.0h
- **Jobs**: 6 total (5 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

</details>

### Iteration 4: gpt-5.5 (designer_stage_1)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 6 total (5 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

</details>

### Iteration 5: gpt-5.5 (designer_stage_2)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h
- **Jobs**: 6 total (5 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

</details>

### Iteration 6: gpt-5.5 (designer_stage_3)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 1m | **GPU**: 0.0h
- **Jobs**: 7 total (6 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

</details>

### Iteration 7: gpt-5.5 (packager)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 3m | **GPU**: 0.0h
- **Jobs**: 7 total (6 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

</details>

### Iteration 8: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 8m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

### [2026-06-01 18:45] - core_claim_plus
- Final verification passed after tightening the aggregate score files, method-agnostic docs, and tracked benchmark data.
- `python validate.py --compare` passes with the added mobility constraint metrics present in `scores.json`.
- The milestone remains `core_claim_plus`; the key limitation is that the gym uses a reduced synthetic benchmark rather than the full paper datasets.

</details>

### Iteration 9: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 7m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

### [2026-06-01 18:46] - core_claim_plus
- Independent audit confirmed that the evaluator reads method artifacts and does not import from `method/`.
- Clarified documentation so paper-reported success is described as articulation-threshold success, while the synthetic gym's success gate is explicitly stricter and includes decomposition and geometry constraints.
- Local reference validation and syntax checks pass; submitting another CPU container verification job to rerun the end-to-end pipeline after the documentation fixes.

### [2026-06-01 18:55] - core_claim_plus
- Final verification confirmed the workspace remains at `core_claim_plus`.
- Cleaned strict method-agnostic evaluation wording and final target documentation.
- `python validate.py --compare` passes with independent artifact-based evaluation.

</details>

### Iteration 10: gpt-6.1-sol (redteam)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 17m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

### [2026-06-01 18:46] - core_claim_plus
- Independent audit confirmed that the evaluator reads method artifacts and does not import from `method/`.
- Clarified documentation so paper-reported success is described as articulation-threshold success, while the synthetic gym's success gate is explicitly stricter and includes decomposition and geometry constraints.
- Local reference validation and syntax checks pass; submitting another CPU container verification job to rerun the end-to-end pipeline after the documentation fixes.

### [2026-06-01 18:55] - core_claim_plus
- Final verification confirmed the workspace remains at `core_claim_plus`.
- Cleaned strict method-agnostic evaluation wording and final target documentation.
- `python validate.py --compare` passes with independent artifact-based evaluation.

</details>

### Iteration 11: claude-opus-5-5 (hardener)
- **Milestone**: `core_claim_plus` | **Status**: error
- **Working time**: 23m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

### [2026-06-01 17:59] - core_claim
- CPU verification job `1c5fb2bf-454` completed successfully with independent evaluation and validation.
- The method reached 0.75 success across four procedural articulated Gaussian scenes, versus 0.0 for the static baseline, with low axis, amount, pivot, and reconstruction errors.
- Added per-scene diagnostic scoring and increased the default optimizer budget for the next run to target the remaining failed scene.

### [2026-06-01 18:10] - core_claim_plus
- CPU verification job `dd07d19d-f0f` completed successfully with independent evaluation and validation.
- The lightweight SPLART reproduction reached 1.0 success on all four expanded scenes, including revolute, tilted revolute, prismatic, and diagonal prismatic settings.
- Per-scene diagnostics in `scoring/per_scene.json` confirm every scene passes the axis, amount, pivot, part IoU, and reconstruction thresholds, while the static baseline remains at 0.0 success.

### [2026-06-01 18:46] - core_claim_plus
- Independent audit confirmed that the evaluator reads method artifacts and does not import from `method/`.
- Clarified documentation so paper-reported success is described as articulation-threshold success, while the synthetic gym's success gate is explicitly stricter and includes decomposition and geometry constraints.
- Local reference validation and syntax checks pass; submitting another CPU container verification job to rerun the end-to-end pipeline after the documentation fixes.

### [2026-06-01 18:55] - core_claim_plus
- Final verification confirmed the workspace remains at `core_claim_plus`.
- Cleaned strict method-agnostic evaluation wording and final target documentation.
- `python validate.py --compare` passes with independent artifact-based evaluation.

</details>


---

# Reproduction Milestones

**Current: core_claim_plus**

## Stop Justification
- Completed at milestone `core_claim_plus`.
