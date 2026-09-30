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
  12. (Removed.) There was a Help button next to Notify; right-click -> Help replaced it (18).
  13. Team feedback (TRN review, 2026-09-29):
     a. Item Desc is wider (to the Dept Description's right edge) so long descriptions show.
     d. "Next Assy Desc:" -> "Assy Desc:" so the label fits its two lines (it showed "Next _Assy").
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
     A script sets the variable EcmrsHelpUrl to the page for the right-clicked component - found
     from an event parameter naming a form component, else GetCurrentComponentName() (the focused
     component), with ?via=parm|focus|none so the help server's log shows which one worked -
     (<HELP_SITE>/go/syteline/ecmrs/<component>, which the Enflite help redirects to that field's
     page) and a ResponseType 39 URL(V(EcmrsHelpUrl)) opens it. HELP_SITE is the hosted help
     (https://help-seven-xi.vercel.app, the Vercel production domain, 2026-09-30; before that a single-deployment
     address, and http://localhost:5173, the dev server). HelpFileName stays as the Infor
     topic, used if SyteLine still runs its own help after ours. Confirmed on TRN 2026-09-29: the
     handler runs (the browser then shows SyteLine's GetFile.aspx page for the file: address).
  18. Help button deleted (team, 2026-09-29: keep right-click -> Help, delete the button): btn_help
     and its OpenEcmrsHelp handler are no longer in the file, so production never gets them. TRN
     already has them: if FormSync leaves the button there, delete it once in Design Mode (Implementation
     Plan 4c). HELP_BUTTON_URL is still the help address used by right-click -> Help.
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
# Right-click -> Help opens the Enflite help (Enflite/help: React + Express + MongoDB), not a
# HelpFileName: SyteLine puts Infor's help address in front of any HelpFileName, and browsers won't
# open file: links from SyteLine (GetFile.aspx page, TRN 2026-09-29). The help's /go/<space>/<form>/
# <component> link redirects to the page for the component clicked (its aliases), else the form's page.
# HELP_SITE is the help's Vercel production domain (2026-09-30), which always serves the latest
# deployment (the help-212448u20-... address before it was one fixed deployment).
# Change it here, rebuild and re-import if the site moves.
HELP_SITE = "https://help-seven-xi.vercel.app"
HELP_FORM_URL = f"{HELP_SITE}/go/syteline/ecmrs"
HELP_BUTTON_URL = HELP_FORM_URL  # used by StdFormHelp and as EcmrsHelpUrl's start value
HELP_BASE_URL = HELP_FORM_URL + "/"

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
    f.place("l_internal_review_date", h=2.7)

    # 11. Form-level help (same topic as QC_CMRs).
    old = "         <Width>160</Width>\r\n         <HelpContextID>-1</HelpContextID>"
    if f.text.count(old) != 1:
        raise SystemExit("form-level Width/HelpContextID not found")
    f.text = f.text.replace(old, "         <Width>160</Width>\r\n         <HelpFileName>"
                            + HELP_URL + "</HelpFileName>\r\n         <HelpContextID>-1</HelpContextID>", 1)


    # 12. (Help button: removed 2026-09-29 - right-click -> Help replaces it, see 16 and 18.)
    # 13d. "Next Assy Desc:" wrapped to three lines in its narrow column and showed "Next _Assy"
    # (TRN screenshot 2026-09-29, the "dash under the Next Assy label"): Caption only.
    f.caption("l_next_assy_description", "Assy Desc:")

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
    # The same script runs for both help events: on TRN (2026-09-30) right-click a field -> Help
    # raised StdFormHelp, not StdFormComponentHelp (the help log showed /go/syteline/ecmrs with no
    # ?via=), so the form's Help also looks for the field. ev= says which event sent the link.
    # For StdFormHelp the script lives in a new event, ENF_FindHelpField, and StdFormHelp step 0 is
    # a one-line script raising it: importing the version where step 0 changed from a URL to a
    # script left TRN with the new type but the old URL(...) text ("SCRIPTTEXT keyword required for
    # InlineScript event handlers"). Step 0 keeps the inline-script type now, so importing this is a
    # text change there, and ENF_FindHelpField is new, so FormSync adds it whole.
    def help_script(event, ev):
        """The find-the-field script: the clicked component is an event parameter naming one, else
        the focused one. Plain text, escaped and split into <Response>/<Response2> when written.
        No comments: a VB comment starts with an apostrophe, and SyteLine reads ' in a response as
        a quote, so an unmatched one hides the keyword ("SCRIPTTEXT keyword required for InlineScript
        event handlers", TRN 2026-09-30). Infor's own inline scripts have none either."""
        return (
            "SCRIPTTEXT(Option Explicit On\r\nOption Strict Off\r\nImports System\r\nImports Mongoose.Scripting\r\n"
            f"Namespace SyteLine.GlobalScripts\r\nPublic Class EvHandler_{event}_0\r\nInherits GlobalScript\r\nSub Main()\r\n"
            'Dim f As Object = ThisForm, s As Object = Me, c As String = "", v As String = "none"\r\n'
            "Try\r\nFor i As Integer = 0 To CInt(s.ParameterCount) - 1\r\n"
            "Dim p As String = CStr(s.GetParameter(i))\r\n"
            'If c = "" AndAlso p <> "" Then\r\nTry\r\nIf f.Components(p) IsNot Nothing Then c = p : v = "parm"\r\n'
            "Catch\r\nEnd Try\r\nEnd If\r\nNext\r\nCatch\r\nEnd Try\r\n"
            'If c = "" Then\r\nTry\r\nc = CStr(f.GetCurrentComponentName())\r\nIf c <> "" Then v = "focus"\r\n'
            "Catch\r\nEnd Try\r\nEnd If\r\n"
            f'ThisForm.Variables("EcmrsHelpUrl").Value = "{HELP_FORM_URL}" & If(c = "", "", "/" & c) & "?via=" & v & "&ev={ev}"\r\n'
            'ReturnValue = "0"\r\nEnd Sub\r\nEnd Class\r\nEnd Namespace\r\n)')
    raise_find_field = (
        "SCRIPTTEXT(Option Explicit On\r\nOption Strict Off\r\nImports System\r\nImports Mongoose.Scripting\r\n"
        "Namespace SyteLine.GlobalScripts\r\nPublic Class EvHandler_StdFormHelp_0\r\nInherits GlobalScript\r\nSub Main()\r\n"
        'ThisForm.GenerateEvent("ENF_FindHelpField")\r\n'
        'ReturnValue = "0"\r\nEnd Sub\r\nEnd Class\r\nEnd Namespace\r\n)')

    # 2026-09-30: a version where both help events collected their parameters and raised
    # ENF_FindHelpField (with a new variable, EcmrsHelpParms) stopped the right-click menu from
    # loading on TRN. These are the handlers from Enflite/eCMRs#16, which load the menu and run.
    def response_xml(text):
        """<Response>, plus <Response2> for a long script: Infor's exports split a response at 500
        characters. Written escaped, so the split never falls inside an entity."""
        if text.startswith("SCRIPTTEXT(") and "'" in text:
            raise SystemExit("inline script contains an apostrophe: SyteLine reads it as a quote")
        head, tail = text[:500], text[500:]
        if head.endswith("\r"):
            head, tail = head[:-1], "\r" + tail
        if len(tail) > 480:
            raise SystemExit(f"response too long for <Response> + <Response2>: {len(text)} characters")
        out = f"               <Response>{html.escape(head, quote=False)}</Response>\r\n"
        if tail:
            out += f"               <Response2>{html.escape(tail, quote=False)}</Response2>\r\n"
        return out

    # StdFormHelp step 0 (2026-09-30): Infor documents StdFormHelp for Help > Current Form, but on TRN
    # right-click a field > Help raised it (ev=form). Diagnostic, in this handler only (no second
    # event: #17 raised one and the menu stopped opening): read what SyteLine passes with Infor's
    # CountParameter/GetParameter (the other scripts call "ParameterCount", which isn't Infor's
    # name, so they never saw any), ask GetCurrentComponentName() for the focused field, and put
    # it all in the link: via=focus|focusempty|focuserr, e=any error.
    # #20 (direct CountParameter/GetParameter + GetCurrentComponentName) failed to compile on TRN
    # with no detail ("Error compiling script EvHandler_StdFormHelp_0->"), so one call at a time:
    # this version has only ThisForm.GetCurrentComponentName(); parameters come back once it compiles.
    # Calls go straight to ThisForm and the script (CountParameter, GetParameter): SyteLine refuses
    # late-bound calls through an Object variable ("Attempt by method ...InvokeMethod... to access
    # method ...ScriptForm.Variables(System.String) failed", TRN 2026-09-30), which is also why the
    # older scripts' f.GetCurrentComponentName() and f.Components(p) never answered (via=none).
    form_help = (
        "SCRIPTTEXT(Option Explicit On\r\nOption Strict Off\r\nImports System\r\nImports Mongoose.Scripting\r\n"
        "Namespace SyteLine.GlobalScripts\r\nPublic Class EvHandler_StdFormHelp_0\r\nInherits GlobalScript\r\nSub Main()\r\n"
        'Dim c As String = "", v As String = "focusempty", e As String = ""\r\n'
        'Try\r\nc = ThisForm.GetCurrentComponentName()\r\nIf c <> "" Then v = "focus"\r\n'
        'Catch x As Exception\r\nv = "focuserr"\r\ne = x.Message\r\nEnd Try\r\n'
        f'ThisForm.Variables("EcmrsHelpUrl").Value = "{HELP_FORM_URL}" & If(c = "", "", "/" & c) & "?via=" & v'
        ' & "&ev=form&e=" & Uri.EscapeDataString(If(e.Length > 200, e.Substring(0, 200), e))\r\n'
        'ReturnValue = "0"\r\nEnd Sub\r\nEnd Class\r\nEnd Namespace\r\n)')

    handlers = [
        ("ENF_NotifyUser", 0, 49,
         "SLEmployees( FILTER(EmpNum=FP(AssignedEmpNum)) SETV(EcmrsNotifyEmail=Username) )"),
        ("ENF_NotifyUser", 1, 43,
         "EVENT(ENF_NotifyUserWithCMR) PARMS(V(ehp1_ENF_NotifyUser0))  ERRORMESSAGE(FAIL TO SEND EMAIL! "
         "CHECK THE ASSIGNED EMPLOYEE, OR USER DOES NOT HAVE ACCESS TO THIS ACTION.) SUCCESSMESSAGE(EMAIL SENT!)"),
        ("StdFormComponentHelp", 0, 33, help_script("StdFormComponentHelp", "field")),
        ("StdFormComponentHelp", 1, 39, "URL(V(EcmrsHelpUrl)) ( )"),
        ("StdFormHelp", 0, 33, form_help),
        ("StdFormHelp", 1, 39, "URL(V(EcmrsHelpUrl)) ( )"),
        ("ENF_FindHelpField", 0, 33, help_script("ENF_FindHelpField", "form")),
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
        + response_xml(resp) +
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
