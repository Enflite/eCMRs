# eCMRs — Build Guide

Two separate mechanisms, don't conflate them:

1. **The table + IDO cannot be imported.** Form Sync only creates/updates **forms** — it has no mechanism for defining a new SQL table or an IDO's property list. This part has to be done by hand in Application Studio, once, following the steps below.
2. **The form CAN be imported via Form Sync**, once the IDO exists. `exports/eCMRs_v1.XML` (see below) is a complete, ready-to-import Form Sync export — the same mechanism used throughout `cmr-project` all session. Import order matters: table/IDO first, form second, because the form's XML binds every field by the exact property names chosen in step 1.

## Step 1 — Create the table + IDO (manual, Application Studio)

1. Under project `ue_ENF` (or wherever you want this to live), create a **new table** — suggested name `ue_ecmr`. Give it every column listed in the table below (name, type, length).
2. Create a **new IDO** on top of it — suggested name `ue_ecmrs`. Set **Primary Base Table** to `ue_ecmr`.
3. Add a **Property** per column (`New Property` → `Bind To` the column). Set `cmr_num` as the key (`KeySequence: 1`).
4. Set `cmr_num`'s `Default Value` to `AUTONUMBER(STEP(1))` (or your preferred numbering step) — this is what makes native **New** work with zero extra scripting, unlike `RS_QCCmrs`'s composite-key trap in `cmr-project`.
5. **Check In.**

### Full column list

Every property below matches `docs/field-mapping.md` exactly — the Form Sync XML in Step 2 assumes these exact names. If you rename anything here, you must rename it to match in the XML before importing (or tell me the new names and I'll regenerate the XML).

| Column | Type | Length/notes |
|---|---|---|
| `cmr_num` | Integer, Autonumber | **Key.** |
| `status` | String | 20 |
| `workflow_status` | String | 30 |
| `create_date` | DateTime | Default `NOW()` |
| `created_by` | String | 30 |
| `priority` | String | 10 |
| `item` | String | 30 |
| `item_description` | String | 60 |
| `wc` | String | 10 |
| `wc_description` | String | 60 |
| `dept` | String | 10 |
| `dept_description` | String | 60 |
| `initial_change` | String | 20 |
| `additional_changes` | Text (long) | |
| `requested_action` | Text (long) | |
| `general_note` | Text (long) | |
| `revision` | String | 10 |
| `latest_revision` | String | 10 |
| `next_assy_item` | String | 30 |
| `next_assy_description` | String | 60 |
| `vendor` | String | 15 |
| `vendor_name` | String | 60 |
| `qty` | Decimal | |
| `job_num` | String | 15 |
| `po_num` | String | 15 |
| `po_line` | String | 10 |
| `rfq_num` | String | 15 |
| `eo_num` | String | 15 |
| `mdl` | String | 40 |
| `poc` | String | 60 |
| `req_costing` / `cost_review_complete` | Boolean / Boolean | |
| `req_documentation` / `documentation_review_complete` | Boolean / Boolean | |
| `req_tool_machine` / `machinery_review_complete` | Boolean / Boolean | |
| `req_process` / `process_review_complete` | Boolean / Boolean | |
| `req_material` / `material_review_complete` | Boolean / Boolean | |
| `general_review_complete` | Boolean | |
| `sox_impacted` | Boolean | |
| `hold_on_po` | Boolean | |
| `auth_supplier_ship` | Boolean | |
| `qc_disposition` | String | 20 |
| `eng_disposition` | String | 20 |
| `assigned_empnum` | String | 10 |
| `assigned_username` | String | 30 |
| `assigned_buyer` | String | 30 |
| `qc_reviewer_empnum` / `qc_reviewer_username` | String / String | 10 / 30 |
| `eng_reviewer_empnum` / `eng_reviewer_username` | String / String | 10 / 30 |
| `planning_reviewer_empnum` / `planning_reviewer_name` | String / String | 10 / 60 |
| `planning_complete` | Boolean | |
| `purchasing_reviewer_empnum` / `purchasing_reviewer_name` | String / String | 10 / 60 |
| `purchasing_complete` | Boolean | |
| `cm_reviewer_empnum` / `cm_reviewer_name` | String / String | 10 / 60 |
| `cm_complete` | Boolean | |
| `due_date` | Date | |
| `internal_review_date` | Date | |
| `close_date` | Date | |
| `closed_by` | String | 30 |
| `general_close_date` | Date | |
| `general_closed_by` | String | 30 |
| `qc_rca_notes` | Text (long) | |
| `eng_rca_notes` | Text (long) | |
| `closed` | Boolean | |

**Costing detail lines are deliberately left out of v1** — see `field-mapping.md`'s open question on the one-to-many Costing grid. Add a `estimated_cost` single decimal column instead if you want a placeholder now.

### Fields needing a real fixed value list (Property Class + Inline List)

These need a Property Class with an Inline List defined in Application Studio — Form Sync can't create one from scratch, only reference an existing `PropertyClassName`. Confirmed real values are listed; the rest need a decision before Step 1 is fully done (the form will still import and work with a plain free-text box in the meantime — just without dropdown validation):

- `initial_change`: **confirmed** — `Documentation`, `Machine`, `Material`, `Other`, `Process`, `Specification`, `Tooling`, `Variance(waiver)`.
- `priority`: likely `High`/`Medium`/`Low` (matches `RS_QCPriority` on the legacy system) — confirm.
- `status`, `workflow_status`, `qc_disposition`, `eng_disposition`: **not yet confirmed** — these were driven by legacy system lookups (`QCStatusListings()`, `UserDefinedType(Cmr_CMR_WorkFlowStatus)`, etc.) that don't carry over. Needs real values decided before building real dropdowns; free-text in the meantime.

## Step 2 — Import the form via Form Sync

Once Step 1 is checked in, import `exports/eCMRs_v1.XML` through Form Sync as usual. It's bound entirely to `object.<property>` on `ue_ecmrs`'s primary collection — no secondary collections, no Variables, no read/write bridge scripts, because every field is a **native, directly-writable property** on this standalone IDO. That's the real payoff of not extending `RS_QCCmrs`: none of `cmr-project`'s Variable+script workaround pattern is needed here.

**If any property name in Step 1 doesn't match `field-mapping.md`/the XML exactly**, the import will fail to bind those fields — reconcile names first, or tell me what you actually named things and I'll regenerate the XML.
