#!/usr/bin/env python3
"""Generates ecmrs_table_columns.csv and ecmrs_ido_properties.csv from one master field list.

Kept as the single source of truth alongside generate_form.py so the table schema,
IDO property list, and form XML never drift out of sync with each other.
"""
import csv

SL_ITEMS = "STDOLE SLItems( PROPERTIES(Item, Description) )"
SL_DEPTS = "STDOLE SLDepts( PROPERTIES(Dept, Description) )"
SL_WCS = "STDOLE SLWcs( PROPERTIES(Wc, Description) )"
SL_VENDORS = "STDOLE SLVendors( PROPERTIES(VendNum, Name) )"
SL_EMPLOYEES = "STDOLE SLEmployees( PROPERTIES(EmpNum,Name,Username) DISPLAY(1,2,3) RECORDCAP(0))"

# Skip these - Application Studio auto-generates them on every new table (confirmed on ue_ecmrs):
AUTO_GENERATED_COLUMNS = {"created_by", "create_date"}

# Real Column Data Type / Label String ID values below are taken directly from the real
# legacy QC_CMRs IDO's own "Export to Excel" of its IDO Properties grid (ToExcel_IdoProperties_1.csv)
# - these are confirmed, reusable, system-wide named types, not guesses. Read Only is
# deliberately False/blank on every field here (per explicit direction: this consolidated
# form should have everything editable) - the legacy Read Only=1 flags only existed because
# those fields were read-only-by-join, which doesn't apply to our native, standalone columns.
# The exception is fields a script auto-populates (username/name lookups, close date/by),
# which stay read-only because typing over them would just get overwritten anyway.

