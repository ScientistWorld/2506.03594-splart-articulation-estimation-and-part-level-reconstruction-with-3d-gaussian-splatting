#!/bin/bash
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
bash redteam/better_mobility_correction/run.sh
bash redteam/shortcut_duplicate_failed_scene/run.sh
python redteam/summarize.py
bash redteam/better_continued_training/run.sh
python redteam/summarize.py
