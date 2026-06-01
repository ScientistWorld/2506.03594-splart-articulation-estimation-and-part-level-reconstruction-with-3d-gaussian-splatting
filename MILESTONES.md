# Reproduction Milestones

**Current: method_runs**

## Progress Log

### [2026-06-01 17:38] - method_runs
- Existing lightweight SPLART benchmark runs the staged Gaussian mobility and articulation optimizer end to end.
- Current iteration hardened the benchmark by adding rendering losses, expanding scene coverage, and moving all metric computation into `eval/`.

### [2026-06-01 17:50] - method_runs
- CPU verification job `13f3315a-b7e` completed on the four-scene independent benchmark and validated the workspace structure.
- The method recovered motion parameters and reconstruction geometry, but `success` remained 0.0 because mean part IoU was 0.700, below the 0.750 target.
- Added a same-object mobility consistency regularizer to prevent complementary state masks from satisfying the cross-static loss without a single static/mobile decomposition.

## Stop Justification
- Not stopped. Continuing toward `core_claim` with a CPU verification job for the mobility consistency fix.
