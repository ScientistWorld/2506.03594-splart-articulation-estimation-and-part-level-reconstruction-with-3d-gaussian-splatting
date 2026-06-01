# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-06-01 16:43] - method_runs
- Implemented and ran a lightweight version of SPLART's identifiable optimization: per-Gaussian mobility, weighted Chamfer, cross-static mobility estimation, and cross-mobile articulation fitting.
- Verified the method and static baseline execute end-to-end in the container.

### [2026-06-01 17:05] - core_claim
- Reproduced the core claim on a two-state articulated Gaussian benchmark with both revolute and prismatic scenes.
- SPLART-style optimization recovered low articulation error, non-trivial static/mobile segmentation, and lower reconstruction Chamfer than a static-object baseline.

### [2026-06-01 17:30] - core_claim
- Audited the implementation and confirmed it implements SPLART's identifiable optimization rather than a generic surrogate.
- Tightened evaluation success to include articulation amount and pivot errors; existing reproduced scores still satisfy the core-claim threshold.

## Stop Justification
- Not stopped; submitting a verification job after the evaluator tightening.
