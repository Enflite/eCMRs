# eCMRs: implementation plan

The runbook for taking **eCMRs** (electronic Change Management Requests) live in **production** on
**Infor CloudSuite (SyteLine)**. eCMRs replaces the three legacy CMR screens (**Create Change
Request**, **Change Request Management**, **QC_CMRs**) with one form on its own table and IDO:
new CMRs are created with **New**, every field is a real, writable column, and nothing Infor owns
is changed. It is built, imported and tested on **TRN** and working end to end (2026-09-29).
Production repeats the same steps from the same files: section **5. Launch** is the step-by-step
list.

## At a glance

| | |
|---|---|
| **Goal** | One CMR form: create, track and close a CMR through Quality, Engineering and Implementation |
| **System** | Infor CloudSuite (no direct SQL access). Built and proven on **TRN**, then production |
| **Form** | `eCMRs`, imported at **Site** scope from [`exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML) |
| **Table / IDO** | New table `ue_ecmrs` (76 columns) and new IDO `ue_ecmrs` (alias `ec`), Application Studio project `ue_ENF` |
| **Naming** | `ue_` for Enflite tables and IDOs; SQL columns `snake_case`, IDO properties `PascalCase` (`cmr_num` → `CmrNum`) |
| **CMR number** | `CMR-YYMMDD-HHMMSS` (e.g. `CMR-260929-111742`), set by the form on **New** |
| **Status** | **Live on TRN, tested end to end (2026-09-29). Production: not started.** |

## The seven phases

| # | Phase | What it means here | Status |
|---|---|---|---|
| 1 | **Scope** | Every field the three legacy screens and the SOW need, on one form | Done |
| 2 | **Design** | Table, IDO, form layout, lookups, scripts | Done |
| 3 | **Develop** | Build table, IDO and form on **TRN** | Done |
| 4 | **Staging** | Test on TRN; compare TRN's exports with the repo | Done (2026-09-29) |
| 5 | **Launch** | Same table, IDO and form in production, in a scheduled window | **Next** |
| 6 | **Test** | Full checklist on TRN before launch; smoke test in production after | TRN done |
| 7 | **Optimize** | Two weeks of follow-up with Quality, Engineering, Purchasing, Planning | After launch |

## TRN first, then Production

| TRN (done) | Production |
|---|---|
| 1. Build table `ue_ecmrs` and IDO `ue_ecmrs` in Application Studio | 1. Import the same columns and properties from the TRN exports ([`exports/production/`](../exports/production/)) |
| 2. Work through the manual IDO settings | 2. Check the result against TRN with one script (`--verify`) |
| 3. Import the form through **FormSync** | 3. Import the same `eCMRs_v2.XML` through **FormSync** |
| 4. Test every field; export SQL Columns + IDO Properties as the production source | 4. Smoke test, then hand over |

---

## 1. Scope

Sources: the three legacy forms (`QC_CMRs`, `Create Change Request`, `Change Request
Management` - exports in [Enflite/cmr-project](https://github.com/Enflite/cmr-project/tree/main/exports)),
the signed CMR Development SOW (Reason/Cause codes, Additional Fields), and the team's requests
during TRN testing. Field-by-field comparison with the originals:
[`field-review.md`](field-review.md).

### What changes

| Section | On the form | Fields | Type | Source |
|---|---|---|---|---|
| Top | Status, Assigned (ID + name), Notify | `Status`, `AssignedEmpNum`, `AssignedUsername` | drop-down, lookup, button | QC_CMRs |
| Top | CMR Num, Create Date, Created By | `CmrNum`, `CreateDate`, `CreatedBy` | automatic | QC_CMRs |
| Top | PO Num, PO Line, Assigned Buyer, Qty, POC, RFQ Num, Job Num, Drawing Revision, Latest Revision, Requested Action | `PoNum`, `PoLine`, `AssignedBuyer`, `Qty`, `Poc`, `RfqNum`, `JobNum`, `Revision`, `LatestRevision`, `RequestedAction` | lookups, text | QC_CMRs |
| Top | Item + Item Desc, Next Lvl Assy + Next Assy Desc, Vendor + Vendor Name, Priority | `Item`, `ItemDescription`, `NextAssyItem`, `NextAssyDescription`, `Vendor`, `VendorName`, `Priority` | lookup + auto-fill | QC_CMRs |
| Change Request Fields | Dept + description, Work Center + description, Reported By, Due Date, Initial Change, 5 Req checkboxes, General Note | `Dept`, `DeptDescription`, `Wc`, `WcDescription`, `ReportedBy`, `DueDate`, `InitialChange`, `Req*`, `GeneralNote` | lookup + auto-fill, cascade | Create Change Request |
| Additional Fields | Serial #, LOT #, Top Level PN, Sub Assembly | `SerialNum`, `LotNum`, `TopLevelPn`, `SubAssembly` | lookup, text | SOW |
| Quality | SOX Impacted, Hold On PO, Authorization For Supplier To Ship, Reason Code, Cause Code, QC Disposition, Reviewer, QC RCA Notes | `SoxImpacted`, `HoldOnPo`, `AuthSupplierShip`, `ReasonCode`, `CauseCode`, `QcDisposition`, `QcReviewer*`, `QcRcaNotes` | checkbox, drop-down, lookup | QC_CMRs, SOW |
| Engineering | EO Num, MDL, Engineering Disposition, Reviewer, Internal Review Date, Eng RCA Notes | `EoNum`, `Mdl`, `EngDisposition`, `EngReviewer*`, `InternalReviewDate`, `EngRcaNotes` | text, drop-down, lookup, date | QC_CMRs |
| Implementation | Planning / Purchasing / CM (done + reviewer), Closed, Close Date, Closed By | `*Complete`, `*ReviewerEmpNum`, `*ReviewerName`, `Closed`, `CloseDate`, `ClosedBy` | checkbox, lookup, automatic | QC_CMRs |

## Business Requirements (BRD)

| ID | Requirement | Detail |
|---|---|---|
| BR-01 | **One form** | Everything the three legacy CMR screens hold, on one `eCMRs` form, created with **New** |
| BR-02 | **Own table** | New table + IDO (`ue_ecmrs`): no dependency on `rs_cmr` / `rs_crcvr` or `RSQC_CreateCmrSp` |
| BR-03 | **Unique CMR number** | `CMR-YYMMDD-HHMMSS`, set on **New**; never repeats a number |
| BR-04 | **Lookups fill descriptions** | Item, Next Assy, Vendor, Dept, Work Center and every Reviewer ID fill their description / name |
| BR-05 | **Requirements cascade** | Initial Change ticks the right Req checkboxes (original mapping) |
| BR-06 | **Codes** | Reason and Cause Codes use the QC_MRRs code lists (13 each) |
| BR-07 | **Close** | Ticking **Closed** sets Close Date and Closed By; unticking clears them |
| BR-08 | **Standards** | No changes to Infor standard objects; Enflite naming (`ue_`, ENF) |
| BR-09 | **Environments** | Built and tested on **TRN** first, then production from the same files |
| BR-10 | **Delivery & rollback** | Form delivered through **FormSync** at Site scope; rollback steps documented |
| BR-11 | **Documentation** | Plan, schema, form files and fixes kept in GitHub (`Enflite/eCMRs`) |

## Open items

1. ~~Dept / WC descriptions don't fill~~ **Answered** (2026-09-29): `SetPropertyFromList` validators.
2. ~~Reason / Cause Code lists (`'FP'` error)~~ **Answered**: own Inline Lists with the QC_MRRs codes.
3. ~~CMR Num repeats (`PK_ue_ecmrs` on save)~~ **Answered**: `CMR-YYMMDD-HHMMSS` set by the form.
4. ~~IDO lengths vs SQL~~ **Answered**: all match (TRN exports 2026-09-29d).
5. **Notify** button shows a message only. Decide: real notification (email to Engineering?) or remove. *Blocks nothing; decide before or during Optimize.*
6. **Reported By** is free text; the original was an employee lookup. Keep or change? *Blocks nothing.*
7. **Assigned Buyer** stores the employee number; the original stored the username. Keep or change? *Blocks nothing.*
8. **Sub Assembly** vs **Next Lvl Assy**: same thing? If so, drop one. *Blocks nothing.*
9. **Legacy screens and history**: when production is live, retire Create Change Request / Change Request Management / QC_CMRs? Migrate old CMRs from `rs_cmr`/`rs_crcvr`? *Blocks retiring the old screens, not the launch.*
10. **Status** IDO length is blank on TRN (works). Optional: set 255 to match the column ([`length-fixes.md`](length-fixes.md)). *Blocks nothing.*

---

## 2. Design

### Table and IDO

| Object | Name | Notes |
|---|---|---|
| SQL table | `ue_ecmrs` | 76 columns + the 7 Application Studio creates itself. Every column: [`production-build-sheet.md`](production-build-sheet.md) |
| Key | `cmr_num` | `nvarchar`, Primary Key. Filled by the form, no default |
| IDO | `ue_ecmrs` | Primary table `ue_ecmrs`, alias `ec`; one property per column |
| Key property | `CmrNum` | Data Type **String**, Length 255, **Default Value blank** (not `AUTONUMBER`, not `NumSortedString`) |
| Text columns | `char(255)` | Our own text fields. Columns on SyteLine types (`ItemType`, `DeptType`, `WcType`, `EmpNumType`, `UsernameType`, `DescriptionType`, `LongDescType`, `RevisionType`, `QCLongCharType`, `QCPriorityType`) keep that type's length |
| Lengths | IDO = SQL | Every IDO property length equals its column's (checked by `scripts/compare_live_lengths.py`) |

### Manual IDO settings (import copies them from TRN; check them)

| Setting | Properties |
|---|---|
| **Inline List** | `Status`, `Priority`, `InitialChange`, `QcDisposition`, `EngDisposition`, `ReasonCode`, `CauseCode` - values in [`deploy-checklist.md`](deploy-checklist.md) |
| **Read Only Record** cleared | Every field the form fills: `ItemDescription`, `NextAssyDescription`, `VendorName`, `DeptDescription`, `WcDescription`, `AssignedUsername`, the five Reviewer names, `CloseDate`, `ClosedBy` |
| **Property Class** blank | All, in particular `ReasonCode` and `CauseCode` |

### How the form fills things in

| On the form | Mechanism (in `eCMRs_v2.XML`) |
|---|---|
| CMR Num on **New** | `StdObjectNewCompleted` script: `"CMR-" & DateTime.Now.ToString("yyMMdd-HHmmss")` |
| Item / Next Assy / Vendor → description | `DefaultFrom` `Item(ItemDescription)`, `Item(NextAssyDescription)`, `VendNum(VendorName)` |
| Dept / Work Center → description | `Validators` `SetPropertyFromList(DeptDescription, Description)` / `(WcDescription, Description)` |
| Reviewer ID → name (Assigned, QC, Eng, Planning, Purchasing, CM) | `DefaultFrom` `EmpNum(<name property>)` on an `SLEmployees` list |
| Initial Change → Req checkboxes | `DefaultFrom` `Change(ReqCosting, ReqProcess, ReqDocumentation, ReqToolMachine, ReqMaterial)` |
| PO Line, Serial #, LOT #, Next Lvl Assy | Lists filtered on PO Num / Item (`'P(...)'`) |
| Closed → Close Date, Closed By | `SetCloseInfo` script + `SetClosedBy` (`SETPROPVALUES(ClosedBy=USERNAME())`) |

Why each one is built this way (and what failed first): [`troubleshooting.md`](troubleshooting.md).

---

## 3. Develop (TRN) - done

1. Table `ue_ecmrs` and IDO `ue_ecmrs` created in Application Studio (project `ue_ENF`); columns and properties imported from the grids' own CSV format. **Done.**
2. Manual IDO settings (Inline Lists, Read Only, `CmrNum`), then **Check In** the IDO. **Done.**
3. Form built by [`tools/apply_form_changes.py`](../tools/apply_form_changes.py) from v1 ([`original/eCMRs.trn.original.xml`](../original/eCMRs.trn.original.xml)) into [`exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML), imported through **FormSync** at Site scope. **Done.**

