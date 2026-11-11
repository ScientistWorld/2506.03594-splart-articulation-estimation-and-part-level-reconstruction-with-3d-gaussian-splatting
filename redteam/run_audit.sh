#!/bin/bash
# Replay the two completed CPU audit batches inside the gym container.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
bash redteam/run_all.sh
bash redteam/run_followup.sh
