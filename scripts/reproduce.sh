#!/bin/bash
# Reproduce the reference end to end: scenes (if missing), baselines, the
# reference method on all scenes, and train-slice scoring.  The held-out test
# slice is scored with scripts/evaluate_test.sh.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
bash scripts/download.sh
bash scripts/baseline.sh
bash scripts/method.sh
bash scripts/evaluate.sh
bash scripts/evaluate_train.sh
