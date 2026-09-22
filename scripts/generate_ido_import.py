#!/usr/bin/env python3
"""Generates exports/ecmrs_ido_properties_import.csv - a ready-to-import file in the exact
format Application Studio's own "Export to Excel" produced for the IDO Properties grid
(UTF-16, tab-delimited, same 42 columns, same quoting convention - confirmed against the
live docs/reference/ToExcel_IdoProperties_4.csv export).

Contains only the 71 NEW properties (continuing Sequence from 8) - deliberately does not
repeat the 7 existing system properties (CreatedBy, UpdatedBy, CreateDate, RecordDate,
RowPointer, NoteExistsFlag, InWorkflow), so an import can't collide with or duplicate them.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from generate_schema_csv import FIELDS, COLDTYPE_OVERRIDES

IDO_NAME = "ue_ecmrs"
TABLE_ALIAS = "ec"
TABLE_NAME = "ue_ecmrs"  # confirmed from the real ToExcel export, not "ue_ecmr"

# Superseded: job_num no longer needs an Input Mask - it's now a plain Edit validated via
# MaintainFromSpec in the form XML instead, mimicking the real JobOrders form's own Job
# field exactly. See generate_form.py.

# Custom Property Class name for each fixed-value-list property - QCPriorityType (reusing a
# real system class) came back blank in the live IDO Properties export, so these get their own.
PROPERTY_CLASS_OVERRIDES = {
    "status": "ue_CmrStatusType",
    "priority": "ue_CmrPriorityType",
    "initial_change": "ue_CmrInitialChangeType",
    "qc_disposition": "ue_CmrQcDispositionType",
    "eng_disposition": "ue_CmrEngDispositionType",
}

# UNCONFIRMED syntax: no real IDO Properties export seen so far (including the live
# ToExcel_IdoProperties_3.csv) has a populated Inline List value to copy the exact delimiter
# from - every real example checked is blank. Comma-separated is the best guess (matches the
# plain-string convention used elsewhere in this same CSV format). If Application Studio
# rejects this on import, the error message will show the expected real format directly.
INLINE_LISTS = {
    "status": "CM,Complete,Data Input,Eng Review,Planning,Purchasing,QC Approval",
    "priority": "High,Medium,Low",
    "initial_change": "Documentation,Machine,Material,Other,Process,Specification,Tooling,Variance(waiver)",
    # Confirmed directly from the real live dropdowns (screenshots of the actual Disposition
    # combo open on both sections) - Engineering's list is a subset of QC's, missing
    # Accept/Hold/Reject.
    "qc_disposition": "Accept,Hold,NFF,NRS,Other,Reject,Rework,Scrap",
    "eng_disposition": "NFF,NRS,Other,Rework,Scrap",
}

# Header names/order/count confirmed directly against docs/reference/ToExcel_IdoProperties_4.csv
# (42 columns, not 40 - a prior version of this generator was missing "Validate Immediately"/
# "Validate Immediately Prompt" at positions 38-39, and used "Data Type"/"Column Data Type"/
# "Read Only" where the live grid actually shows "*Data Type"/"*Column Data Type"/"*Read Only").
HEADER = ["DevelopmentFlagGridCol", "Property Name", "IDO Name", "Property Class",
          "Column Table Alias", "Table Name", "Property Type", "Column Name", "Description",
          "Sequence", "Pseudo Key", "*Data Type", "*Length", "Display Decimal Position",
          "Default Value", "*Column Data Type", "Inline List", "Validators", "Required",
          "Read Only Record", "Domain IDO Name", "Domain Property", "Domain List Properties",
          "Label String ID", "Input Mask", "Prompt Char", "Justify", "Date Format",
          "Binary Format", "IME Char Set", "Boolean True", "Boolean False", "Decimal Position",
          "*Read Only", "Upper Case", "Property Value", "Arguments", "Subcollection Name",
          "Validate Immediately", "Validate Immediately Prompt", "Property Value", ""]

# Columns that are quoted string fields even when empty vs. columns left bare/unquoted, for
# DATA rows only - confirmed against a real data row in ToExcel_IdoProperties_4.csv. The
# header row (see q_header below) quotes every column instead, a different convention.
QUOTED_COLS = {1, 2, 3, 4, 5, 7, 8, 11, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
               30, 31, 34, 35, 36, 37, 39, 40}

def q(col_idx, value):
    value = "" if value is None else str(value)
    if col_idx in QUOTED_COLS:
        return f'"{value}"'
    return value

def q_header(i, value):
    # Confirmed from the live export: every header cell is quoted except the trailing blank
    # column - unlike data rows, this doesn't follow QUOTED_COLS at all.
    return "" if i == len(HEADER) - 1 else f'"{value}"'

def build_row(seq, col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc):
    # Column Data Type defaults to blank - confirmed directly against the live
    # ToExcel_IdoProperties_4 export: every one of the 71 custom eCMRs properties (Status,
    # Item, Vendor, JobNum, ...) has a blank Column Data Type. It's only ever populated on
    # the 7 system-generated properties (UsernameType, CurrentDateType, ...), which this CSV
    # deliberately excludes. The earlier "defaults to dtype, JobBase override for job_num"
    # logic was an untested guess - job_num's own real property is blank too.
    default_value = "AUTONUMBER(STEP(1))" if col == "cmr_num" else ""
    col_data_type = COLDTYPE_OVERRIDES.get(col, "")
    property_class = PROPERTY_CLASS_OVERRIDES.get(col, "")
    inline_list = INLINE_LISTS.get(col, "")
    # *Read Only (unlike Read Only Record) is confirmed from the live export to be set ONLY
    # on the 5 auto-generated system properties (CreatedBy/UpdatedBy/CreateDate/RecordDate/
    # RowPointer) - never on any custom property, read-only or not. This CSV only ever emits
    # custom properties, so *Read Only must always stay blank here; the real read-only flag
    # for a custom property is Read Only Record alone. A prior version of this generator wrote
    # the same `readonly` value into both columns, which would have incorrectly set
    # *Read Only=1 on every read-only custom property (CloseDate, ClosedBy, the description
    # companion fields, ...).
    fields = [
        "1", pname, IDO_NAME, property_class, TABLE_ALIAS, TABLE_NAME, "Bound to Column", col, desc,
        str(seq), "0", dtype, length, "", default_value, col_data_type, inline_list, "", required, readonly,
        "", "", "", labelid, "", "", "", "", "", "", "", "", decimal, "", "", "", "", "", "", "", "", "",
    ]
    return "\t".join(q(i, v) for i, v in enumerate(fields))

def main():
    lines = ["\t".join(q_header(i, v) for i, v in enumerate(HEADER))]
    for seq, (col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc) in enumerate(FIELDS, start=8):
        lines.append(build_row(seq, col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc))
    text = "\r\n".join(lines) + "\r\n"
    with open("exports/ecmrs_ido_properties_import.csv", "wb") as fh:
        fh.write(b"\xff\xfe" + text.encode("utf-16-le"))
    print(f"Wrote {len(FIELDS)} rows (Sequence 8-{7 + len(FIELDS)}) to ecmrs_ido_properties_import.csv")

if __name__ == "__main__":
    main()
