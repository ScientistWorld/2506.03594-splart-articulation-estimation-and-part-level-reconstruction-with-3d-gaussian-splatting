# Verification Report

## Initial Assessment

The workspace started at `core_claim_plus` with a working lightweight reproduction of the paper's two-state articulated-object claim. The claimed milestone was justified by existing container-run results: the reference reproduction succeeds on all four synthetic scenes and the static baseline fails.

## Issues Found

- **Minor:** `scores.json` did not include the newer mobility constraint metrics declared in `reference.json`, although the train/test per-scene outputs already contained them.
- **Minor:** `scoring/EXPERIMENTS.md` listed reference-only paper table anchors in addition to the actual scored experiment, which could confuse future gym users.
- **Minor:** `briefing/evaluation.md` and `scoring/DIRECTION.md` used a few method-specific phrases where method-agnostic wording was clearer.
- **Minor:** the small generated benchmark `.npz` files in `data/synthetic_splart/` were ignored even though they are small, agent-authored data needed for fresh-clone evaluation.
- **Cosmetic:** generated run artifacts and Python caches were present in the working tree; tracked job artifacts had already been removed by the previous iteration.

## Fixes Applied

- Rebuilt `scoring/scores.json`, `scoring/scores_train.json`, and `scoring/scores_test.json` from the completed per-scene evaluator outputs so all declared metrics are present.
- Narrowed `scoring/EXPERIMENTS.md` to the single experiment actually present in `scores.json`.
- Reworded method-agnostic documentation in `briefing/evaluation.md`, `scoring/DIRECTION.md`, and `data/articulated_gaussians.py`.
- Added `.gitignore` exceptions and staged the four small benchmark files under `data/synthetic_splart/`.
- Removed local generated caches and ignored job/log artifacts where possible.

## Final Judgment

The workspace is ready to serve as a gym. Improve-mode agents can run the reference reproduction and compare against the recorded results; from-scratch agents can use the data, evaluation code, constraints, and direction without importing the paper method. The main limitation is that this is a reduced synthetic benchmark rather than the full image-rendering SPLART/PARIS evaluation.

- Milestone: core_claim_plus
- Ready for gym use: yes
- Confidence: medium
- Key limitation: reduced synthetic data only
