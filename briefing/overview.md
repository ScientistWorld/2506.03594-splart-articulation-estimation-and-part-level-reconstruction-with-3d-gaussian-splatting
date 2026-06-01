# Overview

- **Paper ID:** 2506.03594
- **Title:** SPLART: Articulation Estimation and Part-Level Reconstruction with 3D Gaussian Splatting
- **Domain:** Computer Vision / 3D Reconstruction
- **TL;DR:** SPLART reconstructs two-part articulated objects and estimates their motion from two-state posed RGB images using self-supervised 3D Gaussian Splatting.

## Short Summary

The paper targets category-agnostic reconstruction of articulated objects with a static parent and moving child part. SPLART extends 3D Gaussian Splatting with per-Gaussian mobility and a multi-stage optimization pipeline that first reconstructs each state, then estimates mobility, then estimates and refines articulation. Reported results show strong articulation accuracy and novel-view synthesis on PARIS-PMS and SPLART-PMS without 3D supervision.

## Key Results

- PARIS-PMS overall articulation success: 99.0%, with overall PSNR 43.70 and mIoU 0.957 in the main tables.
- SPLART-PMS overall articulation success: 85.5%, with overall PSNR 37.01 and mIoU 0.916.
- The method includes ablations showing that both geometric and photometric stages contribute to robust articulation estimation.
