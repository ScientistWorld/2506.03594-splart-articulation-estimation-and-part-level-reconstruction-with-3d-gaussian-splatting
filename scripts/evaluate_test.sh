#!/bin/bash
# Evaluate the held-out test slice of the articulated Gaussian benchmark.
#
# Usage mirrors scripts/evaluate.sh:
#   bash scripts/evaluate_test.sh
#   bash scripts/evaluate_test.sh checkpoints/my_method/results.json
#
# With no explicit artifacts, methods are discovered from scoring/scores_train.json
# and resolved to checkpoints/*/results.json artifacts so train/test method keys
# match exactly.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p scoring

python eval/test/evaluate.py "$@" \
  --train-scores scoring/scores_train.json \
  --output scoring/scores_test.json \
  --per-scene-output scoring/per_scene_test.json
