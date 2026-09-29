# eCMRs — Field status

Status of every field on the form as of **2026-09-29**, after form v2 was imported on **TRN** and
tested end to end (screenshots and the TRN exports in [`reference/`](reference/):
`ToExcel_IdoProperties_2026-09-29d.csv`, `ToExcel_SqlColumns_2026-09-29d.csv`).
`[x]` = confirmed working on TRN. `[ ]` = something still open. Grouped by form section, in form
order. The field-by-field comparison with the original forms is in
[`field-review.md`](field-review.md); how each problem was solved is in
[`troubleshooting.md`](troubleshooting.md).

Production has not been done yet - see "Production" at the end.

## Top rows

- [x] **Status** — Inline List (CM, Complete, Data Input, Eng Review, Planning, Purchasing, QC
  Approval). Optional tidy-up: its IDO Length is blank; 255 would match its `char(255)` column
  ([`length-fixes.md`](length-fixes.md)). Works as is.
- [x] **Assigned** (`AssignedEmpNum` combo → `AssignedUsername`) — picking the ID fills the name
  (e.g. 3 → Arguelles, Paul G.).
- [x] **Notify** button — shows a message only; sends nothing (see "Open decisions").
- [x] **CMR Num** (`CmrNum`) — set on **New** to `CMR-YYMMDD-HHMMSS` by the form
  (`StdObjectNewCompleted`). IDO: String, length 255, no Default Value. Replaced
  `AUTONUMBER(STEP(1))`, which repeated numbers (PK_ue_ecmrs save error).
- [x] **Create Date**, **Created By** — system fields.
- [x] **PO Num**, **PO Line** — PO Line stores the line number (`DISPLAY(1,2,3)`); earlier it stored
  the Item and saves failed.
- [x] **Assigned Buyer**, **Qty**, **POC**, **RFQ Num**, **Job Num**, **Drawing Revision**,
  **Latest Revision**, **Requested Action**.
- [x] **Item** → **Item Desc**, **Next Lvl Assy** → **Next Assy Desc**, **Vendor** → **Vendor Name**
  — descriptions fill when the code is picked.
- [x] **Priority** — Inline List High/Medium/Low.
- [ ] **PO Num** list has no record cap: it lists every PO line. Fine now; may get slow as POs grow.

## Change Request Fields

- [x] **Dept** → **Dept Description**, **Work Center** → **WC Description** — filled by the
  `SetPropertyFromList(..., Description)` validators (e.g. 100 → Operations, BRAZE → Brazing).
- [x] **Reported By**, **Due Date**, **General Note**.
- [x] **Initial Change** → the 5 **Req** checkboxes — the cascade ticks the right boxes (e.g.
  Machine / Variance(waiver) → Costing, Documentation, Tool/Machine, Process).

## Additional Fields

- [x] **Serial #** — lists the selected Item's serial numbers (empty for items with none, e.g.
  lot-tracked items).
- [x] **LOT #** — lists the selected Item's lots.
- [x] **Top Level PN**, **Sub Assembly**.
- [ ] Open question: is **Sub Assembly** the same thing as **Next Lvl Assy**? If so, drop one.

## Quality

- [x] **SOX Impacted**, **Hold On PO**, **Authorization For Supplier To Ship**.
- [x] **Reason Code**, **Cause Code** — own Inline Lists with the QC_MRRs codes (13 each). Adding a
  code in QCS later means adding it to the Inline List too.
- [x] **QC Disposition**, **Reviewer ID** → **Reviewer**, **QC RCA Notes**.

## Engineering

- [x] **EO Num**, **MDL**, **Engineering Disposition**, **Reviewer ID** → **Reviewer**,
  **Eng RCA Notes**.
- [x] **Internal Review Date** — in Engineering, as on the original form.

## Implementation

- [x] **Planning**, **Purchasing**, **CM** rows — checkbox, **Reviewer ID** → **Reviewer**.
- [x] **Closed** → **Close Date** (today) and **Closed By** (your user) — `SetCloseInfo` +
  `SetClosedBy`, the original form's pattern.

## Not on the form (kept in the table on purpose)

- `workflow_status`, `additional_changes`, the five `*_review_complete` flags,
  `general_review_complete`, `general_close_date`, `general_closed_by` — see `ORPHANED_COLUMNS` in
  `scripts/generate_schema_csv.py`. `workflow_status` is `char(255)` in SQL but 40 on the IDO;
  harmless while it's off the form.
- `ue_reported_by` — a stray SQL column (duplicate of `reported_by`), no IDO property. Remove it
  only if nothing uses it.

## Open decisions

- [ ] Notify: build a real notification (email to Engineering?) or remove the button.
- [ ] Reported By: free text now; the original was an employee lookup.
- [ ] Assigned Buyer: stores the employee number; the original stored the username.
- [ ] Rollout: does eCMRs replace the `cmr-project` consolidated form and the legacy screens
  (Create Change Request, Change Request Management, QC_CMRs)? Historical data migration from
  `rs_cmr`/`rs_crcvr`: when.
- [x] Help: right-click → Help opens Infor's QC CMRs topic (SyteLine only allows Infor's help site
  there). eCMRs' own help pages are in `docs/help/` as a reference (e.g. copied to the S: drive).
- [ ] CAR cross-referencing (`LaunchCAR`): out of scope for this build.

## Production

- [ ] Go live in production: [`Implementation-Plan.md`](Implementation-Plan.md) section 5 (22 steps:
  table and IDO from [`../exports/production/`](../exports/production/), `--verify` against TRN,
  FormSync import of [`../exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML), smoke test, record it).
