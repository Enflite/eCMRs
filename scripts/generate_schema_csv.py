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
    ("item_description", "ItemDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, auto-populated by lookup."),
    ("wc", "Wc", "String", "6", "", "WcType", "sWC", "", "", SL_WCS),
    ("wc_description", "WcDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, auto-populated by lookup."),
    ("dept", "Dept", "String", "6", "", "DeptType", "sDepartment", "", "", SL_DEPTS),
    ("dept_description", "DeptDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, auto-populated by lookup."),
    ("initial_change", "InitialChange", "String", "40", "", "char", "", "", "", "Confirmed 8-value list: Documentation, Machine, Material, Other, Process, Specification, Tooling, Variance(waiver) - needs its own Property Class + Inline List set up directly in Application Studio, not via this import. Drives the Requirements cascade."),
    ("additional_changes", "AdditionalChanges", "String", "1000", "", "char", "sChanges", "", "", "Long/growing note - matches RsCrcvrChangeAll's real Length/type."),
    ("requested_action", "RequestedAction", "String", "1000", "", "QCLongCharType", "sNote", "", "", ""),
    ("general_note", "GeneralNote", "String", "1000", "", "QCLongCharType", "sNote", "", "", ""),
    ("revision", "Revision", "String", "8", "", "RevisionType", "sRevision", "", "", "Drawing Revision."),
    ("latest_revision", "LatestRevision", "String", "8", "", "RevisionType", "sRevision", "", "", ""),
    ("next_assy_item", "NextAssyItem", "String", "30", "", "ItemType", "sItem", "", "", "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(Item)') RECORDCAP(0)) - Next Level Assembly item. Case matters for the 'P(x)' cross-field reference - it's the property name Item, not the column item."),
    ("next_assy_description", "NextAssyDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, auto-populated by lookup."),
    ("vendor", "Vendor", "String", "15", "", "char", "", "", "", SL_VENDORS),
    ("vendor_name", "VendorName", "String", "255", "", "LongDescType", "", "", "1", "Read-only, auto-populated by lookup."),
    ("qty", "Qty", "Decimal", "", "4", "QtyUnit", "", "", "", ""),
    ("job_num", "JobNum", "String", "15", "", "JobBase", "", "", "", "Mimics the real JobOrders form's own Job field exactly: plain Edit (not a filtered combo), validated via MaintainFromSpec: JobOrders( PROPERTY(Job) ) in the form XML - avoids the SLMatltrans leading-zero exact-match bug entirely instead of working around it. Column Data Type tries the real confirmed JobBase class; if rejected like QCSeq/QCInteger were, fall back to String."),
    ("serial_num", "SerialNum", "String", "50", "", "char", "", "", "", "New field per direct request - currently these get copied into the Notes area on the legacy 3-form process, but they're common enough to need their own field on eCMRs. Created live as char, not nvarchar."),
    ("lot_num", "LotNum", "String", "50", "", "char", "", "", "", "New field per direct request - same as SerialNum, currently just copied into Notes on the legacy process. Created live as char, not nvarchar."),
    ("po_num", "PoNum", "String", "15", "", "char", "", "", "", "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() RECORDCAP(0)) - deliberately no FILTER; a self-referencing FILTER(PoNum=FP(po_num)) was tried and dropped because FP() is a plain exact-match against real zero-padded/prefixed PO Numbers (RD00000021, INT0120033) that nobody types literally - see docs/troubleshooting.md."),
    ("po_line", "PoLine", "String", "10", "", "char", "", "", "", "STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum='P(po_num)') RECORDCAP(0))"),
    ("rfq_num", "RfqNum", "String", "15", "", "char", "", "", "", ""),
    ("eo_num", "EoNum", "String", "15", "", "char", "", "", "", ""),
    ("mdl", "Mdl", "String", "40", "", "char", "", "", "", ""),
    ("poc", "Poc", "String", "60", "", "char", "", "", "", "Point of contact, free text."),
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
    ("general_review_complete", "GeneralReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "1", "Read-only checkbox on the form; nothing sets it today - part of the close workflow that no longer exists since the Closed checkbox was removed. See docs/troubleshooting.md."),
    ("sox_impacted", "SoxImpacted", "Byte", "", "", "ListYesNoType", "sRSQCSarbanesImpact", "0", "", "Standalone, not part of the 5-category cascade."),
    ("hold_on_po", "HoldOnPo", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("auth_supplier_ship", "AuthSupplierShip", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("qc_disposition", "QcDisposition", "String", "20", "", "char", "", "", "", "Confirmed real list (from the live dropdown): Accept, Hold, NFF, NRS, Other, Reject, Rework, Scrap. Needs its own Property Class + Inline List set up directly in Application Studio."),
    ("eng_disposition", "EngDisposition", "String", "20", "", "char", "", "", "", "Confirmed real list (from the live dropdown): NFF, NRS, Other, Rework, Scrap - a subset of QcDisposition's list, missing Accept/Hold/Reject. Needs its own Property Class + Inline List set up directly in Application Studio."),
    ("assigned_empnum", "AssignedEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("assigned_username", "AssignedUsername", "String", "128", "", "UsernameType", "sUserName", "", "", "Directly writable - the Assigned combo binds here now (commit e2fc29d), not to AssignedEmpNum. Was originally designed as an auto-populated read-only companion field; that's no longer this property's role, so Read Only must not be set - it still was here, likely causing a write-rejection lock when selecting Assigned live."),
    ("assigned_buyer", "AssignedBuyer", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("qc_reviewer_empnum", "QcReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("qc_reviewer_username", "QcReviewerUsername", "String", "128", "", "UsernameType", "sUserName", "", "", "Directly writable - the Reviewer combo binds here now, same pattern as AssignedUsername. No longer a read-only auto-populated companion field."),
    ("eng_reviewer_empnum", "EngReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("eng_reviewer_username", "EngReviewerUsername", "String", "128", "", "UsernameType", "sUserName", "", "", "Directly writable - the Reviewer combo binds here now, same pattern as AssignedUsername. No longer a read-only auto-populated companion field."),
    ("planning_reviewer_empnum", "PlanningReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("planning_reviewer_name", "PlanningReviewerName", "String", "255", "", "LongDescType", "", "", "", "Repurposed to hold the reviewer's Username, not their full Name, despite the property's own name - the Reviewer combo binds here directly (same pattern as AssignedUsername), no longer a read-only auto-populated companion field. Kept the existing property rather than creating/renaming one in Application Studio."),
    ("planning_complete", "PlanningComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("purchasing_reviewer_empnum", "PurchasingReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("purchasing_reviewer_name", "PurchasingReviewerName", "String", "255", "", "LongDescType", "", "", "", "Repurposed to hold the reviewer's Username, same as PlanningReviewerName above - see that entry's note."),
    ("purchasing_complete", "PurchasingComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("cm_reviewer_empnum", "CmReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("cm_reviewer_name", "CmReviewerName", "String", "255", "", "LongDescType", "", "", "", "Repurposed to hold the reviewer's Username, same as PlanningReviewerName above - see that entry's note."),
    ("cm_complete", "CmComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("due_date", "DueDate", "Date", "", "", "DateType", "sDate", "", "", ""),
    ("internal_review_date", "InternalReviewDate", "Date", "", "", "DateType", "sDate", "", "", ""),
    ("close_date", "CloseDate", "Date", "", "", "DateType", "sDate", "", "1", "Read-only; was meant to be auto-set by a Closed workflow, but that workflow (and the Closed checkbox that drove it) was removed - nothing sets this today. Restore a close mechanism or drop this column; see docs/troubleshooting.md."),
    ("closed_by", "ClosedBy", "String", "128", "", "UsernameType", "sRSQCClosedBy", "", "1", "Read-only; same gap as CloseDate - was meant to be auto-set by the removed Closed workflow, nothing sets it today. See docs/troubleshooting.md."),
    ("general_close_date", "GeneralCloseDate", "Date", "", "", "DateType", "sDate", "", "", "Purpose unclear vs. CloseDate - confirm before relying on it."),
    ("general_closed_by", "GeneralClosedBy", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Same caveat as GeneralCloseDate."),
    ("qc_rca_notes", "QcRcaNotes", "String", "1000", "", "QCLongCharType", "sNote", "", "", "Root cause analysis notes, QC."),
    ("eng_rca_notes", "EngRcaNotes", "String", "1000", "", "QCLongCharType", "sNote", "", "", "Root cause analysis notes, Engineering."),
    ("closed", "Closed", "Byte", "", "", "ListYesNoType", "sClosed", "0", "", "Was meant to be enabled by every ReqX/XReviewComplete pair matching, driven by the Closed checkbox's workflow - that checkbox and its handler were removed (see docs/troubleshooting.md), so this is permanently 0 today. The form's ORDERBY no longer sorts on it as a result. Restore a close mechanism or drop this column."),
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
    "assigned_empnum": "the Assigned combo now writes AssignedUsername directly",
    "qc_reviewer_empnum": "the Reviewer combo now writes QcReviewerUsername directly",
    "eng_reviewer_empnum": "the Reviewer combo now writes EngReviewerUsername directly",
    "planning_reviewer_empnum": "the Reviewer combo now writes PlanningReviewerName directly",
    "purchasing_reviewer_empnum": "the Reviewer combo now writes PurchasingReviewerName directly",
    "cm_reviewer_empnum": "the Reviewer combo now writes CmReviewerName directly",
    "item_description": "the SelectionEvent auto-populate mechanism that filled it was removed project-wide - see docs/troubleshooting.md",
    "wc_description": "the SelectionEvent auto-populate mechanism that filled it was removed project-wide - see docs/troubleshooting.md",
    "dept_description": "the SelectionEvent auto-populate mechanism that filled it was removed project-wide - see docs/troubleshooting.md",
    "next_assy_description": "the SelectionEvent auto-populate mechanism that filled it was removed project-wide - see docs/troubleshooting.md",
    "vendor_name": "the SelectionEvent auto-populate mechanism that filled it was removed project-wide - see docs/troubleshooting.md",
    "cost_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "documentation_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "machinery_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "process_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "material_review_complete": "no cascade UI was ever built for it - no control on the form sets this flag",
    "additional_changes": "not placed on the current form layout",
    "general_note": "not placed on the current form layout",
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
