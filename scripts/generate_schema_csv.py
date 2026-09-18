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

# column, table_type, length, decimals, nullable, pk, table_default, prop_class, ido_key_seq, readonly, required, ido_default_from, list_source, description
FIELDS = [
    ("cmr_num", "Integer", "", "", "No", "Y", "AUTONUMBER(STEP(1))", "", "1", "False", "False", "AUTONUMBER(STEP(1))", "", "CMR number, key, auto-generated."),
    ("status", "String", "20", "", "Yes", "N", "", "", "", "False", "False", "", "", "Overall CMR status. Fixed value list not yet confirmed."),
    ("workflow_status", "String", "30", "", "Yes", "N", "", "", "", "False", "False", "", "", "Workflow status. Fixed value list not yet confirmed."),
    ("create_date", "DateTime", "", "", "No", "N", "NOW()", "CurrentDate", "", "True", "False", "", "", "Set once at creation."),
    ("created_by", "String", "30", "", "No", "N", "", "UserName", "", "True", "False", "UserName()", "", "Set once at creation."),
    ("priority", "String", "10", "", "No", "N", "", "", "", "False", "True", "", "", "High/Medium/Low expected - confirm exact list."),
    ("item", "String", "30", "", "Yes", "N", "", "Item", "", "False", "False", "", SL_ITEMS, ""),
    ("item_description", "String", "60", "", "Yes", "N", "", "Description", "", "True", "False", "", "", "Read-only display, populated by lookup."),
    ("wc", "String", "10", "", "Yes", "N", "", "Wc", "", "False", "False", "", SL_WCS, ""),
    ("wc_description", "String", "60", "", "Yes", "N", "", "Description", "", "True", "False", "", "", "Read-only display, populated by lookup."),
    ("dept", "String", "10", "", "Yes", "N", "", "Dept", "", "False", "False", "", SL_DEPTS, ""),
    ("dept_description", "String", "60", "", "Yes", "N", "", "Description", "", "True", "False", "", "", "Read-only display, populated by lookup."),
    ("initial_change", "String", "20", "", "Yes", "N", "", "", "", "False", "True", "", "", "Fixed 8-value list: Documentation/Machine/Material/Other/Process/Specification/Tooling/Variance(waiver). Drives the Requirements cascade."),
    ("additional_changes", "Text", "", "", "Yes", "N", "", "", "", "False", "False", "", "", "Long/growing note."),
    ("requested_action", "Text", "", "", "Yes", "N", "", "", "", "False", "False", "", "", ""),
    ("general_note", "Text", "", "", "Yes", "N", "", "QCLongChar", "", "False", "False", "", "", ""),
    ("revision", "String", "10", "", "Yes", "N", "", "Revision", "", "False", "False", "", "", "Drawing Revision."),
    ("latest_revision", "String", "10", "", "Yes", "N", "", "Revision", "", "False", "False", "", "", ""),
    ("next_assy_item", "String", "30", "", "Yes", "N", "", "Item", "", "False", "False", "", "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(item)') RECORDCAP(0))", "Next Level Assembly item."),
    ("next_assy_description", "String", "60", "", "Yes", "N", "", "Description", "", "True", "False", "", "", "Read-only display, populated by lookup."),
    ("vendor", "String", "15", "", "Yes", "N", "", "VendNum", "", "False", "False", "", SL_VENDORS, ""),
    ("vendor_name", "String", "60", "", "Yes", "N", "", "Name", "", "True", "False", "", "", "Read-only display, populated by lookup."),
    ("qty", "Decimal", "", "4", "Yes", "N", "", "QtyUnit", "", "False", "False", "", "", ""),
    ("job_num", "String", "15", "", "Yes", "N", "", "", "", "False", "False", "", "", "Free-text for v1 - legacy SLMatltrans filter had a leading-zero bug, not carried over."),
    ("po_num", "String", "15", "", "Yes", "N", "", "PoNum", "", "False", "False", "", "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum=FP(po_num)) RECORDCAP(0))", ""),
    ("po_line", "String", "10", "", "Yes", "N", "", "PoLine", "", "False", "False", "", "STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum='P(po_num)') RECORDCAP(0))", ""),
    ("rfq_num", "String", "15", "", "Yes", "N", "", "", "", "False", "False", "", "", ""),
    ("eo_num", "String", "15", "", "Yes", "N", "", "", "", "False", "False", "", "", ""),
    ("mdl", "String", "40", "", "Yes", "N", "", "", "", "False", "False", "", "", ""),
    ("poc", "String", "60", "", "Yes", "N", "", "", "", "False", "False", "", "", "Point of contact, free text."),
    ("req_costing", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Cascades off initial_change."),
    ("cost_review_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("req_documentation", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Cascades off initial_change."),
    ("documentation_review_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("req_tool_machine", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Cascades off initial_change."),
    ("machinery_review_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("req_process", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Cascades off initial_change."),
    ("process_review_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("req_material", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Cascades off initial_change."),
    ("material_review_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("general_review_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("sox_impacted", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Sarbanes-Oxley impact flag, standalone (not part of the 5-category cascade)."),
    ("hold_on_po", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("auth_supplier_ship", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("qc_disposition", "String", "20", "", "Yes", "N", "", "", "", "False", "False", "", "", "Fixed value list not yet confirmed."),
    ("eng_disposition", "String", "20", "", "Yes", "N", "", "", "", "False", "False", "", "", "Fixed value list not yet confirmed."),
    ("assigned_empnum", "String", "10", "", "Yes", "N", "", "EmpNum", "", "False", "False", "", SL_EMPLOYEES, ""),
    ("assigned_username", "String", "30", "", "Yes", "N", "", "Username", "", "True", "False", "", "", "Read-only display, auto-populated when assigned_empnum is selected."),
    ("assigned_buyer", "String", "30", "", "Yes", "N", "", "Username", "", "False", "False", "UserName()", SL_EMPLOYEES, ""),
    ("qc_reviewer_empnum", "String", "10", "", "Yes", "N", "", "EmpNum", "", "False", "False", "", SL_EMPLOYEES, ""),
    ("qc_reviewer_username", "String", "30", "", "Yes", "N", "", "Username", "", "True", "False", "", "", "Read-only display, auto-populated when qc_reviewer_empnum is selected."),
    ("eng_reviewer_empnum", "String", "10", "", "Yes", "N", "", "EmpNum", "", "False", "False", "", SL_EMPLOYEES, ""),
    ("eng_reviewer_username", "String", "30", "", "Yes", "N", "", "Username", "", "True", "False", "", "", "Read-only display, auto-populated when eng_reviewer_empnum is selected."),
    ("planning_reviewer_empnum", "String", "10", "", "Yes", "N", "", "EmpNum", "", "False", "False", "", SL_EMPLOYEES, ""),
    ("planning_reviewer_name", "String", "60", "", "Yes", "N", "", "EmpName", "", "True", "False", "", "", "Read-only display, auto-populated when planning_reviewer_empnum is selected."),
    ("planning_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("purchasing_reviewer_empnum", "String", "10", "", "Yes", "N", "", "EmpNum", "", "False", "False", "", SL_EMPLOYEES, ""),
    ("purchasing_reviewer_name", "String", "60", "", "Yes", "N", "", "EmpName", "", "True", "False", "", "", "Read-only display, auto-populated when purchasing_reviewer_empnum is selected."),
    ("purchasing_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("cm_reviewer_empnum", "String", "10", "", "Yes", "N", "", "EmpNum", "", "False", "False", "", SL_EMPLOYEES, ""),
    ("cm_reviewer_name", "String", "60", "", "Yes", "N", "", "EmpName", "", "True", "False", "", "", "Read-only display, auto-populated when cm_reviewer_empnum is selected."),
    ("cm_complete", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", ""),
    ("due_date", "Date", "", "", "Yes", "N", "", "Date", "", "False", "False", "", "", ""),
    ("internal_review_date", "Date", "", "", "Yes", "N", "", "Date", "", "False", "False", "", "", ""),
    ("close_date", "Date", "", "", "Yes", "N", "", "Date", "", "True", "False", "", "", "Auto-set by the Closed workflow, not user-typed."),
    ("closed_by", "String", "30", "", "Yes", "N", "", "UserName", "", "True", "False", "", "", "Auto-set by the Closed workflow, not user-typed."),
    ("general_close_date", "Date", "", "", "Yes", "N", "", "Date", "", "False", "False", "", "", "Purpose unclear vs. close_date - confirm before relying on it."),
    ("general_closed_by", "String", "30", "", "Yes", "N", "", "UserName", "", "False", "False", "", "", "Same caveat as general_close_date."),
    ("qc_rca_notes", "Text", "", "", "Yes", "N", "", "", "", "False", "False", "", "", "Root cause analysis notes, QC."),
    ("eng_rca_notes", "Text", "", "", "Yes", "N", "", "", "", "False", "False", "", "", "Root cause analysis notes, Engineering."),
    ("closed", "Boolean", "", "", "No", "N", "False", "ListYesNo", "", "False", "False", "", "", "Enable gated by all req_*/*_review_complete pairs matching - see cew_Closed in the form."),
]

TABLE_HEADER = ["Column Name", "Data Type", "Length", "Decimal Places", "Nullable", "Primary Key", "Default Value", "Description"]
IDO_HEADER = ["Property Name", "Bind To Column", "Property Class", "Key Sequence", "Read Only", "Required", "Default From", "List Source", "Description"]

def main():
    with open("exports/ecmrs_table_columns.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(TABLE_HEADER)
        for (col, dtype, length, decimals, nullable, pk, default, pclass, keyseq, readonly, required, deffrom, listsrc, desc) in FIELDS:
            w.writerow([col, dtype, length, decimals, nullable, pk, default, desc])

    with open("exports/ecmrs_ido_properties.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(IDO_HEADER)
        for (col, dtype, length, decimals, nullable, pk, default, pclass, keyseq, readonly, required, deffrom, listsrc, desc) in FIELDS:
            w.writerow([col, col, pclass, keyseq, readonly, required, deffrom, listsrc, desc])

    print(f"Wrote {len(FIELDS)} rows to ecmrs_table_columns.csv and ecmrs_ido_properties.csv")

if __name__ == "__main__":
    main()
