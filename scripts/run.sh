#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

bash scripts/reproduce.sh
python validate.py --reference-only
python validate.py --compare
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
