# Audit: does this gym reward better research?

## Better results and weaker results

**Measured improvements are rewarded, but the gym does not reliably reward scientific contribution.** A genuine extension of the existing optimizer improves every unsaturated metric and ranks higher. Reduced training ranks lower. However, visible answers, editable evaluation data, and duplicate scene rows also beat the reference. A simple correspondence fit solves the reduced problem better than the reference, so this test is too easy to establish the paper's contribution.

All test metrics below come from the restored hidden evaluator invoked as `bash scripts/evaluate_test.sh` **with no arguments**. `Q` is its `quality_score`; `R*` is the prescribed additive rank calculated on a fixed audit cohort, explained below. The reference is the actual original `scoring/scores_test.json`, not the synthetic target values in `reference.json`.

| Variant (link runs it) | Test Q | Success | Axis error, degrees | Reconstruction Chamfer | R* vs reference |
|---|---:|---:|---:|---:|---:|
| [Original reference](redteam/reference_original/run.sh) | 0.87928953 | 1.00 | 0.787508 | 0.00054197 | 0 |
| [Better: continue training](redteam/better_continued_training/run.sh) | **0.94699391** | 1.00 | **0.337705** | **0.00030789** | **+0.241258** |
| [Weaker: shorter training](redteam/weaker_short_training/run.sh) | **0.83536135** | 1.00 | 1.715017 | 0.00098607 | **−0.196994** |
| [Annealing attempted from the start](redteam/better_annealed/run.sh) | 0.68555471 | 0.50 | 3.991318 | 0.00195267 | −1.547153 |
| [Final mobility-only correction](redteam/better_mobility_correction/run.sh) | 0.88484519 | 0.00 | 0.787508 | 0.00015843 | −1.269710 |
| [Packaged static baseline](redteam/static_baseline/run.sh) | 0.23057596 | 0.00 | 40.740572 | 0.01109214 | −7.409194 |

The better variant adds 840 optimization steps from the saved reference parameters, retaining its cross-mobile geometry, rendering, and mobility-consistency objective. Adam starts at 0.003 and decays to 0.00015 after step 420. It reads observations and known joint type, without ground-truth labels or articulation parameters. Its quality gain is **0.06770438**, 34 times the three-seed quality range. Its rank gain is 9.3 times the corresponding rank range. It strictly improves all seven unsaturated scored metrics, so its positive rank does not depend on the particular positive normalization scales.

The weaker variant reduces mobility/render steps from 160/80 to 16/8, randomized tries from 8 to 1, and coarse/refinement steps from 220/420 to 22/42. Its quality loss of **0.04392818** and rank loss exceed the measured seed ranges by factors of 22 and 7.6. Success alone cannot distinguish this degradation.

The two other attempted refinements are not evidence of an inverted score. Early annealing reaches a worse solution. Adding a standalone paper Stage 3(c) geometric mobility correction reduces Chamfer but produces complementary soft masks: Brier rises to 0.140933 and state disagreement to 0.565926. Its lower rank reflects those actual failures. Full metrics and training commands are saved in each linked folder.

## Seed spread and reproduction check

The unchanged reference source and original training budget were rerun with three seeds:

| Seed (link runs it) | Test Q | Success | R* |
|---|---:|---:|---:|
| [0](redteam/reference_seed0/run.sh) | 0.87923270 | 1.00 | −0.000224 |
| [1](redteam/reference_seed1/run.sh) | 0.87725146 | 1.00 | −0.010267 |
| [2](redteam/reference_seed2/run.sh) | 0.87858799 | 1.00 | −0.026240 |

**Peak-to-peak quality spread: 0.00198124; R* spread: 0.02601676.** Smaller gains are noise at this measured resolution. All four IoU metrics and success are identical across seeds. Other peak-to-peak ranges are axis 0.0868122 degrees, amount 0.00235463, pivot 0.00483635, Chamfer 0.0000290143, Brier 0.0000248003, and disagreement 0.000653856. Three seeds estimate variability; they do not establish the variability of every proposed modification.

**The packaged reference beats its packaged static baseline in the direction reported by the paper:** quality 0.87929 versus 0.23058 and success 1 versus 0. This is only a result on the substituted point-cloud problem. It does not reproduce the published comparisons against PARIS or DTA. In particular, the implementation makes these departures from [the local paper](paper/2506.03594.md):

