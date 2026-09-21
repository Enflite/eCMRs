#!/usr/bin/env python3
"""Generates exports/ecmrs_sql_columns_import.csv - matches the real Sql Columns grid's
own "Export to Excel" format exactly (UTF-16, tab-delimited, same 14 columns).

Excludes cmr_num deliberately - it already exists on the table (created as nvarchar(999)
with a newid() default by mistake) and needs a direct manual fix, not a re-import that
could duplicate/conflict with the existing row. Column Id continues from 9 (cmr_num took 8).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from generate_schema_csv import FIELDS

SCHEMA = "dbo"
TABLE_NAME = "ue_ecmrs"

# Fallback base-type -> System Data Type, only used when a field has no coldtype at all.
SYSTEM_TYPE = {
    "Integer": "int",
    "Long Integer": "int",
    "String": "nvarchar",
    "Byte": "tinyint",
    "Date": "datetime",
    "Decimal": "decimal",
    "NumSortedString": "nvarchar",
}

# Column Data Type ("char", "decimal", or a custom class like ItemType/UsernameType) -> the
# real underlying SQL Server System Data Type. Confirmed directly against the live
# ToExcel_SqlColumns export: every existing "char" column (status, vendor, job_num, po_num,
# qc_disposition, ...) is System Data Type "char" too, not "nvarchar" - "String" never
# appears anywhere as a real Data Type. Custom *Type classes (ItemType, DescriptionType,
# WcType, DeptType, RevisionType, UsernameType, EmpNumType, LongDescType, QCLongCharType,
# QCPriorityType) all resolve to nvarchar, which is the default below for anything unlisted.
COLDTYPE_SYSTEM_TYPE = {
    "char": "char",
    "decimal": "decimal",
    "DateType": "datetime",
    "CurrentDateType": "datetime",
    "RowPointerType": "uniqueidentifier",
    "FlagNyType": "tinyint",
    "ListYesNoType": "tinyint",
}

HEADER = ["Column Name", "Schema", "Table Name", "Data Type", "System Data Type", "Length",
          "Decimal Position", "Default Value", "Is Nullable", "Primary Key", "Key Sequence",
          "Definition", "Is Computed", "Column Id", ""]

QUOTED_COLS = {0, 1, 2, 3, 4, 7, 8, 11, 14}

def q(col_idx, value):
    value = "" if value is None else str(value)
    if col_idx in QUOTED_COLS:
        return f'"{value}"'
    return value

def build_row(col_id, col, dtype, length, decimal, coldtype):
    # Data Type is the real Column Data Type (coldtype) - "char", "decimal", or a named class
    # like ItemType/UsernameType - never the generic placeholder "String", which the live
    # environment rejects outright ("String is not a valid Data Type"). Only falls back to
    # the generic dtype mapping for the handful of fields with no coldtype set.
    data_type = coldtype or dtype
    system_type = COLDTYPE_SYSTEM_TYPE.get(coldtype, SYSTEM_TYPE.get(dtype, "nvarchar")) if coldtype \
        else SYSTEM_TYPE.get(dtype, dtype)
    fields = [
        col, SCHEMA, TABLE_NAME, data_type, system_type, length, decimal,
        "", "YES", "0", "", "", "0", str(col_id), "",
    ]
    return "\t".join(q(i, v) for i, v in enumerate(fields))

def main():
    lines = ["\t".join(q(i, v) for i, v in enumerate(HEADER))]
    col_id = 9
    for (col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc) in FIELDS:
        if col == "cmr_num":
            continue  # already exists on the table, needs a manual fix instead
        lines.append(build_row(col_id, col, dtype, length, decimal, coldtype))
        col_id += 1
    text = "\r\n".join(lines) + "\r\n"
    with open("exports/ecmrs_sql_columns_import.csv", "wb") as fh:
        fh.write(b"\xff\xfe" + text.encode("utf-16-le"))
    print(f"Wrote {col_id - 9} rows (Column Id 9-{col_id - 1}) to ecmrs_sql_columns_import.csv - cmr_num excluded, needs a manual fix")

if __name__ == "__main__":
    main()
