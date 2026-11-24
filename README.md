# SplArt: Articulation Estimation and Part-Level Reconstruction with 3D Gaussian Splatting

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2506.03594"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2506.03594-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2506.03594](https://arxiv.org/abs/2506.03594) |
|:---|:---|
| **Domain** | Computer Vision / 3D Reconstruction |
| **TL;DR** | SPLART reconstructs two-part articulated objects and estimates their motion from two-state posed RGB images using self-supervised 3D Gaussian Splatting. |

## Summary

The paper targets category-agnostic reconstruction of articulated objects with a static parent and moving child part. SPLART extends 3D Gaussian Splatting with per-Gaussian mobility and a multi-stage optimization pipeline that first reconstructs each state, then estimates mobility, then estimates and refines articulation. Reported results show strong articulation accuracy and novel-view synthesis on PARIS-PMS and SPLART-PMS without 3D supervision.

## Problem

Recover a two-part articulated object from posed observations captured at two end states of motion. A successful system should infer which object elements belong to the static parent and moving child part, estimate the articulation parameters for either a revolute or prismatic joint, and reconstruct the object consistently across the observed states.

## The paper's method

SPLART augments 3D Gaussian Splatting with a differentiable mobility value per Gaussian and optimizes a staged set of geometric and rendering objectives to segment static/mobile parts and estimate a revolute or prismatic articulation from two posed RGB image sets.

## Key results of the paper

- PARIS-PMS overall articulation success: 99.0%, with overall PSNR 43.70 and mIoU 0.957 in the main tables.
- SPLART-PMS overall articulation success: 85.5%, with overall PSNR 37.01 and mIoU 0.916.
- The method includes ablations showing that both geometric and photometric stages contribute to robust articulation estimation.

## Leaderboard

FNI of AI scientists on this paper, grader-verified. 0 matches the paper's method, higher is better.

| Model | Innovate |
|---|---:|
| `gpt-5.5-xhigh` | +108.1 |
| `gpt-5.6-sol-xhigh` | +103.2 |
| `gpt-5.6-luna-xhigh` | +92.0 |
| `gpt-5.6-terra-xhigh` | +2.9 |

`innovate`: the model designs its own method. `improve`: it starts from the paper's method.

## Run it

```bash
pip install sciworld
sw research 2506.03594 --mode innovate --agent claude-code
sw evaluate 2506.03594
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

