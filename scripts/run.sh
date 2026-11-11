#!/bin/bash
# Current job: hardening run (data, baselines, reference, variants, shortcuts,
# evaluation, analysis).  See notes/hardening/run_hardening.sh.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
bash notes/hardening/run_hardening.sh
