# AGENTS.md — Enflite SyteLine project SOP

This is the standard operating procedure for every Enflite SyteLine customization repo (e.g. `Enflite/eCMRs`, `Enflite/Incidents-`, `Enflite/ServiceOrders`). The same file goes in every repo, unchanged. Anything specific to one repo goes in its `README.md` and `docs/`, not here. `CLAUDE.md` holds a single line, `@AGENTS.md`, so every agent reads the same rules.

If this file and a repo's docs disagree, the repo's docs describe what is live. Fix whichever one is wrong in the same change.

## 1. What these repos are

- The system is **Infor CloudSuite (SyteLine / CSI + FSP)**. **There is no direct SQL access.** Any `sql/` script is reference only; every check you give the team must be doable in the SyteLine UI (Design Mode, Dataviews, Excel exports from UET forms, "does the form open without errors").
- Each repo is one form or one feature. It holds the form export(s), the scripts that build them, the rollback copies, and the plan and runbook.
- The agent works on files in git only. **It cannot drive SyteLine, Application Studio, FormSync or UET.** Every step in the system is done by a person: write it as numbered steps they can follow, and never claim a system step is done until the user says so (then record it, see §8).

## 2. Hard rules (never break these)

1. **TRN first, then production.** Everything is built and proven on TRN. Production repeats the same steps, in the same order, from the same files.
2. **Never change Infor-owned objects.** Do not edit, extend-and-replace, or add properties to standard IDOs (`FSSROs`, `FSIncidents`, …), tables or Vendor forms. Add fields with **UET**; build new features on a **new table + new IDO** (the eCMRs pattern) when UET does not fit.
3. **Forms go in through FormSync at Site scope**, never over the Vendor definition, never by hand in Design Mode as the delivery method.
4. **Back up before every import.** Export the unchanged form from each environment and commit it to `original/` before the first import there (§5).
5. **Never hand-edit a generated file.** Form XML, CSVs and checklists are rebuilt by the script in `tools/` or `scripts/`. Change the script, re-run it, commit both.
6. **Keep form exports byte-for-byte.** Form XML is UTF-8 **with BOM** and **CRLF** line endings. `.gitattributes` must contain `*.xml -text` and `*.XML -text`. Scripts edit the text in place; never re-serialize the XML with a parser.
7. **The team's source is the source of truth** (their spreadsheet, mockup or request, kept in `docs/` or `plan/mockups/`). Do not invent fields, labels or ordering. If the sources disagree, list it under Open items and ask.
8. **Confirmed vs. assumed.** Only write "confirmed" when the user has seen it work in the system. Otherwise say it is assumed and how to check it.

## 3. Naming standard

`ENF` marks Enflite-created objects. Anything without it is Infor's.

| Object | Pattern | Example |
|---|---|---|
| UET User Field | `Uf_ENF_<Name>` (PascalCase) | `Uf_ENF_DateOfManufacture` |
| UET field reused from another form | keep its existing name | `Uf_ENF_COL_LORC1` |
| UET Class | `ENF_<Area>` | `ENF_SroTracking`, `ENF_IncidentUnit` |
| User Defined Type | `ENF_<Name>` | `ENF_ZeroTime` |
| Application Studio project | `ue_ENF` | |
| Custom SQL table / IDO | `ue_<name>` | `ue_ecmrs` |
| Custom table column / IDO property | `snake_case` column, `PascalCase` property | `cmr_num` → `CmrNum` |
| Form component for a UET field | `Uf<Name>Static`, `Uf<Name>Edit`, `Uf<Name>GridCol` | `UfDateOfManufactureEdit` |

- Dates: User Data Type `Date4Type`, Data Type **`datetime`** (re-open the field after saving to check; `nvarchar` shows dates as `20260909 00:00:00.000`).
- A form binds to a UET field as **`object.<table alias>Uf_ENF_<Name>`** (e.g. `sroUf_ENF_EvalDate`). The alias is confirmed in Design Mode (§6, Staging check A) and passed to the build script as `--prefix`. These properties do not appear in the IDO Properties export, so never use that export to check for them. Never bind to the `Der<alias>ExtBy…` helper properties.

