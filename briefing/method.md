# Paper Method (SPLART) and Its Reproduction

SPLART (Lin et al., 2025, arXiv 2506.03594) reconstructs a two-part articulated object from posed RGB images of two articulation states with 3D Gaussian Splatting, gives every Gaussian a differentiable mobility m in [0, 1] (static component opacity sigma(1-m), mobile component sigma*m), and runs a decoupled multi-stage optimisation:

1. **Stage 1** — a separate 3DGS per state from that state's images (photometric L1 + D-SSIM).
2. **Stage 2a** — duplicate the per-state models (G_ref -> G_tgt) and fit mobilities with the cross-static weighted Chamfer consistency: the static components of both states plus the current state's mobile components must match that state's reference (Eq. 3-6), with a small mobility regulariser.
3. **Stage 2b** — cross-static rendering: render G_l plus the static component of G_{1-l} against state-l images, jointly refining Gaussians and mobilities (Eq. 7).
4. **Stage 3a** — articulation by geometric consistency: K_m randomised tries of the mobile-only Chamfer (Eq. 11-12), then a cross-mobile try continued from the best of them and K_cm randomised cross-mobile tries (Eq. 13), then a final joint articulation + mobility run (Eq. 10).
5. **Stage 3b** — cross-mobile rendering: the other state's mobile component is moved by the estimated joint; Gaussians, mobilities and joint are refined photometrically (Eq. 14).
6. **Stage 3c** — mobility correction with the cross-mobile Chamfer (Eq. 15).

## Reproduction (`method/splart.py`)

All six stages are implemented in PyTorch with a differentiable copy of the benchmark's splatting model. Constants follow the official implementation (`method/splart_upstream`): Chamfer nearest-neighbour targets restricted to weights > 0.1, lambda_photo = 5e-3, articulation randomisation (pivot ~ N(0, 0.3^2), axis ~ uniform, angle ~ U(-pi, pi), distance ~ N(0, 0.1^2)), per-stage learning rates, the convergence rule of the geometric stages (relative change against a running mean), and one view per photometric step with 10000 / 5000 / 10000 steps for Stages 1 / 2b / 3b.

Scaled-down or adapted parts:

- isotropic Gaussians with view-independent colour, 48 x 48 images, initialised from the sparse input point clouds; no densification (low-opacity pruning only);
- lambda_geom = 2e-3 instead of 1e-4: the cross-static term labels a Gaussian mobile when its squared distance to the other state exceeds about lambda_geom, and these reconstructions are ~200x sparser than the paper's;
- mobility logits bounded to [-8, 8] so that Stage 2b can still revise saturated Stage 2a estimates;
- 6 + 6 randomised tries instead of 3 + 3.

`bash scripts/method.sh` runs it on every scene (writes `checkpoints/splart`). Flags reproduce the paper's ablations (`--skip-2a/--skip-2b/--skip-3a/--skip-3b`).
