#!/bin/bash
# Download all data and models needed for this environment.
#
# Run on a node with internet access BEFORE building the container
# or submitting compute jobs.
#
# This script should be idempotent — safe to run multiple times.
# It should skip files that already exist.
#
# Update the storage estimate below as you add downloads.
#
# Estimated total download size: 0 GB for the lightweight benchmark.
# Estimated disk usage after extraction: <1 MB.
#
# This benchmark has no external downloads; it regenerates the small
# procedural data under data/synthetic_splart.

set -e

cd /home/user

python data/articulated_gaussians.py
