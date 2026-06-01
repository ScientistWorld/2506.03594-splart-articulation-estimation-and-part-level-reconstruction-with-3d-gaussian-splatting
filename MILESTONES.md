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

### [2026-06-01 17:33] - core_claim
- Fixed the one-CPU verification stall by reducing the lightweight optimizer budget and adding flushed per-scene method progress.
- Re-ran the full reproducible pipeline in job `16b3c3d5-445`; it completed with exit code 0, regenerated baseline and method artifacts, and passed `validate.py --compare`.

## Stop Justification
- Stopping at `core_claim`: the stricter audited benchmark now runs end-to-end in the compute container and demonstrates SPLART-style mobility/articulation recovery over the static baseline. Higher milestones require substantially expanding into the full CUDA 3DGS image-rendering pipeline and PARIS/SPLART-PMS datasets.
