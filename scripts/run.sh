#!/bin/bash
set -euo pipefail

cd /home/user

bash scripts/reproduce.sh
python validate.py --reference-only
python validate.py --compare
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
