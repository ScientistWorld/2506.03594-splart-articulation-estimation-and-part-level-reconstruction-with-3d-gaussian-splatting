# Research Direction

## Research Problem

Improve self-supervised recovery of part-level geometry and articulation from two observed states of a two-part articulated object.

## Core Contribution

The paper's contribution is staged optimization of articulated object representations with explicit static/mobile decomposition and shared articulation parameters. Improvements should target robustness or accuracy of this kind of self-supervised articulation and part recovery.

## Approach Scope

Methods may change the parameterization, losses, initialization, optimization schedule, or representation details as long as they still infer articulation and part mobility from the two-state observations without external labels.

## Out of Bounds

- Replacing the problem with supervised part classification or direct use of ground-truth labels
- Ignoring part decomposition and only fitting a rigid transform
- Changing to a different benchmark task such as single-view pose prediction or category-level supervised articulation learning
