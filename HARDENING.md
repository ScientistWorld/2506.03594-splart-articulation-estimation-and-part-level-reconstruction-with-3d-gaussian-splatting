# Hardening report (final iteration)

## Verdict

**Better results now score higher and the reported shortcuts no longer pay.** The old gym was a 2-scene point-cloud puzzle with shared point correspondence, visible answers and a saturated reference. It was rebuilt into a benchmark that measures what the paper claims, with:

- independent two-state RGB + point-cloud observations;
- 26 hidden test scenes, 4 of the 13 object families never seen in train;
- articulation and part-level reconstruction scoring.

The reference is a faithful six-stage SPLART. On the hidden test:

- The colour-aware geometric-consistency variant gains R\* +0.50, about 2× the run-to-run noise. It also gains +2.08 ± 0.50 dB paired PSNR and +2 net scenes.
- Heavier private search no longer helps (R\* −0.38).
- Shorter training and three of the paper's four ablations score lower.
- The baselines and brute force sit at R\* ≈ −4.5, and every malformed or forged submission gets worst values.

Two things remain open:

- **Skipping Stage 2a scores above the reference** (R\* +0.44). This is the reverse of the paper's Table 4.
- **Private search with other strategies** can only be measured, not prevented.

R\* below is the prescribed additive rank:

`R* = Σ_exp weight Σ_metric |coef| · dir · (value − reference) / SD`

SD is the population standard deviation over the cohort of every run in the tables below (`notes/hardening/analyze.py`). This makes it illustrative: the real cohort is future attempts. All numbers are on the hidden test slice, produced by the unchanged `eval/test/evaluate.py`.

## What was rebuilt (all fixes applied together, checked in three jobs)

| Problem in REDTEAM.md | Fix |
|---|---|
| Both states shared point count and row order, so a Kabsch fit or enumerating moving-point triples solved the test (Q 0.975 > reference 0.879). | `data/articulated_objects.py`: per state, 20 posed 48×48 RGB images rendered from a dense surface, plus an independently sampled, noisy, visible-surface point cloud (380–600 points, random order, 0–5 % floaters). There is no correspondence, and partial visibility differs between states. |
| Test answers sat in visible NPZ files and could be regenerated from public seeds and settings. | Test inputs (`data/scenes/test/inputs`) hold observations only. The answers live only in `eval/test/gt`. They were generated once by `eval/test/generate_test.py`, which uses secret 62-bit seeds and four object families that exist only in `eval/test/`. The hidden test never regenerates anything; it reads the stored answers. |
| 2 test scenes; the reference was at the bound on five metrics. | 26 test and 18 train scenes over 13 families of revolute and prismatic objects in random pose, colour and texture. Parts are sometimes colour- or shape-similar to the body, and some parts move little or are partly hidden. |
| Duplicate scene rows changed the weights; a fully failed scene could still be outranked by repetition. | One file per scene name. The evaluator iterates over the ground-truth scene list and ignores any other file. |
| Editable data assets were trusted. | Ground truth comes only from `eval/test/gt`, which the hidden test restores. Editing the visible inputs changes only what a method sees. |
| Method discovery came from editable `scores_train.json`, so a failed artifact disappeared. | Every directory under `checkpoints/` is a method, named by its directory. A directory without valid test predictions is a failed run. |
| Out-of-range mobilities were clipped; NaN axes produced NaN scores; null, empty or missing outputs crashed without scores. | Strict validation of every array: dtype, shape, finiteness, colour and opacity in [0, 1] (1e-6 tolerance), scale in (0, 1], non-zero axis, amount range, ≤ 20000 Gaussians, `allow_pickle=False`. Any violation, and any unexpected exception, makes the whole run failed with the worst value in every metric of both experiments. A missing scene gets worst values for that scene. JSON is written with `allow_nan=False`. |
| Success was an additive metric; a failed scene could be compensated. | The paper's per-scene success rule (axis < 5°; revolute pivot < 0.05 and rotation < 10°; prismatic translation < 0.05). Errors are truncated at those thresholds, and a scene whose joint fails gets the worst reconstruction values. A failed scene can never look good, and a failed run gets worst everything. |
| Paper-context experiments had weight but were never emitted, so their scores were always missing. | Two scored experiments, both always emitted: `articulation_estimation` (weight 0.6) and `part_reconstruction` (weight 0.4: held-out-view PSNR, depth MAE and segmentation mIoU at novel views and articulation states q ∈ [−0.1, 1.1], plus static, mobile and whole-object Chamfer). The paper's tables are kept unchanged under `_paper_reported` in `scoring/reference.json`, since they are not on this scale. |
| The method departed from the paper: no RGB stage, photometric loss replaced, a correspondence-dependent regulariser, Stage 3(a) scheme merged, no Stage 3(c). | `method/splart.py` implements Stages 1, 2a, 2b, 3a, 3b and 3c as in the paper and the official code. Constants follow upstream: Chamfer targets restricted to weight > 0.1, λ_geom 1e-4, λ_photo 5e-3, L1 + 0.2 D-SSIM, articulation randomisation, every stage's learning rates, the convergence rule, and one view per step for 10000 / 5000 / 10000 photometric steps. |

