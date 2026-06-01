# Progress

## What Works

- Paper analysis and briefing files are complete.
- Official SPLART implementation is vendored under `method/splart_upstream`.
- A lightweight reproduction in `method/lightweight_splart.py` implements the paper's identifiable staged computations at reduced scale: differentiable per-Gaussian mobility, weighted Chamfer, cross-static mobility fitting, cross-static rendering refinement, cross-mobile articulation fitting, and cross-mobile rendering refinement.
- `eval/` is method-agnostic, reads prediction artifacts, and independently computes all ground-truth-aware metrics from `data/`.
- `baseline/static_alignment.py` provides a static-object baseline.
- `scripts/reproduce.sh` completed successfully in the container and wrote `scoring/scores.json`.
- `python validate.py --compare` passes after the reproduced scores are written.
- `scoring/reference.json` now includes the paper's reported overall quantitative anchors from PARIS-PMS Table 1 and SPLART-PMS Table 4, in addition to the runnable lightweight benchmark target.
- Continuation audit tightened the synthetic success criterion to require low articulation amount and pivot errors as well as low axis error, part IoU, and reconstruction Chamfer.
- Current iteration expands the synthetic benchmark from two to four scenes and removes metric self-reporting from method and baseline artifacts.
- CPU verification job `13f3315a-b7e` completed under the stricter evaluator. It showed strong articulation and reconstruction recovery but exposed a mobility-label degeneracy, so `method/lightweight_splart.py` now regularizes mobility probabilities to agree across the two observed states.
- CPU verification job `1c5fb2bf-454` reached `core_claim`: the method succeeded on three of four expanded scenes and strongly beat the static baseline while preserving articulation, decomposition, and reconstruction constraints.
- `eval/evaluate_synthetic.py` now writes `scoring/per_scene.json` in addition to aggregate `scoring/scores.json`, so future runs expose which scene or constraint failed.
- CPU verification job `dd07d19d-f0f` reached `core_claim_plus`: the method now succeeds on all four expanded scenes, and the per-scene diagnostic file confirms every scene passes independently.
- Final verification rebuilt the aggregate score files from completed per-scene outputs so the mobility constraint metrics declared in `reference.json` are present in `scores.json`, and cleaned up method-agnostic gym documentation.
- Follow-up audit confirmed the artifact-based scoring separation and flagged wording that conflated the paper's articulation-only success definition with this gym's stricter synthetic success gate. `briefing/evaluation.md` and `scoring/reference.json` now distinguish those definitions explicitly.

## Results

The latest completed CPU verification job (`16b3c3d5-445`) reproduced the earlier two-scene lightweight two-state articulated Gaussian benchmark in about one minute:

| Method | Success | Axis error (deg) | Amount error | Mean part IoU | Mobile IoU | Static IoU | Recon. Chamfer |
|---|---:|---:|---:|---:|---:|---:|---:|
| `static_baseline` | 0.0 | 90.0000 | 0.5565 | 0.5000 | 0.0000 | 1.0000 | 0.04559 |
| `splart_lightweight` | 1.0 | 0.4398 | 0.0052 | 0.9513 | 0.9463 | 0.9563 | 0.00344 |

The latest completed CPU verification job (`13f3315a-b7e`) ran the stricter four-scene lightweight two-state articulated Gaussian benchmark:

| Method | Success | Axis error (deg) | Amount error | Pivot error | Mean part IoU | Mobile IoU | Static IoU | Recon. Chamfer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `static_baseline` | 0.0 | 55.8246 | 0.6032 | 0.0395 | 0.2857 | 0.0000 | 0.5714 | 0.01008 |
| `splart_lightweight` | 0.0 | 0.6696 | 0.0237 | 0.0140 | 0.7002 | 0.7089 | 0.6915 | 0.00079 |

The method clearly improves over the static baseline and meets the articulation and geometric thresholds, but it misses the strict success target because mean part IoU is below 0.75. This is not yet `core_claim`. The next submitted job reruns the same benchmark after adding mobility consistency across states.

