# Research Direction

## Research Problem

Self-supervised part-level reconstruction and joint estimation of two-part articulated objects from two observed states (posed RGB images plus sparse, noisy, uncorresponded point clouds), without 3D labels or category priors.

## Core Direction

Make the recovery more reliable and more precise: get the joint right on more objects (including unseen object families, parts that move little, parts geometrically or photometrically similar to the static body, partially visible or occluded surfaces, floaters and noise) and produce part-level reconstructions that render correctly at new views and new articulation states.

## Approach Scope

Any per-scene optimisation, representation, objective, initialisation or search strategy is in scope, as long as each scene is solved from its own observations and the joint type. Learning priors from the visible train scenes is allowed if the method stays category-agnostic (the test slice contains unseen families).

## Out of Bounds

- Using ground-truth answers, external 3D assets or annotations at prediction time.
- Recovering the hidden scenes from the data generator or its random seeds, or hand-writing the object families into the solver.
- Changing the evaluator, the scene files or the output format.
