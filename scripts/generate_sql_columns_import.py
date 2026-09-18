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

SYSTEM_TYPE = {
    "Integer": "int",
    "String": "nvarchar",
    "Byte": "tinyint",
    "Date": "datetime",
    "Decimal": "decimal",
    "NumSortedString": "nvarchar",
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
    fields = [
        col, SCHEMA, TABLE_NAME, coldtype, SYSTEM_TYPE.get(dtype, dtype), length, decimal,
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
