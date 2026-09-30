"""Help text for the eCMRs form: one entry per field, in form order, by section.

Single source for the help pages (scripts/build_help.py writes docs/help/). The pages are a
reference for users, opened by right-click -> Help on the form. Describe what the
form actually does on TRN - see docs/task-list.md and docs/troubleshooting.md - not plans.

Each field: key (help page name), label (as on the form), components (form component names that
open this page from right-click -> Help), and text paragraphs. Optional: values (list), filled
(how the form fills it in), related (keys of other fields).
"""

FORM = {
    "title": "eCMRs (Change Management Requests)",
    "intro": [
        "Use this form to create, track and close a Change Management Request (CMR): a request to "
        "change a part, drawing, process, tooling, material or documentation. One CMR record holds "
        "everything from the request through Quality and Engineering review to Implementation and "
        "closing.",
        "eCMRs replaces the Create Change Request, Change Request Management and QC CMRs forms. It "
        "is an Enflite form on its own table and IDO (ue_ecmrs); standard SyteLine forms and data "
        "are not changed.",
    ],
    "howto": [
        "Click New. The form fills in CMR Num (CMR-YYMMDD-HHMMSS), Create Date and Created By.",
        "Fill in the top of the form: PO, Item, Vendor, Priority and the Requested Action.",
        "Under Change Request Fields, pick the Dept, Work Center and Initial Change. The "
        "Requirement checkboxes are ticked for you; change them if needed.",
        "Quality and Engineering fill in their sections: codes, disposition, reviewer and RCA notes.",
        "Planning, Purchasing and CM tick their box when their part is done and pick a reviewer.",
        "Select Closed to close the CMR. Save after each step.",
    ],
}

SECTIONS = [
    ("header", "Header"),
    ("change", "Change Request Fields"),
    ("additional", "Additional Fields"),
    ("quality", "Quality"),
    ("engineering", "Engineering"),
    ("implementation", "Implementation"),
]

EMP_FILL = ("Select an employee number from the list (employee number, name and user name are "
            "shown). The name is filled in for you.")
EMP_NAME = "The reviewer's name, filled in when a Reviewer ID is selected. You can type over it."

