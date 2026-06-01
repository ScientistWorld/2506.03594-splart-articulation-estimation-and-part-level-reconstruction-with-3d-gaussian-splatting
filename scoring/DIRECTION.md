# Research Direction

## Research Problem

Improve self-supervised recovery of part-level geometry and articulation from two observed states of a two-part articulated object.

## Core Direction

Improvements should target robust, label-free recovery of articulation parameters, part assignments, and state-consistent geometry from two observed configurations of the same object.

## Approach Scope

Methods may change their representation, parameterization, training data usage within the provided benchmark, and inference procedure as long as they still infer articulation and part membership from the two-state observations without external labels.

## Out of Bounds

- Replacing the problem with supervised part classification or direct use of ground-truth labels
- Ignoring part decomposition and only fitting a rigid transform
- Changing to a different benchmark task such as single-view pose prediction or category-level supervised articulation learning
