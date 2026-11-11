# Overview

- **Paper ID:** 2506.03594
- **Title:** SPLART: Articulation Estimation and Part-Level Reconstruction with 3D Gaussian Splatting
- **Domain:** Computer Vision / 3D Reconstruction
- **TL;DR:** SPLART reconstructs two-part articulated objects and estimates their motion from two-state posed RGB images using self-supervised 3D Gaussian Splatting.

## Short Summary

The paper targets category-agnostic reconstruction of articulated objects with a static parent and moving child part. SPLART extends 3D Gaussian Splatting with per-Gaussian mobility and a multi-stage optimization pipeline that first reconstructs each state, then estimates mobility, then estimates and refines articulation. Reported results show strong articulation accuracy and novel-view synthesis on PARIS-PMS and SPLART-PMS without 3D supervision.

## Key Results

- PARIS-PMS overall articulation success: 99.0%, with overall PSNR 43.70 and mIoU 0.957 in the main tables.
- SPLART-PMS overall articulation success: 85.5%, with overall PSNR 37.01 and mIoU 0.916.
- The method includes ablations showing that both geometric and photometric stages contribute to robust articulation estimation.

---

# Problem Definition

## Research Question

Recover a two-part articulated object from posed observations captured at two end states of motion. A successful system should infer which object elements belong to the static parent and moving child part, estimate the articulation parameters for either a revolute or prismatic joint, and reconstruct the object consistently across the observed states.

## Why It Matters

Articulated object reconstruction enables digital twins for robotics, AR/VR, and manipulation planning without requiring manual part annotations or 3D supervision.

## Success Criteria

The method should accurately estimate joint axis and motion amount, identify static and moving parts, preserve 3D geometry across the two observed states, and outperform a no-motion/static-object baseline under the same data and evaluation protocol.

---

# Paper's Method

## Key Contribution

SPLART augments 3D Gaussian Splatting with a differentiable mobility value per Gaussian and optimizes a staged set of geometric and rendering objectives to segment static/mobile parts and estimate a revolute or prismatic articulation from two posed RGB image sets.

## Approach

Stage 1 independently reconstructs a 3DGS model for each articulation end state from photometric supervision. Stage 2 duplicates the per-state Gaussians, gives each Gaussian a mobility scalar, and uses a cross-static formulation in which static components from both states are shared while the current state's mobile components explain the target state. Stage 3 uses a cross-mobile formulation: mobile components from the other state are transformed by the estimated articulation and jointly explain the target state. The full paper refines these stages with 3DGS rendering losses; this reproduction includes the official upstream implementation and a lightweight Gaussian-mean benchmark that executes the same mobility, weighted Chamfer, cross-static, and cross-mobile computations.

## Main Claims

The primary claim is that staged self-supervision over mobile Gaussian components recovers articulation and part-level reconstruction without 3D labels or category priors. Secondary claims are that the staged optimization is more robust than direct joint optimization and that 3DGS provides high-quality, fast rendering once optimized.

---

# Evaluation

## Metrics

The scored task measures whether a method can recover a two-state articulated object from provided observations. Articulation quality is measured by axis angular error, motion amount error, and pivot-line error for revolute joints. Part decomposition quality is measured with mobile/static/mean IoU, worst-part IoU, mobility Brier score, and state-mobility disagreement. Geometric consistency is measured with opacity-weighted reconstruction Chamfer between the predicted two-state representation and the observed states.

The aggregate `quality_score` combines articulation accuracy, part decomposition, and reconstruction consistency; higher is better. A scene-level `success` flag is 1 only when all required articulation, decomposition, calibration, and geometry thresholds are met.

## Baselines and Targets

The included baseline treats all elements as static and estimates no meaningful articulation. The target is to recover both the moving part and articulation parameters from two-state observations, with high success and low geometric error.

## Evaluation Protocol

Standalone evaluation is available through `scripts/evaluate.sh`, which reads prediction artifacts and never imports from `method/`. `scripts/reproduce.sh` demonstrates the packaged end-to-end flow and writes `scoring/scores.json`. Future methods must emit the same JSON artifact format with per-scene predicted axis, pivot, motion amount, and per-state part-mobility values; all ground-truth-aware metrics are computed inside `eval/`.

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


---

# Reproduction Milestones

**Current: core_claim_plus**

## Stop Justification
- Completed at milestone `core_claim_plus`.