## 4. Staging (TRN) - done

| Check | How | Pass | Result |
|---|---|---|---|
| A. Every field works | The test list in section 6, on TRN | All ticked | **Pass** (2026-09-29) |
| B. SQL and IDO match the design | Export **SQL Columns** and **IDO Properties** to Excel, save in `docs/reference/`, run `python3 scripts/compare_live_lengths.py` | [`length-fixes.md`](length-fixes.md) lists nothing to change | **Pass** (Status length optional) |
| C. Production files are current | `python3 scripts/make_production_imports.py --check` | "up to date" | **Pass** |

---

## 5. Launch (production)

In a scheduled window. eCMRs is a **new** form on a **new** table: nothing Infor owns and no
existing Enflite form changes, and the legacy CMR screens keep working until you retire them.
Tick each step as you go.

**Before the window**

- [ ] 1. TRN sign-off from the team (section 6 all ticked). *Done 2026-09-29.*
- [ ] 2. In production, check nothing named `ue_ecmrs` (table or IDO) or `eCMRs` (form) exists yet. If it does, stop and compare it with TRN first.
- [ ] 3. Have these files ready from GitHub: [`exports/production/ue_ecmrs_SqlColumns_import.csv`](../exports/production/ue_ecmrs_SqlColumns_import.csv), [`exports/production/ue_ecmrs_IdoProperties_import.csv`](../exports/production/ue_ecmrs_IdoProperties_import.csv), [`exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML), and [`production-build-sheet.md`](production-build-sheet.md) open for checking.

**Table**

- [ ] 4. **Application Studio** → project `ue_ENF` → **SQL Tables** → new table **`ue_ecmrs`**. Application Studio adds `CreatedBy`, `UpdatedBy`, `CreateDate`, `RecordDate`, `RowPointer`, `NoteExistsFlag`, `InWorkflow` itself - don't add them.
- [ ] 5. **SQL Columns** for `ue_ecmrs` → import `ue_ecmrs_SqlColumns_import.csv` (76 columns), the same way the columns were imported on TRN.
- [ ] 6. Check: 83 columns in total; `cmr_num` is `nvarchar(999)`, **Primary Key**, no default; the text columns are `char(255)`. If a row was rejected, key it in from the build sheet.

**IDO**

- [ ] 7. **IDOs** → new IDO **`ue_ecmrs`**, primary table `ue_ecmrs`, table alias **`ec`**, project `ue_ENF`.
- [ ] 8. **IDO Properties** → import `ue_ecmrs_IdoProperties_import.csv` (76 properties). This carries every length, Inline List and Read Only Record setting from TRN.
- [ ] 9. Check `CmrNum`: Data Type **String**, Length 255, **Default Value blank**, Pseudo Key 1.
- [ ] 10. **Check In** the IDO (IDOs tab → `ue_ecmrs` → **Check In**; the "Source control integration is currently disabled" popup is harmless - OK).

**Verify against TRN**

- [ ] 11. Export production's **SQL Columns** and **IDO Properties** grids to Excel (same as on TRN).
- [ ] 12. Save them in `docs/reference/` as `ToExcel_SqlColumns_PRD_<date>.csv` / `ToExcel_IdoProperties_PRD_<date>.csv` and run:
      `python3 scripts/make_production_imports.py --verify docs/reference/ToExcel_SqlColumns_PRD_<date>.csv docs/reference/ToExcel_IdoProperties_PRD_<date>.csv`
      Pass: *"OK: production matches TRN"*. Otherwise it names each difference: fix it in Application Studio, Check In, export again, re-run. (No computer handy? Check the grids against [`production-build-sheet.md`](production-build-sheet.md) by eye.)

**Form**

- [ ] 13. **FormSync** → import [`exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML) at **Site** scope.
- [ ] 14. Make **eCMRs** available to users the same way as on TRN (menu / Explorer folder, form security), and write down here how it was done.

