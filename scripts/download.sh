#!/bin/bash
# Fetch / create everything this environment needs.
#
# Estimated total download size: 0 GB (no external datasets or weights).
# Estimated disk usage: ~25 MB of procedural scenes.
#
# The benchmark is procedural.  The scene files are committed to git:
#   data/scenes/train/{inputs,gt}/train_XXX.npz   visible development scenes
#   data/scenes/test/inputs/test_XXX.npz          held-out scene inputs (answers are not public)
# The train scenes are regenerated deterministically if missing (idempotent);
# test inputs cannot be regenerated from public code and come from git.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
n=$(ls data/scenes/train/inputs/*.npz 2>/dev/null | wc -l)
if [ "$n" -lt 18 ]; then
  python data/articulated_objects.py --out data/scenes/train --workers "$(python -c 'import os; print(min(16, os.cpu_count() or 1))')"
fi
n_test=$(ls data/scenes/test/inputs/*.npz 2>/dev/null | wc -l)
if [ "$n_test" -lt 26 ]; then
  echo "data/scenes/test/inputs is incomplete ($n_test/26): restore it from git (git checkout -- data/scenes/test)" >&2
  exit 1
fi
echo "scenes present: train=$n test=$n_test"
