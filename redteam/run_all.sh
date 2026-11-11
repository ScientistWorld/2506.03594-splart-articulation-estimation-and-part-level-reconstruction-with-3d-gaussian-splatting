#!/bin/bash
set -uo pipefail
TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_ROOT"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
mkdir -p redteam/_state
# Two independent CPU training processes at a time, each with one torch thread.
# Save every case before proceeding; shortcut cases reuse original trained output.
for pair in 'reference_seed0 reference_seed1' 'reference_seed2 better_annealed'; do
  read -r first second <<< "$pair"
  bash "redteam/$first/run.sh" > "redteam/_state/$first.log" 2>&1 &
  first_pid=$!
  bash "redteam/$second/run.sh" > "redteam/_state/$second.log" 2>&1 &
  second_pid=$!
  wait "$first_pid" || echo "Case failed: $first"
  wait "$second_pid" || echo "Case failed: $second"
done
for name in reference_original weaker_short_training static_baseline \
  shortcut_npz_answers shortcut_generator_answers shortcut_brute_force shortcut_correspondence_baseline \
  shortcut_duplicate_scenes shortcut_self_reported_scores shortcut_all_mobile shortcut_all_static \
  shortcut_empty_results shortcut_null_axis shortcut_nonfinite_axis shortcut_nonfinite_mobility \
  shortcut_impossible_mobility shortcut_missing_scene shortcut_hidden_failed_method \
  shortcut_baseline_replacement shortcut_replace_fixed_data shortcut_fail_success_gate; do
  bash "redteam/$name/run.sh" || echo "Case failed: $name"
done
python redteam/summarize.py
