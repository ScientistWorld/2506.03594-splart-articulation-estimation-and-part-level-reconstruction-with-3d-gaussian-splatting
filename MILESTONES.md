# Reproduction Milestones

**Current: none**

## Progress Log

### [2026-06-01 16:34] - none
- Read the SPLART paper and identified the core multi-stage algorithm: per-state 3DGS reconstruction, per-Gaussian mobility, cross-static mobility estimation, and cross-mobile articulation optimization.
- Vendored the official SPLART code release into `method/splart_upstream`.
- Implemented a lightweight Gaussian-mean reproduction of the core SPLART mobility and articulation optimization for a first CPU smoke job.
- Added method-agnostic evaluation, a static baseline, scripts, environment setup, and scoring reference structure.

## Stop Justification
- Not stopped. A CPU test job is being submitted to verify the runnable reproduction end to end.
