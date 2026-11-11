# Overview

- **Paper:** SPLART: Articulation Estimation and Part-Level Reconstruction with 3D Gaussian Splatting (arXiv 2506.03594).
- **Task:** from posed RGB images (and a sparse visible-surface point cloud) of a two-part articulated object at two end states, recover which parts move, the joint (revolute or prismatic, type known) and a part-level reconstruction that renders at new views and new articulation states.
- **Benchmark here:** procedural articulated objects (13 families: cabinet doors, drawers, laptops, lidded boxes, scissors, levers, sliders, telescopes, sliding panels, and four families only in the hidden test), 18 visible train scenes and 26 held-out test scenes; 20 posed 48x48 views and one independently sampled noisy point cloud per state.
- **Scored experiments:** `articulation_estimation` (paper success rule and errors) and `part_reconstruction` (held-out-view PSNR, part-segmentation mIoU, depth MAE, part Chamfer), see `briefing/evaluation.md`.
- **Reference:** `method/splart.py` (all six SPLART stages); baselines `static_baseline` (nothing moves) and `icp_baseline` (displacement split + multi-start ICP).
- **Paper's reported numbers** (PARIS-PMS / SPLART-PMS) are kept under `_paper_reported` in `scoring/reference.json`; they are on a different scale and are not targets.
