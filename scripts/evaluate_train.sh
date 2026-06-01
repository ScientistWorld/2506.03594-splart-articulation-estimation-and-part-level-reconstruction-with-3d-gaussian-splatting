#!/bin/bash
# Evaluate the visible train slice of the articulated Gaussian benchmark.
#
# Usage mirrors scripts/evaluate.sh:
#   bash scripts/evaluate_train.sh
#   bash scripts/evaluate_train.sh checkpoints/my_method/results.json
#
# With no explicit artifacts, all checkpoints/*/results.json files are scored.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p scoring

python eval/train/evaluate.py "$@" \
  --output scoring/scores_train.json \
  --per-scene-output scoring/per_scene_train.json
