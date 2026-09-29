// Content for the eCMRs implementation plan deck. Edit this file, not build_impl_deck.js.
// Keep it in step with docs/Implementation-Plan.md (same scope, BRD, design tables, steps).
// Rebuild: cd plan && npm install && npm run build && npm run pdf
const b = (text) => ({ text, options: { bold: true } });
const t = (text) => ({ text });

module.exports = {
  fileName: "eCMRs_Implementation_Plan.pptx",
  title: "eCMRs plan",
  subtitle: "SyteLine - one Change Management Request form on its own table and IDO. Live on TRN; next: production",

  phases: [
    ["Scope", "Everything the three legacy CMR screens and the SOW need, on one form."],
    ["Design", "New table and IDO ue_ecmrs, form layout, lookups and scripts."],
    ["Develop", "Built on TRN first — never directly in production. Done."],
    ["Staging", "Tested end to end on TRN; exports checked against the repo. Done 2026-09-29."],
    ["Launch", "Same table, IDO and form in production, from the TRN exports. Next."],
    ["Test", "Full checklist passed on TRN; smoke test in production."],
    ["Optimize", "Two weeks of follow-up with Quality, Engineering, Planning, Purchasing, CM."],
  ],

  scope: {
    sub: "Replace three legacy CMR screens with one form, built on its own table.",
    flow: [
      ["Phase 0", "Requirements: QC_CMRs, Create Change Request, Change Request Mgmt, the SOW"],
      ["Phase A", "Table + IDO ue_ecmrs: 76 columns, no Infor objects changed"],
      ["Phase B", "Form: eCMRs_v2.XML through FormSync"],
      ["Phase C", "Testing on TRN: done 2026-09-29"],
      ["Phase D", "Rollout to production"],
    ],
  },

  brd: [
    [b("One form"), t(" for everything the three legacy CMR screens hold, created with "), b("New")],
    [b("Own table and IDO"), t(" (ue_ecmrs): no dependency on rs_cmr / rs_crcvr")],
    [b("Unique CMR number"), t(" CMR-YYMMDD-HHMMSS, set on New; never repeats")],
    [t("Lookups fill descriptions: Item, Next Assy, Vendor, Dept, Work Center, every "), b("Reviewer ID")],
    [b("Initial Change"), t(" ticks the right Req checkboxes; "), b("Reason / Cause Codes"), t(" from the QC_MRRs lists")],
    [t("Ticking "), b("Closed"), t(" sets Close Date and Closed By")],
    [t("No changes to Infor standard objects; Enflite naming ("), b("ue_"), t(", ENF)")],
    [t("Built and tested on "), b("TRN"), t(" first; delivered through "), b("FormSync"), t("; kept in "), b("GitHub"), t(" (Enflite/eCMRs)")],
  ],

  mockup: null,

  trnSteps: [
    "Build table and IDO ue_ecmrs",
    "Set Inline Lists, Read Only, CmrNum; Check In",
    "Import eCMRs_v2.XML through FormSync; test every field",
    "Export SQL Columns + IDO Properties as the production source",
  ],
  prodSteps: [
    "Import the same columns and properties from the TRN exports",
    "Check In; verify production against TRN with one script",
    "Import the same eCMRs_v2.XML through FormSync",
    "Smoke test, then hand over to the team",
  ],

  design: [
    {
      sub: "A new table and IDO — nothing Infor owns is changed.",
      label: "Table and IDO",
      cols: [["Object", 2.4], ["Name", 2.6], ["Notes", 6.5]],
      rows: [
        ["SQL table", "ue_ecmrs", "76 columns (+7 system). Text columns char(255)"],
        ["Key", "cmr_num", "nvarchar, Primary Key, no default"],
        ["IDO", "ue_ecmrs (alias ec)", "One property per column; lengths equal SQL"],
        ["Key property", "CmrNum", "String, 255, Default Value blank"],
        ["Lists", "Inline Lists", "Status, Priority, Initial Change, Dispositions, Reason, Cause"],
        ["Auto-filled", "Read Only cleared", "Descriptions, reviewer names, Close Date, Closed By"],
      ],
      note: "Every column and property: docs/production-build-sheet.md",
    },
    {
      sub: "How the form fills things in — all in eCMRs_v2.XML.",
      label: "Form mechanisms",
      cols: [["On the form", 4.0], ["Mechanism", 7.5]],
      rows: [
        ["CMR Num on New", "StdObjectNewCompleted: CMR- + yyMMdd-HHmmss"],
        ["Item / Next Assy / Vendor → text", "DefaultFrom Item(...), VendNum(VendorName)"],
        ["Dept / Work Center → description", "Validators SetPropertyFromList(..., Description)"],
        ["Reviewer ID → name (×6)", "DefaultFrom EmpNum(<name>) on SLEmployees"],
        ["Initial Change → Req boxes", "DefaultFrom Change(ReqCosting, ...)"],
        ["Closed → date, user", "SetCloseInfo + SetClosedBy scripts"],
      ],
      note: "Why each one is built this way, and what failed first: docs/troubleshooting.md",
    },
  ],

  develop: [
    [t("Create table and IDO "), b("ue_ecmrs"), t(" in Application Studio (project ue_ENF)")],
    [t("Import columns and properties in the grids' own CSV format")],
    [t("Set "), b("Inline Lists"), t(", clear "), b("Read Only"), t(" on auto-filled fields, "), b("CmrNum"), t(" String / no default")],
    [b("Check In"), t(" the IDO — edits don't take effect until it is checked in")],
    [t("Build the form with tools/apply_form_changes.py; import through "), b("FormSync")],
  ],

  formsync: [
    "Keep the TRN v1 form in GitHub as the original (rollback copy)",
    "tools/apply_form_changes.py edits v1 in place into exports/eCMRs_v2.XML (--check)",
    "Import eCMRs_v2.XML into TRN through FormSync, at Site scope",
    "Use FormSync to bring the same XML to production at Launch",
  ],

  staging: [
    "Test every field on TRN — passed 2026-09-29",
    "Export SQL Columns + IDO Properties; compare_live_lengths.py: nothing to change",
    "make_production_imports.py builds the production files from those exports",
    "Team sign-off on TRN",
  ],

  launch: [
    "Scheduled window; check ue_ecmrs / eCMRs don't exist in production yet",
    "New table ue_ecmrs; import exports/production/ue_ecmrs_SqlColumns_import.csv",
    "New IDO ue_ecmrs (alias ec); import ue_ecmrs_IdoProperties_import.csv; Check In",
    "Export both grids; make_production_imports.py --verify: production matches TRN",
    "Import eCMRs_v2.XML through FormSync at Site scope; give users access as on TRN",
    "Smoke test: New, lookups, cascade, codes, save twice, Closed",
  ],
  rollback: [t("New form on a new table — take "), b("eCMRs"), t(" off the menu and keep using the legacy CMR screens, which are untouched. No data is lost.")],

  test: [
    "New gives CMR-YYMMDD-HHMMSS; saves work; no duplicate-key error",
    "Every lookup fills its description / name; PO Line shows the line number",
    "Initial Change ticks the right Req boxes; Reason / Cause codes list",
    "Serial # and LOT # list the item's serials / lots; Closed sets date and user",
    "Existing records open without errors; team signs off",
  ],

  optimize: [
    "Track issues from each team using eCMRs; fix on TRN first",
    "Decide: Notify, Reported By lookup, Assigned Buyer, Sub Assembly",
    "Retire the legacy CMR screens; decide on history migration",
    "Update the CMR procedure (QA-300-037); manager approval",
  ],
};