1. Stage 1 RGB-to-3DGS reconstruction is omitted. Dense noisy 3D Gaussian centers and opacities are supplied directly for both states. The states share point count and row correspondence, information unavailable from the paper's independent reconstructions.
2. Photometric supervision is replaced by MSE on four normalized 32×32 orthographic isotropic Gaussian-density images. Colored anisotropic 3DGS, perspective RGB rendering, and full Gaussian-attribute optimization in Stages 2(b)/3(b) are absent; geometry and opacity remain fixed.
3. An added `0.03 * MSE(m0, m1)` regularizer uses the shared row identities. This is not the paper's mobility objective and depends on the easier corresponding-point setup.
4. Stage 3(a) merges mobile-only and cross-mobile objectives within each randomized try. The paper instead runs mobile-only tries, separate cross-mobile tries plus initialization from the mobile-only solution, and then joint geometric articulation/mobility refinement. These computational steps are not preserved.
5. The final stage combines geometry, density rendering, and correspondence consistency. Paper Stage 3(b) uses full photometric joint refinement, followed by a separate mobility-only Stage 3(c), absent from the original reference. The audit's standalone correction does not repair the earlier departures.
6. Four procedural 140-point clouds replace PARIS-PMS's 10 objects and SPLART-PMS's 22 objects; only two scenes are in the hidden slice. There is no evaluation of RGB reconstruction, novel views/intermediate articulations, background segmentation, depth, extracted meshes, rendering speed, or real captures. Static alignment replaces the published competing methods.
7. The reference uses one seed; the paper uses ten trials per scene. The gym averages errors over all rows, whereas the paper reports errors over successful runs alongside success rates. Rotation success uses 0.05 radians (about 2.86 degrees), versus the paper's 10 degrees, and adds decomposition, calibration, and geometry thresholds. Known joint type is consistent with the paper.

These are changes to the procedure and problem, beyond reducing resources. The original `core_claim_plus` milestone does not establish reproduction of the paper's full algorithm or claims.

## Scoring checks and interpretation of rank

The original reference is already at its upper bound on **`success`, `mean_part_iou`, `mobile_iou`, `static_iou`, and `worst_part_iou`**, all 1. The remaining seven metrics have headroom: quality is below 1 and all six error/calibration/disagreement metrics are above 0. A zero pivot error on the prismatic scene is structural; the aggregate pivot error is not saturated.

The static baseline leaves apparent headroom, but it is too weak. The observation-only correspondence shortcut reaches Q **0.97491481** and success 1. The brute-force shortcut enumerates all moving-point triples (34,220 candidates on the held-out revolute scene), refits the winning inliers, and gets the **same predictions and score**. That enumeration takes **0.62174 seconds** on the held-out revolute scene; the held-out slider's 60 displacement candidates take 0.00140 seconds. Both use only the observed states and joint type, without labels, seeds, or articulation answers. See [timing evidence](redteam/shortcut_brute_force/brute_force_diagnostics.json). The tiny corresponding-point test is solvable by brute force and by a simpler algebraic fit.

The actual future ranking cohort and its standard deviations do not exist yet. Accordingly, **R* is illustrative, not an asserted future official score**. [summarize.py](redteam/summarize.py) computes

`R* = sum_experiments weight * sum_metrics abs(coefficient) * direction * (value − reference) / cohort_SD`,

where direction is +1 for `higher_is_better` and −1 otherwise. It uses the 23 finite evaluated case rows listed in [summary.json](redteam/summary.json), including unsuccessful methods, with population SD per metric. Negative error coefficients are treated by magnitude; they never reverse the stated better direction. This removes dependence on metric units. The copied original schema is [rank_metadata.json](redteam/rank_metadata.json); the actual score anchor is [reference_anchor.json](redteam/reference_anchor.json). Conclusions involving tradeoffs can change with the eventual cohort; Pareto improvements and exact ties cannot.

Only `synthetic_articulated_gaussians` is emitted, with nominal weight 0.5 and all 12 metrics on successful evaluations. The two paper-context experiments in `reference.json`, weighted 0.25 each, are never emitted and are therefore skipped. Published context values cannot provide evidence that a future method reproduces those experiments. The synthetic target anchors in `reference.json` also differ from actual original test measurements; this report compares against the latter as required.

**Task failure can outrank the reference.** The duplicate-failed-scene shortcut entirely fails one of the two distinct test scenes, yet obtains success 100/101 and R* +0.211491 by repeating the successful scene. Its failed revolute scene has mobile IoU 0, axis error 72.50 degrees, and Q 0.138509; the slider has Q 0.971012. Equal weighting of the two distinct scenes would give Q 0.554761 and success 0.5. The evaluator checks scene presence as a set but averages prediction rows, allowing the method to choose experiment weights. In addition, success is an additive metric rather than a hard eligibility gate. The separate all-scenes Brier-gate violation tested here ranks below the reference; a universal guarantee cannot follow from these additive, cohort-dependent weights.