## Better results score higher (variants before → after)

Before (old gym, REDTEAM.md, quality Q and old-cohort R\*):

| Variant | Before |
|---|---|
| continued training | Q 0.947, R\* +0.24 |
| shorter training | Q 0.835, R\* −0.20 |
| shortcuts | five paid more than the reference (up to R\* +0.42, Q 1.000) |

After (hidden test, final code):

| Run | success | axis err ° | PSNR | mIoU | depth MAE | CD whole | R\* |
|---|---:|---:|---:|---:|---:|---:|---:|
| **better: colour-aware Chamfer** (`--color-weight 0.1`) | **0.885** | 0.97 | **36.05** | **0.768** | 0.138 | 0.0711 | **+0.500** |
| ablation: skip Stage 2a | 0.885 | 0.90 | 34.73 | 0.750 | 0.140 | 0.0719 | +0.442 |
| reference, repeat run (identical config, earlier job) | 0.846 | 0.95 | 33.38 | 0.719 | 0.178 | 0.0767 | +0.236 |
| reference seed 2 | 0.808 | 0.97 | 32.34 | 0.692 | 0.214 | 0.0825 | +0.058 |
| **reference SPLART (seed 0)** | **0.808** | 1.26 | **31.94** | **0.690** | 0.216 | 0.0830 | **0** |
| reference seed 1 | 0.808 | 1.27 | 32.04 | 0.690 | 0.215 | 0.0824 | −0.002 |
| λ_geom scaled to 2e-3 (my earlier deviation) | 0.769 | 1.43 | 31.00 | 0.654 | 0.252 | 0.0885 | −0.191 |
| heavier private search (12 + 12 tries, 1.5× steps) | 0.731 | 1.56 | 29.96 | 0.626 | 0.291 | 0.0950 | −0.375 |
| weaker: 1/10 photometric steps, 1 + 1 tries | 0.615 | 1.74 | 27.72 | 0.532 | 0.402 | 0.1022 | −0.917 |
| ablation: skip Stage 3b | 0.654 | 2.26 | 25.57 | 0.548 | 0.376 | 0.1052 | −1.129 |
| ablation: skip Stage 2b | 0.500 | 2.60 | 23.84 | 0.429 | 0.515 | 0.1279 | −1.757 |
| ablation: skip Stage 3a | 0.077 | 4.71 | 12.12 | 0.060 | 0.928 | 0.1890 | −4.291 |
| ICP baseline (displacement split + 24-start ICP) | 0.038 | 4.75 | 10.59 | 0.029 | 0.967 | 0.1941 | −4.451 |
| brute force: ICP with 512 restarts | 0 | 4.83 | 10.00 | 0 | 1.000 | 0.2000 | −4.648 |
| static baseline | 0 | 4.81 | 10.00 | 0 | 1.000 | 0.2000 | −4.688 |

**Noise:**
- **Across seeds:** the three seeds have identical success (0.808), and their R\* range is 0.06.
- **Across runs:** with the same seed, GPU nondeterminism makes separate jobs diverge. Over four runs of the identical configuration, the R\* range is 0.24 (success 0.808–0.846). That 0.24 is the noise floor used here.

**Paired comparisons** against the reference on the same 26 inputs (`notes/hardening/summary.json`):

| Run | scenes gained / lost | PSNR on scenes both solve | mIoU on scenes both solve |
|---|---|---|---|
| colour variant | +4 / −2 | +2.08 ± 0.50 dB (n 19) | +0.018 ± 0.008 |
| each seed | +3 / −3 | +0.07 ± 0.31, −0.18 ± 0.34 | |
| heavier search | +1 / −3 | | |
| skip 3b | +0 / −4 | −3.4 ± 0.6 dB | |
| skip 2b | +2 / −10 | | |
| skip 3a | +0 / −19 | | |

