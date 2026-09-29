#!/usr/bin/env python3
"""Builds exports/eCMRs_v2.XML from the form currently on TRN (original/eCMRs.trn.original.xml).

Why a patch script and not scripts/generate_form.py: the form on TRN carries hand edits made in
Application Studio (the notes sidebars, Item Desc, the _v2 component names) that the old
generator can no longer reproduce. This script edits that export's text in place (AGENTS.md
rule 6: no XML re-serializing), so everything already working on TRN stays exactly as it is and
only the changes below are applied.

What it changes (v1 -> v2):
  1-2. Dept -> Dept Description and Work Center -> WC Description auto-fill: Validators
     "SetPropertyFromList(DeptDescription, Description)" on c_dept and
     "SetPropertyFromList(WcDescription, Description)" on c_wc. Infor's generic validator
     (used on the live Incidents form, reason grid): copies one column of the selected
     dropdown row (Description, already in the SLDepts/SLWcs list sources) into one property,
     and writes nothing else. The Dept(...) validator was tried first and failed on TRN
     2026-09-29 - it also writes DivName/OfcAddr4, which ue_ecmrs doesn't have
     ("Bad SETPROPERTIES specification in validator Dept: this cache property DivName not in
     cache"), even with its second argument left empty. WcDesc(...) is the same kind of
     validator, so it's replaced too.
  3. Reason Code / Cause Code: PropertyClassName QCReasonCode/QCCauseCode removed. Those classes
     filter on QC_MRRs fields (FP(...)) that ue_ecmrs does not have, which caused the
     "'FP' is not a recognized built-in function name" error and the empty Reason list. The
     lists now come from each property's own Inline List (scripts/generate_ido_import.py
     INLINE_LISTS, codes taken from the live QC_MRRs dropdowns). Both components are renamed
     c_reason_code_v2 / c_cause_code_v2 so FormSync creates them fresh - re-importing the old
     names kept the class on TRN.
  4. Implementation section re-laid out on one grid: checkbox | Reviewer ID | Reviewer, with
     Closed / Close Date / Closed By as the last row of the same grid.
  5. Internal Review Date moved back to Engineering (where the original QC_CMRs form has it,
     next to Disposition) instead of hanging off the bottom of Implementation.
  6. PO Line list back to DISPLAY(1,2,3). DISPLAY(2,1,3) (show Item first) made the combo
     write the Item into PoLine - confirmed on TRN 2026-09-29: PO Line showed 92185-001-17 and
     save failed with "Data length for Notify (12) is greater than effective length (10)".
     The combo writes the first DISPLAYed column, not the first PROPERTIES() entry.
  7. Every bound field gets Caption C(<its label>), the same way Infor's own forms link a field
     to its label, so error messages name the right field (the one above said "Notify"
     because the fields had no caption of their own).
  8. Closed checkbox script (SetCloseInfo) fixed: it used ThisForm.UserName, which doesn't exist
     ("Error compiling script EvHandler_SetCloseInfo_0", TRN 2026-09-29). Now the same as the
     working original QC_CMRs form: the script raises event SetClosedBy, a ResponseType 22
     handler doing SETPROPVALUES(ClosedBy=USERNAME()), and uses Namespace SyteLine.GlobalScripts
     like the original.
  9. Cut-off labels (TRN screenshot 2026-09-29): Reason Code, Vendor Name and Next Assy
     Description were one line high, Internal Review Date needed three lines. Heights raised
     (1.8 = two lines, like QC Disposition; 2.7 = three), and "Next Assy Description:" is
     shortened to "Next Assy Desc:" to fit its narrow column, like "Item Desc:".
  10. CMR Num is CMR-YYMMDD-HHMMSS (e.g. CMR-260929-111742), set by the form when you click New:
     StdObjectNewCompleted script (same pattern as the Incidents form's StdObjectNewCompleted)
     doing SetCurrentObjectPropertyPlusModifyRefresh("CmrNum", "CMR-" & Now...). Replaces the
     IDO's AUTONUMBER(STEP(1)), which repeated numbers (PK_ue_ecmrs error, 2026-09-29). The IDO
     Default Value can't format a date, so this has to be on the form. Grid column widened to
     fit the 17 characters.
  11. Form help: right-click → Help said "Invalid URL string, or no help is defined for this form
     or field" (TRN 2026-09-29) - the form had no HelpFileName. Now points to the same Infor help
     topic as the original QC_CMRs form (qc_cmrs.htm), with the HelpFileName placed before
     HelpContextID as in that export. Fields use the form's help, as on Infor's own forms.
     Right-click Help can only open Infor's help site: SyteLine puts its help address in front of
     any HelpFileName (a file:/// link became docs.infor.com/.../file:///S:/...).
  12. Help button next to Notify: opens the eCMRs help pages (docs/help/) from the repo copy on
     the S: drive (HELP_BUTTON_URL) through an OpenEcmrsHelp event, ResponseType 39 URL(...) - the
     response Infor's forms use for links. Right-click Help stays on the Infor QC_CMRs topic.
  13. Team feedback (TRN review, 2026-09-29):
     a. Item Desc is wider (to the Dept Description's right edge) so long descriptions show.
     b. Top Level PN is hidden (label and field, Hidden=True). Not deleted: FormSync only applies
        what is in the file, so a component left out of the file would stay on the form. The
        top_level_pn column and TopLevelPn property stay, so existing data is kept.
     c. Requested Action: and General Note: labels sit directly above the top-left corner of
        their text boxes (they floated to the left, away from the boxes). Requested Action's box
        starts one row lower to make room.
  14. Dept / WC Description fill in as soon as a Dept / Work Center is picked, not on save:
     Flags 1 -> 33 on c_dept and c_wc. Bit 32 is Validate Immediately - every Infor component with
     a validator has it (Service Orders DeptEdit: Flags 33; QC_CreateChangeRequest DeptEdit:
     8225 = 8192 + 32 + 1). Without it the validator only runs when the record is saved.
  15. Notify sends the email, the same way the original QC_CMRs form did: raises the Enflite
     application event ENF_NotifyUserWithCMR (ResponseType 43, same parameters CmrNum, EAddres,
     Priority). EAddres is the Assigned employee's Username (the e-mail address in this tenant),
     looked up from SLEmployees by AssignedEmpNum into a form variable first (ResponseType 49,
     SETV - no SETP, so nothing on the record is changed). Replaces the NotifyEngineering
     placeholder message.
  16. Right-click -> Help opens the eCMRs help: handlers for the standard events
     StdFormComponentHelp (right-click a field -> Help) and StdFormHelp (the form's Help).
     A script sets the variable EcmrsHelpUrl to the page for the right-clicked component
     (docs/help/c/<component>.html, built by scripts/build_help.py for every component on the
     form) and a ResponseType 39 URL(V(EcmrsHelpUrl)) opens it. HelpFileName stays as the Infor
     topic, used if SyteLine still runs its own help after ours. Confirmed on TRN 2026-09-29: the
     handler runs (the browser then shows SyteLine's GetFile.aspx page for the file: address).
  18. Help button hidden (Hidden=True): right-click -> Help does the job (team, 2026-09-29). Kept
     in the file rather than dropped, because FormSync doesn't delete a component that is missing
     from the file - TRN already has it. HELP_BUTTON_URL is still the help address.
  17. IDM documents widget: the business-context handlers every Infor form uses (QC_CMRs, Lots,
     Service Orders, Customer Order Lines): StdFormPredisplay loads the form's message template
     (SLFormExtMsgEntities.LoadJSONVar, form name eCMRs) and StdObjectSelectCurrentCompleted
     fills it for the current record and sends it (JSONMSGTYPE(inforBusinessContext)). What the
     widget looks up (the Item) is set in SyteLine for the form name eCMRs - see the Implementation
     Plan.
  Tab order is renumbered for the moved components so tabbing follows the screen.

Run:   python3 tools/apply_form_changes.py          (writes exports/eCMRs_v2.XML)
Check: python3 tools/apply_form_changes.py --check  (fails if the committed file differs)
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "original", "eCMRs.trn.original.xml")
OUT = os.path.join(ROOT, "exports", "eCMRs_v2.XML")
IND = "               "  # indentation of a Component's child tags in the export

# Implementation grid (form units). Rows share these columns so the IDs, names, dates and
# Closed By all line up under each other.
IMPL_Y = {"planning": 83.3, "purchasing": 85.1, "cm": 86.9}
CLOSE_Y = 89.1
X_CHECK, W_CHECK = 2, 16.5
X_LBL1, W_LBL1 = 19, 9.5      # "Reviewer ID:" / "Close Date:"
X_CTL1, W_CTL1 = 29, 12       # ID combo / Close Date
X_LBL2, W_LBL2 = 42, 9.5      # "Reviewer:" / "Closed By:"
X_CTL2, W_CTL2 = 52, 40       # reviewer name / Closed By

# Form help: Infor's online-help topic for the original QC_CMRs form (copied from its export).
HELP_URL = "default.html?helpcontent=mergedProjects/sl_qcs/forms/nonmaterial/qc_cmrs.htm"
# Right-click -> Help can only open Infor's help site: SyteLine puts its help address in front of
# any HelpFileName (a file:/// link became docs.infor.com/.../csbiolh/file:///S:/..., TRN 2026-09-29).
# The eCMRs help pages (docs/help/) open from the Help button instead: the repo copied to the shared
# drive S:/Engineering/Individual Folders/JSmith/eCMRs (spaces as %20).
HELP_BUTTON_URL = "file:///S:/Engineering/Individual%20Folders/JSmith/eCMRs/docs/help/index.html"

# Right-click -> Help pages, one per form component (docs/help/c/<component>.html redirects to
# the field's page), next to HELP_BUTTON_URL.
HELP_BASE_URL = HELP_BUTTON_URL.rsplit("/", 1)[0] + "/"

# Engineering: new row under Reviewer, left column (the Eng RCA Notes box sits at x>=44).
IRD_Y = 78.2


def fmt(v):
    return f"{v:g}"


class Form:
    def __init__(self, text):
        self.text = text

    def _span(self, name):
        m = re.search(rf'<Component Name="{re.escape(name)}">.*?</Component>', self.text, re.S)
        if not m:
            raise SystemExit(f"component not found: {name}")
        return m.start(), m.end()

    def _edit(self, name, fn):
        a, b = self._span(name)
        block = self.text[a:b]
        new = fn(block)
        self.text = self.text[:a] + new + self.text[b:]

    def set(self, name, tag, value):
        def fn(block):
            new, n = re.subn(rf"<{tag}>[^<]*</{tag}>", f"<{tag}>{value}</{tag}>", block, count=1)
            if n != 1:
                raise SystemExit(f"{name}: no <{tag}>")
            return new
        self._edit(name, fn)

    def remove(self, name, tag):
        def fn(block):
            new, n = re.subn(rf"\r\n *<{tag}>[^<]*</{tag}>", "", block, count=1)
            if n != 1:
                raise SystemExit(f"{name}: no <{tag}> to remove")
            return new
        self._edit(name, fn)

    def insert_after(self, name, after_tag, tag, value):
        def fn(block):
            if f"<{tag}>" in block:
                raise SystemExit(f"{name}: already has <{tag}>")
            new, n = re.subn(rf"(<{after_tag}>[^<]*</{after_tag}>)",
                             rf"\1\r\n{IND}<{tag}>{value}</{tag}>", block, count=1)
            if n != 1:
                raise SystemExit(f"{name}: no <{after_tag}>")
            return new
        self._edit(name, fn)

    def place(self, name, y=None, x=None, w=None, h=None, tab=None):
        if y is not None:
            self.set(name, "TopPos", fmt(y))
        if x is not None:
            self.set(name, "LeftPos", fmt(x))
        if w is not None:
            self.set(name, "Width", fmt(w))
        if h is not None:
            self.set(name, "Height", fmt(h))
        if tab is not None:
            self.set(name, "TabOrder", str(tab))

    def rename(self, old, new):
        a, b = self._span(old)
        if f'<Component Name="{new}">' in self.text:
            raise SystemExit(f"component already exists: {new}")
        self.text = self.text[:a] + self.text[a:b].replace(f'Name="{old}"', f'Name="{new}"', 1) + self.text[b:]

    def caption(self, name, text):
        self.set(name, "Caption", text)
        self.set(name, "EffectiveCaption", text)


def build(text):
    f = Form(text)

    # 1-2. Description auto-fill through real validators (Validators sits right after Width
    # on components without a Caption, same order as Infor's own exports).
    f.insert_after("c_dept", "Width", "Validators", "SetPropertyFromList(DeptDescription, Description)")
    f.insert_after("c_wc", "Width", "Validators", "SetPropertyFromList(WcDescription, Description)")

    # 3. Reason/Cause: drop the MRR-only property classes; the Inline List drives the list.
    # Renamed to *_v2 as well: confirmed on TRN (2026-09-28) that importing the same component
    # name without <PropertyClassName> left the old QCCauseCode class on the live component
    # (FormSync doesn't clear a setting that is simply missing from the file), so the 'FP'
    # error stayed. A new name makes FormSync create the component fresh. The class-derived
    # EffectiveCaption (sCode / sRSQCCause) goes too.
    for col in ("reason_code", "cause_code"):
        f.remove(f"c_{col}", "PropertyClassName")
        f.remove(f"c_{col}", "EffectiveCaption")
        f.rename(f"c_{col}", f"c_{col}_v2")

    # 4. Implementation grid. Tab order: after Internal Review Date (54) and Eng RCA Notes (55).
    tab = 56
    for key, check, empnum, name in [
        ("planning", "c_planning_complete", "planning_reviewer_empnum", "planning_reviewer_name"),
        ("purchasing", "c_purchasing_complete", "purchasing_reviewer_empnum", "purchasing_reviewer_name"),
        ("cm", "c_cm_complete", "cm_reviewer_empnum", "cm_reviewer_name"),
    ]:
        y = IMPL_Y[key]
        f.place(check, y=y, x=X_CHECK, w=W_CHECK, tab=tab)
        f.place(f"l_{empnum}", y=y + 0.15, x=X_LBL1, w=W_LBL1)
        f.caption(f"l_{empnum}", "Reviewer ID:")
        f.place(f"c_{empnum}_v2", y=y, x=X_CTL1, w=W_CTL1, tab=tab + 1)
        f.place(f"l_{name}", y=y + 0.15, x=X_LBL2, w=W_LBL2)
        f.place(f"c_{name}_v2", y=y, x=X_CTL2, w=W_CTL2, tab=tab + 2)
        tab += 3
    # Closed / Close Date / Closed By: one row, same columns as the reviewer rows above.
    f.place("c_closed", y=CLOSE_Y, x=X_CHECK, w=W_CHECK, tab=65)
    f.place("l_close_date", y=CLOSE_Y + 0.15, x=X_LBL1, w=W_LBL1)
    f.place("c_close_date", y=CLOSE_Y, x=X_CTL1, w=W_CTL1, h=1.4, tab=66)
    f.place("l_closed_by", y=CLOSE_Y + 0.15, x=X_LBL2, w=W_LBL2)
    f.place("c_closed_by", y=CLOSE_Y, x=X_CTL2, w=W_CTL2, h=1.4, tab=67)
    # Keep the two late-added identity fields after that, unique tab numbers.
    f.place("c_next_assy_description", tab=68)
    f.place("c_vendor_name", tab=69)

    # 5. Internal Review Date back in Engineering. Two-line label, like "Drawing Revision:".
    f.place("l_internal_review_date", y=IRD_Y - 0.1, x=2, w=8.75, h=1.8)
    f.place("c_internal_review_date", y=IRD_Y, x=11.25, w=17.25, tab=54)
    f.place("c_eng_rca_notes", tab=55)

    # 6. PO Line writes PoLine again.
    f._edit("c_po_line", lambda b: b.replace(
        "PROPERTIES(PoLine,Item,PoNum) DISPLAY(2,1,3)", "PROPERTIES(PoLine,Item,PoNum) DISPLAY(1,2,3)"))

    # 7. Caption C(label) on every bound, caption-less field that has an l_<column> label.
    for m in list(re.finditer(r'<Component Name="(c_[a-z_]+?)(_v2)?">(.*?)</Component>', f.text, re.S)):
        name, col, block = m.group(1) + (m.group(2) or ""), m.group(1)[2:], m.group(3)
        label = f"l_{col}"
        if "<Caption>" in block or "<DataSource>object." not in block:
            continue
        if f'<Component Name="{label}">' not in f.text:
            continue
        f.insert_after(name, "Width", "Caption", f"C({label})")
    # The two that don't follow the l_<column> naming: Assigned ID shares the "Assigned:"
    # label with Assigned (username); Item Desc was hand-added in Application Studio.
    f.insert_after("c_assigned_empnum_v2", "Width", "Caption", "C(l_assigned_username)")
    f.insert_after("edit1_SITE", "Width", "Caption", "C(l_item1_SITE)")

    # 9. Cut-off labels.
    f.place("l_reason_code", y=55.95, h=1.8)
    f.place("l_vendor_name", y=21.4, h=1.8)
    f.place("l_next_assy_description", y=19.35, h=1.8)
    f.caption("l_next_assy_description", "Next Assy Desc:")
    f.place("l_internal_review_date", h=2.7)

    # 11. Form-level help (same topic as QC_CMRs).
    old = "         <Width>160</Width>\r\n         <HelpContextID>-1</HelpContextID>"
    if f.text.count(old) != 1:
        raise SystemExit("form-level Width/HelpContextID not found")
    f.text = f.text.replace(old, "         <Width>160</Width>\r\n         <HelpFileName>"
                            + HELP_URL + "</HelpFileName>\r\n         <HelpContextID>-1</HelpContextID>", 1)


    # 12. Help button (right of Notify) opening the eCMRs help pages at HELP_BUTTON_URL. Raises
    # OpenEcmrsHelp, a ResponseType 39 "URL(<address>) ( )" handler - the response Infor's
    # Customer Order Lines (tracking link) and Incidents / Service Orders (mailto) forms use.
    m = re.search(r'<Component Name="btn_notify">.*?</Component>', f.text, re.S)
    btn = m.group(0).replace('Name="btn_notify"', 'Name="btn_help"')
    for tag, val in [("LeftPos", "100"), ("Width", "12"), ("TabOrder", "70"), ("Caption", "Help"),
                     ("EventToGenerate", "OpenEcmrsHelp"), ("EffectiveCaption", "Help")]:
        btn, n = re.subn(rf"<{tag}>[^<]*</{tag}>", f"<{tag}>{val}</{tag}>", btn, count=1)
        if n != 1:
            raise SystemExit(f"btn_help: no <{tag}>")
    btn = btn.replace("BACKCOLOR(TYPE=0; ARGB=[255, 47,111,237]; )", "BACKCOLOR(TYPE=0; ARGB=[255, 26,26,26]; )")
    # 18. Hidden: right-click -> Help replaces it.
    btn, n = re.subn(r"<Hidden>False</Hidden>", "<Hidden>True</Hidden>", btn, count=1)
    if n != 1:
        raise SystemExit("btn_help: no <Hidden>")
    f.text = f.text[:m.end()] + "\r\n            " + btn + f.text[m.end():]
    ev_anchor = "         </EventHandlers>"
    f.text = f.text.replace(ev_anchor,
        '            <EventHandler Name="OpenEcmrsHelp" Sequence="0">\r\n'
        '               <ResponseType>39</ResponseType>\r\n'
        f'               <Response>URL({HELP_BUTTON_URL}) ( )</Response>\r\n'
        '            </EventHandler>\r\n' + ev_anchor, 1)

    # 10. CMR Num = CMR-YYMMDD-HHMMSS on New.
    new_script = (
        "SCRIPTTEXT(Option Explicit On\r\nOption Strict On\r\n\r\nImports System\r\n"
        "Imports Microsoft.VisualBasic\r\nImports Mongoose.IDO.Protocol\r\nImports Mongoose.Scripting\r\n\r\n"
        "Namespace SyteLine.GlobalScripts\r\nPublic Class EvHandler_StdObjectNewCompleted_0\r\n"
        "Inherits GlobalScript\r\n\r\nSub Main()\r\n"
        "            If ThisForm.PrimaryIDOCollection.CurrentItem.Properties.Item(\"CmrNum\").GetValueOfString(\"\") = \"\" Then\r\n"
        "                ThisForm.PrimaryIDOCollection.SetCurrentObjectPropertyPlusModifyRefresh(\"CmrNum\", "
        "\"CMR-\" &amp; DateTime.Now.ToString(\"yyMMdd-HHmmss\"))\r\n"
        "            End If\r\nEnd Sub\r\nEnd Class\r\nEnd Namespace\r\n) COLID(object)")
    anchor = "         </EventHandlers>"
    if anchor not in f.text or 'EventHandler Name="StdObjectNewCompleted"' in f.text:
        raise SystemExit("EventHandlers anchor missing or StdObjectNewCompleted already there")
    f.text = f.text.replace(anchor,
        '            <EventHandler Name="StdObjectNewCompleted" Sequence="0">\r\n'
        '               <ResponseType>33</ResponseType>\r\n'
        f'               <Response>{new_script}</Response>\r\n'
        '            </EventHandler>\r\n' + anchor, 1)
    # Grid: CMR Num column 10 -> 16 wide, shift the columns after it.
    grid = re.findall(r'<Component Name="(grid_[a-z_]+)">.*?<LeftPos>([\d.]+)</LeftPos>', f.text, re.S)
    f.set("grid_cmr_num", "Width", "16")
    for name, left in grid:
        if name != "grid_cmr_num":
            f.set(name, "LeftPos", fmt(float(left) + 6))

    # 8. SetCloseInfo: copy the original QC_CMRs pattern (see docstring).
    m = re.search(r'(<EventHandler Name="SetCloseInfo" Sequence="0">.*?<Response>)(.*?)'
                  r'(</Response>\s*<Response2>)(.*?)(</Response2>\s*</EventHandler>)', f.text, re.S)
    if not m:
        raise SystemExit("SetCloseInfo handler not found")
    script = html.unescape(m.group(2) + m.group(4))
    for old, new in [
        ("Namespace Mongoose.GlobalScripts", "Namespace SyteLine.GlobalScripts"),
        ('ThisForm.Components("c_closed_by").Text = ThisForm.UserName',
         'ThisForm.GenerateEvent("SetClosedBy")'),
    ]:
        if old not in script:
            raise SystemExit(f"SetCloseInfo: '{old}' not found")
        script = script.replace(old, new)
    esc = lambda t: html.escape(t, quote=False)
    handler = (m.group(1) + esc(script[:500]) + m.group(3) + esc(script[500:]) + m.group(5)
               + "\r\n            <EventHandler Name=\"SetClosedBy\" Sequence=\"0\">"
               + "\r\n               <ResponseType>22</ResponseType>"
               + "\r\n               <Response> SETPROPVALUES(ClosedBy=USERNAME())</Response>"
               + "\r\n            </EventHandler>")
    f.text = f.text[:m.start()] + handler + f.text[m.end():]

    # 13a. Item Desc to the Dept Description's right edge (11.25 + 40).
    f.place("edit1_SITE", w=51.25 - 11.625)
    # 13b. Top Level PN hidden (see docstring).
    for name in ("l_top_level_pn", "c_top_level_pn"):
        f.set(name, "Hidden", "True")
    # 13c. Labels above their text boxes, left-aligned with the box.
    f.place("l_requested_action", y=10.35, x=54, w=14, h=1)
    f.remove("l_requested_action", "Format")
    f.place("c_requested_action", y=11.6, h=23.6667 - 11.6)
    f.place("l_general_note", y=36.8, x=31.125, w=12, h=1)
    f.remove("l_general_note", "Format")

    # 14. Validate Immediately on the two description validators.
    for name in ("c_dept", "c_wc"):
        f.set(name, "Flags", "33")

    # 15-17. New event handlers and the variables they use.
    f.set("btn_notify", "EventToGenerate", "ENF_NotifyUser")
    m = re.search(r'\r\n            <EventHandler Name="NotifyEngineering" Sequence="0">.*?</EventHandler>', f.text, re.S)
    if not m:
        raise SystemExit("NotifyEngineering handler not found")
    f.text = f.text[:m.start()] + f.text[m.end():]
    help_script = (
        "SCRIPTTEXT(Option Explicit On\r\nOption Strict Off\r\n\r\nImports System\r\n"
        "Imports Microsoft.VisualBasic\r\nImports Mongoose.IDO.Protocol\r\nImports Mongoose.Scripting\r\n\r\n"
        "Namespace SyteLine.GlobalScripts\r\nPublic Class EvHandler_StdFormComponentHelp_0\r\n"
        "Inherits GlobalScript\r\n\r\nSub Main()\r\n"
        "            Dim page As String = \"index.html\"\r\n"
        "            Try\r\n"
        "                Dim frm As Object = ThisForm\r\n"
        "                Dim comp As String = CStr(frm.GetCurrentComponentName())\r\n"
        "                If comp &lt;&gt; \"\" Then page = \"c/\" &amp; comp &amp; \".html\"\r\n"
        "            Catch\r\n"
        "            End Try\r\n"
        f"            ThisForm.Variables(\"EcmrsHelpUrl\").Value = \"{HELP_BASE_URL}\" &amp; page\r\n"
        "            ReturnValue = \"0\"\r\n"
        "End Sub\r\nEnd Class\r\nEnd Namespace\r\n)")
    handlers = [
        ("ENF_NotifyUser", 0, 49,
         "SLEmployees( FILTER(EmpNum=FP(AssignedEmpNum)) SETV(EcmrsNotifyEmail=Username) )"),
        ("ENF_NotifyUser", 1, 43,
         "EVENT(ENF_NotifyUserWithCMR) PARMS(V(ehp1_ENF_NotifyUser0))  ERRORMESSAGE(FAIL TO SEND EMAIL! "
         "CHECK THE ASSIGNED EMPLOYEE, OR USER DOES NOT HAVE ACCESS TO THIS ACTION.) SUCCESSMESSAGE(EMAIL SENT!)"),
        ("StdFormComponentHelp", 0, 33, help_script),
        ("StdFormComponentHelp", 1, 39, "URL(V(EcmrsHelpUrl)) ( )"),
        ("StdFormHelp", 0, 39, f"URL({HELP_BUTTON_URL}) ( )"),
        ("StdFormPredisplay", 0, 0,
         "SLFormExtMsgEntities.LoadJSONVar( PARMS(VAR eCMRs, RVAR V(JSONVarNotInterpretWithLIT)) )"),
        ("StdFormPredisplay", 1, 22, "SETVARVALUES(JSONVarNotInterpret=V(JSONVarNotInterpretWithLIT))"),
        ("StdObjectSelectCurrentCompleted", 0, 0,
         "SLFormExtMsgEntities.FormatJSONVar( PARMS(VAR eCMRs, VAR V(JSONVarNotInterpret), "
         "RVAR V(JSONVarWithLIT)) COLID(object) )"),
        ("StdObjectSelectCurrentCompleted", 1, 22, "SETVARVALUES(JSONVar=V(JSONVarWithLIT)) COLID(object)"),
        ("StdObjectSelectCurrentCompleted", 2, 47,
         "JSONMSGTYPE(inforBusinessContext) JSONPAYLOAD(V(JSONVar)) JSONMSGTOCHLD()  COLID(object)"),
    ]
    for name, _, _, _ in handlers:
        if f'<EventHandler Name="{name}"' in f.text:
            raise SystemExit(f"handler already there: {name}")
    anchor = "         </EventHandlers>"
    f.text = f.text.replace(anchor, "".join(
        f'            <EventHandler Name="{name}" Sequence="{seq}">\r\n'
        f'               <ResponseType>{rt}</ResponseType>\r\n'
        f'               <Response>{resp}</Response>\r\n'
        '            </EventHandler>\r\n' for name, seq, rt, resp in handlers) + anchor, 1)
    variables = [
        ("ehp1_ENF_NotifyUser0", "CmrNum=P(CmrNum), EAddres=V(EcmrsNotifyEmail), Priority = P(Priority)"),
        ("EcmrsNotifyEmail", ""),
        ("EcmrsHelpUrl", HELP_BUTTON_URL),
    ]
    anchor = "         </Variables>"
    if f.text.count(anchor) != 1:
        raise SystemExit("Variables anchor not found")
    f.text = f.text.replace(anchor, "".join(
        f'            <Variable Name="{name}">\r\n'
        + (f'               <Value>{val}</Value>\r\n' if val else '               <Value />\r\n')
        + '               <Value2 />\r\n               <Value3 />\r\n               <Description />\r\n'
        '            </Variable>\r\n' for name, val in variables) + anchor, 1)

    return f.text


def main():
    raw = open(SRC, "rb").read()
    if not raw.startswith(b"\xef\xbb\xbf") or b"\r\n" not in raw:
        raise SystemExit("source must be UTF-8 with BOM and CRLF")
    text = build(raw[3:].decode("utf-8"))
    data = b"\xef\xbb\xbf" + text.encode("utf-8")
    if "--check" in sys.argv:
        if open(OUT, "rb").read() != data:
            raise SystemExit(f"{OUT} is out of date - re-run without --check")
        print("OK: exports/eCMRs_v2.XML matches the script")
        return
    with open(OUT, "wb") as fh:
        fh.write(data)
    print(f"Wrote {os.path.relpath(OUT, ROOT)} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
