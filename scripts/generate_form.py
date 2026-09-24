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

# Widths/positions below are measured directly from the real legacy form's own export
# (cmr-project's exports/QC_CMRs_Original.XML) - Form Width=160, banner Width=113.25 - not
# invented numbers. The identity block up top is a real THREE-column grid there (a narrow
# label+control pair on the far left, a second narrow label+control pair a bit further
# right sharing the same "left side" - e.g. PO Num next to PO Line, RFQ Num next to Job
# Num - then a much wider label+control on the right - e.g. Assigned Buyer, POC, Initial
# Change). LABEL_X_A/CTRL_X_A is that first pair, LABEL_X_A2/CTRL_X_A2 the second, and
# LABEL_X_B/CTRL_X_B/CTRL_W_B the wide right-hand one (unchanged from the earlier widening
# pass - already matches the real Assigned Buyer/POC controls almost exactly). Positions
# aren't pixel-identical to the original's own idiosyncratic per-row placement (e.g. Create
# Date/Created By sit stacked further right than a plain 3-column grid would put them there)
# but the column widths and, more importantly, the actual FIELD ORDER now match it exactly.
LABEL_X_A, CTRL_X_A, CTRL_W = 2, 11.25, 17.25
LABEL_X_A2, CTRL_X_A2, CTRL_W_A2 = 30, 37, 15
LABEL_X_B, CTRL_X_B, CTRL_W_B = 53, 65, 49
ROW_H = 1.75
SECTION_H = 1.6
SPAN_X, SPAN_W = 14.5, 98

def label_width(x_label, x_ctrl):
    return x_ctrl - x_label - 0.5

# Calibrated against the real form's own static labels: "Drawing Revision:" (17 chars) at
# label width 10.25 wraps to two lines there (Height=1.83 instead of the normal 1) and gets
# extra row pitch (2.0 instead of the usual ~1.75-1.83) to avoid colliding with the row
# below; "Assigned Buyer:" (15 chars) at width 11.125 stays one line at normal height. The
# ratio boundary between those two real data points is ~1.35-1.66 chars/unit-width; 1.45 is
# the middle of that range, erring toward "give it room" since under-provisioning height for
# a caption that actually wraps produces a visible overlap bug (this was directly reported),
# while over-provisioning for one that doesn't just leaves a little extra whitespace.
def is_tall(caption, width):
    return len(caption) > width * 1.45