**Smoke test (in production)**

- [ ] 15. **New**: CMR Num shows `CMR-YYMMDD-HHMMSS`.
- [ ] 16. Pick an Item, a Dept, a Work Center, a Vendor, a PO Num then PO Line, one Reviewer ID: every description / name fills; PO Line shows a line number.
- [ ] 17. Initial Change **Machine**: Costing, Documentation, Tool/Machine, Process tick.
- [ ] 18. Reason Code and Cause Code list their codes (no error).
- [ ] 19. Save; **New** again and save a second one; reopen both.
- [ ] 20. Tick **Closed** on a test CMR: Close Date = today, Closed By = you. Delete the test CMRs.

**Record it**

- [ ] 21. README **Release**: `- **YYYY-MM-DD:** eCMRs live in **production** (after TRN). Form: exports/eCMRs_v2.XML; table/IDO from exports/production/.` Commit the production exports from step 12.
- [ ] 22. This plan's **Status** row: `Live in production (YYYY-MM-DD)`. Start **Optimize**.

## 6. Test

On TRN - all passed 2026-09-29 (see [`task-list.md`](task-list.md)):

- [x] **New** gives `CMR-YYMMDD-HHMMSS`; saves work; no duplicate-key error
- [x] Item → Item Desc, Next Lvl Assy → Next Assy Desc, Vendor → Vendor Name
- [x] Dept → Dept Description, Work Center → WC Description
- [x] PO Num → PO Line (line number, not Item); Job Num list
- [x] Assigned, QC, Eng, Planning, Purchasing, CM: Reviewer ID fills the name
- [x] Initial Change ticks the right Req checkboxes
- [x] Serial # (serial-tracked item), LOT # (lot-tracked item)
- [x] Reason Code, Cause Code lists; Status, Priority, Dispositions lists
- [x] Closed sets Close Date and Closed By
- [x] Existing records open without errors; the list (grid) shows CMR Num, Status, Priority, Item, Dept, WC, Created By/Date, Due Date, Closed
- [x] Team sign-off on TRN

