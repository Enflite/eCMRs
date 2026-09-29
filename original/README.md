# original/ — rollback copies

| File | Environment | What it is |
|---|---|---|
| [`eCMRs.trn.original.xml`](eCMRs.trn.original.xml) | TRN | Form v1, the first eCMRs form imported to TRN (was `exports/eCMRs_v1.XML`). Input to `tools/apply_form_changes.py`, which builds v2 from it; the rollback copy for the form on TRN. |

**Production has no rollback copy, on purpose**: eCMRs is a new form on a new table, so there is
nothing in production to back up before the first import (the Implementation Plan, section 5
step 2, checks that). If eCMRs has to be pulled from production, take it off the menu / form
security and keep using the legacy CMR screens, which are untouched. After production go-live,
export the production form here as `eCMRs.production.original.xml` before any later change.

To roll back v2 on TRN: import `eCMRs.trn.original.xml` through **FormSync** at Site scope.
Data is not affected (the table and IDO don't change). v1 used the QC_MRRs classes for Reason /
Cause (the `'FP'` error) and AUTONUMBER for CMR Num, so a rollback brings those problems back.

Never edit this file. `tools/apply_form_changes.py` must reproduce `exports/eCMRs_v2.XML` from it
exactly (`--check`).
