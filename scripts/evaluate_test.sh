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

cd /home/user

mkdir -p scoring

python eval/test/evaluate.py "$@" \
  --train-scores scoring/scores_train.json \
  --output scoring/scores_test.json \
  --per-scene-output scoring/per_scene_test.json