## 4. Repo layout

Use these paths so every repo reads the same. Leave out what a project does not need.

| Path | What |
|---|---|
| `README.md` | What the change is (bullets), **Release** log, **Layout** table of every file |
| `AGENTS.md` / `CLAUDE.md` | This SOP / `@AGENTS.md` |
| `.gitattributes` | `*.xml -text`, `*.XML -text` |
| `<Form>.xml` | The form export **with the changes applied**, ready to import (for new-table projects: `exports/<Name>_vN.XML`) |
| `original/<Form>.trn.original.xml`, `original/<Form>.production.original.xml` | Unchanged exports, the rollback copies, with an `original/README.md` |
| `tools/` or `scripts/` | Python scripts that build every generated file from the originals / one master field list |
| `docs/Implementation-Plan.md` | **Start here.** The seven-phase runbook (§6) |
| `docs/troubleshooting.md` (or a Troubleshooting section) | Every confirmed gotcha: symptom → cause → fix |
| `docs/` | The team's source files (spreadsheet, mockups), reference exports, UET or build guides |
| `plan/<Project>_Implementation_Plan.pptx` + `.pdf` | The plan as a deck, with its build script |
| `plan/mockups/` | Requested mockups |
| `sql/` | Reference-only SQL (say so at the top of each file) |

Never commit `node_modules/`, `__pycache__/` or secrets; keep them in `.gitignore`.

## 5. Form change workflow

1. **Export the original** from TRN (and later production) and commit it under `original/` with a README table: file, environment, when exported. Compare the two with SHA-256 and write down whether they are identical (if not, production has local changes: stop and ask).
2. **Write a build script** in `tools/` that reads the original and writes `<Form>.xml`. Its docstring says what it changes, where the layout comes from, and how to run it (`python3 tools/apply_form_changes.py [--prefix <alias>]`). The script must reproduce the committed `<Form>.xml` exactly; re-run it and check `git diff` is empty before committing.
3. **Highlight every new or changed component in purple** so testers can find them: labels `BACKCOLOR(112,48,160) FORECOLOR(255,255,255)`, fields and grid columns `BACKCOLOR(221,204,255)`. Removing the highlight is its own later change (drop the keywords in the script, rebuild, re-import).
4. Add a grid-view column for every new field. Keep existing components where they are unless the source says to move them; if something must move or resize, say why in the plan.
5. Relabels are **Caption changes only**: binding, lists and validators stay the same.

For new-table projects (eCMRs pattern): one master field list in `scripts/` generates the table CSV, IDO property CSV, form XML and `docs/deploy-checklist.md`, plus a consistency check script. Import CSVs must match the live export's exact header, column count and quoting. Manual Application Studio steps that import cannot do (Read Only flags, Inline Lists, **Check In** the IDO) go in the generated deploy checklist.

## 6. The Implementation Plan (seven phases)

`docs/Implementation-Plan.md` always has these sections, in this order:

