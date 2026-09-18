#!/usr/bin/env python3
"""Generates the eCMRs Form Sync XML export from the field-mapping.md field list."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from generate_schema_csv import FIELDS as _SCHEMA_FIELDS

# snake_case column -> real PascalCase IDO Property Name, single source of truth
# shared with generate_schema_csv.py so the form's object.* bindings never drift
# out of sync with what's actually created in Application Studio.
PROP = {col: pname for (col, pname, *_rest) in _SCHEMA_FIELDS}
PROP["created_by"] = "CreatedBy"   # auto-generated system property, not in _SCHEMA_FIELDS
PROP["create_date"] = "CreateDate"  # auto-generated system property, not in _SCHEMA_FIELDS

TYPE_STATIC = 0
TYPE_EDIT = 1
TYPE_CHECKBOX = 5
TYPE_MULTILINE = 18
TYPE_DATE = 26
TYPE_COMBO = 27

LABEL_X_A, CTRL_X_A, CTRL_W = 2, 14.5, 24
LABEL_X_B, CTRL_X_B = 43, 55.5
ROW_H = 1.75
SECTION_H = 1.6
SPAN_X, SPAN_W = 14.5, 65

SL_ITEMS = "STDOLE SLItems( PROPERTIES(Item, Description) )"
SL_DEPTS = "STDOLE SLDepts( PROPERTIES(Dept, Description) )"
SL_WCS = "STDOLE SLWcs( PROPERTIES(Wc, Description) )"
SL_VENDORS = "STDOLE SLVendors( PROPERTIES(VendNum, Name) )"
SL_EMPLOYEES = "STDOLE SLEmployees( PROPERTIES(EmpNum,Name,Username) DISPLAY(1,2,3) RECORDCAP(0))"
# Real list sources adapted from the legacy form's own combos (CB_NextAssy, comboBox1_SITE,
# comboBox2_SITE, comboBox4_SITE), just swapped to our own property names.
SL_JOBMATLS_NEXT_ASSY = "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(Item)') RECORDCAP(0))"
SL_POITEMS_NUM = "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum=FP(PoNum)) RECORDCAP(0))"
SL_POITEMS_LINE = "STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum='P(PoNum)') RECORDCAP(0))"
# Job Num deliberately does NOT use an SLMatltrans combo (that's what had the leading-zero
# exact-match bug). The real JobOrders form's own Job field is a plain Edit bound to
# PropertyClassName JobBase, validated via MaintainFromSpec instead of a filtered combo -
# see job_num's LAYOUT entry below, which mimics that real mechanism directly.

# (label, column, ctype, list_source, readonly)
FIELD = "field"
PAIR = "pair"          # (fieldA, fieldB) sharing one row
SPAN = "span"          # full-width field (multiline)
HEADER = "header"

def f(label, column, ctype, list_source=None, readonly=False, maintain_from_spec=None):
    return (FIELD, label, column, ctype, list_source, readonly, maintain_from_spec)

LAYOUT = [
    # Everything below, up to QUALITY, sat in one continuous unlabeled area on the real
    # legacy form - it never had IDENTITY/CHANGE DETAILS/ITEM DETAILS/SOURCING/DATES
    # banners. Keeping it as one section here for the same reason: don't invent new
    # groupings the users aren't used to. QUALITY/ENGINEERING/IMPLEMENTATION below are
    # the only section banners that were ever real on the original form.
    (HEADER, "CMR DETAILS"),
    (PAIR, f("CMR Num:", "cmr_num", TYPE_EDIT, readonly=True), f("Status:", "status", TYPE_EDIT)),
    (PAIR, f("Workflow Status:", "workflow_status", TYPE_EDIT), f("Create Date:", "create_date", TYPE_DATE, readonly=True)),
    (PAIR, f("Created By:", "created_by", TYPE_EDIT, readonly=True), None),
    (PAIR, f("Priority:", "priority", TYPE_COMBO), f("Initial Change:", "initial_change", TYPE_COMBO)),
    (SPAN, f("Additional Changes:", "additional_changes", TYPE_MULTILINE)),
    (SPAN, f("Requested Action:", "requested_action", TYPE_MULTILINE)),
    (SPAN, f("General Note:", "general_note", TYPE_MULTILINE)),
    (PAIR, f("Item:", "item", TYPE_COMBO, SL_ITEMS), f("Item Description:", "item_description", TYPE_EDIT)),
    (PAIR, f("Work Center:", "wc", TYPE_COMBO, SL_WCS), f("WC Description:", "wc_description", TYPE_EDIT)),
    (PAIR, f("Dept:", "dept", TYPE_COMBO, SL_DEPTS), f("Dept Description:", "dept_description", TYPE_EDIT)),
    (PAIR, f("Drawing Revision:", "revision", TYPE_EDIT), f("Latest Revision:", "latest_revision", TYPE_EDIT)),
    (PAIR, f("Next Lvl Assy:", "next_assy_item", TYPE_COMBO, SL_JOBMATLS_NEXT_ASSY), f("Next Lvl Assy Desc:", "next_assy_description", TYPE_EDIT)),
    (PAIR, f("Qty:", "qty", TYPE_EDIT), None),
    (PAIR, f("Vendor:", "vendor", TYPE_COMBO, SL_VENDORS), f("Vendor Name:", "vendor_name", TYPE_EDIT)),
    (PAIR, f("Job Num:", "job_num", TYPE_EDIT, maintain_from_spec="JobOrders( PROPERTY(Job) )"), None),
    (PAIR, f("PO Num:", "po_num", TYPE_COMBO, SL_POITEMS_NUM), f("PO Line:", "po_line", TYPE_COMBO, SL_POITEMS_LINE)),
    (PAIR, f("RFQ Num:", "rfq_num", TYPE_EDIT), f("EO Num:", "eo_num", TYPE_EDIT)),
    (PAIR, f("MDL:", "mdl", TYPE_EDIT), f("POC:", "poc", TYPE_EDIT)),
    (PAIR, f("Due Date:", "due_date", TYPE_DATE), f("Internal Review Date:", "internal_review_date", TYPE_DATE)),
    (PAIR, f("Close Date:", "close_date", TYPE_DATE, readonly=True), f("Closed By:", "closed_by", TYPE_EDIT, readonly=True)),
    (PAIR, f("General Close Date:", "general_close_date", TYPE_DATE), f("General Closed By:", "general_closed_by", TYPE_EDIT)),
    (PAIR, f("Closed", "closed", TYPE_CHECKBOX), None),

    (HEADER, "QUALITY"),
    (PAIR, f("Req: Costing", "req_costing", TYPE_CHECKBOX), f("Costing Review Complete", "cost_review_complete", TYPE_CHECKBOX, readonly=True)),
    (PAIR, f("Req: Documentation", "req_documentation", TYPE_CHECKBOX), f("Documentation Review Complete", "documentation_review_complete", TYPE_CHECKBOX, readonly=True)),
    (PAIR, f("Req: Tool/Machine", "req_tool_machine", TYPE_CHECKBOX), f("Tool/Machine Review Complete", "machinery_review_complete", TYPE_CHECKBOX, readonly=True)),
    (PAIR, f("Req: Process", "req_process", TYPE_CHECKBOX), f("Process Review Complete", "process_review_complete", TYPE_CHECKBOX, readonly=True)),
    (PAIR, f("Req: Material", "req_material", TYPE_CHECKBOX), f("Material Review Complete", "material_review_complete", TYPE_CHECKBOX, readonly=True)),
    (PAIR, f("General Review Complete", "general_review_complete", TYPE_CHECKBOX, readonly=True), f("SOX Impacted", "sox_impacted", TYPE_CHECKBOX)),
    (PAIR, f("Hold On PO", "hold_on_po", TYPE_CHECKBOX), f("Authorization For Supplier To Ship", "auth_supplier_ship", TYPE_CHECKBOX)),
    (PAIR, f("QC Disposition:", "qc_disposition", TYPE_EDIT), None),
    (PAIR, f("QC Reviewer:", "qc_reviewer_empnum", TYPE_COMBO, SL_EMPLOYEES), f("QC Reviewer (Username):", "qc_reviewer_username", TYPE_EDIT)),
    (SPAN, f("QC RCA Notes:", "qc_rca_notes", TYPE_MULTILINE)),

    (HEADER, "ENGINEERING"),
    (PAIR, f("Engineering Disposition:", "eng_disposition", TYPE_EDIT), None),
    (PAIR, f("Engineering Reviewer:", "eng_reviewer_empnum", TYPE_COMBO, SL_EMPLOYEES), f("Eng Reviewer (Username):", "eng_reviewer_username", TYPE_EDIT)),
    (SPAN, f("Eng RCA Notes:", "eng_rca_notes", TYPE_MULTILINE)),

    (HEADER, "IMPLEMENTATION"),
    (PAIR, f("Assigned:", "assigned_empnum", TYPE_COMBO, SL_EMPLOYEES), f("Assigned (Username):", "assigned_username", TYPE_EDIT)),
    (PAIR, f("Assigned Buyer:", "assigned_buyer", TYPE_COMBO, SL_EMPLOYEES), None),
    (PAIR, f("Planning Reviewer:", "planning_reviewer_empnum", TYPE_COMBO, SL_EMPLOYEES), f("Planning Reviewer Name:", "planning_reviewer_name", TYPE_EDIT)),
    (PAIR, f("Planning Complete", "planning_complete", TYPE_CHECKBOX), None),
    (PAIR, f("Purchasing Reviewer:", "purchasing_reviewer_empnum", TYPE_COMBO, SL_EMPLOYEES), f("Purchasing Reviewer Name:", "purchasing_reviewer_name", TYPE_EDIT)),
    (PAIR, f("Purchasing Complete", "purchasing_complete", TYPE_CHECKBOX), None),
    (PAIR, f("CM Reviewer:", "cm_reviewer_empnum", TYPE_COMBO, SL_EMPLOYEES), f("CM Reviewer Name:", "cm_reviewer_name", TYPE_EDIT)),
    (PAIR, f("CM Complete", "cm_complete", TYPE_CHECKBOX), None),
]

# Grid pane (left side) - a master-list overview of multiple records at once, matching the
# real legacy form's FormCollectionGrid. Separate coordinate space from the detail pane below,
# scoped by ContainerName="FormCollectionGrid" and sized via the Form's own PaneZeroSize.
GRID_COLUMNS = [
    ("cmr_num", "CMR Num", 10),
    ("status", "Status", 14),
    ("priority", "Priority", 10),
    ("item", "Item", 14),
    ("dept", "Dept", 10),
    ("wc", "WC", 10),
    ("created_by", "Created By", 14),
    ("create_date", "Create Date", 14),
    ("due_date", "Due Date", 14),
    ("closed", "Closed", 8),
]
PANE_ZERO_SIZE = 40.25

# The SelectionEvent/EventHandler(ResponseType 49) companion-lookup mechanism that used to be
# driven from a LOOKUP_EVENTS list here was removed - confirmed live that triggering any of
# these (even the ones matching the legacy form's own working patterns byte-for-byte) jams the
# form's edit/commit pipeline for every other field afterward, combo or plain, forever. The 11
# description/name fields below are now plain editable fields instead (see LAYOUT).

_tab = [0]
def next_tab():
    _tab[0] += 1
    return _tab[0]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def emit_label(name, caption, x, y, w=CTRL_W - 2, seq=0):
    return f"""            <Component Name="{name}">
               <DeviceID>-1</DeviceID>
               <Type>{TYPE_STATIC}</Type>
               <TabOrder>0</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>{x:.3f}</LeftPos>
               <Height>1</Height>
               <ListHeight>0</ListHeight>
               <Width>{w}</Width>
               <Caption>{esc(caption)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>{seq}</ContainerSequence>
               <Binding>0</Binding>
               <Flags>3</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Format>JUSTIFY(R)</Format>
               <Post301Format />
               <EffectiveCaption>{esc(caption)}</EffectiveCaption>
            </Component>
"""

def emit_control(column, ctype, x, y, list_source, readonly, w=CTRL_W, h=1.4, maintain_from_spec=None):
    name = "c_" + column
    lines = [f'            <Component Name="{name}">',
             "               <DeviceID>-1</DeviceID>",
             f"               <Type>{ctype}</Type>",
             f"               <TabOrder>{next_tab()}</TabOrder>",
             f"               <TopPos>{y:.3f}</TopPos>",
             f"               <LeftPos>{x:.3f}</LeftPos>",
             f"               <Height>{h}</Height>",
             "               <ListHeight>0</ListHeight>",
             f"               <Width>{w}</Width>"]
    if ctype == TYPE_CHECKBOX:
        # caption lives on the checkbox itself; column's own label passed as caption via caller
        pass
    lines.append("               <MaxCharacters>0</MaxCharacters>")
    lines.append("               <ContainerName />")
    lines.append("               <ContainerSequence>0</ContainerSequence>")
    lines.append(f"               <DataSource>object.{PROP[column]}</DataSource>")
    lines.append("               <Binding>1</Binding>")
    if ctype == TYPE_CHECKBOX and column == "closed":
        lines.append("               <EventToGenerate>SetCloseInfo</EventToGenerate>")
    # SelectionEvent -> ResponseType 49 EventHandler (FILTER()  MOV()  SONON()  SETP()) removed:
    # confirmed live that using ANY combo wired to one of these jams the whole form's edit/commit
    # pipeline after a single use - every other field can then only be edited once before locking,
    # even fields with no lookup at all. ComboListSource-only combos (no SelectionEvent) are fine.
    if list_source:
        lines.append(f"               <ComboListSource>{esc(list_source)}</ComboListSource>")
    if maintain_from_spec:
        lines.append(f"               <MaintainFromSpec>{esc(maintain_from_spec)}</MaintainFromSpec>")
    lines.append("               <Flags>1</Flags>")
    lines.append(f"               <ReadOnly>{'True' if readonly else 'False'}</ReadOnly>")
    lines.append("               <Hidden>False</Hidden>")
    lines.append("               <HelpContextID>0</HelpContextID>")
    if column == "closed":
        lines.append("               <Post301Format>ENABLEDWHEN(V(cew_Closed))</Post301Format>")
    else:
        lines.append("               <Post301Format />")
    lines.append("            </Component>")
    return "\n".join(lines) + "\n"

def emit_field(label, column, ctype, list_source, readonly, x_label, x_ctrl, y, ctrl_w=CTRL_W, maintain_from_spec=None):
    out = ""
    if ctype == TYPE_CHECKBOX:
        # checkbox carries its own caption, no separate static label
        name = "c_" + column
        out += f"""            <Component Name="{name}">
               <DeviceID>-1</DeviceID>
               <Type>{TYPE_CHECKBOX}</Type>
               <TabOrder>{next_tab()}</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>{x_label:.3f}</LeftPos>
               <Height>1.3</Height>
               <ListHeight>0</ListHeight>
               <Width>{ctrl_w + (x_ctrl - x_label)}</Width>
               <Caption>{esc(label)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <DataSource>object.{PROP[column]}</DataSource>
               <Binding>1</Binding>
"""
        if column == "closed":
            out += "               <EventToGenerate>SetCloseInfo</EventToGenerate>\n"
        out += f"""               <Flags>1</Flags>
               <ReadOnly>{'True' if readonly else 'False'}</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
"""
        if column == "closed":
            out += "               <Post301Format>ENABLEDWHEN(V(cew_Closed))</Post301Format>\n"
        else:
            out += "               <Post301Format />\n"
        out += "            </Component>\n"
        return out
    out += emit_label("l_" + column, label, x_label, y + 0.15, w=(x_ctrl - x_label - 0.5))
    out += emit_control(column, ctype, x_ctrl, y, list_source, readonly, w=ctrl_w, maintain_from_spec=maintain_from_spec)
    return out

def emit_span(label, column, ctype, y):
    out = emit_label("l_" + column, label, SPAN_X, y)
    out += emit_control(column, ctype, SPAN_X, y + 1.1, None, False, w=SPAN_W, h=4.5)
    return out

def emit_header(text, y):
    return f"""            <Component Name="hdr_{text.replace(' ', '_').replace('/', '_')}">
               <DeviceID>-1</DeviceID>
               <Type>0</Type>
               <TabOrder>0</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>1</LeftPos>
               <Height>1.5</Height>
               <ListHeight>0</ListHeight>
               <Width>96</Width>
               <Caption>{esc(text)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <Binding>0</Binding>
               <Flags>1</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Post301Format>FONT(14,0,0,0,700,0,0,0,0,0,0,0,0,Microsoft Sans Serif) FORECOLOR(255,255,255) BACKCOLOR(TYPE=0; ARGB=[255, 0,0,0]; ) JUSTIFY(C) THEMECLASS(G2Header)</Post301Format>
               <EffectiveCaption>{esc(text)}</EffectiveCaption>
            </Component>
"""

def emit_title(text, y):
    return f"""            <Component Name="hdr_FormTitle">
               <DeviceID>-1</DeviceID>
               <Type>0</Type>
               <TabOrder>0</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>1</LeftPos>
               <Height>2.4</Height>
               <ListHeight>0</ListHeight>
               <Width>96</Width>
               <Caption>{esc(text)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <Binding>0</Binding>
               <Flags>1</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Post301Format>FONT(20,0,0,0,700,0,0,0,0,0,0,0,0,Microsoft Sans Serif) FORECOLOR(255,255,255) BACKCOLOR(TYPE=0; ARGB=[255, 0,0,0]; ) JUSTIFY(C) THEMECLASS(G2Header)</Post301Format>
               <EffectiveCaption>{esc(text)}</EffectiveCaption>
            </Component>
"""

def emit_grid_pane(pane_height):
    """Master-list grid on the left (Pane 0) - a full-height, narrow sidebar listing
    multiple records at once, matching the real legacy form's FormCollectionGrid
    (Height there matched the whole form's Height, Width was under half the form's
    Width - tall and narrow, not wide and short). Uses its own local coordinate space,
    separate from the detail pane's components, with PaneZeroSize as the splitter width."""
    out = [f"""            <Component Name="FormCollectionGrid">
               <DeviceID>-1</DeviceID>
               <Type>14</Type>
               <TabOrder>0</TabOrder>
               <TopPos>0</TopPos>
               <LeftPos>0</LeftPos>
               <Height>{pane_height:.2f}</Height>
               <ListHeight>2</ListHeight>
               <Width>{PANE_ZERO_SIZE:.2f}</Width>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <DataSource>objects</DataSource>
               <Binding>3</Binding>
               <Flags>384</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <DefaultFrom>StdGrid()</DefaultFrom>
               <Post301Format />
            </Component>
"""]
    x = 0
    for i, (column, caption, width) in enumerate(GRID_COLUMNS):
        out.append(f"""            <Component Name="grid_{column}">
               <DeviceID>-1</DeviceID>
               <Type>15</Type>
               <TabOrder>0</TabOrder>
               <TopPos>0</TopPos>
               <LeftPos>{x}</LeftPos>
               <Height>{pane_height:.2f}</Height>
               <ListHeight>0</ListHeight>
               <Width>{width}</Width>
               <Caption>{esc(caption)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName>FormCollectionGrid</ContainerName>
               <ContainerSequence>{i}</ContainerSequence>
               <DataSource>object.{PROP[column]}</DataSource>
               <Binding>1</Binding>
               <Flags>0</Flags>
               <ReadOnly>True</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <MenuName>StdDefault</MenuName>
               <Post301Format />
               <EffectiveCaption>{esc(caption)}</EffectiveCaption>
            </Component>
""")
        x += width
    return "".join(out)

def build_components():
    y = 0.0
    out = [emit_title("eCMRs — Change Management Request", y)]
    y = 2.9
    for item in LAYOUT:
        kind = item[0]
        if kind == HEADER:
            out.append(emit_header(item[1], y))
            y += SECTION_H + 0.3
        elif kind == PAIR:
            a, b = item[1], item[2]
            row_h = 0
            if a:
                _, label, column, ctype, list_source, readonly, maintain_from_spec = a
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_A, CTRL_X_A, y, maintain_from_spec=maintain_from_spec))
                row_h = max(row_h, 1.4)
            if b:
                _, label, column, ctype, list_source, readonly, maintain_from_spec = b
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_B, CTRL_X_B, y, maintain_from_spec=maintain_from_spec))
                row_h = max(row_h, 1.4)
            y += ROW_H
        elif kind == SPAN:
            _, label, column, ctype, list_source, readonly, maintain_from_spec = item[1]
            out.append(emit_span(label, column, ctype, y))
            y += 5.8
    return "".join(out), y

