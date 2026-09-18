# eCMRs

A ground-up, original SyteLine QCS form and data model for Change Management Requests (CMRs) — **not** an extension of the existing `RS_QCCmrs`/`RS_QCCRcvrs` IDOs.

## Why this repo is separate from `cmr-project`

[`Enflite/cmr-project`](https://github.com/Enflite/cmr-project) consolidates the three legacy screens (`Create Change Request`, `Change Request Management`, `QC_CMRs`) by *extending* the existing tables (`rs_cmr`, `rs_crcvr`) — new IDOs (`ue_rs_qccmrs`, `ue_rs_qccrcvrs`) joined onto them, reusing their unused generic columns (`charfld1`/`charfld2`, etc.) where possible.

That approach hit real, structural ceilings along the way:
- `RS_QCCmrs`'s composite primary key (`CmrNum` + `RsCrcvrRcvrNum` + `RsPriorityPriority`) makes native "New" impossible — creation only works through a stored procedure (`RSQC_CreateCmrSp`) tied to an existing receiver row.
- Most of the fields a CMR actually needs (Item, Dept, WC, Initial Change, Requested Action) are read-only-by-join on the legacy tables, requiring a Variable + script workaround for every single one.
- Real new fields (Reason Code, Cause Code) don't have an obvious home on either legacy table.

**eCMRs starts over.** A brand-new custom SQL table, a brand-new IDO, and a brand-new form — no join to `rs_cmr` or `rs_crcvr`, no dependency on `RSQC_CreateCmrSp`, no inherited primary-key constraint. Everything a CMR needs gets its own real column, named and typed the way this project actually wants it, from day one.

`cmr-project`'s docs (especially `docs/field-mapping.md` and the "Requirements checkbox cascade" section) are the requirements reference — every business rule confirmed there (what a CMR needs, how the 5 Requirement checkboxes cascade off Initial Change via the real `DefaultFrom: Change(...)` function, how the Assigned/employee lookup works, etc.) still applies here. What's different is *how* it gets built: original schema, not a legacy extension.

## Structure

- `docs/task-list.md` — phased build plan
- `docs/field-mapping.md` — the new table's field/column design
- `exports/` — Form Sync XML exports as the form gets built

## Status

Just started. No table, IDO, or form exists yet — see `docs/task-list.md` Phase A.
