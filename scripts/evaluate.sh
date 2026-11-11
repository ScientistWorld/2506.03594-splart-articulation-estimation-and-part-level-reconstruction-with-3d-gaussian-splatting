#!/bin/bash
# Standard evaluation entry point: scores every method directory under
# checkpoints/ on the visible train slice and writes scoring/scores.json.
# Uses only eval/ (never method/).  Prediction format: briefing/evaluation.md.
#
#   bash scripts/evaluate.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
mkdir -p scoring
python eval/train/evaluate.py --output scoring/scores.json