DETAIL_XML, TOTAL_HEIGHT = build_components()
COMPONENTS_XML = emit_grid_pane(TOTAL_HEIGHT) + DETAIL_XML

EVENT_HANDLERS = """
            <EventHandler Name="SetCloseInfo" Sequence="0">
               <ResponseType>33</ResponseType>
               <Response>SCRIPTTEXT(Option Explicit On
Option Strict On

Imports System
Imports Microsoft.VisualBasic
Imports Mongoose.IDO.Protocol
Imports Mongoose.Scripting

Namespace Mongoose.GlobalScripts
Public Class EvHandler_SetCloseInfo_0
Inherits GlobalScript

        Sub Main()
            If ThisForm.Components("c_closed").Text &lt;&gt; "1" Then
                ThisForm.Components("c_closed_by").Text = ""
                ThisForm.Components("c_close_date").Text = ""
            Else
                ThisForm.Components("c_closed_by").Text = ThisForm.UserName
                ThisForm.Components("c_close_date").Text = CStr(Today)
            End If
            ReturnValue = "0"
        End Sub
End Class
End Namespace
)</Response>
            </EventHandler>
"""

# The 11 companion-lookup EventHandlers (ResponseType 49) that used to live here are removed -
# confirmed live that triggering any of them jams the form's edit/commit pipeline for every
# other field afterward, even ones with no lookup at all. See emit_control().

