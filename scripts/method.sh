#!/bin/bash
# Run the reference method (method/splart.py) on every train and test scene.
# Scenes are split into shards run in parallel (4 per GPU, or one per CPU core).
# Finished scenes are skipped, so the script can be re-run to resume.
#
#   bash scripts/method.sh                 # writes checkpoints/splart/predictions
#   OUT=checkpoints/x SEED=1 bash scripts/method.sh --color-weight 0.1
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
OUT="${OUT:-checkpoints/splart}"
SEED="${SEED:-0}"
NGPU=$(python -c "import torch; print(torch.cuda.device_count() if torch.cuda.is_available() else 0)")
if [ "$NGPU" -gt 0 ]; then SHARDS=$((NGPU * 4)); else SHARDS=$(python -c "import os; print(max(1, min(32, os.cpu_count() or 1)))"); fi
echo "[method.sh] gpus=$NGPU shards=$SHARDS out=$OUT seed=$SEED"
pids=()
for i in $(seq 0 $((SHARDS - 1))); do
  python method/splart.py --out "$OUT" --seed "$SEED" --shard "$i" --num-shards "$SHARDS" "$@" &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
