#!/bin/bash
# Score every method directory under checkpoints/ on the held-out test slice.
#
#   bash scripts/evaluate_test.sh
#
# Takes no arguments: every checkpoints/<name>/ directory is a method and is
# scored (a directory without valid test predictions is scored as a failed
# run).  Writes scoring/scores_test.json.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
mkdir -p scoring
python eval/test/evaluate.py --output scoring/scores_test.json