FORM_XML = f"""<?xml version="1.0" encoding="utf-8"?>
<FormsAndObjectsExport Version="010000">
   <Forms Type="1">
      <Form Name="eCMRs" Scope="1" ScopeName="[NULL]">
         <Caption>eCMRs</Caption>
         <Type>0</Type>
         <!-- 1019, not the legacy QC_CMRs value of 953: that legacy form deliberately disabled New
              because record creation happened on a separate QC_CreateChangeRequest form (995).
              This form is single-screen browse+create, so it needs New enabled - 1019 matches the
              real JobOrders form (also single-screen full CRUD) exactly: 953 | 1019's extra bits (66). -->
         <StandardOperations>1019</StandardOperations>
         <!-- Confirmed via the real Items form export (StandardOperations=1019, Flags=202,
              same LOCKMODE(Row) fds_DataSource, no field-locking issue) that 202 was never the
              problem - the 1048778 guess tried here previously is reverted. -->
         <Flags>202</Flags>
         <Height>{TOTAL_HEIGHT + 2:.1f}</Height>
         <LeftPos>0</LeftPos>
         <TopPos>0</TopPos>
         <Width>140</Width>
         <PaneZeroSize>{PANE_ZERO_SIZE:.2f}</PaneZeroSize>
         <HelpContextID>-1</HelpContextID>
         <PrimaryDataSource>V(fds_DataSource)</PrimaryDataSource>
         <MasterDeviceID>0</MasterDeviceID>
         <Components>
{COMPONENTS_XML}         </Components>
         <EventHandlers>
{EVENT_HANDLERS}         </EventHandlers>
         <Variables>
            <Variable Name="fds_DataSource">
               <Value>ue_ecmrs( ORDERBY({PROP['cmr_num']} desc) LOCKMODE(Row) )</Value>
               <Value2 />
               <Value3 />
               <Description />
            </Variable>
            <Variable Name="cew_Closed">
               <Value>Enabled:#C(c_closed), #P({PROP['req_costing']}) = #P({PROP['cost_review_complete']}) &amp; #P({PROP['req_documentation']}) = #P({PROP['documentation_review_complete']}) &amp; #P({PROP['req_tool_machine']}) = #P({PROP['machinery_review_complete']}) &amp; #P({PROP['req_process']}) = #P({PROP['process_review_complete']}) &amp; #P({PROP['req_material']}) = #P({PROP['material_review_complete']}), "True"</Value>
               <Value2 />
               <Value3 />
               <Description />
            </Variable>
         </Variables>
      </Form>
   </Forms>
</FormsAndObjectsExport>
"""

if __name__ == "__main__":
    import sys
    out_path = sys.argv[1] if len(sys.argv) > 1 else "eCMRs_v1.XML"
    with open(out_path, "wb") as fh:
        data = FORM_XML.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
        fh.write(b"\xef\xbb\xbf" + data)
    print(f"Wrote {out_path}, {len(data)} bytes")
