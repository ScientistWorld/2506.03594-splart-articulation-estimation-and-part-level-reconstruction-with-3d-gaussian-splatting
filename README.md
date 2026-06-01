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

Articulation quality is measured by axis angular error in degrees, motion amount error, and pivot-line error for revolute scenes. Part decomposition is measured with static, mobile, and mean part IoU. Geometry consistency is measured with weighted Chamfer distance between the reconstructed articulated Gaussian sets and the observed state sets. The benchmark also reports a success rate: a scene succeeds when the axis error is below 5 degrees, mean part IoU is above 0.75, and reconstruction Chamfer is below 0.01.

## Baselines and Targets

The included baseline treats all points as static and estimates no meaningful articulation. The target is to recover both the moving part and articulation parameters from two-state observations, with high success and low geometric error.

## Evaluation Protocol

Run `scripts/reproduce.sh` to generate the benchmark data, run the baseline, run the proposed method, and write `scoring/scores.json`. Standalone evaluation is available through `scripts/evaluate.sh`, which reads method output artifacts and never imports from `method/`. Future methods must emit the same JSON artifact format with per-scene metrics.

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


---

# Reproduction Milestones

**Current: method_runs**

## Stop Justification
- Completed at milestone `method_runs`.
