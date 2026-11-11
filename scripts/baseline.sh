#!/bin/bash
# Run the two baselines on every train and test scene:
#   static_baseline : nothing moves (whole object static, zero motion)
#   icp_baseline    : displacement-based part split + multi-start ICP
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
python baseline/static_baseline.py --out checkpoints/static_baseline
python baseline/icp_articulation.py --out checkpoints/icp_baseline
