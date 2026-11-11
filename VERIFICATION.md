# Verification Report

Final verification is part of `HARDENING.md` (final iteration). Summary:

- `python validate.py` passes (reference, score files, import separation, train/test independence, script rewiring, method keys).
- The reference runs (`splart`, `icp_baseline`, `static_baseline`) were produced from the final code in job `244435e3-b11`; `scoring/scores_{train,test}.json` contain only them.
- Milestone: core_claim_plus. Key limitation: procedural low-resolution benchmark instead of the paper's PartNet-Mobility datasets; the Stage-2a ablation does not reproduce the paper's direction.
