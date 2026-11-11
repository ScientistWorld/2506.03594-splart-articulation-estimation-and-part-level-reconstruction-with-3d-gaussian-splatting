# Train/Test Evaluation Design Notes

Superseded by the final hardening iteration; see `HARDENING.md` and `briefing/evaluation.md`.

- `scripts/evaluate_train.sh` -> `eval/train/evaluate.py` -> `scoring/scores_train.json` (+ `scoring/per_scene_train.json`); ground truth in `data/scenes/train/gt`.
- `scripts/evaluate_test.sh` (no arguments) -> `eval/test/evaluate.py` -> `scoring/scores_test.json`; ground truth only in `eval/test/gt`, generated once by `eval/test/generate_test.py`.
- The two evaluators share no code and never import `method/`; every directory under `checkpoints/` is scored, every number is recomputed from the submitted prediction arrays, invalid runs get the worst value of every metric of both experiments.