SL_ITEMS = "STDOLE SLItems( PROPERTIES(Item, Description) )"
SL_DEPTS = "STDOLE SLDepts( PROPERTIES(Dept, Description) )"
SL_WCS = "STDOLE SLWcs( PROPERTIES(Wc, Description) )"
SL_VENDORS = "STDOLE SLVendors( PROPERTIES(VendNum, Name) )"
SL_EMPLOYEES = "STDOLE SLEmployees( PROPERTIES(EmpNum,Name,Username) DISPLAY(1,2,3) RECORDCAP(0))"
# Used by Assigned and all five Reviewer combos (QC/Eng/Planning/Purchasing/CM) - not the
# shared SL_EMPLOYEES above, which only Assigned Buyer still uses today, bound to EmpNum: the
# combo writes back whichever property is listed FIRST in PROPERTIES() - confirmed from
# Vendor's own combo (DataSource=Vendor, PROPERTIES(VendNum,...) - first entry doesn't even
# name-match the DataSource property, so this is positional, not name-matched). Listing
# Username first here makes each of these combos bind and store the employee's Username (a
# real email address in this tenant, confirmed from a live screenshot earlier - e.g.
# gcaraway@enflite.com) directly - every target property (AssignedUsername, QcReviewerUsername,
# EngReviewerUsername, PlanningReviewerName, PurchasingReviewerName, CmReviewerName) is sized
# for a Username (String(128) or String(255)), not the tiny 7-char EmpNum columns.
SL_EMPLOYEES_ASSIGNED = "STDOLE SLEmployees( PROPERTIES(Username,EmpNum,Name) DISPLAY(1,2,3) RECORDCAP(0))"
# Real list sources adapted from the legacy form's own combos (CB_NextAssy, comboBox1_SITE,
# comboBox2_SITE, comboBox4_SITE), just swapped to our own property names.
SL_JOBMATLS_NEXT_ASSY = "STDOLE SLJobmatls( PROPERTIES(JobItem) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() FILTER(Item='P(Item)') RECORDCAP(0))"
# PO Num deliberately has NO self-referencing FILTER (unlike the legacy form's own combo) -
# confirmed live that FP(x) is a plain exact-equality match against the raw typed text, no
# wildcard/padding (the same root cause already found for Job Number's leading-zero bug in
# cmr-project). Real PO Numbers are zero-padded with a prefix (e.g. RD00000021, confirmed
# live) - nobody types that exact string, so the filter always returned zero matches. Fixed
# by dropping the FILTER entirely and listing every PoItems row, same pattern already proven
# working on Item/Wc/Dept/Vendor above - the EnhancedCombo's own client-side type-ahead
# narrows it down instead of a server-side exact match.
SL_POITEMS_NUM = "STDOLE SLPoItems( PROPERTIES(PoNum,Item,PoLine) DISPLAY(1,2,3) READMODE(UNCOMMITTED) DISTINCT() RECORDCAP(0))"
# PO Line's filter is a legitimate cascade off the already-selected PoNum (a real value from
# the object, not free-typed guesswork), not a self-referencing exact-match - left as-is.
# DISPLAY(2,1,3) puts Item before PoLine in the visual/label order (was DISPLAY(1,2,3)), since
# a bare PoLine number ("1", "2", "3") isn't identifiable on its own once the combo is closed -
# per direct request, keep PoLine as the actual stored/written-back value (still correct,
# write-back is positional against PROPERTIES()'s own order, which is unchanged: PoLine stays
# first there) while making Item show first in whatever label the closed box displays.
# UNCONFIRMED whether DISPLAY() order actually affects the closed/collapsed combo's text (as
# opposed to only the open dropdown grid's column order) - needs a live check after re-import.
SL_POITEMS_LINE = "STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum) DISPLAY(2,1,3) READMODE(UNCOMMITTED) DISTINCT() FILTER(PoNum='P(PoNum)') RECORDCAP(0))"
# Job Num: real syntax confirmed directly from the legacy QC_CMRs form's own Job Num combo
# (comboBox4_SITE) - STDOLE SLMatltrans( PROPERTIES(RefNum) DISPLAY(1) READMODE(UNCOMMITTED)
# DISTINCT() FILTER(RefNum=FP(rs_cmrUf_ENF_CMR_JobNum)) RECORDCAP(0)). Two wrong guesses tried
# and disproven before landing here: SLJobs (a real but unrelated IDO - returns generic
# sequential values like C000000001/C000000002 regardless of input), and assuming no combo
# exists at all because the real JobOrders form's own Job field is a plain Edit with no List
# Source (true, but irrelevant - that form's Job field IS the job record itself, so it has
# nothing to look up; CMR's Job Num field is a reference to some other job, same relationship
# as CMR's own PO Num field referencing PO Items). The legacy combo's self-referencing
# exact-match FILTER is the same class of bug already fixed for PO Number (FP() has no
# wildcard/padding, and real Job Numbers are zero-padded - DK84716 never matches the stored
# DK00084716) - same fix: drop the FILTER entirely, list every row via SLMatltrans unfiltered,
# let the EnhancedCombo's own client-side type-ahead narrow it down. The property that holds
# the job number in SLMatltrans is RefNum, not Job/JobNum - confirmed from the same real combo.
SL_MATLTRANS_JOB = "STDOLE SLMatltrans( PROPERTIES(RefNum) DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT() RECORDCAP(0))"

# (label, column, ctype, list_source, readonly)
FIELD = "field"
PAIR = "pair"          # (fieldA, fieldB) sharing one row
TRIPLE = "triple"      # (fieldA, fieldA2, fieldB) - the real form's 3-column identity-block
                       # rows (e.g. PO Num/PO Line/Assigned Buyer, RFQ Num/Job Num/Initial
                       # Change) - any slot may be None.
SPAN = "span"          # full-width field (multiline)
HEADER = "header"
GROUPLABEL = "grouplabel"  # a plain bold text label (not a full colored banner) marking a sub-group
IMPL_ROW = "impl_row"  # checkbox + Reviewer: combo + name, one row (Implementation's Planning/Purchasing/CM)
TOP_ROW = "top_row"    # Status / Assigned ID / Assigned / Notify - the real form's very
                       # first row, four components wide, unlike anything else on the form

# Matches the design mockup's .new-box class exactly (background: #ede0ff -> RGB 237,224,255).
# Marks every brand-new/carried-over field (Change Request Fields, Additional Fields, Reason
# Code/Cause Code) so they visually stand out as additions on the live form. SyteLine's
# Post301Format has no border property, so the mockup's #9b6fd1 border can't be replicated -
# background match is the closest available approximation. FORECOLOR(107,63,160) added per
# direct request - the same purple already used for the section GROUPLABEL text
# ("Change Request Fields"/"Additional Fields") - so the new fields' labels, values, and
# checkboxes carry purple TEXT as well as the purple background, not background alone.
HIGHLIGHT_FORMAT = "BACKCOLOR(TYPE=0; ARGB=[255, 237,224,255]; ) FORECOLOR(107,63,160)"

def f(label, column, ctype, list_source=None, readonly=False, maintain_from_spec=None, property_class_name=None, default_from=None, highlight=False, ctrl_w=None):
    # ctrl_w: optional per-field override of the control width the row's slot (A/A2/B) would
    # otherwise default to - added because a slot's default width is tuned for that COLUMN's
    # typical field (e.g. B defaults to 49, sized for long fields like Assigned Buyer/POC),
    # not every field that happens to land in it (e.g. Work Center is a short code, not a
    # long field, even though it shares Dept's row on the B side).
    return (FIELD, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w)

