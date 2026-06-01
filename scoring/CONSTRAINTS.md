# Scientist Constraints

## Data

Use the generated scenes in `data/synthetic_splart` with the generator in `data/articulated_gaussians.py`. Do not add extra scenes, labels, external 3D assets, or additional supervision when reporting the benchmark score.

## Evaluation

Report scores only through `scripts/evaluate.sh`, which reads output artifacts. Do not modify `eval/` or `scoring/reference.json` to improve results.

## Problem Formulation

The method must solve the two-part, two-state articulation problem with known articulation type. It must output per-scene metrics for motion, part decomposition, and reconstruction consistency in the expected artifact format.

## Compliance Checklist

- [ ] Uses only the provided generated scenes for scored results
- [ ] Does not train or tune on hidden ground-truth labels except through final evaluation
- [ ] Writes method outputs as artifacts consumed by `scripts/evaluate.sh`
- [ ] Keeps the benchmark's two-state articulated object setting fixed
