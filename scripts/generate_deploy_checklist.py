#!/usr/bin/env python3
"""Generates docs/deploy-checklist.md - every manual Application Studio step Form Sync/CSV
import can't perform, derived directly from the schema so a new field needing one of these
can't silently ship without it. Every silent form-wide lockup found this project (see
docs/troubleshooting.md) was one of these two categories of missed manual step.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from generate_schema_csv import REPURPOSED_WRITABLE
from generate_ido_import import INLINE_LISTS

def main():
    lines = ["# eCMRs — Deploy Checklist", "",
             "**All done on TRN and confirmed working, 2026-09-29** (TRN exports in `reference/`). "
             "Use this list for production.", "",
             "Generated from the schema by `scripts/generate_deploy_checklist.py` - re-run it",
             "after adding a field to either tracking dict below, don't hand-edit this file.",
             "See `docs/troubleshooting.md` for why each category exists.", "",
             "**After every item below**: editing a property in the IDO Properties grid does",
             "not persist by itself - the IDO itself must be Check In'd (IDOs tab -> find the",
             "IDO -> Check In) before the change takes effect, even with no source control",
             "configured (a \"Source control integration is currently disabled\" popup is",
             "harmless - click OK, the local check-in still applies). Skipping this produced a",
             "real \"Missing property data type\" error on form save. See",
             "`docs/troubleshooting.md`.", ""]

    lines.append("## CMR Num key")
    lines.append("")
    lines.append("- [ ] `CmrNum` (cmr_num): **Data Type** `String`, **Length** 255, **Default Value** blank "
                 "(no `AUTONUMBER`). The form sets it to `CMR-YYMMDD-HHMMSS` on **New**. See "
                 "`docs/troubleshooting.md` (PK_ue_ecmrs).")
    lines.append("")
    lines.append("## Lengths and Property Class")
    lines.append("")
    lines.append("- [ ] Every IDO property's **Length** equals its SQL column's (`docs/length-fixes.md` "
                 "lists any difference - run `scripts/compare_live_lengths.py` on fresh exports).")
    lines.append("- [ ] `ReasonCode`, `CauseCode`: **Property Class** blank (the QC_MRRs classes cause the "
                 "`'FP'` error).")
    lines.append("")
    lines.append("## Read Only must be manually unchecked")
    lines.append("")
    lines.append("These are filled automatically by the form, which can't write a Read Only property. "
                 "Form Sync re-import never touches an existing property's Read Only flag.")
    lines.append("")
    for col, note in REPURPOSED_WRITABLE.items():
        pname = "".join(w.capitalize() for w in col.split("_"))
        lines.append(f"- [ ] `{pname}` ({col}) - {note}")
    lines.append("")

    lines.append("## Inline List must be manually configured")
    lines.append("")
    lines.append("Cannot be pushed via CSV/Form Sync import at all - set the property's own")
    lines.append("`*Inline List` field directly to the `ENTRIES(...)` value below. `Property")
    lines.append("Class` stays blank - there is no separate class to create in this")
    lines.append("environment (confirmed live on Status; see docs/troubleshooting.md).")
    lines.append("")
    for col, values in INLINE_LISTS.items():
        pname = "".join(w.capitalize() for w in col.split("_"))
        if values:
            lines.append(f"- [ ] `{pname}` - Inline List: `{values}`")
        else:
            lines.append(f"- [ ] `{pname}` - Inline List: **not yet defined** - waiting on real values from the team, set `ENTRIES(...)` here once known.")
    lines.append("")

    with open("docs/deploy-checklist.md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Wrote docs/deploy-checklist.md: {len(REPURPOSED_WRITABLE)} Read Only items, "
          f"{len(INLINE_LISTS)} Inline List items")

if __name__ == "__main__":
    main()
