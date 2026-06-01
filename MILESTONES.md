# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-06-01 16:34] - none
- Read the SPLART paper and identified the core multi-stage algorithm: per-state 3DGS reconstruction, per-Gaussian mobility, cross-static mobility estimation, and cross-mobile articulation optimization.
- Vendored the official SPLART code release into `method/splart_upstream`.
- Implemented a lightweight Gaussian-mean reproduction of the core SPLART mobility and articulation optimization for a first CPU smoke job.
- Added method-agnostic evaluation, a static baseline, scripts, environment setup, and scoring reference structure.

### [2026-06-01 16:42] - core_claim
- CPU smoke job completed successfully with `scripts/reproduce.sh` and `python validate.py --compare`.
- The lightweight SPLART reproduction achieved `success=1.0`, `axis_error_deg=0.5531`, `mean_part_iou=0.8420`, and `reconstruction_chamfer=0.00609` on the two-state articulated Gaussian benchmark.
- The static baseline scored `success=0.0`, `axis_error_deg=90.0`, `mobile_iou=0.0`, and `reconstruction_chamfer=0.04559`, confirming the benchmark distinguishes articulation recovery from static alignment.

## Stop Justification
- Completed at milestone `core_claim`.
