#!/usr/bin/env python3
"""Pre-flight check: diffs the generated form XML's writable object.* bindings against our
own schema's Read Only flags, so a self-inflicted version of the Rule #1B lockup (see
docs/troubleshooting.md) gets caught here instead of live. This can only catch a mismatch in
OUR OWN design files - it cannot see the live IDO's actual Read Only flag in Application
Studio, which is why docs/deploy-checklist.md (a separate, manual step) still exists.

Run after generate_form.py, before committing:
    python3 scripts/generate_form.py exports/eCMRs_v1.XML && python3 scripts/validate_schema_consistency.py
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from generate_schema_csv import FIELDS

# FIELDS tuples are (col, pname, dtype, length, decimal, coldtype, labelid, required, readonly, desc)
READONLY_BY_COL = {f[0]: (f[8] == "1") for f in FIELDS}
PNAME_BY_COL = {f[0]: f[1] for f in FIELDS}
COL_BY_PNAME = {f[1]: f[0] for f in FIELDS}

def main():
    with open("exports/eCMRs_v1.XML", encoding="utf-8") as fh:
        text = fh.read()

    errors = []
    for comp in re.finditer(r'<Component Name="(\w+)">(.*?)</Component>', text, re.S):
        name, body = comp.group(1), comp.group(2)
        ds = re.search(r"<DataSource>object\.(\w+)</DataSource>", body)
        if not ds:
            continue
        pname = ds.group(1)
        col = COL_BY_PNAME.get(pname)
        if col is None:
            continue  # a system/auto-generated property (CreatedBy, CreateDate, ...) - not in FIELDS
        binding = re.search(r"<Binding>(\d+)</Binding>", body)
        readonly_attr = re.search(r"<ReadOnly>(True|False)</ReadOnly>", body)
        form_writable = binding and binding.group(1) == "1" and readonly_attr and readonly_attr.group(1) == "False"
        if form_writable and READONLY_BY_COL.get(col):
            errors.append(
                f"{name}: binds writably (Binding=1, ReadOnly=False) to object.{pname}, "
                f"but generate_schema_csv.py still marks {col}'s Read Only flag as \"1\". "
                f"Either the form shouldn't write here, or FIELDS needs its Read Only cleared "
                f"(and this property added to REPURPOSED_WRITABLE if it used to be a read-only "
                f"companion - see docs/troubleshooting.md Rule #1B)."
            )

    if errors:
        print(f"FAILED: {len(errors)} schema/form mismatch(es) found:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK: checked {len(PNAME_BY_COL)} known properties against the form's object.* bindings, no mismatches.")

if __name__ == "__main__":
    main()
