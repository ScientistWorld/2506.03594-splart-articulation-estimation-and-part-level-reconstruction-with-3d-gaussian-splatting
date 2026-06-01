# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

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

## Stop Justification
- Not stopped; a CPU verification job is being submitted to re-run the packaged reproduction path.
