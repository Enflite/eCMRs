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

# bind_to (snake_case column), property_name (PascalCase), data_type, length, decimal, column_data_type, description
FIELDS = [
    ("cmr_num", "CmrNum", "Integer", "", "", "", "CMR number, key, auto-generated via AUTONUMBER on the table."),
    ("status", "Status", "String", "20", "", "", "Overall CMR status. Fixed value list not yet confirmed."),
    ("workflow_status", "WorkflowStatus", "String", "30", "", "", "Workflow status. Fixed value list not yet confirmed."),
    ("priority", "Priority", "String", "10", "", "", "High/Medium/Low expected - confirm exact list."),
    ("item", "Item", "String", "30", "", "", SL_ITEMS),
    ("item_description", "ItemDescription", "String", "60", "", "", "Read-only display, populated by lookup."),
    ("wc", "Wc", "String", "10", "", "", SL_WCS),
    ("wc_description", "WcDescription", "String", "60", "", "", "Read-only display, populated by lookup."),
    ("dept", "Dept", "String", "10", "", "", SL_DEPTS),
    ("dept_description", "DeptDescription", "String", "60", "", "", "Read-only display, populated by lookup."),
    ("initial_change", "InitialChange", "String", "20", "", "", "Fixed 8-value list: Documentation/Machine/Material/Other/Process/Specification/Tooling/Variance(waiver). Drives the Requirements cascade."),
    ("additional_changes", "AdditionalChanges", "String", "2000", "", "", "Long/growing note."),
    ("requested_action", "RequestedAction", "String", "2000", "", "", ""),
    ("general_note", "GeneralNote", "String", "2000", "", "", ""),
    ("revision", "Revision", "String", "10", "", "", "Drawing Revision."),
    ("latest_revision", "LatestRevision", "String", "10", "", "", ""),
    ("next_assy_item", "NextAssyItem", "String", "30", "", "", "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(item)') RECORDCAP(0)) - Next Level Assembly item."),
    ("next_assy_description", "NextAssyDescription", "String", "60", "", "", "Read-only display, populated by lookup."),
    ("vendor", "Vendor", "String", "15", "", "", SL_VENDORS),
    ("vendor_name", "VendorName", "String", "60", "", "", "Read-only display, populated by lookup."),
    ("qty", "Qty", "Decimal", "", "4", "", ""),
    ("job_num", "JobNum", "String", "15", "", "", "Free-text for v1 - legacy SLMatltrans filter had a leading-zero bug, not carried over."),
    ("po_num", "PoNum", "String", "15", "", "", "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum=FP(po_num)) RECORDCAP(0))"),
    ("po_line", "PoLine", "String", "10", "", "", "STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum='P(po_num)') RECORDCAP(0))"),
    ("rfq_num", "RfqNum", "String", "15", "", "", ""),
    ("eo_num", "EoNum", "String", "15", "", "", ""),
    ("mdl", "Mdl", "String", "40", "", "", ""),
    ("poc", "Poc", "String", "60", "", "", "Point of contact, free text."),
    ("req_costing", "ReqCosting", "Byte", "", "", "FlagNyType", "Cascades off InitialChange."),
    ("cost_review_complete", "CostReviewComplete", "Byte", "", "", "FlagNyType", ""),
    ("req_documentation", "ReqDocumentation", "Byte", "", "", "FlagNyType", "Cascades off InitialChange."),
    ("documentation_review_complete", "DocumentationReviewComplete", "Byte", "", "", "FlagNyType", ""),
    ("req_tool_machine", "ReqToolMachine", "Byte", "", "", "FlagNyType", "Cascades off InitialChange."),
    ("machinery_review_complete", "MachineryReviewComplete", "Byte", "", "", "FlagNyType", ""),
    ("req_process", "ReqProcess", "Byte", "", "", "FlagNyType", "Cascades off InitialChange."),
    ("process_review_complete", "ProcessReviewComplete", "Byte", "", "", "FlagNyType", ""),
    ("req_material", "ReqMaterial", "Byte", "", "", "FlagNyType", "Cascades off InitialChange."),
    ("material_review_complete", "MaterialReviewComplete", "Byte", "", "", "FlagNyType", ""),
    ("general_review_complete", "GeneralReviewComplete", "Byte", "", "", "FlagNyType", ""),
    ("sox_impacted", "SoxImpacted", "Byte", "", "", "FlagNyType", "Standalone, not part of the 5-category cascade."),
    ("hold_on_po", "HoldOnPo", "Byte", "", "", "FlagNyType", ""),
    ("auth_supplier_ship", "AuthSupplierShip", "Byte", "", "", "FlagNyType", ""),
    ("qc_disposition", "QcDisposition", "String", "20", "", "", "Fixed value list not yet confirmed."),
    ("eng_disposition", "EngDisposition", "String", "20", "", "", "Fixed value list not yet confirmed."),
    ("assigned_empnum", "AssignedEmpNum", "String", "10", "", "", SL_EMPLOYEES),
    ("assigned_username", "AssignedUsername", "String", "30", "", "", "Read-only display, auto-populated when AssignedEmpNum is selected."),
    ("assigned_buyer", "AssignedBuyer", "String", "10", "", "", SL_EMPLOYEES),
    ("qc_reviewer_empnum", "QcReviewerEmpNum", "String", "10", "", "", SL_EMPLOYEES),
    ("qc_reviewer_username", "QcReviewerUsername", "String", "30", "", "", "Read-only display, auto-populated when QcReviewerEmpNum is selected."),
    ("eng_reviewer_empnum", "EngReviewerEmpNum", "String", "10", "", "", SL_EMPLOYEES),
    ("eng_reviewer_username", "EngReviewerUsername", "String", "30", "", "", "Read-only display, auto-populated when EngReviewerEmpNum is selected."),
    ("planning_reviewer_empnum", "PlanningReviewerEmpNum", "String", "10", "", "", SL_EMPLOYEES),
    ("planning_reviewer_name", "PlanningReviewerName", "String", "60", "", "", "Read-only display, auto-populated when PlanningReviewerEmpNum is selected."),
    ("planning_complete", "PlanningComplete", "Byte", "", "", "FlagNyType", ""),
    ("purchasing_reviewer_empnum", "PurchasingReviewerEmpNum", "String", "10", "", "", SL_EMPLOYEES),
    ("purchasing_reviewer_name", "PurchasingReviewerName", "String", "60", "", "", "Read-only display, auto-populated when PurchasingReviewerEmpNum is selected."),
    ("purchasing_complete", "PurchasingComplete", "Byte", "", "", "FlagNyType", ""),
    ("cm_reviewer_empnum", "CmReviewerEmpNum", "String", "10", "", "", SL_EMPLOYEES),
    ("cm_reviewer_name", "CmReviewerName", "String", "60", "", "", "Read-only display, auto-populated when CmReviewerEmpNum is selected."),
    ("cm_complete", "CmComplete", "Byte", "", "", "FlagNyType", ""),
    ("due_date", "DueDate", "DateTime", "", "", "", ""),
    ("internal_review_date", "InternalReviewDate", "DateTime", "", "", "", ""),
    ("close_date", "CloseDate", "DateTime", "", "", "", "Auto-set by the Closed workflow, not user-typed."),
    ("closed_by", "ClosedBy", "String", "30", "", "", "Auto-set by the Closed workflow, not user-typed."),
    ("general_close_date", "GeneralCloseDate", "DateTime", "", "", "", "Purpose unclear vs. CloseDate - confirm before relying on it."),
    ("general_closed_by", "GeneralClosedBy", "String", "30", "", "", "Same caveat as GeneralCloseDate."),
    ("qc_rca_notes", "QcRcaNotes", "String", "2000", "", "", "Root cause analysis notes, QC."),
    ("eng_rca_notes", "EngRcaNotes", "String", "2000", "", "", "Root cause analysis notes, Engineering."),
    ("closed", "Closed", "Byte", "", "", "FlagNyType", "Enable gated by every ReqX/XReviewComplete pair matching - see cew_Closed in the form."),
]

