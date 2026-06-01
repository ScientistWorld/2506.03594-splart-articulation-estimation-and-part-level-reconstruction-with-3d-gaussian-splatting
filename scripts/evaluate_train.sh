#!/bin/bash
# Evaluate the visible train slice of the articulated Gaussian benchmark.
#
# Usage mirrors scripts/evaluate.sh:
#   bash scripts/evaluate_train.sh
#   bash scripts/evaluate_train.sh checkpoints/my_method/results.json
#
# With no explicit artifacts, all checkpoints/*/results.json files are scored.

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate.py "$@" \
  --output scoring/scores_train.json \
  --per-scene-output scoring/per_scene_train.json