In production: the smoke test in section 5 (steps 15-20).

## 7. Optimize (2 weeks after launch)

- Track issues from each team (Quality, Engineering, Planning, Purchasing, CM) using eCMRs
- Fix bugs through TRN first, then production, same way (new form version in `exports/`, FormSync)
- Decide the open items (Notify, Reported By, Assigned Buyer, Sub Assembly, legacy screens)
- Update the CMR procedure (QA-300-037, section 5.5) for eCMRs; submit for manager approval

## Rollback

- **Form problem**: re-import the previous form version through FormSync (TRN's v1 is [`original/eCMRs.trn.original.xml`](../original/eCMRs.trn.original.xml)). In production there is no earlier eCMRs form: if eCMRs has to be pulled, take it off the menu / form security and keep using the legacy CMR screens, which are untouched.
- **Table / IDO**: new objects only - nothing existing depends on them. Leave them in place (no data is lost); fix forward on TRN.
- Data entered in eCMRs stays in `ue_ecmrs` either way.

## Reference

| File | What |
|---|---|
| [`../README.md`](../README.md) | What eCMRs is, Release log, Layout of every file |
| [`../exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML) | The form to import (FormSync, Site scope) |
| [`../tools/apply_form_changes.py`](../tools/apply_form_changes.py) | Builds the form from v1; `--check` |
| [`../exports/production/`](../exports/production/) | SQL Columns and IDO Properties import files for production (from the TRN exports) |
| [`production-build-sheet.md`](production-build-sheet.md) | Every column and property, readable |
| [`../scripts/make_production_imports.py`](../scripts/make_production_imports.py) | Builds the production files; `--verify` compares production with TRN |
| [`../scripts/compare_live_lengths.py`](../scripts/compare_live_lengths.py) / [`length-fixes.md`](length-fixes.md) | IDO vs SQL lengths check |
| [`deploy-checklist.md`](deploy-checklist.md) | Manual IDO settings (Inline Lists, Read Only, CmrNum) |
| [`task-list.md`](task-list.md) | Field-by-field status |
| [`field-review.md`](field-review.md) | Comparison with the original forms |
| [`troubleshooting.md`](troubleshooting.md) | Every problem solved: symptom, cause, fix |
| [`reference/`](reference/) | Live exports (TRN SQL Columns / IDO Properties) |
| [`../plan/eCMRs_Implementation_Plan.pptx`](../plan/eCMRs_Implementation_Plan.pptx) / [`.pdf`](../plan/eCMRs_Implementation_Plan.pdf) | This plan as a deck |