The colour variant's gain, about 2× the run-to-run range and 8× the seed range, is a genuine improvement. It addresses the paper's own Fig. 3 failure (mobile parts geometrically similar to the static body). It improves all 11 aggregate metrics (a Pareto improvement; only the paired Chamfer on jointly solved scenes is a tie), so its positive rank does not depend on the cohort scale.

## Shortcuts: fix and score before → after

The "after" rows are submissions under `tmp/hardening/shortcuts/`, built by `notes/hardening/make_shortcuts.py` from the saved reference and static predictions and scored with `eval/test/evaluate.py --root tmp/hardening/shortcuts`.

| Shortcut | Before | Fix | After |
|---|---|---|---|
| Copy answers from visible test NPZ | Q 0.997, R\* +0.40 | Test inputs contain only observations (keys: `articulation_type`, `points*`, `colors*`, `images*`, `cams*`, `intrinsics`, `image_size`, `background`). Answers are only in `eval/test/gt`. | Not possible: nothing to copy. |
| Regenerate answers from public generator and seeds | Q 0.997, R\* +0.40 | Secret 62-bit seeds and 4 hidden families, stored only in `eval/test/`. | Not possible by enumeration. |
| Correspondence / Kabsch fit | Q 0.975, R\* +0.34 | No correspondence; partial, independent sampling. | Closest honest analogue, ICP baseline: R\* −4.45, success 0.038. |
| Brute-force enumeration | Q 0.975, R\* +0.34 | Same. | ICP with 512 restarts: R\* −4.65, success 0. |
| Duplicate scene rows / duplicate a failed scene | R\* +0.30 / +0.21 | One file per ground-truth scene; extra files ignored. | Duplicate files: exact tie (R\* 0.000); no gain. |
| Replace fixed data assets | Q 1.000, R\* +0.42 | Ground truth only in `eval/test/gt`. | Editing inputs can only hurt the editor. |
| Hide a failed method via `scores_train.json` | tie; failed artifact vanished | Every directory is scored. | Empty method directory: failed, worst everywhere (R\* −4.80). |
| Impossible mobility / opacity | R\* +0.04 | Range validation; failed run. | Opacity × 1e100 in one scene: failed (R\* −4.80). |
| NaN / null axis, NaN values | NaN metrics or no score | Finite checks; failed run with worst values. | NaN axis in one scene: failed (R\* −4.80). |
| Empty results / missing scenes | no score (exit 1) | Missing scene gets worst values; no predictions means failed run. | Half the scenes missing: R\* −2.60. |
| Self-reported scores | already failed | Evaluator ignores every file except `predictions/<scene>.npz`. | Forged score files next to static predictions: identical to static (R\* −4.69). |
| (new) Pickled payload | — | `allow_pickle=False`; unreadable file means failed run. | Failed (R\* −4.80). |
| (new) Too many Gaussians | — | ≤ 20000 per scene. | Failed (R\* −4.80). |
| (new) Faint Gaussian grid to game the opacity-thresholded Chamfer | — | Chamfer uses opacity ≥ 0.1 in both directions; renders are scored too. | R\* −0.95 (PSNR 16.4). |
| (new) Correct joint, all Gaussians labelled static | — | Novel articulation states and segmentation are scored. | R\* −0.69 (PSNR 24.1, mIoU 0.44, CD mobile worst). |
| Baseline poisoning | tie | No baseline enters any score. | Not applicable. |

## Shortcuts left open, and why

- **Private search on the visible test inputs.** A per-scene optimiser must see its inputs, and the self-supervised objective is computable from them, so compute per instance cannot be limited by the evaluator. Measured: 12 + 12 tries with 1.5× steps scores *below* the reference (R\* −0.38), so plain extra search does not pay now. Other search strategies could; the separate grader has to judge them.
- **Fitting the public object families by hand.** Nine of the 13 families are defined in the visible generator, so a solver that hard-codes them could do well on the 18 test scenes from those families. The 8 scenes from the four hidden families would defeat it. This is forbidden in `CONSTRAINTS.md`/`DIRECTION.md` and left to the grader; it was not run.
- **Skipping Stage 2a.** This is a simple variant that beats the reference by R\* +0.44 (+3 / −1 scenes). It is just above the 0.24 noise floor and reverses the paper's Table 4, where skipping 2a costs 1.8 points. It is an honest alternative, not a loophole, but a future agent can collect this gain cheaply. Stage 2a's geometric cross-static estimate is noisier on these sparse (~500-Gaussian) reconstructions than on the paper's dense ones.

## Reference score before → after