**Failed runs do not receive worst values.** Empty results, missing scenes, null axes, and NaN mobility terminate the hidden test with exit 1 and no score file in the clean sandbox. No per-method/per-experiment worst metric vector is written. This violates the completeness requirement when missing values are skipped. This audit does not claim an untested stale-score or external failed-job-ranking behavior.

**Not every method on disk is written.** Final no-argument discovery trusts method names in editable `scoring/scores_train.json`. The tested hidden-failed-method shortcut leaves two artifacts on disk, but advertises only the reference-quality one; the failed artifact disappears from final `results` and receives no penalty. The test exits 0 despite the preceding train evaluator exiting 1. [Status evidence](redteam/shortcut_hidden_failed_method/status.json) records both artifacts.

## Tested shortcuts

Each link runs that shortcut, installs its files in a disposable workspace under its own folder, runs visible train evaluation, restores the original hidden evaluator, and runs the final no-argument test. Its directory contains predictions, status, and test scores when written. Reference comparison is Q **0.87928953**, success **1**, R* **0**. Exact reference ties are explicitly labeled shortcut ties; a tie alone does not establish that the attempted mutation improved anything.

| Shortcut (run) | What it does | Test Q / success / R* | Works or fails |
|---|---|---|---|
| [shortcut_npz_answers](redteam/shortcut_npz_answers/run.sh) | Copies `axis`, `pivot`, `amount`, and `labels` from the visible NPZ files. | **0.99689150 / 1 / +0.399903** | **Works.** Visible test answers; Pareto-better than reference. |
| [shortcut_generator_answers](redteam/shortcut_generator_answers/run.sh) | Regenerates the answers using public `DEFAULT_SCENES`, seeds, and hardcoded articulation settings. | **0.99689150 / 1 / +0.399903** | **Works.** Removing NPZ labels alone would not close this shortcut. |
| [shortcut_brute_force](redteam/shortcut_brute_force/run.sh) | Enumerates moving-point triples/displacements using observed correspondence and fits rigid motion. | **0.97491481 / 1 / +0.335433** | **Works.** Shortcut: honest alternative solving the undersized substituted test; not a SPLART reproduction. |
| [shortcut_correspondence_baseline](redteam/shortcut_correspondence_baseline/run.sh) | Thresholds observed displacement, then applies a direct Kabsch/translation fit. | **0.97491481 / 1 / +0.335433** | **Works.** Shortcut: honest alternative the test cannot distinguish from the exhaustive shortcut; exact prediction tie between them. |
| [shortcut_duplicate_scenes](redteam/shortcut_duplicate_scenes/run.sh) | Keeps reference predictions unchanged; repeats each public prismatic scene 100 times. | **0.96919562 / 1 / +0.299110** | **Works** in audit cohort. Changes row weights without improving a single unique prediction. |
| [shortcut_duplicate_failed_scene](redteam/shortcut_duplicate_failed_scene/run.sh) | Makes revolute predictions completely wrong; repeats unchanged prismatic predictions 100 times. | **0.96276931 / 0.990099 / +0.211491** | **Works** in audit cohort despite completely failing one of two distinct test scenes. |
| [shortcut_replace_fixed_data](redteam/shortcut_replace_fixed_data/run.sh) | Replaces fixed NPZ observations/truth with zero-motion scenes, matched by constant articulation and a fixed-index part mask. | **1.00000000 / 1 / +0.418498** | **Works.** Perfect all-metric score; finalization restores evaluator code but trusts editable data assets. |
| [shortcut_hidden_failed_method](redteam/shortcut_hidden_failed_method/run.sh) | Leaves an empty failed artifact on disk and selects only the cached reference artifact through editable train-score keys. | **0.87928953 / 1 / 0** | **Works: shortcut tie.** Failed on-disk method is omitted rather than assigned a loss. |
| [shortcut_impossible_mobility](redteam/shortcut_impossible_mobility/run.sh) | Maps cached reference mobilities to ±10^100 according to their thresholded sign. | **0.88393868 / 1 / +0.035592** | **Works.** Invalid probabilities are clipped, yielding Brier/disagreement 0 and lower Chamfer. Valid hard thresholding would yield the same result; this establishes a validation gap, not a new scientific method. |
| [shortcut_baseline_replacement](redteam/shortcut_baseline_replacement/run.sh) | Changes and reruns the fixed static baseline with motion amount 10^6; keeps candidate predictions unchanged. | **0.87928953 / 1 / 0** | **Shortcut tie** from reused reference predictions; baseline-poisoning mechanism **fails** to increase the candidate's absolute score. |
| [shortcut_self_reported_scores](redteam/shortcut_self_reported_scores/run.sh) | Forges perfect final scores, per-row success/quality/errors, impossible loss, and zero timing for static predictions. | 0.23057596 / 0 / −7.409194 | **Fails.** Successful hidden evaluation overwrites the forged file and recomputes metrics; no timing is scored. |
| [shortcut_all_mobile](redteam/shortcut_all_mobile/run.sh) | Uses reference articulation but constant mobile masks. | 0.57321534 / 0 / −5.071123 | **Fails.** Static IoU 0, high Brier and Chamfer. |
| [shortcut_all_static](redteam/shortcut_all_static/run.sh) | Uses reference articulation but constant static masks, effectively copying observed geometry without motion. | 0.60897422 / 0 / −4.548086 | **Fails.** Mobile IoU 0 and high Brier/Chamfer. |
| [shortcut_fail_success_gate](redteam/shortcut_fail_success_gate/run.sh) | Uses observation-fit motion but softens the masks to 0.29/0.71, violating Brier < 0.08 on every scene. | 0.89464117 / 0 / −1.165542 | **Fails** in audit cohort despite higher quality and perfect IoUs. |
| [shortcut_empty_results](redteam/shortcut_empty_results/run.sh) | Emits an empty prediction list. | No score; test exit 1 | **Fails to produce a ranked score.** Also exposes missing worst-case metric handling. |
| [shortcut_missing_scene](redteam/shortcut_missing_scene/run.sh) | Omits all revolute scenes. | No score; test exit 1 | **Fails to produce a ranked score.** Missing-scene check raises; no worst vector is written. |
| [shortcut_null_axis](redteam/shortcut_null_axis/run.sh) | Returns null axes with otherwise reference outputs. | No score; test exit 1 | **Fails to produce a ranked score.** Type error rather than a complete failure score. |
| [shortcut_nonfinite_mobility](redteam/shortcut_nonfinite_mobility/run.sh) | Inserts NaN in mobility arrays. | No score; test exit 1 | **Fails to produce a ranked score.** Explicit finite check rejects it without worst values. |
| [shortcut_nonfinite_axis](redteam/shortcut_nonfinite_axis/run.sh) | Returns NaN axes with reference masks. | NaN quality/errors / 0 / undefined | **Accepted invalid output; paying shortcut unconfirmed.** Test exits 0 and writes nonstandard JSON NaNs. External NaN ranking behavior is unavailable; it is excluded from R*. |

