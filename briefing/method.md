# Paper's Method

## Key Contribution

SPLART augments 3D Gaussian Splatting with a differentiable mobility value per Gaussian and optimizes a staged set of geometric and rendering objectives to segment static/mobile parts and estimate a revolute or prismatic articulation from two posed RGB image sets.

## Approach

Stage 1 independently reconstructs a 3DGS model for each articulation end state from photometric supervision. Stage 2 duplicates the per-state Gaussians, gives each Gaussian a mobility scalar, and uses a cross-static formulation in which static components from both states are shared while the current state's mobile components explain the target state. Stage 3 uses a cross-mobile formulation: mobile components from the other state are transformed by the estimated articulation and jointly explain the target state. The full paper refines these stages with 3DGS rendering losses; this reproduction includes the official upstream implementation and a lightweight Gaussian-mean benchmark that executes the same mobility, weighted Chamfer, cross-static, and cross-mobile computations.

## Main Claims

The primary claim is that staged self-supervision over mobile Gaussian components recovers articulation and part-level reconstruction without 3D labels or category priors. Secondary claims are that the staged optimization is more robust than direct joint optimization and that 3DGS provides high-quality, fast rendering once optimized.
