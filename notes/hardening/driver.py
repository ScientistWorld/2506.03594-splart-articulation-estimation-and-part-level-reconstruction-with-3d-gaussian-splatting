"""Run the reference method and its variants as a prioritised pool of scene shards.

Used by notes/hardening/run_hardening.sh.  Each task runs method/splart.py on
chunks of scenes; finished scenes are skipped on restart.  New chunks stop
being launched after --launch-deadline seconds and running ones are killed
after --kill-deadline seconds, so the evaluation that follows always runs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAIN = "data/scenes/train/inputs"
TEST = "data/scenes/test/inputs"
VAR = "tmp/hardening/variants"

# (name, output dir, inputs, extra args) in priority order
TASKS = [
    ("splart", "checkpoints/splart", [TRAIN, TEST], []),
    ("splart_seed1", f"{VAR}/splart_seed1", [TEST], ["--seed", "1"]),
    ("better_color_geom", f"{VAR}/better_color_geom", [TEST], ["--color-weight", "0.1"]),
    ("weaker_short", f"{VAR}/weaker_short", [TEST], ["--s1-iters", "300", "--s2b-iters", "150", "--s3b-iters", "300", "--k-m", "1", "--k-cm", "1"]),
    ("splart_seed2", f"{VAR}/splart_seed2", [TEST], ["--seed", "2"]),
    ("ablation_no3a", f"{VAR}/ablation_no3a", [TEST], ["--skip-3a"]),
    ("ablation_no3b", f"{VAR}/ablation_no3b", [TEST], ["--skip-3b"]),
    ("search_more", f"{VAR}/search_more", [TEST], ["--k-m", "8", "--k-cm", "8", "--s1-iters", "4000", "--s2b-iters", "2000", "--s3b-iters", "4000", "--geom-max-iters", "6000"]),
    ("ablation_no2a", f"{VAR}/ablation_no2a", [TEST], ["--skip-2a"]),
    ("ablation_no2b", f"{VAR}/ablation_no2b", [TEST], ["--skip-2b"]),
    ("better_color_geom_train", f"{VAR}/better_color_geom", [TRAIN], ["--color-weight", "0.1"]),
]


def gpu_count() -> int:
    code = "import torch\ntry:\n  n=torch.cuda.device_count() if torch.cuda.is_available() else 0\n  [torch.zeros(1,device=f'cuda:{i}').sum().item() for i in range(n)]\nexcept Exception:\n  n=0\nprint(n)"
    try:
        return int(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300).stdout.strip() or 0)
    except Exception:
        return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-gpu", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=2)
    ap.add_argument("--launch-deadline", type=float, default=4.3 * 3600)
    ap.add_argument("--kill-deadline", type=float, default=5.1 * 3600)
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    os.chdir(ROOT)
    start = time.time()
    n_gpu = gpu_count()
    if n_gpu:
        workers = n_gpu * args.per_gpu
        devices = [f"cuda:{i % n_gpu}" for i in range(workers)]
    else:
        workers = max(1, min(os.cpu_count() or 1, 64))
        devices = ["cpu"] * workers
    print(f"[driver] gpus={n_gpu} workers={workers} cpus={os.cpu_count()}", flush=True)
    logs = ROOT / "tmp/hardening/logs"
    logs.mkdir(parents=True, exist_ok=True)

    queue = []
    for name, out, inputs, extra in TASKS:
        if args.only and name not in args.only:
            continue
        scenes = sorted(p.stem for d in inputs for p in (ROOT / d).glob("*.npz"))
        todo = [s for s in scenes if not (ROOT / out / "predictions" / f"{s}.npz").exists()]
        for k in range(0, len(todo), args.chunk):
            queue.append((name, out, inputs, extra, todo[k : k + args.chunk]))
    print(f"[driver] {len(queue)} chunks queued", flush=True)

    running = {}
    free = list(range(workers))
    launched = 0
    while queue or running:
        now = time.time() - start
        while queue and free and now < args.launch_deadline:
            slot = free.pop(0)
            name, out, inputs, extra, chunk = queue.pop(0)
            cmd = [sys.executable, "method/splart.py", "--out", out, "--inputs", *inputs, "--scenes", *chunk,
                   "--device", devices[slot], "--threads", "1" if n_gpu else "1", *extra]
            log = open(logs / f"{name}_{launched:04d}.log", "w")
            running[slot] = (subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT), log, name, chunk)
            launched += 1
        if now >= args.launch_deadline and queue:
            print(f"[driver] launch deadline reached; {len(queue)} chunks not run: "
                  f"{sorted(set(q[0] for q in queue))}", flush=True)
            queue = []
        for slot, (proc, log, name, chunk) in list(running.items()):
            if proc.poll() is not None:
                log.close()
                free.append(slot)
                del running[slot]
                print(f"[driver] {time.time() - start:7.0f}s {name} {chunk} rc={proc.returncode}", flush=True)
            elif now >= args.kill_deadline:
                proc.kill()
                proc.wait()
                log.close()
                free.append(slot)
                del running[slot]
                print(f"[driver] killed {name} {chunk} at kill deadline", flush=True)
        time.sleep(2)
    summary = {}
    for name, out, inputs, extra in TASKS:
        scenes = sorted(p.stem for d in inputs for p in (ROOT / d).glob("*.npz"))
        done = sum((ROOT / out / "predictions" / f"{s}.npz").exists() for s in scenes)
        summary[name] = f"{done}/{len(scenes)}"
    print("[driver] completion " + json.dumps(summary), flush=True)
    (ROOT / "tmp/hardening/driver_summary.json").write_text(json.dumps({"gpus": n_gpu, "workers": workers, "elapsed_s": time.time() - start, "completion": summary}, indent=1))


if __name__ == "__main__":
    main()