# bind_to, property_name, data_type, length, decimal, column_data_type, label_string_id, required, readonly, description
FIELDS = [
    ("cmr_num", "CmrNum", "NumSortedString", "10", "", "", "", "", "", "CMR number, key, auto-generated via AUTONUMBER on the table. Kept as nvarchar/NumSortedString (not a true int) - both QCSeq and QCInteger came back invalid Data Types in this environment's picker, and changing the SQL column's own type hit a DF_ue_ecmrs_cmr_num default-constraint dependency error. Stored as digits in a string column, AUTONUMBER(STEP(1)) still gives sequential, unique values starting at 1 - the actual requirement - without fighting either problem."),
    ("status", "Status", "String", "40", "", "char", "sStatus", "", "", "Overall CMR status. Confirmed 7-value list: CM, Complete, Data Input, Eng Review, Planning, Purchasing, QC Approval - needs its own Property Class + Inline List set up directly in Application Studio (QCPriorityType-style reuse of a real system class was tried for Priority below and came back blank live, so don't repeat that for Status)."),
    ("workflow_status", "WorkflowStatus", "String", "40", "", "char", "", "", "", "Workflow status. Fixed value list not yet confirmed."),
    ("priority", "Priority", "String", "12", "", "", "sPriority", "", "", "Confirmed list: High, Medium, Low. Reusing the system's own QCPriorityType as Property Class came back blank in the live IDO Properties export - needs its own custom Property Class + Inline List instead, same as Status/InitialChange."),
    ("item", "Item", "String", "30", "", "ItemType", "sItem", "", "", SL_ITEMS),
    ("item_description", "ItemDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, restored to the form next to Item. Auto-populate now via DefaultFrom on Item's own component (Item(ItemDescription)), not SelectionEvent (confirmed dead - see docs/troubleshooting.md) - copied directly from the real PurchaseOrders form's TermsCode/ShipCode fields, which use this exact pattern with no SelectionEvent at all. Item as the real Property Class name is an extrapolation from that same live form, not independently confirmed for this class name - verify after import."),
    ("wc", "Wc", "String", "6", "", "WcType", "sWC", "", "", SL_WCS),
    ("wc_description", "WcDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, restored to the form next to Wc. Auto-populate now via DefaultFrom on Wc's own component (Wc(WcDescription)), not SelectionEvent (confirmed dead - see docs/troubleshooting.md) - copied directly from the real PurchaseOrders form's TermsCode/ShipCode fields, which use this exact pattern with no SelectionEvent at all. Wc as the real Property Class name is an extrapolation from that same live form, not independently confirmed for this class name - verify after import."),
    ("dept", "Dept", "String", "6", "", "DeptType", "sDepartment", "", "", SL_DEPTS),
    ("dept_description", "DeptDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, restored to the form next to Dept. Auto-populate now via DefaultFrom on Dept's own component (Dept(DeptDescription)), not SelectionEvent (confirmed dead - see docs/troubleshooting.md) - copied directly from the real PurchaseOrders form's TermsCode/ShipCode fields, which use this exact pattern with no SelectionEvent at all. Dept as the real Property Class name is an extrapolation from that same live form, not independently confirmed for this class name - verify after import."),
    ("initial_change", "InitialChange", "String", "40", "", "char", "", "", "", "Confirmed 8-value list: Documentation, Machine, Material, Other, Process, Specification, Tooling, Variance(waiver) - needs its own Property Class + Inline List set up directly in Application Studio, not via this import. Drives the Requirements cascade."),
    ("additional_changes", "AdditionalChanges", "String", "1000", "", "char", "sChanges", "", "", "Long/growing note - matches RsCrcvrChangeAll's real Length/type."),
    ("requested_action", "RequestedAction", "String", "1000", "", "QCLongCharType", "sNote", "", "", ""),
    ("general_note", "GeneralNote", "String", "1000", "", "QCLongCharType", "sNote", "", "", ""),
    ("revision", "Revision", "String", "8", "", "RevisionType", "sRevision", "", "", "Drawing Revision."),
    ("latest_revision", "LatestRevision", "String", "8", "", "RevisionType", "sRevision", "", "", ""),
    ("next_assy_item", "NextAssyItem", "String", "30", "", "ItemType", "sItem", "", "", "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(Item)') RECORDCAP(0)) - Next Level Assembly item. Case matters for the 'P(x)' cross-field reference - it's the property name Item, not the column item."),
    ("next_assy_description", "NextAssyDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, restored to the form next to NextAssyItem. Auto-populate now via DefaultFrom on NextAssyItem's own component (Item(NextAssyDescription)), not SelectionEvent (confirmed dead - see docs/troubleshooting.md) - copied directly from the real PurchaseOrders form's TermsCode/ShipCode fields, which use this exact pattern with no SelectionEvent at all. Item as the real Property Class name is an extrapolation from that same live form, not independently confirmed for this class name - verify after import."),
    ("vendor", "Vendor", "String", "15", "", "char", "", "", "", SL_VENDORS),
    ("vendor_name", "VendorName", "String", "255", "", "LongDescType", "", "", "1", "Read-only, restored to the form next to Vendor. Auto-populate now via DefaultFrom on Vendor's own component (VendNum(VendorName)), not SelectionEvent (confirmed dead - see docs/troubleshooting.md) - VendNum is the real, confirmed Property Class name for a vendor number field, taken directly from the real PurchaseOrders form's own VendNumEdit component, not a guess."),
    ("qty", "Qty", "Decimal", "", "4", "QtyUnit", "", "", "", ""),
    ("job_num", "JobNum", "String", "15", "", "char", "", "", "", "STDOLE SLMatltrans( PROPERTIES(RefNum) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() RECORDCAP(0)) - deliberately no FILTER. Confirmed real syntax straight from the legacy QC_CMRs form's own Job Num combo, which had FILTER(RefNum=FP(rs_cmrUf_ENF_CMR_JobNum)) - same self-referencing exact-match bug already fixed for po_num (FP() has no padding, real Job Numbers are zero-padded like DK00084716), same fix: drop the FILTER. See docs/troubleshooting.md. Coldtype uses char, matching po_num/vendor's pattern."),
    ("serial_num", "SerialNum", "String", "50", "", "char", "", "", "", "New field per direct request - currently these get copied into the Notes area on the legacy 3-form process, but they're common enough to need their own field on eCMRs. Created live as char, not nvarchar."),
    ("lot_num", "LotNum", "String", "50", "", "char", "", "", "", "New field per direct request - same as SerialNum, currently just copied into Notes on the legacy process. Created live as char, not nvarchar."),
    ("top_level_pn", "TopLevelPn", "String", "30", "", "char", "", "", "", "New field per direct request - the BRD's 'Top Level PN', not on the legacy form at all. Plain editable field, same treatment as SerialNum/LotNum - no confirmed combo/lookup source for this concept, just a typed part number."),
    ("sub_assembly", "SubAssembly", "String", "30", "", "char", "", "", "", "New field per direct request - the BRD's 'Sub Assembly'. Deliberately distinct from NextAssyItem (Next Level Assembly, already on the form) rather than reusing it - see docs/task-list.md's still-open note on whether the two are the same concept. Plain editable field, same treatment as SerialNum/LotNum."),
    ("po_num", "PoNum", "String", "15", "", "char", "", "", "", "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() RECORDCAP(0)) - deliberately no FILTER; a self-referencing FILTER(PoNum=FP(po_num)) was tried and dropped because FP() is a plain exact-match against real zero-padded/prefixed PO Numbers (RD00000021, INT0120033) that nobody types literally - see docs/troubleshooting.md."),
    ("po_line", "PoLine", "String", "10", "", "char", "", "", "", "STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum='P(po_num)') RECORDCAP(0))"),
    ("rfq_num", "RfqNum", "String", "15", "", "char", "", "", "", ""),
    ("eo_num", "EoNum", "String", "15", "", "char", "", "", "", ""),
    ("mdl", "Mdl", "String", "40", "", "char", "", "", "", ""),
    ("poc", "Poc", "String", "60", "", "char", "", "", "", "Point of contact, free text."),
    ("reported_by", "ReportedBy", "String", "60", "", "char", "", "", "", "New field per direct request - who requested/reported the change on the legacy Create Change Request form (distinct from CreatedBy, the system field for who created this CMR record). Plain free-text field, same treatment as SerialNum/LotNum."),
    ("req_costing", "ReqCosting", "Byte", "", "", "ListYesNoType", "", "0", "", "Cascades off InitialChange."),
    ("cost_review_complete", "CostReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("req_documentation", "ReqDocumentation", "Byte", "", "", "ListYesNoType", "", "0", "", "Cascades off InitialChange."),
    ("documentation_review_complete", "DocumentationReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("req_tool_machine", "ReqToolMachine", "Byte", "", "", "ListYesNoType", "", "0", "", "Cascades off InitialChange."),
    ("machinery_review_complete", "MachineryReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("req_process", "ReqProcess", "Byte", "", "", "ListYesNoType", "", "0", "", "Cascades off InitialChange."),
    ("process_review_complete", "ProcessReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("req_material", "ReqMaterial", "Byte", "", "", "ListYesNoType", "", "0", "", "Cascades off InitialChange."),
    ("material_review_complete", "MaterialReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("general_review_complete", "GeneralReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "1", "Read-only checkbox on the form; nothing sets it today. Unlike Closed (which got its SetCloseInfo mechanism restored), this one was never wired to anything and still is not. See docs/troubleshooting.md."),
    ("sox_impacted", "SoxImpacted", "Byte", "", "", "ListYesNoType", "sRSQCSarbanesImpact", "0", "", "Standalone, not part of the 5-category cascade."),
    ("hold_on_po", "HoldOnPo", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("auth_supplier_ship", "AuthSupplierShip", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("qc_disposition", "QcDisposition", "String", "20", "", "char", "", "", "", "Confirmed real list (from the live dropdown): Accept, Hold, NFF, NRS, Other, Reject, Rework, Scrap. Needs its own Property Class + Inline List set up directly in Application Studio."),
    ("eng_disposition", "EngDisposition", "String", "20", "", "char", "", "", "", "Confirmed real list (from the live dropdown): NFF, NRS, Other, Rework, Scrap - a subset of QcDisposition's list, missing Accept/Hold/Reject. Needs its own Property Class + Inline List set up directly in Application Studio."),
    ("reason_code", "ReasonCode", "String", "40", "", "char", "", "", "", "Combo's form component references the real, existing QCReasonCode system Property Class directly (same class the live QC_MRRs form's own Reason combo uses) - per direct request: \"we can use this list that exists right now\", may get its own separate CMR-specific list later. Property Class stays blank here at the IDO-property level (component-level override instead, see generate_form.py) - no Inline List needed on this property. See docs/troubleshooting.md."),
    ("cause_code", "CauseCode", "String", "40", "", "char", "", "", "", "Same as ReasonCode, referencing the real QCCauseCode system Property Class (matches QC_MRRs' own Cause combo) instead of an Inline List of our own. See docs/troubleshooting.md."),
    ("assigned_empnum", "AssignedEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Restored to the form as a plain writable ID field next to Assigned (Username) - the combo binds to AssignedUsername, not this. No confirmed live mechanism keeps this in sync with the selected employee automatically; verify after import whether it needs to be typed manually. See docs/troubleshooting.md."),
    ("assigned_username", "AssignedUsername", "String", "128", "", "UsernameType", "sUserName", "", "", "Directly writable - the Assigned combo binds here now (commit e2fc29d), not to AssignedEmpNum. Was originally designed as an auto-populated read-only companion field; that's no longer this property's role, so Read Only must not be set - it still was here, likely causing a write-rejection lock when selecting Assigned live."),
    ("assigned_buyer", "AssignedBuyer", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("qc_reviewer_empnum", "QcReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Restored to the form as a plain writable ID field next to the Reviewer combo - the combo binds to QcReviewerUsername, not this. No confirmed live mechanism keeps this in sync automatically; verify after import. See docs/troubleshooting.md."),
    ("qc_reviewer_username", "QcReviewerUsername", "String", "128", "", "UsernameType", "sUserName", "", "", "Directly writable - the Reviewer combo binds here now, same pattern as AssignedUsername. No longer a read-only auto-populated companion field."),
    ("eng_reviewer_empnum", "EngReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Restored to the form as a plain writable ID field next to the Reviewer combo - the combo binds to EngReviewerUsername, not this. No confirmed live mechanism keeps this in sync automatically; verify after import. See docs/troubleshooting.md."),
    ("eng_reviewer_username", "EngReviewerUsername", "String", "128", "", "UsernameType", "sUserName", "", "", "Directly writable - the Reviewer combo binds here now, same pattern as AssignedUsername. No longer a read-only auto-populated companion field."),
    ("planning_reviewer_empnum", "PlanningReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Restored to the form as a plain writable ID field next to the Reviewer combo - the combo binds to PlanningReviewerName, not this. No confirmed live mechanism keeps this in sync automatically; verify after import. See docs/troubleshooting.md."),
    ("planning_reviewer_name", "PlanningReviewerName", "String", "255", "", "LongDescType", "", "", "", "Repurposed to hold the reviewer's Username, not their full Name, despite the property's own name - the Reviewer combo binds here directly (same pattern as AssignedUsername), no longer a read-only auto-populated companion field. Kept the existing property rather than creating/renaming one in Application Studio."),
    ("planning_complete", "PlanningComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("purchasing_reviewer_empnum", "PurchasingReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Restored to the form as a plain writable ID field next to the Reviewer combo - the combo binds to PurchasingReviewerName, not this. No confirmed live mechanism keeps this in sync automatically; verify after import. See docs/troubleshooting.md."),
    ("purchasing_reviewer_name", "PurchasingReviewerName", "String", "255", "", "LongDescType", "", "", "", "Repurposed to hold the reviewer's Username, same as PlanningReviewerName above - see that entry's note."),
    ("purchasing_complete", "PurchasingComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("cm_reviewer_empnum", "CmReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Restored to the form as a plain writable ID field next to the Reviewer combo - the combo binds to CmReviewerName, not this. No confirmed live mechanism keeps this in sync automatically; verify after import. See docs/troubleshooting.md."),
    ("cm_reviewer_name", "CmReviewerName", "String", "255", "", "LongDescType", "", "", "", "Repurposed to hold the reviewer's Username, same as PlanningReviewerName above - see that entry's note."),
    ("cm_complete", "CmComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("due_date", "DueDate", "Date", "", "", "DateType", "sDate", "", "", ""),
    ("internal_review_date", "InternalReviewDate", "Date", "", "", "DateType", "sDate", "", "", ""),
    ("close_date", "CloseDate", "Date", "", "", "DateType", "sDate", "", "1", "Read-only; auto-set by the Closed checkbox's SetCloseInfo EventHandler in the Implementation section (checked -> today's date, unchecked -> cleared). Not user-typed."),
    ("closed_by", "ClosedBy", "String", "128", "", "UsernameType", "sRSQCClosedBy", "", "1", "Read-only; auto-set by the Closed checkbox's SetCloseInfo EventHandler in the Implementation section (checked -> current username, unchecked -> cleared). Not user-typed."),
    ("general_close_date", "GeneralCloseDate", "Date", "", "", "DateType", "sDate", "", "", "Purpose unclear vs. CloseDate - confirm before relying on it."),
    ("general_closed_by", "GeneralClosedBy", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Same caveat as GeneralCloseDate."),
    ("qc_rca_notes", "QcRcaNotes", "String", "1000", "", "QCLongCharType", "sNote", "", "", "Root cause analysis notes, QC."),
    ("eng_rca_notes", "EngRcaNotes", "String", "1000", "", "QCLongCharType", "sNote", "", "", "Root cause analysis notes, Engineering."),
    ("closed", "Closed", "Byte", "", "", "ListYesNoType", "sClosed", "0", "", "Plain checkbox in the Implementation section, manually checked by the user - not gated by the ReqX/XReviewComplete flags (no such gating is implemented). Checking it fires SetCloseInfo, which auto-sets CloseDate/ClosedBy; unchecking it clears both. Drives the form's ORDERBY (open CMRs sort first)."),
]

# Columns still in the schema/IDO but not bound to any component on the current form -
# tracked here (not silently dropped) so a future contributor doesn't mistake "not on the
# form" for "not real" and doesn't have to re-derive why each one is dead. None of these are
# removed from FIELDS itself: the live SQL columns/IDO properties already exist from earlier
# imports, and dropping a live column/property is a separate, destructive action (needs an
# explicit decision, not a schema-generator side effect). Each entry's description below gets
# an "[ORPHANED - ...]" prefix at generation time so every export (table columns, IDO
# properties, deploy checklist) says so consistently instead of drifting.
ORPHANED_COLUMNS = {
    # assigned_empnum/qc_reviewer_empnum/eng_reviewer_empnum/planning_reviewer_empnum/
    # purchasing_reviewer_empnum/cm_reviewer_empnum and item_description/wc_description/
    # dept_description/next_assy_description/vendor_name were here (combos write Username
    # directly / SelectionEvent removed) - restored to the form per direct request, see their
    # LAYOUT entries in generate_form.py and docs/troubleshooting.md.
    "cost_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "documentation_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "machinery_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "process_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "material_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "additional_changes": "not placed on the current form layout",
    "workflow_status": "not placed on the current form layout; its fixed value list was never confirmed either",
    "general_close_date": "not placed on the current form layout; purpose still unclear vs. CloseDate",
    "general_closed_by": "not placed on the current form layout; same caveat as GeneralCloseDate",
}

_field_cols = {f[0] for f in FIELDS}
assert ORPHANED_COLUMNS.keys() <= _field_cols, \
    f"ORPHANED_COLUMNS references unknown column(s): {ORPHANED_COLUMNS.keys() - _field_cols}"

FIELDS = [
    f if f[0] not in ORPHANED_COLUMNS
    else (*f[:9], f"[ORPHANED - not bound to any form control: {ORPHANED_COLUMNS[f[0]]}] {f[9]}".rstrip())
    for f in FIELDS
]

TABLE_HEADER = ["Column Name", "Data Type", "Length", "Decimal Places", "Nullable", "Primary Key", "Default Value", "Description"]
IDO_HEADER = ["Bind To", "Property Name", "Property Class", "Data Type", "Length", "Decimal",
              "Column Data Type", "Label String ID", "Required", "Read Only", "Description"]

# Column Data Type defaults to blank - confirmed directly against the live
# ToExcel_IdoProperties_3 export (docs/reference/): every one of the 69 custom eCMRs
# properties (Status, Item, Vendor, JobNum, ...) has a blank Column Data Type. It's only
# ever populated on the 7 system-generated properties (UsernameType, CurrentDateType, ...),
# which these CSVs deliberately exclude. The earlier JobBase guess for job_num is disproven
# by the same live export - its real property is blank too. Kept as an empty dict (not
# removed outright) in case a genuine future exception is confirmed the same way.
COLDTYPE_OVERRIDES = {}

# Properties that were originally read-only auto-populated companion fields and were later
# repurposed to be a combo's primary, directly-writable binding (the Username pattern - see
# docs/troubleshooting.md Rule #1B). Every one of these needs its live Read Only flag manually
# unchecked in Application Studio's IDO Properties grid - Form Sync re-import never touches an
# existing property's Read Only setting. Tracked here (not just in commit messages) so
# generate_deploy_checklist.py can't miss one on the next field that gets this same treatment.
REPURPOSED_WRITABLE = {
    "assigned_username": "Combo binds here directly (Username-first list source) - was a read-only companion.",
    "qc_reviewer_username": "Combo binds here directly (Username-first list source) - was a read-only companion.",
    "eng_reviewer_username": "Combo binds here directly (Username-first list source) - was a read-only companion.",
    "planning_reviewer_name": "Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.",
    "purchasing_reviewer_name": "Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.",
    "cm_reviewer_name": "Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.",
}

def main():
    with open("exports/ecmrs_table_columns.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(TABLE_HEADER)
        for (col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc) in FIELDS:
            table_type = ("int" if dtype in ("Integer", "Long Integer") else
                          ("Bit" if dtype == "Byte" else
                           ("String" if dtype == "NumSortedString" else dtype)))
            pk = "Y" if col == "cmr_num" else "N"
            nullable = "No" if col == "cmr_num" else "Yes"
            default = "AUTONUMBER(STEP(1))" if col == "cmr_num" else ""
            w.writerow([col, table_type, length, decimal, nullable, pk, default, desc])

    with open("exports/ecmrs_ido_properties.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(IDO_HEADER)
        for (col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc) in FIELDS:
            col_data_type = COLDTYPE_OVERRIDES.get(col, "")
            w.writerow([col, pname, "", dtype, length, decimal, col_data_type, labelid, required, readonly, desc])

    print(f"Wrote {len(FIELDS)} rows to each CSV. CreatedBy/CreateDate deliberately excluded - "
          f"already auto-generated by Application Studio on the new table.")

if __name__ == "__main__":
    main()
