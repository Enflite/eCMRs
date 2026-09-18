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

# Skip these - Application Studio auto-generates them on every new table (confirmed on ue_ecmr):
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
    ("next_assy_item", "NextAssyItem", "String", "30", "", "ItemType", "sItem", "", "", "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(item)') RECORDCAP(0)) - Next Level Assembly item."),
    ("next_assy_description", "NextAssyDescription", "String", "40", "", "DescriptionType", "sDescription", "", "1", "Read-only, auto-populated by lookup."),
    ("vendor", "Vendor", "String", "15", "", "char", "", "", "", SL_VENDORS),
    ("vendor_name", "VendorName", "String", "255", "", "LongDescType", "", "", "1", "Read-only, auto-populated by lookup."),
    ("qty", "Qty", "Decimal", "", "4", "QtyUnit", "", "", "", ""),
    ("job_num", "JobNum", "String", "15", "", "JobBase", "", "", "", "Mimics the real JobOrders form's own Job field exactly: plain Edit (not a filtered combo), validated via MaintainFromSpec: JobOrders( PROPERTY(Job) ) in the form XML - avoids the SLMatltrans leading-zero exact-match bug entirely instead of working around it. Column Data Type tries the real confirmed JobBase class; if rejected like QCSeq/QCInteger were, fall back to String."),
    ("po_num", "PoNum", "String", "15", "", "char", "", "", "", "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum=FP(po_num)) RECORDCAP(0))"),
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
    ("general_review_complete", "GeneralReviewComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("sox_impacted", "SoxImpacted", "Byte", "", "", "ListYesNoType", "sRSQCSarbanesImpact", "0", "", "Standalone, not part of the 5-category cascade."),
    ("hold_on_po", "HoldOnPo", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("auth_supplier_ship", "AuthSupplierShip", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("qc_disposition", "QcDisposition", "String", "20", "", "char", "", "", "", "Fixed value list not yet confirmed."),
    ("eng_disposition", "EngDisposition", "String", "20", "", "char", "", "", "", "Fixed value list not yet confirmed."),
    ("assigned_empnum", "AssignedEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("assigned_username", "AssignedUsername", "String", "128", "", "UsernameType", "sUserName", "", "1", "Read-only, auto-populated when AssignedEmpNum is selected."),
    ("assigned_buyer", "AssignedBuyer", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("qc_reviewer_empnum", "QcReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("qc_reviewer_username", "QcReviewerUsername", "String", "128", "", "UsernameType", "sUserName", "", "1", "Read-only, auto-populated when QcReviewerEmpNum is selected."),
    ("eng_reviewer_empnum", "EngReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("eng_reviewer_username", "EngReviewerUsername", "String", "128", "", "UsernameType", "sUserName", "", "1", "Read-only, auto-populated when EngReviewerEmpNum is selected."),
    ("planning_reviewer_empnum", "PlanningReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("planning_reviewer_name", "PlanningReviewerName", "String", "255", "", "LongDescType", "", "", "1", "Read-only, auto-populated when PlanningReviewerEmpNum is selected."),
    ("planning_complete", "PlanningComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("purchasing_reviewer_empnum", "PurchasingReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("purchasing_reviewer_name", "PurchasingReviewerName", "String", "255", "", "LongDescType", "", "", "1", "Read-only, auto-populated when PurchasingReviewerEmpNum is selected."),
    ("purchasing_complete", "PurchasingComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("cm_reviewer_empnum", "CmReviewerEmpNum", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", SL_EMPLOYEES),
    ("cm_reviewer_name", "CmReviewerName", "String", "255", "", "LongDescType", "", "", "1", "Read-only, auto-populated when CmReviewerEmpNum is selected."),
    ("cm_complete", "CmComplete", "Byte", "", "", "ListYesNoType", "", "0", "", ""),
    ("due_date", "DueDate", "Date", "", "", "DateType", "sDate", "", "", ""),
    ("internal_review_date", "InternalReviewDate", "Date", "", "", "DateType", "sDate", "", "", ""),
    ("close_date", "CloseDate", "Date", "", "", "DateType", "sDate", "", "1", "Auto-set by the Closed workflow, not user-typed."),
    ("closed_by", "ClosedBy", "String", "128", "", "UsernameType", "sRSQCClosedBy", "", "1", "Auto-set by the Closed workflow, not user-typed."),
    ("general_close_date", "GeneralCloseDate", "Date", "", "", "DateType", "sDate", "", "", "Purpose unclear vs. CloseDate - confirm before relying on it."),
    ("general_closed_by", "GeneralClosedBy", "NumSortedString", "7", "", "EmpNumType", "sEmployee", "", "", "Same caveat as GeneralCloseDate."),
    ("qc_rca_notes", "QcRcaNotes", "String", "1000", "", "QCLongCharType", "sNote", "", "", "Root cause analysis notes, QC."),
    ("eng_rca_notes", "EngRcaNotes", "String", "1000", "", "QCLongCharType", "sNote", "", "", "Root cause analysis notes, Engineering."),
    ("closed", "Closed", "Byte", "", "", "ListYesNoType", "sClosed", "0", "", "Enable gated by every ReqX/XReviewComplete pair matching - see cew_Closed in the form."),
]

TABLE_HEADER = ["Column Name", "Data Type", "Length", "Decimal Places", "Nullable", "Primary Key", "Default Value", "Description"]
IDO_HEADER = ["Bind To", "Property Name", "Property Class", "Data Type", "Length", "Decimal",
              "Column Data Type", "Label String ID", "Required", "Read Only", "Description"]

# Column Data Type defaults to matching Data Type (see below) since every QC-module-specific
# semantic name (QCSeq/QCInteger/QtyUnit) got rejected for a new property. job_num is a
# deliberate, evidence-based exception: JobBase is the real class the actual JobOrders form
# uses for its own Job field - try it; if it's rejected the same way, fall back to "String".
COLDTYPE_OVERRIDES = {"job_num": "JobBase"}

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
            # Column Data Type = same value as Data Type by default (matches what actually
            # worked on the Sql Columns side), except for the explicit overrides above.
            col_data_type = COLDTYPE_OVERRIDES.get(col, dtype)
            w.writerow([col, pname, "", dtype, length, decimal, col_data_type, labelid, required, readonly, desc])

    print(f"Wrote {len(FIELDS)} rows to each CSV. CreatedBy/CreateDate deliberately excluded - "
          f"already auto-generated by Application Studio on the new table.")

if __name__ == "__main__":
    main()
