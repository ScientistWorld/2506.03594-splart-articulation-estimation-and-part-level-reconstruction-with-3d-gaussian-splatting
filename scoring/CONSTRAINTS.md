# Scientist Constraints

## Data

- Use only the provided observations: `data/scenes/{train,test}/inputs`. Each scene must be solved from its own two-state observations plus the known joint type.
- Train answers (`data/scenes/train/gt`) may be used for development and tuning, never as inputs at prediction time for any scene.
- Do not use external 3D assets, part annotations, pretrained articulation models or extra rendered views. Do not try to recover the hidden test answers (e.g. by reverse-engineering the scene generator or its seeds); a separate review checks submissions for this.

## Output

- Write `checkpoints/<method>/predictions/<scene>.npz` for every train and test scene in the format of `briefing/evaluation.md`. Every directory under `checkpoints/` is scored, so remove abandoned ones.
- The representation must stay renderable by the evaluator's splatting model (static and mobile Gaussian sets plus one joint).

## Evaluation

- Scores come only from `scripts/evaluate_train.sh` / `scripts/evaluate.sh` (train) and the hidden test evaluator. Do not modify `eval/`, `data/scenes/`, `data/articulated_objects.py` or `scoring/reference.json`.
- Thresholds, held-out cameras and articulation states, the test size and the rendering model are fixed by the evaluator.

## Compliance Checklist

- [ ] Each scene's prediction is computed only from that scene's inputs and the joint type
- [ ] No ground-truth file is read at prediction time
- [ ] One prediction file per scene, numeric arrays only, within the documented ranges
- [ ] No stale method directories left in `checkpoints/`
