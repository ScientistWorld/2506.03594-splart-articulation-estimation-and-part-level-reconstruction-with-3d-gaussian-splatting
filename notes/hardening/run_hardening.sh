#!/bin/bash
# Hardening job: data, baselines, reference SPLART, variants, shortcuts,
# evaluation through the hidden test evaluator, and the summary tables.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
mkdir -p tmp/hardening/eval tmp/hardening/logs
NW=$(python -c "import os; print(max(1, min(32, os.cpu_count() or 1)))")

echo "=== environment"
nvidia-smi || true
python -c "import torch, numpy, os; print('torch', torch.__version__, 'numpy', numpy.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.device_count(), 'cpus', os.cpu_count())"

echo "=== data ($NW workers)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python data/articulated_objects.py --out data/scenes/train --workers "$NW" || exit 1
python eval/test/generate_test.py --workers "$NW" || exit 1
ls data/scenes/train/inputs data/scenes/test/inputs eval/test/gt | head -5

echo "=== baselines"
python baseline/static_baseline.py || exit 1
python baseline/icp_articulation.py > tmp/hardening/logs/icp_baseline.log 2>&1 || { tail -30 tmp/hardening/logs/icp_baseline.log; exit 1; }

echo "=== evaluator check on baselines"
python eval/train/evaluate.py --output tmp/hardening/eval/early_train.json || exit 1
python eval/test/evaluate.py --output tmp/hardening/eval/early_test.json || exit 1

echo "=== method smoke test"
python method/splart.py --out tmp/hardening/smoke_root/smoke --scenes train_000 train_005 \
  --s1-iters 20 --s2b-iters 10 --s3b-iters 10 --geom-max-iters 40 || exit 1
n_smoke=$(ls tmp/hardening/smoke_root/smoke/predictions/*.npz 2>/dev/null | wc -l)
if [ "$n_smoke" -ne 2 ]; then echo "smoke test produced $n_smoke predictions"; exit 1; fi
python eval/train/evaluate.py --root tmp/hardening/smoke_root --output tmp/hardening/eval/smoke_train.json || exit 1
cat tmp/hardening/smoke_root/smoke/logs/train_000.json | head -c 1500; echo

echo "=== brute-force ICP (background, skipped if already complete)"
ICP_PID=""
if [ "$(ls tmp/hardening/variants/icp_bruteforce/predictions/*.npz 2>/dev/null | wc -l)" -lt 26 ]; then
  python baseline/icp_articulation.py --inputs data/scenes/test/inputs --out tmp/hardening/variants/icp_bruteforce \
    --restarts 512 > tmp/hardening/logs/icp_bruteforce.log 2>&1 &
  ICP_PID=$!
fi

echo "=== reference and variants"
python notes/hardening/driver.py
[ -n "$ICP_PID" ] && wait $ICP_PID

echo "=== evaluation"
bash scripts/evaluate.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
python eval/train/evaluate.py --output tmp/hardening/eval/checkpoints_train.json --per-scene-output tmp/hardening/eval/checkpoints_train_per_scene.json
python eval/test/evaluate.py --output tmp/hardening/eval/checkpoints_test.json --per-scene-output tmp/hardening/eval/checkpoints_test_per_scene.json
python eval/test/evaluate.py --root tmp/hardening/variants --output tmp/hardening/eval/variants_test.json --per-scene-output tmp/hardening/eval/variants_test_per_scene.json
python eval/train/evaluate.py --root tmp/hardening/variants --output tmp/hardening/eval/variants_train.json
python notes/hardening/make_shortcuts.py
python eval/test/evaluate.py --root tmp/hardening/shortcuts --output tmp/hardening/eval/shortcuts_test.json --per-scene-output tmp/hardening/eval/shortcuts_test_per_scene.json
python notes/hardening/analyze.py

echo "=== save evidence"
mkdir -p notes/hardening/eval notes/hardening/method_logs
cp tmp/hardening/eval/*.json notes/hardening/eval/
cp tmp/hardening/driver_summary.json notes/hardening/ 2>/dev/null || true
for d in checkpoints/splart tmp/hardening/variants/*; do
  [ -d "$d/logs" ] && mkdir -p "notes/hardening/method_logs/$(basename "$d")" && cp "$d"/logs/*.json "notes/hardening/method_logs/$(basename "$d")/" 2>/dev/null
done
python validate.py || true
echo "=== done"