LAYOUT = [
    # Everything below, up to QUALITY, sat in one continuous unlabeled area on the real
    # legacy form - it never had IDENTITY/CHANGE DETAILS/ITEM DETAILS/SOURCING/DATES
    # banners (dropped "CMR DETAILS" - it wasn't real). QUALITY/ENGINEERING/IMPLEMENTATION
    # below are the only section banners that were ever real on the original form.
    #
    # This whole identity block's ORDER matches the original, row for row, extracted directly
    # from cmr-project's QC_CMRs_Original.XML: Status+Assigned+Notify, CMR Num+Create
    # Date+Created By, PO Num+PO Line+Assigned Buyer, Qty+POC, RFQ Num+Job Num,
    # Drawing Revision+Latest Revision, Requested Action, Next Lvl Assy, Vendor, Priority.
    # Item and Initial Change are the two exceptions - per direct request they're consolidated
    # into the Change Request Fields section below instead of staying in their original
    # position, since that section is meant to gather everything Create Change Request touches
    # in one place. They keep their ORIGINAL (non-purple) styling there, per "unrelated
    # existing fields should retain their original styling" - they're relocated for
    # consolidation, not restyled as new. (Item Description/Next Assy Description/Vendor
    # Name/Internal Review Date were also previously inserted here as extra fields that don't
    # exist on the real form at all - dropped entirely; their DefaultFrom/PropertyClassName
    # auto-fill on Item/Next Lvl Assy/Vendor is dropped along with them since it had no other
    # purpose.)
    (TOP_ROW,),
    (TRIPLE, f("CMR Num:", "cmr_num", TYPE_EDIT, readonly=True), f("Create Date:", "create_date", TYPE_DATE, readonly=True), f("Created By:", "created_by", TYPE_EDIT, readonly=True)),
    (TRIPLE, f("PO Num:", "po_num", TYPE_COMBO, SL_POITEMS_NUM), f("PO Line:", "po_line", TYPE_COMBO, SL_POITEMS_LINE), f("Assigned Buyer:", "assigned_buyer", TYPE_COMBO, SL_EMPLOYEES)),
    (PAIR, f("Qty:", "qty", TYPE_EDIT), f("POC:", "poc", TYPE_EDIT)),
    (TRIPLE, f("RFQ Num:", "rfq_num", TYPE_EDIT), f("Job Num:", "job_num", TYPE_COMBO, SL_MATLTRANS_JOB), None),
    (TRIPLE, f("Drawing Revision:", "revision", TYPE_EDIT), f("Latest Revision:", "latest_revision", TYPE_EDIT), None),
    (SPAN, f("Requested Action:", "requested_action", TYPE_MULTILINE)),
    (PAIR, f("Next Lvl Assy:", "next_assy_item", TYPE_COMBO, SL_JOBMATLS_NEXT_ASSY), None),
    # VendNum is directly confirmed as the real Property Class name for a vendor number field -
    # taken from the live PurchaseOrders form's own VendNumEdit component, not a guess. Kept
    # even without a visible Vendor Name display field, in case some other live mechanism
    # (e.g. a MaintainFromSpec on the property itself) still depends on it being set.
    (PAIR, f("Vendor:", "vendor", TYPE_COMBO, SL_VENDORS, property_class_name="VendNum"), None),
    (PAIR, f("Priority:", "priority", TYPE_COMBO), None),

    # Everything from here down, up to QUALITY, is new-since-the-legacy-form - grouped and
    # labeled to match the design mockup (Change Request carryover, then the BRD's brand-new
    # Additional Fields), instead of being scattered piecemeal among the base identity fields
    # above wherever there happened to be room. Row order per direct request: Dept/WC,
    # Dept Description/WC Description, Item/Reported By, Initial Change, Requirements,
    # General Note - consolidating Item and Initial Change here rather than leaving a second,
    # separated "Change Request" concept split across the form.
    (GROUPLABEL, "Change Request Fields"),
    # Work Center is a short code, same as Dept - not a long field like Assigned Buyer/POC,
    # which is what the B slot's default width (49) is tuned for - overridden to a compact
    # width matching Dept's own (per direct request: "WC should be compact").
    (PAIR, f("Dept:", "dept", TYPE_COMBO, SL_DEPTS, property_class_name="Dept", default_from="Dept(DeptDescription)", highlight=True), f("Work Center:", "wc", TYPE_COMBO, SL_WCS, property_class_name="Wc", default_from="Wc(WcDescription)", highlight=True, ctrl_w=17.25)),
    # Dept Description widened - a description field, same as WC Description, not a short
    # code like Dept itself (per direct request: "probably too narrow, give more room").
    (PAIR, f("Dept Description:", "dept_description", TYPE_EDIT, readonly=True, highlight=True, ctrl_w=40), f("WC Description:", "wc_description", TYPE_EDIT, readonly=True, highlight=True)),
    # Item and Reported By consolidated here per direct request. Item is now purple per
    # direct request ("all Change Request fields should be purple") - superseding the earlier
    # non-purple treatment. Reported By is a person's name, not a long descriptive field - the
    # B slot's 49-wide default is sized for Assigned Buyer/POC, not this, so narrowed to a
    # medium width.
    (PAIR, f("Item:", "item", TYPE_COMBO, SL_ITEMS, highlight=True), f("Reported By:", "reported_by", TYPE_EDIT, highlight=True, ctrl_w=30)),
    # Reverted to plain per direct request - Due Date isn't one of the new Change Request
    # fields after all (superseding the earlier confirmation to keep it purple).
    (PAIR, f("Due Date:", "due_date", TYPE_DATE), None),
    # Initial Change: now purple per direct request, but kept as a Type 27 combo rather than
    # converted to a multiline text area - generate_schema_csv.py's own field comment
    # confirms InitialChange is a String(40) bound to a fixed 8-value list (Documentation,
    # Machine, Material, Other, Process, Specification, Tooling, Variance(waiver)) that drives
    # the Requirements checkbox cascade, not a free-text change narrative. Converting it to
    # Type 18 would replace a working dropdown with an empty text box and break that
    # cascade's whole reason for existing. Narrowed from 60 to 30 - still a combo, not a
    # narrative field, so it doesn't need to be nearly as wide as a multiline box.
    (PAIR, f("Initial Change:", "initial_change", TYPE_COMBO, highlight=True, ctrl_w=30), None),
    # Moved up from inside QUALITY (per the plan deck's Design slide - these are part of the
    # Create Change Request carryover, not Quality-specific) - still cascade off Initial Change
    # above, just visually grouped with the rest of the Change Request fields now.
    (PAIR, f("Req: Costing", "req_costing", TYPE_CHECKBOX, highlight=True), f("Req: Documentation", "req_documentation", TYPE_CHECKBOX, highlight=True)),
    (PAIR, f("Req: Tool/Machine", "req_tool_machine", TYPE_CHECKBOX, highlight=True), f("Req: Process", "req_process", TYPE_CHECKBOX, highlight=True)),
    (PAIR, f("Req: Material", "req_material", TYPE_CHECKBOX, highlight=True), None),
    (SPAN, f("General Note:", "general_note", TYPE_MULTILINE, highlight=True)),

    (GROUPLABEL, "Additional Fields"),
    (PAIR, f("Serial #:", "serial_num", TYPE_EDIT, highlight=True), f("LOT #:", "lot_num", TYPE_EDIT, highlight=True)),
    (PAIR, f("Top Level PN:", "top_level_pn", TYPE_EDIT, highlight=True), f("Sub Assembly:", "sub_assembly", TYPE_EDIT, highlight=True)),

    (HEADER, "QUALITY"),
    (PAIR, f("General Review Complete", "general_review_complete", TYPE_CHECKBOX, readonly=True), f("SOX Impacted", "sox_impacted", TYPE_CHECKBOX)),
    (PAIR, f("Hold On PO", "hold_on_po", TYPE_CHECKBOX), f("Authorization For Supplier To Ship", "auth_supplier_ship", TYPE_CHECKBOX)),
    # References the same real, existing system Property Classes the live QC_MRRs form's own
    # Reason/Cause combos use (ReasonEdit/CauseEdit - confirmed directly from that form's own
    # XML export), not a custom Inline List of our own - per direct request: "we can use this
    # list that exists right now" (may get its own separate, CMR-specific list later - this
    # is a deliberate, known-temporary choice, not a permanent architectural tie to MRR's
    # list). No ComboListSource - PropertyClassName alone drives the combo's list here, same
    # as how QC_MRRs' own components have zero ComboListSource, just PropertyClassName. Our
    # own ReasonCode/CauseCode properties stay Property Class-blank at the IDO level (same as
    # every other property here) - this is a per-component override, not a property-level
    # setting. UNCONFIRMED whether a component's PropertyClassName can validly point at a
    # class distinct from anything set on its own bound property - this is architecturally
    # sound and directly copied from a real working form, but genuinely untested in this
    # tenant; verify live after import.
    (PAIR, f("Reason Code:", "reason_code", TYPE_COMBO, property_class_name="QCReasonCode", highlight=True), f("Cause Code:", "cause_code", TYPE_COMBO, property_class_name="QCCauseCode", highlight=True)),
    # Reviewer combo binds directly to the Username property (same pattern as Assigned) and
    # returns the username, not the employee number. Reviewer ID restored on its own row
    # (per direct request) - plain writable box, same no-confirmed-sync caveat as Assigned ID.
    (PAIR, f("QC Disposition:", "qc_disposition", TYPE_COMBO), None),
    (PAIR, f("Reviewer ID:", "qc_reviewer_empnum", TYPE_EDIT), f("Reviewer:", "qc_reviewer_username", TYPE_COMBO, SL_EMPLOYEES_ASSIGNED)),
    (SPAN, f("QC RCA Notes:", "qc_rca_notes", TYPE_MULTILINE)),

    (HEADER, "ENGINEERING"),
    (PAIR, f("EO Num:", "eo_num", TYPE_EDIT), None),
    (PAIR, f("MDL:", "mdl", TYPE_EDIT), None),
    # Same treatment as Quality's Reviewer above.
    (PAIR, f("Engineering Disposition:", "eng_disposition", TYPE_COMBO), None),
    (PAIR, f("Reviewer ID:", "eng_reviewer_empnum", TYPE_EDIT), f("Reviewer:", "eng_reviewer_username", TYPE_COMBO, SL_EMPLOYEES_ASSIGNED)),
    (SPAN, f("Eng RCA Notes:", "eng_rca_notes", TYPE_MULTILINE)),

    (HEADER, "IMPLEMENTATION"),
    # Reviewer combo binds directly to the *_reviewer_name property (repurposed to hold the
    # username, same as Quality/Engineering above). Reviewer ID box restored between the
    # checkbox and the combo, per direct request - see emit_impl_row.
    (IMPL_ROW, "planning_complete", "Planning", "planning_reviewer_name", "planning_reviewer_empnum"),
    (IMPL_ROW, "purchasing_complete", "Purchasing", "purchasing_reviewer_name", "purchasing_reviewer_empnum"),
    (IMPL_ROW, "cm_complete", "CM", "cm_reviewer_name", "cm_reviewer_empnum"),
    (PAIR, f("Close Date:", "close_date", TYPE_DATE, readonly=True), f("Closed By:", "closed_by", TYPE_EDIT, readonly=True)),
    (PAIR, f("Closed", "closed", TYPE_CHECKBOX), None),
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
#
# Experimental replacement, test case: EventToGenerate (the same wiring SetCloseInfo already
# uses safely on the Closed checkbox) pointing at a ResponseType 33 inline VB script that calls
# Me.IDOClient.LoadCollection(...) directly, instead of the declarative
# FILTER()/MOV()/SONON()/SETP() response language that jammed the form. Two real, separate
# pieces of evidence combined here: EventToGenerate on a Type=27 combo is real (JobOrders' and
# Items' own ItemEdit/CustNumEdit/WhseEdit etc. use it, just for a built-in event name), and
# Me.IDOClient.LoadCollection(request) is the real IDO-query pattern from cmr-project's
# QC_CMRs.vb FormScript - used here as a literal copy (Me, not ThisForm) since GlobalScript and
# FormScript are sibling classes in the same Mongoose.Scripting framework, so IDOClient may be
# a member of a shared base both inherit. First attempt substituted ThisForm for Me and the
# script silently did nothing live - confirmed dead either way (also tried Me.IDOClient, same
# silent no-op). Item Description was removed from the form entirely per direct request, so
# this mechanism has no remaining target - left empty rather than deleted outright in case a
# genuinely new lead on the underlying problem turns up later.
SCRIPT_LOOKUP_EVENTS = []

_tab = [0]
def next_tab():
    _tab[0] += 1
    return _tab[0]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def emit_label(name, caption, x, y, w=CTRL_W - 2, seq=0, highlight=False, h=1, justify="R"):
    post301 = f"<Post301Format>{HIGHLIGHT_FORMAT}</Post301Format>" if highlight else "<Post301Format />"
    return f"""            <Component Name="{name}">
               <DeviceID>-1</DeviceID>
               <Type>{TYPE_STATIC}</Type>
               <TabOrder>0</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>{x:.3f}</LeftPos>
               <Height>{h}</Height>
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
               <Format>JUSTIFY({justify})</Format>
               {post301}
               <EffectiveCaption>{esc(caption)}</EffectiveCaption>
            </Component>
"""

def emit_control(column, ctype, x, y, list_source, readonly, w=CTRL_W, h=1.4, maintain_from_spec=None, property_class_name=None, default_from=None, highlight=False):
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
    if column in [e[0] for e in SCRIPT_LOOKUP_EVENTS]:
        ev = [e[2] for e in SCRIPT_LOOKUP_EVENTS if e[0] == column][0]
        lines.append(f"               <EventToGenerate>{ev}</EventToGenerate>")
    if list_source:
        lines.append(f"               <ComboListSource>{esc(list_source)}</ComboListSource>")
    if maintain_from_spec:
        lines.append(f"               <MaintainFromSpec>{esc(maintain_from_spec)}</MaintainFromSpec>")
    if default_from:
        lines.append(f"               <DefaultFrom>{esc(default_from)}</DefaultFrom>")
    if property_class_name:
        lines.append(f"               <PropertyClassName>{esc(property_class_name)}</PropertyClassName>")
    lines.append("               <Flags>1</Flags>")
    lines.append(f"               <ReadOnly>{'True' if readonly else 'False'}</ReadOnly>")
    lines.append("               <Hidden>False</Hidden>")
    lines.append("               <HelpContextID>0</HelpContextID>")
    lines.append(f"               <Post301Format>{HIGHLIGHT_FORMAT}</Post301Format>" if highlight else "               <Post301Format />")
    lines.append("            </Component>")
    return "\n".join(lines) + "\n"

def emit_field(label, column, ctype, list_source, readonly, x_label, x_ctrl, y, ctrl_w=CTRL_W, maintain_from_spec=None, property_class_name=None, default_from=None, highlight=False):
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
        out += f"               <Post301Format>{HIGHLIGHT_FORMAT}</Post301Format>\n" if highlight else "               <Post301Format />\n"
        out += "            </Component>\n"
        return out
    w = label_width(x_label, x_ctrl)
    tall = is_tall(label, w)
    out += emit_label("l_" + column, label, x_label, y + (0.05 if tall else 0.15), w=w, highlight=highlight, h=1.8 if tall else 1)
    out += emit_control(column, ctype, x_ctrl, y, list_source, readonly, w=ctrl_w, maintain_from_spec=maintain_from_spec, property_class_name=property_class_name, default_from=default_from, highlight=highlight)
    return out

def emit_span(label, column, ctype, y, highlight=False):
    # Span labels sit alone on their own line ABOVE a full-width box, not beside it like a
    # normal paired field's label - so right-justifying it (emit_label's default, correct for
    # a label hugging its control to the right) instead floats the caption away from the
    # box's left edge, inside an arbitrary-width box. Left-justified and flush with the box's
    # own LeftPos (SPAN_X) instead, matching a plain "Label:" tag sitting directly above it.
    # Applies uniformly to all four multiline fields (Requested Action, General Note, QC RCA
    # Notes, Eng RCA Notes) - they already share identical box geometry (98 wide, 4.5 tall,
    # 1.1 label-to-box gap) since they all go through this same function; only General Note
    # additionally carries the purple highlight, which stays scoped to it via the `highlight`
    # arg its own LAYOUT entry passes - not touched here.
    out = emit_label("l_" + column, label, SPAN_X, y, w=40, highlight=highlight, justify="L")
    out += emit_control(column, ctype, SPAN_X, y + 1.1, None, False, w=SPAN_W, h=4.5, highlight=highlight)
    return out

def emit_impl_row(checkbox_col, checkbox_caption, combo_col, id_col, y):
    # Widened to use the same overall span as the rest of the now-160-wide form (was cramped
    # into the old 2-37.5 range) - checkbox on the far left, then ID and Reviewer spread out
    # across the extra width instead of bunching in the first third of the row.
    out = emit_field(checkbox_caption, checkbox_col, TYPE_CHECKBOX, None, False, LABEL_X_A, CTRL_X_A, y, ctrl_w=15)
    out += emit_field("ID:", id_col, TYPE_EDIT, None, False, 31, 35, y, ctrl_w=9)
    out += emit_field("Reviewer:", combo_col, TYPE_COMBO, SL_EMPLOYEES_ASSIGNED, False, 48, 56, y, ctrl_w=30)
    return out

def emit_button(name, caption, event_to_generate, x, y, w=15, h=1.4):
    # Matches the design mockup's Notify button exactly (background: #2f6fed -> RGB
    # 47,111,237, white text) - previously left uncolored (plain system-gray button).
    return f"""            <Component Name="{name}">
               <DeviceID>-1</DeviceID>
               <Type>8</Type>
               <TabOrder>{next_tab()}</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>{x:.3f}</LeftPos>
               <Height>{h}</Height>
               <ListHeight>0</ListHeight>
               <Width>{w}</Width>
               <Caption>{esc(caption)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <Binding>0</Binding>
               <EventToGenerate>{event_to_generate}</EventToGenerate>
               <Flags>1</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Post301Format>FONT(9,0,0,0,700,0,0,0,0,0,0,0,0,Microsoft Sans Serif) FORECOLOR(255,255,255) BACKCOLOR(TYPE=0; ARGB=[255, 47,111,237]; )</Post301Format>
            </Component>
"""

def emit_top_row(y):
    # The real form's actual first row: Status, then "Assigned:" followed by TWO controls
    # (a plain EmpNum box, then the Username combo - confirmed directly from the original's
    # own ClosedByComboBox4_SITE5_USER/ClosedByComboBox3_SITE pair), then Notify. This is the
    # real, correct home for "Assigned ID" (it's not an invented field - the original binds
    # it to AssignedUserEmpNum right here), not a plain extra row further down like before.
    out = emit_field("Status:", "status", TYPE_COMBO, None, False, LABEL_X_A, CTRL_X_A, y, ctrl_w=19)
    out += emit_label("l_assigned_username", "Assigned:", 34, y + 0.15, w=11.5)
    out += emit_control("assigned_empnum", TYPE_EDIT, 46, y, None, False, w=10)
    out += emit_control("assigned_username", TYPE_COMBO, 57, y, SL_EMPLOYEES_ASSIGNED, False, w=28)
    out += emit_button("btn_notify", "Notify", "NotifyEngineering", 86, y, w=13)
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
               <Width>113.25</Width>
               <Caption>{esc(text)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <Binding>0</Binding>
               <Flags>1</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Post301Format>FONT(14,0,0,0,700,0,0,0,0,0,0,0,0,Microsoft Sans Serif) FORECOLOR(255,255,255) BACKCOLOR(TYPE=0; ARGB=[255, 41,163,224]; ) JUSTIFY(C) THEMECLASS(G2Header)</Post301Format>
               <EffectiveCaption>{esc(text)}</EffectiveCaption>
            </Component>
"""

def emit_grouplabel(text, y):
    # A plain bold purple text label (no colored banner) - marks a sub-group within the
    # continuous unlabeled area (e.g. "Change Request Fields", "Additional Fields"),
    # matching the design mockup's .grouplabel color exactly (#6b3fa0 -> RGB 107,63,160).
    # Distinct from emit_header's full-width blue banner, which is reserved for the three
    # section banners (QUALITY/ENGINEERING/IMPLEMENTATION) that were real on the original form.
    return f"""            <Component Name="grp_{text.replace(' ', '_').replace('/', '_')}">
               <DeviceID>-1</DeviceID>
               <Type>0</Type>
               <TabOrder>0</TabOrder>
               <TopPos>{y:.3f}</TopPos>
               <LeftPos>{LABEL_X_A}</LeftPos>
               <Height>1.2</Height>
               <ListHeight>0</ListHeight>
               <Width>70</Width>
               <Caption>{esc(text)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <Binding>0</Binding>
               <Flags>1</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Post301Format>FONT(10,0,0,0,700,0,0,0,0,0,0,0,0,Microsoft Sans Serif) FORECOLOR(107,63,160) JUSTIFY(L)</Post301Format>
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
               <Width>113.25</Width>
               <Caption>{esc(text)}</Caption>
               <MaxCharacters>0</MaxCharacters>
               <ContainerName />
               <ContainerSequence>0</ContainerSequence>
               <Binding>0</Binding>
               <Flags>1</Flags>
               <ReadOnly>False</ReadOnly>
               <Hidden>False</Hidden>
               <HelpContextID>0</HelpContextID>
               <Post301Format>FONT(20,0,0,0,700,0,0,0,0,0,0,0,0,Microsoft Sans Serif) FORECOLOR(255,255,255) BACKCOLOR(TYPE=0; ARGB=[255, 41,163,224]; ) JUSTIFY(C) THEMECLASS(G2Header)</Post301Format>
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
        elif kind == GROUPLABEL:
            out.append(emit_grouplabel(item[1], y))
            y += 1.6
        elif kind == PAIR:
            a, b = item[1], item[2]
            tall = False
            if a:
                _, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w = a
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_A, CTRL_X_A, y, ctrl_w=ctrl_w if ctrl_w is not None else CTRL_W, maintain_from_spec=maintain_from_spec, property_class_name=property_class_name, default_from=default_from, highlight=highlight))
                tall = tall or is_tall(label, label_width(LABEL_X_A, CTRL_X_A))
            if b:
                _, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w = b
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_B, CTRL_X_B, y, ctrl_w=ctrl_w if ctrl_w is not None else CTRL_W_B, maintain_from_spec=maintain_from_spec, property_class_name=property_class_name, default_from=default_from, highlight=highlight))
                tall = tall or is_tall(label, label_width(LABEL_X_B, CTRL_X_B))
            y += ROW_H + 0.3 if tall else ROW_H
        elif kind == TRIPLE:
            a, a2, b = item[1], item[2], item[3]
            tall = False
            if a:
                _, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w = a
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_A, CTRL_X_A, y, ctrl_w=ctrl_w if ctrl_w is not None else CTRL_W, maintain_from_spec=maintain_from_spec, property_class_name=property_class_name, default_from=default_from, highlight=highlight))
                tall = tall or is_tall(label, label_width(LABEL_X_A, CTRL_X_A))
            if a2:
                _, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w = a2
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_A2, CTRL_X_A2, y, ctrl_w=ctrl_w if ctrl_w is not None else CTRL_W_A2, maintain_from_spec=maintain_from_spec, property_class_name=property_class_name, default_from=default_from, highlight=highlight))
                tall = tall or is_tall(label, label_width(LABEL_X_A2, CTRL_X_A2))
            if b:
                _, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w = b
                out.append(emit_field(label, column, ctype, list_source, readonly, LABEL_X_B, CTRL_X_B, y, ctrl_w=ctrl_w if ctrl_w is not None else CTRL_W_B, maintain_from_spec=maintain_from_spec, property_class_name=property_class_name, default_from=default_from, highlight=highlight))
                tall = tall or is_tall(label, label_width(LABEL_X_B, CTRL_X_B))
            y += ROW_H + 0.3 if tall else ROW_H
        elif kind == TOP_ROW:
            out.append(emit_top_row(y))
            y += ROW_H
        elif kind == SPAN:
            _, label, column, ctype, list_source, readonly, maintain_from_spec, property_class_name, default_from, highlight, ctrl_w = item[1]
            out.append(emit_span(label, column, ctype, y, highlight=highlight))
            y += 5.8
        elif kind == IMPL_ROW:
            _, checkbox_col, checkbox_caption, combo_col, id_col = item
            out.append(emit_impl_row(checkbox_col, checkbox_caption, combo_col, id_col, y))
            y += ROW_H
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
            <EventHandler Name="NotifyEngineering" Sequence="0">
               <ResponseType>33</ResponseType>
               <Response>SCRIPTTEXT(Option Explicit On
Option Strict On

Imports System
Imports Microsoft.VisualBasic
Imports Mongoose.IDO.Protocol
Imports Mongoose.Scripting

Namespace Mongoose.GlobalScripts
Public Class EvHandler_NotifyEngineering_0
Inherits GlobalScript

        Sub Main()
            ' Placeholder only: confirms the button/event wiring works via a plain VB.NET
            ' MsgBox call (Microsoft.VisualBasic, already imported and confirmed safe in this
            ' GlobalScript context). Real notification (email to Engineering) needs a decided
            ' mechanism first - no confirmed syntax for that exists anywhere in this project's
            ' real evidence yet, and guessing at one risks the same kind of silent failures the
            ' SelectionEvent/IDOClient experiments already hit this session. The message below
            ' deliberately does NOT claim a notification was sent - nothing is sent yet.
            MsgBox("Notify clicked for CMR " &amp; ThisForm.Components("c_cmr_num").Text &amp; " - no notification mechanism is wired up yet.")
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
#
# Replacement being tested on Item only (SCRIPT_LOOKUP_EVENTS): a ResponseType 33 inline VB
# script, same mechanism as SetCloseInfo above, using Me.IDOClient.LoadCollection(...) - the
# real pattern from cmr-project's QC_CMRs.vb FormScript - via ThisForm instead of Me, since
# ThisForm (not Me) is the confirmed-accessible object inside a GlobalScript (see SetCloseInfo's
# own ThisForm.Components/.UserName calls above). Imports match that FormScript's exactly,
# including Mongoose.Core.Common for SqlLiteral.Format.
for trigger_col, display_col, event_name, sl_table, filter_prop, source_prop in SCRIPT_LOOKUP_EVENTS:
    _vb = f"""Option Explicit On
Option Strict On

Imports System
Imports Microsoft.VisualBasic
Imports Mongoose.IDO.Protocol
Imports Mongoose.Scripting
Imports Mongoose.Core.Common

Namespace Mongoose.GlobalScripts
Public Class EvHandler_{event_name}_0
Inherits GlobalScript

        Sub Main()
            Dim triggerVal As String = ThisForm.Components("c_{trigger_col}").Text
            If triggerVal <> "" Then
                Dim request As New LoadCollectionRequestData()
                request.IDOName = "{sl_table}"
                request.PropertyList.SetProperties("{filter_prop},{source_prop}")
                request.Filter = "{filter_prop} = " & SqlLiteral.Format(triggerVal, SqlLiteralFormatFlags.UseQuotes)
                request.RecordCap = 1
                Dim response As LoadCollectionResponseData = Me.IDOClient.LoadCollection(request)
                If response.Items.Count > 0 Then
                    ThisForm.Components("c_{display_col}").Text = response.Items(0).PropertyValues(1).Value.ToString()
                End If
            Else
                ThisForm.Components("c_{display_col}").Text = ""
            End If
            ReturnValue = "0"
        End Sub
End Class
End Namespace
"""
    EVENT_HANDLERS += f"""            <EventHandler Name="{event_name}" Sequence="0">
               <ResponseType>33</ResponseType>
               <Response>SCRIPTTEXT({esc(_vb)})</Response>
            </EventHandler>
"""

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
         <Width>160</Width>
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
               <!-- Closed asc puts open CMRs first, closed ones last - restored now that the
                    Closed checkbox and its SetCloseInfo handler are back (see the Implementation
                    section's Closed checkbox below), so closed is no longer permanently 0.
                    GeneralReviewComplete is still orphaned (nothing sets it) - not part of this
                    sort, and not part of what was restored here. Priority is deliberately NOT
                    in this sort either - High/Medium/Low as plain text alphabetizes to High,
                    Low, Medium, which is wrong for urgency order; sorting by it would be
                    actively misleading rather than just incomplete. -->
               <Value>ue_ecmrs( ORDERBY({PROP['closed']} asc, {PROP['cmr_num']} desc) LOCKMODE(Row) )</Value>
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
