# Evaluation Targets

## Primary: synthetic_articulated_gaussians

Tests whether a method can infer articulation and part mobility from two-state observations.
- **Metric**: success (higher is better)
- **Run**: `bash scripts/reproduce.sh` or `bash scripts/evaluate.sh <artifact.json>`

## Constraint: synthetic_articulated_gaussians

Tests whether success comes while preserving geometric consistency with the observed object states.
- **Metric**: reconstruction_chamfer (lower is better)
- **Run**: `bash scripts/evaluate.sh <artifact.json>`

## Constraint: synthetic_articulated_gaussians

Tests whether the inferred decomposition actually separates static and mobile parts rather than only fitting a transform.
- **Metric**: mean_part_iou (higher is better)
- **Run**: `bash scripts/evaluate.sh <artifact.json>`
