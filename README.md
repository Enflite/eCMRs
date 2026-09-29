# eCMRs

One SyteLine form for **Change Management Requests (CMRs)** on its own table and IDO
(`ue_ecmrs`), replacing the three legacy screens **Create Change Request**, **Change Request
Management** and **QC_CMRs**. **Working on TRN (2026-09-29); production is next.**

**Going live? Start with [`docs/Implementation-Plan.md`](docs/Implementation-Plan.md)** - section
5 is the production runbook, step by step. The same plan as a deck:
[`plan/eCMRs_Implementation_Plan.pdf`](plan/eCMRs_Implementation_Plan.pdf).

## What it is

- New CMRs are created with **New**; CMR Num is `CMR-YYMMDD-HHMMSS` (e.g. `CMR-260929-111742`).
- Every field is a real, writable column on `ue_ecmrs` (76 columns) - no joins to `rs_cmr` /
  `rs_crcvr`, no `RSQC_CreateCmrSp`, no Infor object changed.
- Lookups fill their descriptions: Item, Next Lvl Assy, Vendor, Dept, Work Center, and the six
  Reviewer / Assigned IDs.
- **Initial Change** ticks the right Requirement checkboxes; **Reason** / **Cause Code** use the
  QC_MRRs code lists; **Serial #** / **LOT #** list the selected Item's serials / lots.
- Sections: Change Request Fields, Additional Fields, **Quality**, **Engineering**,
  **Implementation** (Planning / Purchasing / CM reviewers, **Closed** sets Close Date and Closed By).

Why a new table instead of extending the legacy ones: `RS_QCCmrs`'s composite key makes **New**
impossible without `RSQC_CreateCmrSp`, and most CMR fields are read-only joins there. The earlier
extension attempt is [Enflite/cmr-project](https://github.com/Enflite/cmr-project); its exports of the
legacy forms are the requirements reference.

## Release

- **2026-09-28:** Form **v2** built (imported on TRN 2026-09-29). Fixes from the TRN review
  ([`docs/field-review.md`](docs/field-review.md)): Dept/WC descriptions auto-fill (`SetPropertyFromList`
  validators), Reason/Cause Code get their own code lists (fixes the `'FP'` error), Implementation
  section re-laid out, Internal Review Date moved back to Engineering.
- **2026-09-29:** v2 also fixes PO Line (it stored the Item, so saves failed with "Data length for
  Notify (12) ...") and links every field to its label so error messages name the right field.
  Text columns we own go to 255 (`char(255)`; `cause_code` was `char(1)`), and every IDO length
  matches its column ([`docs/length-fixes.md`](docs/length-fixes.md)).
- **2026-09-29:** CMR Num is now `CMR-YYMMDD-HHMMSS`, set by the form on **New** (AUTONUMBER
  repeated numbers: PK_ue_ecmrs error). Closed checkbox script fixed; cut-off labels fixed.
- **2026-09-29:** v2 **confirmed working on TRN** end to end: Dept/WC descriptions, Reason/Cause,
  PO Line, Serial #/LOT #, Requirements cascade, reviewer names, Closed, CMR Num, saves. SQL and
  IDO match (exports `docs/reference/*_2026-09-29d.csv`; optional: `Status` IDO length).
- **2026-09-29:** Production kit: [`docs/Implementation-Plan.md`](docs/Implementation-Plan.md)
  (seven phases, production runbook), deck in [`plan/`](plan/), production import files built from
  the TRN exports ([`exports/production/`](exports/production/)) with a `--verify` check.

- **2026-09-29:** Right-click → Help works: the form points to the Infor CMR help topic (was "Invalid
  URL string, or no help is defined").

Production go-live gets a line here: `- **YYYY-MM-DD:** eCMRs live in **production** (after TRN).`

## Layout

| Path | What |
|---|---|
| [`docs/Implementation-Plan.md`](docs/Implementation-Plan.md) | **Start here.** Seven phases, BRD, open items, the production runbook (section 5), test, rollback |
| [`plan/eCMRs_Implementation_Plan.pptx`](plan/eCMRs_Implementation_Plan.pptx) / [`.pdf`](plan/eCMRs_Implementation_Plan.pdf) | The plan as a deck (Enflite style). Content in [`plan/deck.config.js`](plan/deck.config.js), layout in `plan/build_impl_deck.js`; rebuild: `cd plan && npm install && npm run build && npm run pdf` |
| `plan/brand/`, `plan/icons/` | Logo and deck icons (from Enflite/Form-Project-Templates) |
| [`exports/eCMRs_v2.XML`](exports/eCMRs_v2.XML) | **The form to import** (FormSync, Site scope). Built by `tools/apply_form_changes.py` |
| [`exports/production/`](exports/production/) | **Production import files**: `ue_ecmrs_SqlColumns_import.csv`, `ue_ecmrs_IdoProperties_import.csv` - TRN's working columns and properties, grid format |
| [`original/eCMRs.trn.original.xml`](original/eCMRs.trn.original.xml) | Form v1 as first on TRN - input to the build script and the rollback copy ([README](original/README.md)) |
| [`tools/apply_form_changes.py`](tools/apply_form_changes.py) | Builds v2 from v1 by editing the XML text in place; `--check` verifies the committed file |
| [`scripts/make_production_imports.py`](scripts/make_production_imports.py) | Builds `exports/production/` and the build sheet from the TRN exports; `--check`; `--verify` compares production with TRN |
| [`scripts/compare_live_lengths.py`](scripts/compare_live_lengths.py) | Checks live SQL / IDO exports against the schema; writes `docs/length-fixes.md` |
| [`scripts/generate_schema_csv.py`](scripts/generate_schema_csv.py) | Schema master list (`FIELDS`); with `generate_ido_import.py`, `generate_sql_columns_import.py`, `generate_deploy_checklist.py`, `validate_schema_consistency.py`. `generate_form.py` is retired (built v1) |
| `exports/ecmrs_*.csv` | Schema-generator output (design reference). For production use `exports/production/` |
| [`docs/production-build-sheet.md`](docs/production-build-sheet.md) | Generated: every column and property to build, readable |
| [`docs/deploy-checklist.md`](docs/deploy-checklist.md) | Generated: the manual IDO settings (CmrNum, Inline Lists, Read Only, Property Class) |
| [`docs/length-fixes.md`](docs/length-fixes.md) | Generated: IDO vs SQL length differences (currently only the optional `Status`) |
| [`docs/task-list.md`](docs/task-list.md) | Field-by-field status and open decisions |
| [`docs/field-review.md`](docs/field-review.md) | Every field compared with the original forms |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Every problem solved: symptom, cause, fix, confirmation |
| [`docs/reference/`](docs/reference/) | Live Excel exports (SQL Columns, IDO Properties) from TRN, dated |
| [`docs/field-mapping.md`](docs/field-mapping.md), [`docs/build-guide.md`](docs/build-guide.md) | Design-time documents, kept for the reasoning |
| `AGENTS.md` / `CLAUDE.md` | The Enflite SOP (master in Enflite/Form-Project-Templates) |

## Before every commit

```
python3 tools/apply_form_changes.py --check
python3 scripts/make_production_imports.py --check
python3 scripts/validate_schema_consistency.py
python3 scripts/compare_live_lengths.py        # after saving new exports in docs/reference/
```
