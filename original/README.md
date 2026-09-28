# original/ — rollback copies

| File | Environment | What it is |
|---|---|---|
| [`eCMRs.trn.original.xml`](eCMRs.trn.original.xml) | TRN | Form v1: the last file imported to TRN before v2 (was `exports/eCMRs_v1.XML`; assumed to match TRN as of 2026-09-28). Input to `tools/apply_form_changes.py`, and the rollback copy for v2. |

To roll back v2 on TRN: import `eCMRs.trn.original.xml` through **FormSync** at Site scope.
Data is not affected (the table and IDO don't change). If you roll back, also remove the Reason
and Cause Inline Lists, or v1's Reason/Cause dropdowns show the Inline List instead of the
QC_MRRs classes. There is no production copy yet: eCMRs isn't in production.

Never edit this file. `tools/apply_form_changes.py` must reproduce `exports/eCMRs_v2.XML` from it
exactly (`--check`).