FIELDS = [
    # --- Header -----------------------------------------------------------------------------
    dict(key="status", section="header", label="Status", components=["c_status"],
         text=["The stage the CMR is at in the change process."],
         values=["Data Input", "QC Approval", "Eng Review", "Planning", "Purchasing", "CM", "Complete"]),
    dict(key="assigned", section="header", label="Assigned", components=["c_assigned_empnum_v2", "c_assigned_username_v2"],
         text=["The employee the CMR is assigned to. The first box is the employee number; the "
               "second box shows the employee's name."],
         filled=EMP_FILL),
    dict(key="notify", section="header", label="Notify", components=["btn_notify"],
         text=["Emails the person in Assigned that the CMR needs their attention, with the CMR Num and "
               "Priority. The email goes to the Assigned employee's SyteLine user (their email address). "
               "Save the CMR first, and make sure Assigned is filled in."],
         related=["assigned"]),
    dict(key="cmr_num", section="header", label="CMR Num", components=["c_cmr_num"],
         text=["The CMR's unique number, in the form CMR-YYMMDD-HHMMSS: the date and time "
               "New was clicked (for example CMR-260929-111742). It can't be changed."],
         filled="Set by the form when you click New."),
    dict(key="create_date", section="header", label="Create Date", components=["c_create_date"],
         text=["The date the CMR was created."], filled="Set by the system when the CMR is saved."),
    dict(key="created_by", section="header", label="Created By", components=["c_created_by"],
         text=["The user who created the CMR."], filled="Set by the system when the CMR is saved."),
    dict(key="po_num", section="header", label="PO Num", components=["c_po_num"],
         text=["The purchase order the change relates to, if any. The list shows every purchase "
               "order line (PO, item and line); type to narrow it down."],
         related=["po_line", "vendor"]),
    dict(key="po_line", section="header", label="PO Line", components=["c_po_line"],
         text=["The line on the selected PO. The list shows only the lines of the PO in PO Num, with "
               "their item."], related=["po_num"]),
    dict(key="assigned_buyer", section="header", label="Assigned Buyer", components=["c_assigned_buyer"],
         text=["The buyer responsible for the purchasing side of the change. Select an employee "
               "from the list; the employee number is stored."]),
    dict(key="qty", section="header", label="Qty", components=["c_qty"],
         text=["The quantity affected by the change."]),
    dict(key="poc", section="header", label="POC", components=["c_poc"],
         text=["The point of contact for this CMR."]),
    dict(key="rfq_num", section="header", label="RFQ Num", components=["c_rfq_num"],
         text=["The request for quote number, if the change involves a quote."]),
    dict(key="job_num", section="header", label="Job Num", components=["c_job_num"],
         text=["The job the change relates to, if any. The list shows job numbers from material "
               "transactions; type to narrow it down."]),
    dict(key="revision", section="header", label="Drawing Revision", components=["c_revision"],
         text=["The drawing revision the request is based on."], related=["latest_revision"]),
    dict(key="latest_revision", section="header", label="Latest Revision", components=["c_latest_revision"],
         text=["The latest drawing revision, when it differs from the Drawing Revision."],
         related=["revision"]),
    dict(key="requested_action", section="header", label="Requested Action", components=["c_requested_action"],
         text=["What is being asked for: describe the problem and the change requested. Always state "
               "what the part should be versus what it is, with sheet number and zone if applicable."]),
    dict(key="item", section="header", label="Item", components=["c_item"],
         text=["The item (part number) the change is for. Selecting an item also filters the "
               "Next Lvl Assy, Serial # and LOT # lists."],
         filled="Item Desc is filled in from the item.", related=["item_description", "serial_num", "lot_num"]),
    dict(key="item_description", section="header", label="Item Desc", components=["edit1_SITE"],
         text=["The description of the selected item."], filled="Filled in when an Item is selected. You can type over it.",
         related=["item"]),
    dict(key="next_assy_item", section="header", label="Next Lvl Assy", components=["c_next_assy_item"],
         text=["The next-level assembly that uses the item. The list shows the job items that use "
               "the selected Item."],
         filled="Assy Desc is filled in from the assembly.", related=["item", "next_assy_description"]),
    dict(key="next_assy_description", section="header", label="Assy Desc", components=["c_next_assy_description"],
         text=["The description of the next-level assembly."],
         filled="Filled in when a Next Lvl Assy is selected. You can type over it.", related=["next_assy_item"]),
    dict(key="vendor", section="header", label="Vendor", components=["c_vendor"],
         text=["The vendor involved in the change, if any."], filled="Vendor Name is filled in from the vendor.",
         related=["vendor_name"]),
    dict(key="vendor_name", section="header", label="Vendor Name", components=["c_vendor_name"],
         text=["The name of the selected vendor."], filled="Filled in when a Vendor is selected. You can type over it.",
         related=["vendor"]),
    dict(key="priority", section="header", label="Priority", components=["c_priority"],
         text=["How urgent the change is."], values=["High", "Medium", "Low"]),

    # --- Change Request Fields ----------------------------------------------------------------
    dict(key="dept", section="change", label="Dept", components=["c_dept"],
         text=["The department where the change is needed."], filled="Dept Description is filled in from the department.",
         related=["dept_description"]),
    dict(key="dept_description", section="change", label="Dept Description", components=["c_dept_description"],
         text=["The name of the selected department."], filled="Filled in as soon as a Dept is selected.",
         related=["dept"]),
    dict(key="wc", section="change", label="Work Center", components=["c_wc"],
         text=["The work center where the change is needed."], filled="WC Description is filled in from the work center.",
         related=["wc_description"]),
    dict(key="wc_description", section="change", label="WC Description", components=["c_wc_description"],
         text=["The name of the selected work center."], filled="Filled in as soon as a Work Center is selected.",
         related=["wc"]),
    dict(key="reported_by", section="change", label="Reported By", components=["c_reported_by"],
         text=["Who reported or requested the change (free text)."]),
    dict(key="due_date", section="change", label="Due Date", components=["c_due_date"],
         text=["The date the change should be completed by."]),
    dict(key="initial_change", section="change", label="Initial Change", components=["c_initial_change"],
         text=["The type of change requested. Selecting it ticks the Requirement checkboxes that "
               "apply (see the table); you can then change the checkboxes by hand."],
         values=["Documentation", "Machine", "Material", "Other", "Process", "Specification", "Tooling", "Variance(waiver)"],
         table=(["Initial Change", "Costing", "Documentation", "Process", "Tool/Machine", "Material"],
                [["Documentation", "", "✓", "", "", ""],
                 ["Machine", "✓", "✓", "✓", "✓", ""],
                 ["Material", "✓", "✓", "", "", ""],
                 ["Other", "", "", "", "", ""],
                 ["Process", "✓", "✓", "✓", "✓", ""],
                 ["Specification", "✓", "✓", "✓", "✓", ""],
                 ["Tooling", "", "", "", "✓", ""],
                 ["Variance(waiver)", "✓", "✓", "✓", "✓", ""]]),
         related=["requirements"]),
    dict(key="requirements", section="change", label="Req: Costing, Documentation, Tool/Machine, Process, Material",
         components=["c_req_costing", "c_req_documentation", "c_req_tool_machine", "c_req_process", "c_req_material"],
         text=["Which reviews the change needs: Costing, Documentation, Tool/Machine, Process and "
               "Material. Select each one that applies."],
         filled="Ticked for you when Initial Change is selected. You can change them.",
         related=["initial_change"]),
    dict(key="general_note", section="change", label="General Note", components=["c_general_note"],
         text=["Any other information about the request."]),

    # --- Additional Fields --------------------------------------------------------------------
    dict(key="serial_num", section="additional", label="Serial #", components=["c_serial_num_v2"],
         text=["The serial number of the affected unit. The list shows the serial numbers of the "
               "selected Item; it is empty for items that aren't serial-tracked. You can also type a value."],
         related=["item", "lot_num"]),
    dict(key="lot_num", section="additional", label="LOT #", components=["c_lot_num_v2"],
         text=["The lot of the affected material. The list shows the lots of the selected Item; it is "
               "empty for items that aren't lot-tracked. You can also type a value."],
         related=["item", "serial_num"]),

    # --- Quality --------------------------------------------------------------------------------
    dict(key="sox_impacted", section="quality", label="SOX Impacted", components=["c_sox_impacted"],
         text=["Select if the change affects Sarbanes-Oxley (SOX) controls."]),
    dict(key="hold_on_po", section="quality", label="Hold On PO", components=["c_hold_on_po"],
         text=["Select if the purchase order is on hold because of this CMR."]),
    dict(key="auth_supplier_ship", section="quality", label="Authorization For Supplier To Ship", components=["c_auth_supplier_ship"],
         text=["Select when the supplier is authorized to ship."]),
    dict(key="reason_code", section="quality", label="Reason Code", components=["c_reason_code_v2"],
         text=["Why the CMR was raised. The codes are the same as on QC MRRs."],
         values=["ASMBL - Incorrect Assembly", "DAMAGED - Damaged in house", "DELIVERY - Vendor delivered wrong product",
                 "DOCUMENT - Missing / Incorrect document", "FEATURE - Missing feature", "FUNCTION - Part does not work",
                 "INTERNAL - Enflite at Fault", "MATERIAL - Material mismatch", "MEASURE - Dimensional Issue",
                 "PURCHASE - Purchased incorrect item", "REVISION - Incorrect Revision",
                 "SUPDAM - Damaged by supplier or shipping", "VISUAL - Visual defect"],
         related=["cause_code"]),
    dict(key="cause_code", section="quality", label="Cause Code", components=["c_cause_code_v2"],
         text=["The cause found for the problem. The codes are the same as on QC MRRs."],
         values=["ENF - Enflite error", "ENG - Engineering/Drawing/Design error", "EXC - Supplier Exception",
                 "FUNC - Functional Issue", "HANDLE - Internal handling error", "NFF - No fault found",
                 "QCM - Supplier Error / Enflite Quality Miss", "SHIP - Damaged in Shipping", "SHORTAGE - Parts Shortage",
                 "SUP - Supplier Error", "TOOL - Inadequate Tooling", "UNK - Cause Unknown", "VOID - VOID"],
         related=["reason_code"]),
    dict(key="qc_disposition", section="quality", label="QC Disposition", components=["c_qc_disposition"],
         text=["Quality's decision on the affected material or parts."],
         values=["Accept", "Hold", "NFF", "NRS", "Other", "Reject", "Rework", "Scrap"]),
    dict(key="qc_reviewer", section="quality", label="Reviewer ID / Reviewer (Quality)",
         components=["c_qc_reviewer_empnum_v2", "c_qc_reviewer_username_v2"],
         text=["The Quality reviewer for this CMR."], filled=EMP_FILL),
    dict(key="qc_rca_notes", section="quality", label="QC RCA Notes", components=["c_qc_rca_notes"],
         text=["Quality's root cause analysis notes."]),

    # --- Engineering ----------------------------------------------------------------------------
    dict(key="eo_num", section="engineering", label="EO Num", components=["c_eo_num"],
         text=["The engineering order number for the change."]),
    dict(key="mdl", section="engineering", label="MDL", components=["c_mdl"],
         text=["The MDL reference for the change."]),
    dict(key="eng_disposition", section="engineering", label="Engineering Disposition", components=["c_eng_disposition"],
         text=["Engineering's decision on the affected material or parts."],
         values=["NFF", "NRS", "Other", "Rework", "Scrap"]),
    dict(key="eng_reviewer", section="engineering", label="Reviewer ID / Reviewer (Engineering)",
         components=["c_eng_reviewer_empnum_v2", "c_eng_reviewer_username_v2"],
         text=["The Engineering reviewer for this CMR."], filled=EMP_FILL),
    dict(key="internal_review_date", section="engineering", label="Internal Review Date", components=["c_internal_review_date"],
         text=["The date of Engineering's internal review."]),
    dict(key="eng_rca_notes", section="engineering", label="Eng RCA Notes", components=["c_eng_rca_notes"],
         text=["Engineering's root cause analysis notes."]),

    # --- Implementation -------------------------------------------------------------------------
    dict(key="planning", section="implementation", label="Planning",
         components=["c_planning_complete", "c_planning_reviewer_empnum_v2", "c_planning_reviewer_name_v2"],
         text=["Planning's part of the change. Select the checkbox when Planning is done, and pick "
               "the Planning reviewer in Reviewer ID."], filled=EMP_FILL),
    dict(key="purchasing", section="implementation", label="Purchasing",
         components=["c_purchasing_complete", "c_purchasing_reviewer_empnum_v2", "c_purchasing_reviewer_name_v2"],
         text=["Purchasing's part of the change. Select the checkbox when Purchasing is done, and pick "
               "the Purchasing reviewer in Reviewer ID."], filled=EMP_FILL),
    dict(key="cm", section="implementation", label="CM",
         components=["c_cm_complete", "c_cm_reviewer_empnum_v2", "c_cm_reviewer_name_v2"],
         text=["Configuration Management's part of the change. Select the checkbox when CM is done, "
               "and pick the CM reviewer in Reviewer ID."], filled=EMP_FILL),
    dict(key="closed", section="implementation", label="Closed", components=["c_closed"],
         text=["Select to close the CMR. Clear it to reopen the CMR."],
         filled="Selecting it fills in Close Date (today) and Closed By (you); clearing it empties both.",
         related=["close_date", "closed_by"]),
    dict(key="close_date", section="implementation", label="Close Date", components=["c_close_date"],
         text=["The date the CMR was closed."], filled="Set when Closed is selected.", related=["closed"]),
    dict(key="closed_by", section="implementation", label="Closed By", components=["c_closed_by"],
         text=["The user who closed the CMR."], filled="Set when Closed is selected.", related=["closed"]),
]
