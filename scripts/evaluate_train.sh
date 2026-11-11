#!/bin/bash
# Score every method directory under checkpoints/ on the visible train slice.
#
#   bash scripts/evaluate_train.sh
#
# A method is a directory checkpoints/<name>/ holding predictions/<scene>.npz
# (format: briefing/evaluation.md).  Writes scoring/scores_train.json (and
# per-scene details in scoring/per_scene_train.json).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
mkdir -p scoring
python eval/train/evaluate.py --output scoring/scores_train.json --per-scene-output scoring/per_scene_train.json