1. Title and one-paragraph summary.
2. **At a glance** table: Goal, System, Form (and scope), IDO / table, Naming, **Status**.
3. **The seven phases** table: **Scope → Design → Develop → Staging → Launch → Test → Optimize**.
4. **TRN first, then Production** side-by-side table.
5. **1. Scope**: "What changes" table (Tab, On the form, Field, Type, Source), citing the source file.
6. **Business Requirements (BRD)**: `BR-01…` table. Always include: no Infor object changes / Enflite naming, TRN then production, FormSync delivery with rollback, docs kept in GitHub.
7. **Open items**: numbered, each with what it blocks. Strike through and mark **Answered** when resolved; do not delete.
8. **2. Design**: one table per UET form, in setup order: User Defined Types, User Fields, Classes, Class/Field Relationships, Table/Class Relationships (Active ✔, Extend All Records ✔). Then "How the form reaches the field".
9. **3. Develop (TRN)**: 3a UET setup in that order; 3b **UET Impact Schema** (users out of the form, Commit Form Changes + Impact Schema, Process, then **Unload IDO Metadata**); 3c the form with FormSync (§5).
10. **4. Staging (TRN)**: 4a confirm the fields are on the IDO before importing (A: Design Mode property list, B: throw-away Dataview, C: import, save, reopen), with what each failure means; 4b refresh and import.
11. **5. Launch (production)**: the numbered list, in a scheduled window, ending in a smoke test. Use TRN's UET Excel exports as the checklist.
12. **6. Test**: `- [ ]` checklist (saves, reloads, clears, new record, existing records open without errors, grid column, relabels, team sign-off).
13. **7. Optimize (2 weeks)**: follow-up, bug fixes, procedure updates for manager approval.
14. **Rollback**: re-import `original/<Form>.<env>.original.xml` through FormSync; say what happens to UET fields and data.
15. **Reference**: table of every file, linked.

When the plan changes, update the deck in `plan/` to match and rebuild the `.pdf`.

## 7. Decks and Word documents

- Follow the Enflite brand style guide: [`Enflite/eCMRs/docs/branding/enflite-style-guide.md`](https://github.com/Enflite/eCMRs/blob/main/docs/branding/enflite-style-guide.md). Enflite Red `#CF0C2C`, Ink `#1A1A1A`, Charcoal `#252525`; black/white/red with red used sparingly; no cards, no shadows; light display type with one bold word; real logo from `docs/branding/assets/`.
- Deck order: title, Scope, BRD, one Design slide per UET form, Develop, Staging, Launch, Test, Optimize, Rollback.
- Build decks from a script (`plan/build_*.js` with pptxgenjs) and commit the `.pptx`, `.pdf` and the script. Word copies of Markdown docs are built with `tools/md_to_docx.py` (pandoc), never edited by hand.

## 8. Writing style for docs

- Plain, short sentences for the people doing the work. Imperative steps, numbered when order matters.
- **Bold** SyteLine screen names, buttons and on-form labels; `code` for field, class, table, IDO, property and file names.
- Tables over prose for fields, checks and files. Each check: what to do, where, and what "pass" looks like.
- Link files relatively (`../original/…`) and link sister repos when reusing their approach.
- Record status as it happens: a `**Done:**` note on the step in the plan, and a dated line in the README **Release** section on go-live (e.g. `**2026-09-25:** … live in **production**`).
- Every problem solved in the system becomes a troubleshooting entry: symptom (exact error text), cause, fix steps, how to confirm, and which environments need it.

## 9. Git

- Work on the branch you were given; never push to `main` directly. Changes reach `main` through a pull request, reviewed by a person.
- One logical change per commit. Subject in the imperative, specific, under ~72 characters, prefixed with the area when it helps: `Troubleshooting: date field showing 20260909 00:00:00.000 (Data Type nvarchar)`, `Back up the production ServiceOrders form export before the production import`.
- Commit the generated file together with the script change that produced it.
- Before every commit: re-run the build scripts (no diff), check the XML still has BOM + CRLF, check every link and path in the docs exists, and update the README **Layout** table if files were added or moved.

## 10. Checklist for a new repo

- [ ] Copy this `AGENTS.md`; add `CLAUDE.md` containing `@AGENTS.md`
- [ ] `.gitattributes` with `*.xml -text` and `*.XML -text`; `.gitignore`
- [ ] Team's source files in `docs/` or `plan/mockups/`
- [ ] `original/` TRN export + README
- [ ] Build script in `tools/`, generated `<Form>.xml`
- [ ] `docs/Implementation-Plan.md` in the §6 structure
- [ ] `README.md` with change bullets, Release, Layout
- [ ] Deck in `plan/` in the brand style