- **Before:** Q 0.879 and success 1.0 on 2 test scenes of the old point-cloud task, at the bound on five metrics.
- **After (final reference, seed 0):** test success 0.808 (21/26), axis error 1.26°, PSNR 31.9 dB, mIoU 0.690, depth MAE 0.216, CD whole 0.083. Train success is 0.889 (16/18) at PSNR 34.4. By family, seen families reach 15/18 on test and the hidden families 6/8.
- **Paper's direction:** the paper reports SPLART-PMS 85.5 % and PARIS-PMS 99 %, kept under `_paper_reported`. The reproduction shows the paper's claim in its direction: far above the static and correspondence-free baselines; Stage 3a essential (0.08 without it vs the paper's 6.4 %); Stages 3b and 2b each helpful.

How the reproduction got here, across this iteration's runs:

| Run | Configuration | Success |
|---|---|---:|
| 1 | Shortened schedule, upstream λ_geom, no logit bound | 0.38 |
| 2 | Logit bound plus my scaled λ_geom = 2e-3 | 0.77 |
| 3 (final) | Paper's λ_geom restored | 0.81 |

Run 1's diagnosis: Stage 2a's learning rate of 3 saturated the mobility logits beyond Adam's reach (eps 1e-15). Run 2's earlier run at the paper's λ_geom (now `repeat_run_check`) did better than the scaled value, so the paper's value was restored.

## Headroom check

**No scored metric is at its bound for the reference.** Success is 0.808 < 1, every truncated error is above 0, PSNR is 31.9 against a better variant's 36.1, mIoU is 0.69 < 1, and depth and Chamfer are above 0. The test was itself built from where the paper's method falls short:

- sparse, noisy, partially visible reconstructions with floaters;
- parts similar in shape or colour to the body (paper Fig. 3);
- small or slightly moving parts;
- unseen object families.

The 5 reference failures are a faucet (unseen family), a window sash (unseen family), a lever, a pair of scissors and a sliding panel. A genuinely better variant already scores +0.50, and neither heavier search nor brute force reaches the reference. No extra experiment was needed.

## Weights

- **articulation_estimation, weight 0.6:** the paper's headline claims are its articulation success rates and errors (Tables 1, 4). `success_rate` has coefficient 1.0, the axis error 0.5, and pivot, rotation and translation errors 0.25 each.
- **part_reconstruction, weight 0.4:** Tables 1, 2 and 5. PSNR 0.6, mIoU 0.5, depth 0.3, mobile Chamfer 0.3, static and whole Chamfer 0.2 each.

Reconstruction is gated on per-scene articulation success. Paired with truncated errors, this means a method cannot buy rank by failing hard scenes, and a run that fails the task gets worst values everywhere.

## Departures from the paper still in place

- **Data:** procedural objects instead of PARIS-PMS / SPLART-PMS, with 48×48 images; Chamfer is computed on Gaussian centres instead of TSDF meshes.
- **Representation:** isotropic Gaussians with view-independent colour and no densification; Stage 1 is initialised from the given sparse point cloud. The upstream depth-consistency loss in 2b is omitted.
- **Optimisation:** 6 + 6 instead of 3 + 3 randomised tries, mobility logits bounded to ±8, and a fresh optimiser for the final joint 3(a) run.
- **Protocol:** one run per scene instead of 10 seeds, with truncated error means over all scenes instead of means over successful runs.
- **Baselines:** static and ICP baselines instead of PARIS / DTA.

## Could not fix / caveats

- **The Stage-2a ablation direction** is reversed at this scale (above).
- **GPU nondeterminism:** a rerun of the same configuration can differ by up to R\* 0.24, so improvements smaller than that are not resolvable with this test size.
- **`python validate.py`** passes. `validate.py --post-design` flags the ICP baseline only: success 0.167 on train (3/18) vs 0.038 on test (1/26), a ratio check on near-zero counts. The setup was not changed to move it.
- **R\* is illustrative:** its scale depends on the cohort SDs. The Pareto statements (the colour variant improves all 11 metrics; the failed runs are at the worst values) do not.

## Evidence

- Final run: `notes/hardening/summary.md` and `summary.json`, `notes/hardening/eval/*.json` (aggregate and per-scene for checkpoints, variants and shortcuts), `notes/hardening/method_logs/`.
- Earlier runs in this iteration: `notes/hardening/run1/`, `notes/hardening/run2/`.
- The job script is `notes/hardening/run_hardening.sh`; jobs `6bdd2324-fe2`, `88ae4f8b-5a7` and `244435e3-b11`.
- `scoring/scores_test.json` and `scores_train.json` hold the reference runs only: `splart`, `icp_baseline`, `static_baseline`.
