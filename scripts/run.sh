#!/bin/bash
# Reproduce the reference end to end: scenes check, baselines, the reference
# SPLART on all train and test scenes, train and test scoring, validation.
# (The hardening experiments are in notes/hardening/run_hardening.sh.)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
bash scripts/reproduce.sh
bash scripts/evaluate_test.sh
python validate.py
