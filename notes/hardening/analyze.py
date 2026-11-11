"""Summarise hardening runs: aggregate scores, seed spread, paired comparisons, illustrative rank.

Reads the evaluator outputs written by run_hardening.sh under tmp/hardening/eval
and writes notes/hardening/summary.json and notes/hardening/summary.md.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EV = ROOT / "tmp/hardening/eval"
REF = "splart"
SEEDS = ["splart", "splart_seed1", "splart_seed2"]


def load(tag: str):
    agg = json.loads((EV / f"{tag}.json").read_text())
    ps = json.loads((EV / f"{tag}_per_scene.json").read_text()) if (EV / f"{tag}_per_scene.json").exists() else {}
    return agg, ps


def flat(agg: dict) -> dict:
    out = {}
    for exp, d in agg["experiments"].items():
        for m, metrics in d["results"].items():
            out.setdefault(m, {})[exp] = metrics
    return out


def main() -> None:
    ref_json = json.loads((ROOT / "scoring/reference.json").read_text())["experiments"]
    scores, per_scene, status = {}, {}, {}
    for tag in ("checkpoints_test", "variants_test", "shortcuts_test"):
        if not (EV / f"{tag}.json").exists():
            continue
        agg, ps = load(tag)
        for m, v in flat(agg).items():
            scores[m] = v
            per_scene[m] = ps.get(m, {})
            status[m] = agg["_meta"]["status"].get(m, "?")
    train = {}
    for tag in ("checkpoints_train", "variants_train"):
        if (EV / f"{tag}.json").exists():
            for m, v in flat(load(tag)[0]).items():
                train[m] = v

    # illustrative additive rank over the cohort of everything evaluated here
    cohort = sorted(scores)
    sd = {}
    for exp, spec in ref_json.items():
        for metric in spec["metrics"]:
            vals = [scores[m][exp][metric] for m in cohort if exp in scores[m]]
            sd[(exp, metric)] = float(np.std(vals)) if len(vals) > 1 else 0.0

    def rank(m: str, anchor: str = REF) -> float:
        total = 0.0
        for exp, spec in ref_json.items():
            for metric, mdef in spec["metrics"].items():
                s = sd[(exp, metric)]
                if s <= 0 or exp not in scores[m] or exp not in scores[anchor]:
                    continue
                sign = 1.0 if mdef["higher_is_better"] else -1.0
                total += spec["weight"] * abs(mdef["coefficient"]) * sign * (scores[m][exp][metric] - scores[anchor][exp][metric]) / s
        return total

    ranks = {m: rank(m) for m in cohort} if REF in scores else {}

    # seed spread
    seeds = [m for m in SEEDS if m in scores]
    spread = {}
    for exp, spec in ref_json.items():
        for metric in spec["metrics"]:
            vals = [scores[m][exp][metric] for m in seeds]
            spread[f"{exp}.{metric}"] = float(max(vals) - min(vals)) if vals else None
    spread["rank"] = float(max(ranks[m] for m in seeds) - min(ranks[m] for m in seeds)) if seeds and ranks else None

    # paired per-scene comparisons against the reference
    paired = {}
    ref_rows = per_scene.get(REF, {})
    for m, rows in per_scene.items():
        if m == REF or not rows:
            continue
        common = [s for s in ref_rows if s in rows]
        d_succ = [float(bool(rows[s].get("success"))) - float(bool(ref_rows[s].get("success"))) for s in common]
        entry = {"n": len(common), "success_gained": int(sum(x > 0 for x in d_succ)), "success_lost": int(sum(x < 0 for x in d_succ))}
        for key in ("raw_psnr", "raw_depth_mae", "raw_part_miou", "raw_cd_whole", "axis_error_deg"):
            both = [s for s in common if rows[s].get("success") and ref_rows[s].get("success") and key in rows[s] and key in ref_rows[s]]
            diffs = np.array([rows[s][key] - ref_rows[s][key] for s in both])
            if len(diffs) > 1:
                entry[key] = {"mean_diff": float(diffs.mean()), "se": float(diffs.std(ddof=1) / math.sqrt(len(diffs))), "n": len(diffs)}
        paired[m] = entry

    summary = {"status": status, "test": scores, "train": train, "rank_vs_reference": ranks, "seed_spread": spread,
               "paired_vs_reference": paired, "cohort_sd": {f"{e}.{k}": v for (e, k), v in sd.items()}}
    (ROOT / "notes/hardening/summary.json").write_text(json.dumps(summary, indent=1, default=float))

    metrics = [(exp, k) for exp, spec in ref_json.items() for k in spec["metrics"]]
    lines = ["| method | status | R* | " + " | ".join(k for _, k in metrics) + " |", "|" + "---|" * (len(metrics) + 3)]
    for m in sorted(cohort, key=lambda x: -ranks.get(x, -1e9)):
        vals = " | ".join(f"{scores[m][e][k]:.4g}" for e, k in metrics)
        lines.append(f"| {m} | {status[m]} | {ranks.get(m, float('nan')):+.3f} | {vals} |")
    lines += ["", "## Train slice", "", "| method | " + " | ".join(k for _, k in metrics) + " |", "|" + "---|" * (len(metrics) + 1)]
    for m in sorted(train):
        lines.append(f"| {m} | " + " | ".join(f"{train[m][e][k]:.4g}" for e, k in metrics) + " |")
    lines += ["", "## Seed spread (max - min over seeds 0,1,2)", "", "```", json.dumps(spread, indent=1), "```",
              "", "## Paired vs reference (test scenes)", "", "```", json.dumps(paired, indent=1), "```"]
    (ROOT / "notes/hardening/summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
