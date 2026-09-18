# eCMRs — Field Mapping

Rebuilt from the **real, complete** `QC_CMRs` Form Sync export (every component the stakeholder pasted directly) — not just the subset `cmr-project` had tracked as its "confirmed editable scope." Every field below gets its own original column on the new standalone table. No `RsCrcvr*`/`rs_cmrUf_*` legacy names, no joins, no dependency on `rs_cmr`/`rs_crcvr`/any other table.

Status vocabulary: **Planned** (in this list, not yet built), **Built**, **Tested**.

## Header / Identity

| Field (legacy label) | Legacy property | New column | Type | Notes |
|---|---|---|---|---|
| CMR Num | `CmrNum` | `cmr_num` | Autonumber (key) | Numbering mechanism still to be decided — see `task-list.md` Phase A. |
| Status | `Status` (`DefaultFrom: QCStatusListings()`) | `status` | String / small list | Legacy `DefaultFrom` is a system function tied to `RS_QCCmrs`'s own status list — decide whether eCMRs defines its own fixed list or reimplements the lookup. |
| Workflow Status | `rs_cmrUf_ENF_CMR_WorkFlowStatus` (`DefaultFrom: UserDefinedType(Cmr_CMR_WorkFlowStatus)`) | `workflow_status` | String / small list | `UserDefinedType(...)` is a legacy configured value-list mechanism tied to a UDT defined elsewhere in the system (`Cmr_CMR_WorkFlowStatus`) — **can't be copied as-is**; eCMRs needs its own fixed/inline list or its own new UDT. |
| Create Date | `CreateDate` | `create_date` | DateTime | Defaults to now on creation. |
| Created By | `CreatedBy` | `created_by` | String | |

## Priority / Item / Change