CPU verification job `1c5fb2bf-454` reran the same four-scene benchmark after the mobility consistency fix:

| Method | Success | Axis error (deg) | Amount error | Pivot error | Mean part IoU | Mobile IoU | Static IoU | Recon. Chamfer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `static_baseline` | 0.0 | 55.8246 | 0.6032 | 0.0395 | 0.2857 | 0.0000 | 0.5714 | 0.01008 |
| `splart_lightweight` | 0.75 | 0.7175 | 0.0227 | 0.0102 | 0.9964 | 0.9958 | 0.9969 | 0.00086 |

This supports the core claim for the reduced-scale benchmark: SPLART-style cross-static/cross-mobile optimization recovers mobile/static decomposition and articulation parameters from two-state observations, while a static baseline cannot. One of the four scenes still misses at least one strict threshold, so the next run uses a larger optimizer budget and records per-scene diagnostics.

CPU verification job `dd07d19d-f0f` reran the four-scene benchmark with the larger default optimizer budget and per-scene diagnostics:

| Method | Success | Axis error (deg) | Amount error | Pivot error | Mean part IoU | Mobile IoU | Static IoU | Recon. Chamfer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `static_baseline` | 0.0 | 55.8246 | 0.6032 | 0.0395 | 0.2857 | 0.0000 | 0.5714 | 0.01008 |
| `splart_lightweight` | 1.0 | 0.6455 | 0.0137 | 0.0050 | 0.9964 | 0.9958 | 0.9969 | 0.00054 |

Per-scene success is 1.0 for `prismatic_diagonal`, `prismatic_slider`, `revolute_hinge`, and `revolute_tilted_axis`. This is the current best reproduction result and reaches `core_claim_plus`.

Final scoring also reports constraint metrics that discourage shortcut decompositions: `splart_lightweight` has worst-part IoU 0.9958, mobility Brier score 0.0018, and state-mobility disagreement 0.0104; `static_baseline` has worst-part IoU 0.0 and mobility Brier score 0.4286.

## Remaining

- Expand toward the full upstream 3DGS pipeline on downloaded SPLART/PARIS data.
- Add image-space PSNR/depth/mIoU/mesh Chamfer once the full renderer and datasets are available.
- Reproduce more paper table entries, especially PARIS-PMS and SPLART-PMS articulation success rates.

## Issues

- The full SPLART code depends on Nerfstudio, gsplat, PyTorch3D, tiny-cuda-nn, and CUDA extension builds. To get an initial reproducible benchmark quickly, the first job uses a lightweight Gaussian benchmark instead of the full image-rendering pipeline.
- Local login-node Python lacks NumPy, so numerical method execution was left to the compute container. Package installation is handled through `environment/setup.sh`.
- A continuation CPU verification run stalled after the baseline when using the original lightweight optimizer budget on a one-CPU test node. The method now keeps the same stages but uses fewer default Adam steps, a smaller randomized-try budget, `torch.set_num_threads(1)`, and flushed per-scene progress messages. The follow-up job completed successfully.
- The current reproduction is defensible as `core_claim_plus` for the reduced synthetic SPLART gym, not as a full reproduction of the paper's RGB 3DGS experiments. The official upstream implementation is vendored, but the full datasets and CUDA 3DGS training path remain future work.

## Deviations from Paper

- Paper data: PARIS-PMS and SPLART-PMS posed RGB datasets with full 3DGS photometric optimization. Substitute: a small procedural two-state articulated Gaussian benchmark generated by `data/articulated_gaussians.py`. Reason: the first iteration needs an end-to-end, no-download smoke benchmark that preserves the two-state articulation and mobility-estimation problem.
- Paper rendering stages: full photometric 3DGS rendering losses. Substitute: a lightweight orthographic Gaussian density renderer plus weighted Chamfer losses over Gaussian means. Reason: this preserves the cross-static/cross-mobile rendering and geometric optimization structure while avoiding CUDA-extension build risk for the current benchmark. The official full implementation remains vendored for later expansion.