There is no fixed learned detector/reference model consumed by this evaluator to retrain. The fixed-data replacement above tests the corresponding trusted-artifact weakness. No shortcut modifies the hidden evaluator, installs Python hooks, changes its interpreter/environment, or requires a surviving training process.

## Evidence, replay, and next-iteration fixes

The two CPU jobs completed successfully: `30fc141a-080` and `13826c05-cce`. There are 28 case runs: 24 final test invocations exit 0 (one writes NaNs), and four exit 1. [summary.json](redteam/summary.json) preserves every numeric metric and status; failed cases have saved error excerpts. [job_evidence.json](redteam/job_evidence.json) records job completion metadata and final output.

Run a case with `bash redteam/<name>/run.sh` inside the provided gym container. [run_audit.sh](redteam/run_audit.sh) replays both batches. The [harness](redteam/case.py) prepares each case from the scientist-visible files; only after preparation does it restore `eval/` and `scripts/evaluate_test.sh`. The audit-only paper, reference schema, and hidden evaluator are not supplied to shortcut implementations. Cases use fresh evaluator subprocesses within the scheduled CPU container, with all preparation processes finished before testing. Disk-only behavior is tested; no result relies on process state that would disappear in a fresh final container. Original trained outputs are reused where authorized for scoring-only changes, and are the starting point of the continued-training variant.

For the next iteration: keep held-out answers, seeds, and generation parameters outside the scientist-visible tree; restore immutable test data as well as evaluator code; reject duplicate scene rows; discover and score every submitted method independently of editable train scores; validate all numeric fields and write complete worst-case vectors for failures. If task success is mandatory, enforce it before additive ranking. Replace the static baseline with the tested observation-fit baseline, and restore the actual RGB reconstruction procedure and difficult independent/occluded geometry before using this gym to judge SPLART research. Score the advertised reconstruction/constraint experiments rather than leaving paper-context entries permanently missing.

The temporary root job script is restored to its starting git version. Original method, data, baseline, evaluator, scoring, briefing, and environment files are unchanged; [restoration_check.json](redteam/restoration_check.json) records verification against the starting commit. Audit implementation and evidence live under `redteam/` plus this report; `action.yaml` is updated only for the required completion protocol.