TABLE_HEADER = ["Column Name", "Data Type", "Length", "Decimal Places", "Nullable", "Primary Key", "Default Value", "Description"]
IDO_HEADER = ["Bind To", "Property Name", "Property Class", "Data Type", "Length", "Decimal", "Column Data Type", "Description"]

def main():
    with open("exports/ecmrs_table_columns.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(TABLE_HEADER)
        for (col, pname, dtype, length, decimal, coldtype, desc) in FIELDS:
            table_type = "Integer" if dtype == "Integer" else ("Bit" if dtype == "Byte" else dtype)
            pk = "Y" if col == "cmr_num" else "N"
            nullable = "No" if col == "cmr_num" else "Yes"
            default = "AUTONUMBER(STEP(1))" if col == "cmr_num" else ""
            w.writerow([col, table_type, length, decimal, nullable, pk, default, desc])

    with open("exports/ecmrs_ido_properties.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(IDO_HEADER)
        for (col, pname, dtype, length, decimal, coldtype, desc) in FIELDS:
            w.writerow([col, pname, "", dtype, length, decimal, coldtype, desc])

    print(f"Wrote {len(FIELDS)} rows to each CSV. CreatedBy/CreateDate deliberately excluded - "
          f"already auto-generated by Application Studio on the new table.")

if __name__ == "__main__":
    main()
