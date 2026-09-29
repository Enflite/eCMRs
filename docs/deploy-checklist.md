# eCMRs — Deploy Checklist

**All done on TRN and confirmed working, 2026-09-29** (TRN exports in `reference/`). Use this list for production.

Generated from the schema by `scripts/generate_deploy_checklist.py` - re-run it
after adding a field to either tracking dict below, don't hand-edit this file.
See `docs/troubleshooting.md` for why each category exists.

**After every item below**: editing a property in the IDO Properties grid does
not persist by itself - the IDO itself must be Check In'd (IDOs tab -> find the
IDO -> Check In) before the change takes effect, even with no source control
configured (a "Source control integration is currently disabled" popup is
harmless - click OK, the local check-in still applies). Skipping this produced a
real "Missing property data type" error on form save. See
`docs/troubleshooting.md`.

## CMR Num key

- [ ] `CmrNum` (cmr_num): **Data Type** `String`, **Length** 255, **Default Value** blank (no `AUTONUMBER`). The form sets it to `CMR-YYMMDD-HHMMSS` on **New**. See `docs/troubleshooting.md` (PK_ue_ecmrs).

## Lengths and Property Class

- [ ] Every IDO property's **Length** equals its SQL column's (`docs/length-fixes.md` lists any difference - run `scripts/compare_live_lengths.py` on fresh exports).
- [ ] `ReasonCode`, `CauseCode`: **Property Class** blank (the QC_MRRs classes cause the `'FP'` error).

## Read Only must be manually unchecked

These are filled automatically by the form, which can't write a Read Only property. Form Sync re-import never touches an existing property's Read Only flag.

- [ ] `AssignedUsername` (assigned_username) - Filled from Assigned ID (DefaultFrom EmpNum(AssignedUsername)).
- [ ] `QcReviewerUsername` (qc_reviewer_username) - Filled from QC Reviewer ID (DefaultFrom EmpNum(QcReviewerUsername)).
- [ ] `EngReviewerUsername` (eng_reviewer_username) - Filled from Eng Reviewer ID (DefaultFrom EmpNum(EngReviewerUsername)).
- [ ] `PlanningReviewerName` (planning_reviewer_name) - Filled from Planning Reviewer ID (DefaultFrom EmpNum(PlanningReviewerName)).
- [ ] `PurchasingReviewerName` (purchasing_reviewer_name) - Filled from Purchasing Reviewer ID (DefaultFrom EmpNum(PurchasingReviewerName)).
- [ ] `CmReviewerName` (cm_reviewer_name) - Filled from CM Reviewer ID (DefaultFrom EmpNum(CmReviewerName)).
- [ ] `DeptDescription` (dept_description) - Filled from Dept (Validators SetPropertyFromList(DeptDescription, Description)).
- [ ] `WcDescription` (wc_description) - Filled from Work Center (Validators SetPropertyFromList(WcDescription, Description)).
- [ ] `ItemDescription` (item_description) - Filled from Item (DefaultFrom Item(ItemDescription)).
- [ ] `VendorName` (vendor_name) - Filled from Vendor (DefaultFrom VendNum(VendorName)).
- [ ] `NextAssyDescription` (next_assy_description) - Filled from Next Lvl Assy (DefaultFrom Item(NextAssyDescription)).
- [ ] `CloseDate` (close_date) - Set by the Closed checkbox script (SetCloseInfo).
- [ ] `ClosedBy` (closed_by) - Set by the Closed checkbox script (SetClosedBy: SETPROPVALUES(ClosedBy=USERNAME())).

## Inline List must be manually configured

Cannot be pushed via CSV/Form Sync import at all - set the property's own
`*Inline List` field directly to the `ENTRIES(...)` value below. `Property
Class` stays blank - there is no separate class to create in this
environment (confirmed live on Status; see docs/troubleshooting.md).

- [ ] `Status` - Inline List: `ENTRIES(CM,Complete,Data Input,Eng Review,Planning,Purchasing,QC Approval)`
- [ ] `Priority` - Inline List: `ENTRIES(High,Medium,Low)`
- [ ] `InitialChange` - Inline List: `ENTRIES(Documentation,Machine,Material,Other,Process,Specification,Tooling,Variance(waiver))`
- [ ] `QcDisposition` - Inline List: `ENTRIES(Accept,Hold,NFF,NRS,Other,Reject,Rework,Scrap)`
- [ ] `EngDisposition` - Inline List: `ENTRIES(NFF,NRS,Other,Rework,Scrap)`
- [ ] `ReasonCode` - Inline List: `ENTRIES(ASMBL,DAMAGED,DELIVERY,DOCUMENT,FEATURE,FUNCTION,INTERNAL,MATERIAL,MEASURE,PURCHASE,REVISION,SUPDAM,VISUAL)`
- [ ] `CauseCode` - Inline List: `ENTRIES(ENF,ENG,EXC,FUNC,HANDLE,NFF,QCM,SHIP,SHORTAGE,SUP,TOOL,UNK,VOID)`

