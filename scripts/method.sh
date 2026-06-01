#!/bin/bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

python data/articulated_gaussians.py
python method/lightweight_splart.py \
  --data-dir data/synthetic_splart \
  --output checkpoints/lightweight_splart/results.json \
  --seed "${SEED:-0}" \
  --device "${DEVICE:-cpu}" \
  --mobility-steps "${MOBILITY_STEPS:-160}" \
  --render-steps "${RENDER_STEPS:-80}" \
  --tries "${TRIES:-8}" \
  --coarse-steps "${COARSE_STEPS:-220}" \
  --refine-steps "${REFINE_STEPS:-420}"

if [ -e checkpoints/static_baseline/results.json ]; then
  bash scripts/evaluate.sh checkpoints/lightweight_splart/results.json checkpoints/static_baseline/results.json
else
  bash scripts/evaluate.sh checkpoints/lightweight_splart/results.json
fi