| Field | Legacy property | New column | Type | Notes |
|---|---|---|---|---|
| Priority | `RsCrcvrPriority` (read-only, receiver-joined) + `RsPriorityPriority` (description) | `priority` | String / small list | Legacy form carries **two** read-only, joined properties for one concept. eCMRs collapses this to one native, writable field. |
| Item | `RsCrcvrItem` | `item` | String | `SLItems` list source. |
| Item Description | `ItmDescription` | `item_description` | String (read-only display) | |
| Work Center | `RsCrcvrWc` | `wc` | String | `SLWcs` list source. |
| WC Description | `WcDescription` | `wc_description` | String (read-only display) | |
| Dept | `RsCrcvrDept` | `dept` | String | `SLDepts` list source. |
| Dept Description | `DepDescription` | `dept_description` | String (read-only display) | |
| Initial Change (real reason code) | `RsCrcvrChange` (hidden on the legacy form) | `initial_change` | String, fixed 8-value list | Drives the Requirements cascade — see below. |
| Additional Changes (running notes) | `RsCrcvrChangeAll` | `additional_changes` | Multiline text | Distinct field from Initial Change — a growing note, not the single reason code. |
| Requested Action (receiver's original note) | `RsCrcvrNote` | `requested_action` | Multiline text | |
| General Note | `Note` (`QCLongChar`) | `general_note` | Multiline text | **A second, separate note field from Requested Action** — confirmed distinct property on the legacy form, not a duplicate. Purpose (ongoing QC/review commentary vs. the original request) worth confirming, but both get their own column. |
| Drawing Revision | `Revision` | `revision` | String | |
| Latest Revision | `rs_cmrUf_ENF_CMR_LatestRev` | `latest_revision` | String | Hidden on the legacy form — confirm still wanted. |
| Next Lvl Assy (item) | `rs_cmrUf_ENF_CMR_NextAssyItem` | `next_assy_item` | String | `SLJobmatls` list source, filtered by `Item`. |
| Next Lvl Assy Description | `rs_cmrUf_ENF_CMR_NextAssyDescription` | `next_assy_description` | String (read-only display) | Auto-populated via `UpdateDescriptionNextAssy` — see Business Logic below. |
| Vendor | `rs_cmrUf_ENF_CMR_Vendor` (`DefaultFrom: VendNum()`) | `vendor` | String | |
| Vendor Name | `rs_cmrUf_ENF_CMR_VendorName` | `vendor_name` | String (read-only display) | Auto-populated via `UpdateVendorDescription`. |
| Qty | `rs_cmrUf_ENF_CMR_Qty` | `qty` | Number | |
| Job Num | `rs_cmrUf_ENF_CMR_JobNum` | `job_num` | String | Legacy `SLMatltrans` filter has a real leading-zero exact-match bug (documented in `cmr-project`) — fix it correctly here, don't inherit it. |
| PO Num / PO Line | `rs_cmrUf_ENF_CMR_PoNum` / `PoNumLine` | `po_num` / `po_line` | String | `SLPoItems` list source. |
| RFQ Num | `rs_cmrUf_ENF_CMR_RFQNum` | `rfq_num` | String | |
| EO Num | `rs_cmrUf_ENF_CMR_EO_Num` | `eo_num` | String | |
| MDL | `rs_cmrUf_ENF_CMR_MDL` | `mdl` | String | |
| POC | `rs_cmrUf_ENF_CMR_POC` | `poc` | String | Plain text field, distinct from Created By/Reported By. |

## Requirements checkboxes + Review-Complete flags (5 categories)

Same business mapping as `cmr-project` (Initial Change drives which of these are required) — see that table below. Each category has **two** legacy properties: a read-only "is this required" flag and a separate "has review been completed" flag.

| Category | Required flag (legacy) | New "required" column | Review-complete flag (legacy) | New "complete" column |
|---|---|---|---|---|
| Costing | `RsChangeCosting` | `req_costing` | `CostReviewComplete` | `cost_review_complete` |
| Documentation | `RsChangeDocumentation` | `req_documentation` | `DocumentationReviewComplete` | `documentation_review_complete` |
| Tool/Machine | `RsChangeToolmachine` | `req_tool_machine` | `MachineryReviewComplete` | `machinery_review_complete` |
| Process | `RsChangeProcess` | `req_process` | `ProcessReviewComplete` | `process_review_complete` |
| Material | `RsChangeMaterial` | `req_material` | `MaterialReviewComplete` | `material_review_complete` |
| — (general, hidden on legacy form) | — | — | `GeneralComplete` | `general_review_complete` |

Also found, not tied to the 5-category system:
- **SOX Impacted** (`SOXImpacted`) → `sox_impacted` — a standalone Sarbanes-Oxley impact flag.
- **Hold On PO** (`rs_cmrUf_ENF_CMR_HoldOnPo`) → `hold_on_po`.
- **Authorization For Supplier To Ship** (`rs_cmrUf_ENF_CMR_AuthForSuppShip`) → `auth_supplier_ship`.

## Disposition

| Field | Legacy property | New column | Notes |
|---|---|---|---|
| QC Disposition | `rs_cmrUf_ENF_CMR_QCDisposition` (`DefaultFrom: UserDefinedType(Cmr_QCDispositionStatus)`) | `qc_disposition` | Same `UserDefinedType` caveat as Workflow Status — needs its own list on eCMRs, not a copy of the legacy UDT reference. |
| Engineering Disposition | `rs_cmrUf_ENF_CMR_EngDisposition` (`DefaultFrom: UserDefinedType(Cmr_EngDispositionStatus)`) | `eng_disposition` | Same caveat. |

## Assignment / Reviewers

**⚠ Real duplication found on the legacy form, needs a decision, not a blind carry-over**: two separate "Assigned" mechanisms exist simultaneously —
1. The native `AssignedTo` property (`EmpNum` class) — a plain, simple field.
2. A custom pair, `rs_cmrUf_ENF_CMR_AssignedUserEmpNum` (the real selectable combo, `SLEmployees` list source) + companion `rs_cmrUf_ENF_CMR_AssignedUser` (auto-populated username, via `UpdateAssignedToNameDisp`).

eCMRs should pick **one** assignment mechanism, not carry both. Recommend the custom EmpNum+Username pair (mechanism #2) since it's the one with a real working name/email display, and drop the plain native duplicate.

| Field | Legacy property | New column | Notes |
|---|---|---|---|
| Assigned (EmpNum) | `rs_cmrUf_ENF_CMR_AssignedUserEmpNum` | `assigned_empnum` | `SLEmployees` combo. |
| Assigned (username display) | `rs_cmrUf_ENF_CMR_AssignedUser` | `assigned_username` | Auto-set via `SelectionEvent`, same proven pattern as `cmr-project`'s Assigned field. |
| Assigned Buyer | `rs_cmrUf_ENF_CMR_BuyerPlannerUsr` (`DefaultFrom: UserName()`) | `assigned_buyer` | Separate role from "Assigned" above. |
| QC Reviewer (EmpNum) | `rs_cmrUf_ENF_CMR_QCReviewerEmpNum` | `qc_reviewer_empnum` | |
| QC Reviewer (username display) | `rs_cmrUf_ENF_CMR_QCReviewer` | `qc_reviewer_username` | Auto-set via `UpdateQLTYReviewerNameDisp`. |
| Engineering Reviewer (EmpNum) | `rs_cmrUf_ENF_CMR_EngReviewerEmpNum` | `eng_reviewer_empnum` | |
| Engineering Reviewer (username display) | `rs_cmrUf_ENF_CMR_EngReviewer` | `eng_reviewer_username` | Auto-set via `UpdateENGReviewerNameDisp`. |
| Planning Reviewer (EmpNum) | `rs_cmrUf_ENF_CMR_IMP_PlanningEmpNum` | `planning_reviewer_empnum` | |
| Planning Reviewer (name display) | `rs_cmrUf_ENF_CMR_IMP_PlanningEmpName` | `planning_reviewer_name` | Auto-set via `UpdatePlannerNameDisp`. |
| Planning sign-off checkbox | `rs_cmrUf_ENF_CMR_IMP_PlanningCB` | `planning_complete` | |
| Purchasing Reviewer (EmpNum) | `rs_cmrUf_ENF_CMR_IMP_PurchasingEmpNum` | `purchasing_reviewer_empnum` | |
| Purchasing Reviewer (name display) | `rs_cmrUf_ENF_CMR_IMP_PurchasingEmpName` | `purchasing_reviewer_name` | Auto-set via `UpdatePurchasingNameDisp`. |
| Purchasing sign-off checkbox | `rs_cmrUf_ENF_CMR_IMP_PurchasingCB` | `purchasing_complete` | |
| CM Reviewer (EmpNum) | `rs_cmrUf_ENF_CMR_IMP_CMEmpNum` | `cm_reviewer_empnum` | |
| CM Reviewer (name display) | `rs_cmrUf_ENF_CMR_IMP_CMEmpName` | `cm_reviewer_name` | Auto-set via `UpdateCMNameDisp`. |
| CM sign-off checkbox | `rs_cmrUf_ENF_CMR_IMP_CMCB` | `cm_complete` | |

## Dates

| Field | Legacy property | New column | Notes |
|---|---|---|---|
| Due Date | `DueDate` | `due_date` | |
| Internal Review Date | `InternalReviewDate` | `internal_review_date` | |
| Close Date | `CloseDate` | `close_date` | Shown in multiple places on the legacy form (top-level + IMPLEMENTATION section) — same underlying property, collapses to one column. Auto-set to today when `Closed` is checked, via `SetCloseInfo`. |
| Closed By | `ClosedBy` | `closed_by` | Same collapsing note as Close Date. Auto-set to current user via `SetClosedBy`. |
| General Close Date | `GeneralCloseDate` (hidden) | `general_close_date` | Purpose unclear — hidden on the legacy form, separate from the main Close Date. Confirm whether it's still needed before building. |
| General Closed By | `GeneralClosedBy` (hidden) | `general_closed_by` | Same caveat as General Close Date. |

## Notes (free text)

| Field | Legacy property | New column |
|---|---|---|
| QC RCA Notes | `rs_cmrUf_ENF_CMR_QCRCANotes` | `qc_rca_notes` |
| Eng RCA Notes | `rs_cmrUf_ENF_CMR_EngRCANotes` | `eng_rca_notes` |

## Closed

| Field | Legacy property | New column |
|---|---|---|
| Closed (flag) | `Closed` | `closed` |

## Costing detail lines — ⚠ open design question, one-to-many

The legacy form has a **Costing** grid (`RS_QCCosts`: `Sequence`, `DocType`, `DocNum`, `Activity`, `Costtype`, `Qty`, `UnitCost`, `Description`, `Note`) — multiple cost line-items per CMR, not a single value. This is genuinely **one-to-many**, unlike everything else in this document.

`cmr-project` already hit a real wall trying to build a one-to-many relationship from scratch: the `New Property` wizard's `Bind To` picker only offers scalar columns, with no `Subcollection`/`Derived` option, and no way to build one from the UI alone (see that project's `task-list.md`, "Grid/Subcollection binding is a one-to-many mechanism"). **Decide before building**:
- Whether eCMRs needs cost line-items at all in its first version, or whether a single rolled-up `estimated_cost` field is enough for now.
- If real line-items are needed, whether that requires help from whoever manages IDO configuration (same conclusion `cmr-project` reached), since it's not achievable solo through Design mode based on prior findings.

## Requirements checkbox cascade (unchanged from `cmr-project`)

| Initial Change | Costing | Documentation | Material | Process | Tool/Machine |
|---|:---:|:---:|:---:|:---:|:---:|
| Documentation | | ✓ | | | |
| Machine | ✓ | ✓ | | ✓ | ✓ |
| Material | ✓ | ✓ | | | |
| Other | | | | | |
| Process | ✓ | ✓ | | ✓ | ✓ |
| Specification | ✓ | ✓ | | ✓ | ✓ |
| Tooling | | | | | ✓ |
| Variance(waiver) | ✓ | ✓ | | ✓ | ✓ |

Mechanism: on the legacy form, a native `DefaultFrom: Change(RsChangeCosting, RsChangeProcess, RsChangeDocumentation, RsChangeToolmachine, RsChangeMaterial)` function, tied to the real `Change` property class. **Unverified whether this works on brand-new property names on eCMRs's own IDO** — see `task-list.md` Phase A; build a scripted equivalent if it doesn't.

## Business logic to replicate (found in the real form's scripts/event handlers)

- **`EnableClosed()`** — gates whether the `Closed` checkbox can even be checked: for each of the 5 categories, if its `req_*` flag is true, the matching `*_review_complete` flag must also be true before `Closed` is allowed. Real business rule, must be rebuilt on eCMRs.
- **`SetCloseInfo`/`SetClosedBy`** — when `closed` is checked, auto-set `closed_by` = current user and `close_date` = today; when unchecked, clear both.
- **The "auto-populate companion display name" pattern** (`UpdateAssignedToNameDisp`, `UpdateCMNameDisp`, `UpdateENGReviewerNameDisp`, `UpdatePlannerNameDisp`, `UpdatePurchasingNameDisp`, `UpdateQLTYReviewerNameDisp`, `UpdateVendorDescription`, `UpdateDescriptionNextAssy`) — every `*_empnum`/code field has a matching `SelectionEvent` that looks up and writes a human-readable name into its companion column. Same proven, portable pattern for every EmpNum/Item/Vendor field in this document.
- **Notify** (`ENF_NotifyUser`) — sends an email using `assigned_username` and `priority`. Portable as-is.
- **`LaunchCosting`/`LaunchDocumentation`/`LaunchMachineTool`/`LaunchMaterial`/`LaunchProcess`** — the 5 sub-form buttons. Still out of scope for now (per `cmr-project`'s own finding that they're unrelated to CMR creation) — revisit only if/when eCMRs builds its own equivalent review sub-forms.
- **`UnlinkCmrRef` / `RefreshCMRParentProperty`** — explicitly **not carried over**. Both are receiver/parent-form-specific (unlinking a CMR from its `RS_QCCRcvrs` receiver row, refreshing a parent form that launched this one as a child). eCMRs has no receiver dependency and isn't launched as a child form, so neither applies.

## Explicitly not carried over

- **CAR cross-referencing** — dependency on `RS_QCMrrs`, out of scope per the "no dependencies" rule.
- **Any receiver reference** (`RcvrNum`, `RsCrcvr*` joins) — no column for this. eCMRs does not link back to `RS_QCCRcvrs`/`rs_crcvr`.
- **The Costing/Documentation/Tool-Machine/Material/Process sub-form Launch buttons** — see Business Logic above.
