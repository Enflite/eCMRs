# eCMRs — Troubleshooting & Confirmed Tricks

Hard-won lessons from building this form, kept here so the same mistakes
don't get repeated (by a human, or by whichever AI is helping next). Every
entry below is confirmed against real live behavior in this tenant, not a
guess — if a fix here didn't actually get confirmed working, that's noted
explicitly.

## Rule #1: a silent form-wide lock/grey-out almost always means a
## property-level rejection, not a form-side event

**Symptom**: select/edit one field, the *entire* form greys out and locks
for further edits. No error, no popup — completely silent.

Two different root causes have produced this exact symptom in this
project, and both are silent:

### A. `SelectionEvent` / `ResponseType 49` (declarative companion lookup)

The old `FILTER()/MOV()/SONON()/SETP()` pattern used to auto-populate a
description/name field from a picked value. **Confirmed dead**: using it
on *any* combo — even isolated to a single field, even with syntax copied
byte-for-byte from a real, working legacy form — jams the whole form's
edit/commit pipeline after one use. Every other field, including ones with
no lookup at all, can then only be edited once before locking.

**Do not use `SelectionEvent` in this tenant.** No exceptions found. This
was tested at both "all 11 companion fields wired" and "just 1 wired"
scale — same failure either way, so it's not a volume problem.

### B. A property's own `Read Only` flag not matching the form's usage

**Confirmed real, repeated cause**: when a property was originally
designed as a read-only, auto-populated *companion* field (e.g.
`AssignedUsername`, `QcReviewerUsername`, `PlanningReviewerName`) and later
repurposed to be the **primary, directly-writable** field a combo binds to
— the property's `Read Only` flag in Application Studio's IDO Properties
grid has to be manually unchecked. It is *not* something a Form Sync
re-import touches for an already-existing property, no matter how many
times you re-import the form XML or re-run an IDO Properties CSV import.

**The trap**: the Form Designer's Events panel for the component, and the
form's own Event Handlers list, can both be completely clean (no
`SelectionEvent`, no stray handler) — which rules out cause A — while the
real cause (B) is invisible from the Form Designer entirely. It only shows
up in the **IDO Properties grid**, on the property itself.

**Checklist when this symptom shows up on a newly-repurposed field:**
1. Confirm the form XML has zero `SelectionEvent`/`EventToGenerate`/
   `ENABLEDWHEN` tied to that field (rules out A).
2. Check that field's underlying property in Application Studio's IDO
   Properties grid — is `Read Only` checked? If the property used to be a
   read-only auto-populated companion, assume yes until confirmed
   otherwise.
3. Uncheck it there directly. This is a manual, per-property, live edit —
   generating a corrected schema CSV and re-importing does **not** flip
   this flag on an existing property.

**Confirmed instances of this exact bug, same fix each time:**
`AssignedUsername`, `QcReviewerUsername`, `EngReviewerUsername`,
`PlanningReviewerName`, `PurchasingReviewerName`, `CmReviewerName` — all
six were repurposed from read-only companions to primary writable fields
in the same session, and all six locked the form until their `Read Only`
flag was manually cleared in Application Studio.

**When this happens again on a newly-repurposed field, check the property's
Read Only flag first**, before opening a fresh diagnostic (typing vs.
selecting, checking for errors, etc.) — don't re-derive this from scratch.

### C. A component's `Type` (Edit vs. Combo) doesn't change on an existing component either

**Confirmed real, twice in a row on the same fields**: changing a
component's `<Type>` in the form XML (e.g. `1` Edit → `27` Combo, or back)
and re-importing does not change what actually renders live, when that
component already exists on the form from an earlier import. The XML
export can say `Type=27` and the live form still shows a plain text box -
no error, no warning, it just silently keeps the old control type. Same
underlying class of bug as B above (Form Sync re-import happily updates
*some* attributes of an existing component but not this one), confirmed
independently on `qc_reviewer_empnum`/`eng_reviewer_empnum`/
`planning_reviewer_empnum`/`purchasing_reviewer_empnum`/
`cm_reviewer_empnum` (meant to become combos) and their paired
`*Username`/`*ReviewerName` fields (meant to go back to plain edits) -
after two separate re-imports, the live form still showed the pre-fix
Type on all ten.

**Fix**: don't try to change an existing component's `Type` via Form Sync
XML re-import - it silently won't take. Either delete the component in
Application Studio's Form Designer first (so the next import creates it
fresh, not "updates" it), or change its Type by hand directly in the
Form Designer. A fresh XML re-import alone is not enough, no matter how
many times it's repeated.

**XML-only alternative tried, and it did not work.** Renaming a component
(giving it a new `Name` and leaving everything else the same), on the
theory that Form Sync would treat it as brand-new rather than an update -
applied to all ten fields above plus `c_assigned_empnum`/
`c_assigned_username` and `c_serial_num`/`c_lot_num` (fresh `_v2` suffix
on each, commit `55c0f7c`). **Confirmed live after re-import: the exact
same symptom persists under the new name** - every renamed ID/EmpNum
field still shows as a plain textbox and every renamed Username/Reviewer/
Name field still shows as the dropdown, the reverse of the intended Type
for each. Screenshots of Assigned, QC/Eng Reviewer, and all three
Implementation Reviewer rows all show the identical swapped arrangement
after the `_v2` re-import.

This also throws doubt on the premise the rename was based on: General
Review Complete's own checkbox is **still visible on the live form**
(grayed out) despite being fully removed from the schema/XML - so "an
absent-by-name component correctly vanishes live" may not be as reliably
true as it looked when this was proposed, which would explain why
treating a renamed component as "not present under this name yet" didn't
produce the hoped-for fresh creation either.

**Conclusion: there is no known XML-only fix for this bug.** Both XML
approaches (changing `Type` directly, and renaming to force a fresh
component) have now been tried and confirmed to fail, live, on the same
14 fields. The only remaining fix is manual, in Application Studio's Form
Designer: delete each affected component and let the next re-import
create it fresh, or change its Type by hand directly in the Designer.
Affected components (as currently named, `_v2` suffix): `c_assigned_empnum_v2`,
`c_assigned_username_v2`, `c_qc_reviewer_empnum_v2`, `c_qc_reviewer_username_v2`,
`c_eng_reviewer_empnum_v2`, `c_eng_reviewer_username_v2`,
`c_planning_reviewer_empnum_v2`, `c_planning_reviewer_name_v2`,
`c_purchasing_reviewer_empnum_v2`, `c_purchasing_reviewer_name_v2`,
`c_cm_reviewer_empnum_v2`, `c_cm_reviewer_name_v2`, `c_serial_num_v2`,
`c_lot_num_v2` (the last two also still render as plain edit boxes, no
dropdown arrow, in the same live screenshot).

**Re-verified directly against the checked-in XML** (not just recycled from
memory): every one of these components' `Type`/`DataSource` pairing in
`exports/eCMRs_v1.XML` (now `original/eCMRs.trn.original.xml`) is already exactly correct - e.g.
`c_qc_reviewer_empnum_v2` is `Type=27`/`DataSource=object.QcReviewerEmpNum`,
`c_qc_reviewer_username_v2` is `Type=1`/`DataSource=object.QcReviewerUsername`.
There is no further XML edit that changes this - the file already says the
right thing; only the live render disagrees. This confirms the bug is
entirely on the Application Studio/Form Sync side and genuinely needs a
human at that console; there is no tool available in this session (or any
prior one) that can drive Application Studio's desktop UI, run its Form
Designer, or exercise the live running form. One lead worth checking before
doing all 14 by hand: does Form Sync's import wizard have a "remove
components not in the file" option that isn't currently enabled? If it
matches existing components by their bound `DataSource` rather than by
`Name`, that would explain why the `_v2` rename didn't force a fresh
component - it would silently re-merge onto the old one by binding instead.
Untested, but cheap to check before assuming delete-and-recreate on all 14
is the only path.

## `EventToGenerate` custom scripts on a combo's value-change: not real here

Tried an inline VB `ResponseType 33` script (`Me.IDOClient.LoadCollection`
or `ThisForm.IDOClient.LoadCollection`) wired via `EventToGenerate` on a
Type=27 `EnhancedCombo`, as a replacement for the broken `SelectionEvent`
mechanism above. **Confirmed dead**: fires silently, does nothing, no
error, regardless of `Me` vs `ThisForm`.

Searched every real `EventToGenerate` usage in the legacy codebase
(`cmr-project`) to find a working precedent: custom-named scripts only
ever fire from **Buttons** (Type 8, click) or **Checkboxes**/grid columns
(Type 5/15, toggle) there. The one real Type=27 combo example uses a
*built-in* system event (`StdCurCompDetails`), not a custom script. There
is no confirmed real mechanism for firing custom logic off a combo's value
change in this environment, other than the broken `SelectionEvent`.

**Net result at the time**: no reliable way to auto-populate a companion
field from a combo selection via an *event* (`SelectionEvent` or
`EventToGenerate`) in this tenant. **Superseded** - see "Auto-populating a
description field via `DefaultFrom`" below for the real mechanism, which
doesn't use an event at all. Fields that don't fit that mechanism are
still plain manual-entry fields, or the combo binds directly to the
property that holds the value you actually want — see the `Username`
pattern below.

## Auto-populating a description field via `DefaultFrom` (the real mechanism)

**Confirmed real, directly from a live form's own XML export**
(`PurchaseOrders.XML`, `TermsCodeEdit`/`ShipCodeEdit` components) - a
plain declarative attribute on the *code* field's own component, no event
handler, no script, and critically **no `SelectionEvent`**:

```
<DefaultFrom>TermsCode(TermsCodeDesc)</DefaultFrom>
<PropertyClassName>TermsCode</PropertyClassName>
```

Syntax: `DefaultFrom: <PropertyClassName>(<OtherPropertyOnThisIDO>)`, set
on the code property's own component (`DataSource=object.TermsCode` in
this example). `<OtherProperty>` (`TermsCodeDesc`) doesn't need any
`DefaultFrom` of its own - it's a plain read-only display field
(`TermsCodeDescEdit`, `PropertyClassName=Description`, `ReadOnly=True`).
Confirmed as a repeated pattern in the same file, not a one-off:
`ShipCode(ShipCodeDesc)`, `TaxCodeOfTaxSystem(Tx1Description,'1',...)`, etc.

**Why this is safe to use, unlike `SelectionEvent`**: it's a plain
attribute evaluated by the property/class system, not a `ResponseType 49`
`EventHandler` with the `FILTER()/MOV()/SONON()/SETP()` pipeline that
jams the whole form (Rule #1A above). Nothing here touches that pipeline.

**What this does NOT confirm**: whether an arbitrary custom Property
Class (e.g. `QCReasonCode`, or a class we invent ourselves) supports this
same `DefaultFrom` behavior - `TermsCode`/`ShipCode` are real, compiled
system classes with native lookup logic tied to the class name itself.
Applied here to `Item`/`Wc`/`Dept`/`VendNum` (real system classes,
extrapolated from the same pattern - `VendNum` is independently confirmed
from the same PurchaseOrders form's own `VendNumEdit` component, `Item`/
`Wc`/`Dept` are not) for `ItemDescription`/`WcDescription`/
`DeptDescription`/`NextAssyDescription`/`VendorName` - **verify live
after import**.

**Update, live-tested on `Dept`: it broke.** (Fixed another way in form v2 - see "Description
auto-fill for Dept and Work Center" below.) Importing
`DefaultFrom="Dept(DeptDescription)"` (paired with `PropertyClassName="Dept"`)
threw, live, the moment a Dept value was selected: *"internal validation
error on c_dept validator Dept... Bad SETPROPERTIES specification in
validator Dept: this cache property OfcAddr4 not in cache."* Root cause:
`Dept` isn't a safe, form-scoped label here - it's SyteLine's real,
system-wide Department property class, and departments carry an office
address in the standard data model (hence `OfcAddr4`). Naming it in
`DefaultFrom`'s `ClassName(TargetProperty)` syntax pulls in *that whole
class's validators*, which expect properties our `ue_ecmrs` IDO's cache
doesn't have - a different, incompatible mechanism from `TermsCode`/
`ShipCode` above despite the identical syntax. `Wc` was removed
pre-emptively from this form for the same reason (same extrapolation,
never independently confirmed, same real system-class name) - not
independently tested, but not worth risking. **Do not reuse a real
system Property Class name in `DefaultFrom` (or bare `PropertyClassName`)
on this IDO without testing that exact class live first** - a class
being real and compiled somewhere does not mean it's compatible with a
cache that doesn't carry its expected properties.

**Update: `Item(ItemDescription)` and `VendNum(VendorName)` both confirmed
live-working.** Neither is a real system class the way `Dept` is (Item's
combo names `Item` as its `PropertyClassName`; `VendNum` is the real,
confirmed class from the live `PurchaseOrders` form) - narrower classes
without an address-style sub-structure, so they didn't hit Dept's
`OfcAddr4` crash. But `Item(ItemDescription)` still locked the whole form
on first try, for a **different** reason than Dept - see the next section.
`QCReasonCode`/`QCCauseCode` (Reason Code/Cause Code, referenced via bare
`PropertyClassName`, no `DefaultFrom`) remain untested against any of
this - they simply haven't been tried yet, not confirmed safe.

## A `DefaultFrom` target locking the form isn't always the Read Only flag (Rule #1B) - check for a stray `ComboListSource` too

`Item(ItemDescription)` locked the whole form the moment an Item was
selected - the exact same symptom as Rule #1B (a `DefaultFrom` target
whose Read Only flag is still set). Clearing `ItemDescription`'s Read
Only flag (both the form component's and, per Rule #1B, its IDO-level
flag) was necessary but **not sufficient** - the lock persisted.

**Real second cause, found by diffing a live-working auto-fill pair
against the locking one**: `ItemDescription`'s form component
(`edit1_SITE`, hand-added directly in Application Studio, not through
the generator) carried its own leftover `ComboListSource` - a
self-referential `STDOLE SLItems( PROPERTIES(Description,Item)
DISPLAY(1)RECORDCAP(0))` lookup - left over from however it was
originally copied into place. None of the six already-working auto-fill
targets (`AssignedUsername`, `QcReviewerUsername`, `EngReviewerUsername`,
`PlanningReviewerName`, `PurchasingReviewerName`, `CmReviewerName`) carry
a `ComboListSource` at all, even the ones that are plain `Type=1` Edit
fields exactly like this one. With `Item`'s own `DefaultFrom` trying to
write into `ItemDescription` while `ItemDescription`'s own component
*also* runs a self-referential lookup against the same `SLItems`
collection, the write collides with that list-source validation - a
different flavor of "something extra fights the `DefaultFrom` write,"
not a missing-combo problem (the intuitive guess would be the opposite -
that the target needs to *become* a combo - but every working target is
deliberately a bare `Type=1` Edit with nothing else attached).

**Fix**: remove the stray `ComboListSource` entirely, so the target
component is bare - just `DataSource`/`Binding`/`ReadOnly`/`Hidden`,
nothing else. Confirmed live working after this fix, alongside the Read
Only clear.

**Checklist for a `DefaultFrom` target that locks the form:**
1. Clear the target's Read Only flag, both the form component's own
   `ReadOnly` attribute and its IDO-level flag in Application Studio
   (Rule #1B) - the more common cause.
2. If it still locks after that, check whether the target component
   carries any leftover `ComboListSource`/other list-source attribute it
   shouldn't have (especially likely on hand-added components, not ones
   built through the generator) - remove it. The target should be a
   bare, plain field.

## Binding a combo directly to return `Username` instead of `EmpNum`

To make a combo return an employee's `Username` (a real email address in
this tenant, e.g. `gcaraway@enflite.com`) instead of their `EmpNum`,
without any auto-populate script: rebind the combo's own `DataSource` to
the `Username`-holding property, and reorder the `ComboListSource`'s
`PROPERTIES()` list so `Username` is listed **first**.

> **Correction 2026-09-29:** it's the first column in `DISPLAY(...)`, not in
> `PROPERTIES(...)`. With `DISPLAY(1,2,3)` the two are the same, which is why this looked
> positional on `PROPERTIES`. See "Data length for Notify" below.

STDOLE combos write back whichever property is listed first in
`PROPERTIES(...)` — confirmed **positional, not name-matched** (Vendor's
own combo proves this: `DataSource=Vendor`, but the list's first entry is
`VendNum`, a different name, and it still writes back correctly).

```
STDOLE SLEmployees( PROPERTIES(Username,EmpNum,Name) DISPLAY(1,2,3) RECORDCAP(0))
```

**This works once the target property's `Read Only` flag is cleared** —
see Rule #1B above. If you make this change and the field locks, that's
almost certainly the Read Only flag, not the binding itself. Confirmed
across 6 fields (`Assigned`, `QC/Eng Reviewer`, `Planning/Purchasing/CM
Reviewer`) — same symptom, same fix, every time.

If the target property was never meant to hold a Username (e.g.
`PlanningReviewerName` was designed for a full Name, not a Username), it's
fine to repurpose the existing property rather than create a new one in
Application Studio — just note it clearly in the schema description so
the property's name doesn't mislead anyone browsing the IDO Properties
grid later.

## `FP(x)` in a `FILTER()` clause is a plain exact-match — no wildcard, no padding

`FILTER(SomeColumn=FP(x))` matches the raw typed/selected text **exactly**
against `SomeColumn`. No partial match, no leading-zero padding, no
wildcard.

**Confirmed root cause of two separate bugs:**
- **Job Number**: typing `DK84716` never matched the real stored
  `DK00084716` (zero-padded) via the legacy `QC_CMRs` form's own Job Num
  combo (`comboBox4_SITE`): `STDOLE SLMatltrans( PROPERTIES(RefNum)
  DISPLAY(1) READMODE(UNCOMMITTED) DISTINCT()
  FILTER(RefNum=FP(rs_cmrUf_ENF_CMR_JobNum)) RECORDCAP(0))` - confirmed
  directly from that real combo's own List Source (read live via
  Application Studio's Form Designer). The property holding the job
  number in `SLMatltrans` is `RefNum`, not `Job`/`JobNum`.
- **PO Number**: `FILTER(PoNum=FP(PoNum))` (self-referencing) never
  matched anything, because real PO Numbers are zero-padded with a
  variable-length prefix (confirmed real examples: `RD00000021`,
  `INT0120033` — different prefix lengths, same total length, no single
  padding rule could reconstruct either from partial input).

**Fix used for both**: drop the `FILTER()` entirely and list every row
unfiltered - `STDOLE SLPoItems(...)` for PO Number, `STDOLE
SLMatltrans( PROPERTIES(RefNum) ... )` (no `FILTER`) for Job Number -
same pattern already proven working for `Item`/`Work Center`/`Dept`/
`Vendor` on this form. The `EnhancedCombo`'s own client-side type-ahead
handles narrowing it down instead of a server-side exact match.

**Two wrong turns taken before landing on the real fix for Job Number -
worth remembering the shape of both**:
1. **Guessing an IDO name from a naming convention instead of reading a
   real combo.** `SLJobs` was assumed from the same `SL<Name>` pattern
   that worked for `SLItems`/`SLDepts`/`SLWcs`/`SLVendors`/`SLPoItems` -
   but it turned out to be a real, different IDO in this tenant
   (returns generic sequential values like `C000000001`, `C000000002`,
   unrelated to Job Orders, regardless of what's typed). It didn't
   error, so the wrongness was silent - the working `SL<Name>`
   IDOs above were all confirmed from a real combo first, this one
   wasn't, and that's the difference that mattered.
2. **Assuming "the real form's own field has no combo" means "no combo
   exists to copy."** The real `JobOrders` form's own `Job` field is a
   plain Edit (`Binding: object.Job`, no List Source at all) - true, but
   irrelevant, because that field IS the job record itself with nothing
   to look up. `eCMRs`'s Job Num field is a *reference* to some other
   job, the same relationship PO Num has to PO Items - so the right
   place to look was a *different* real form that references a job the
   same way (the legacy `QC_CMRs` form itself), not the job's own master
   record form.

The general lesson holds from every other combo on this form: **read a
real, already-working combo's List Source directly instead of inferring
one from a pattern**, even when the pattern has worked several times
before.

**Don't confuse this with `'P(x)'`** (single-quoted, no leading `F`) —
that's a different, legitimate mechanism: a cross-field reference to the
*current record's own already-set value* of property `x`. Used
successfully for cascading combos, e.g. `PO Line`'s filter
`FILTER(PoNum='P(PoNum)')` narrows Line options to the already-selected PO
Number — that one is fine and not the same bug.

## SQL Columns import: `Data Type` must be a real concrete type

Application Studio's SQL Columns grid rejects the generic word `"String"`
outright: **"String is not a valid Data Type."** Confirmed live. It needs
a real type — `char`, `nvarchar`, `decimal`, `datetime`,
`uniqueidentifier`, `tinyint`, or a named class like `ItemType`/
`UsernameType`/`QCPriorityType` — confirmed by cross-checking a live
`ToExcel_SqlColumns` export where every existing column uses one of these,
never the literal word `String`.

## IDO Properties/SQL Columns import CSVs must match the live export's exact header, column count, and quoting

A full review against a fresher live export (`docs/reference/ToExcel_IdoProperties_4.csv`,
42 columns) found our generated `ecmrs_ido_properties_import.csv` had drifted from it in three
ways, all silent (no rejected-import error to notice, since these are formatting mismatches,
not value-validation errors):

- **Missing columns.** The live grid grew two columns since the reference export our generator
  was originally built against (`ToExcel_IdoProperties_3.csv`, 40 columns): `Validate
  Immediately` and `Validate Immediately Prompt`, inserted right before the trailing `Property
  Value`/blank columns. Our generator was still emitting the old 40-column shape. If the import
  is positional rather than header-matched, this silently shifts every column after that point
  into the wrong field.
- **Wrong header names.** The live grid's header uses `*Data Type`, `*Length`, `*Column Data
  Type`, and `*Read Only` (asterisk-prefixed) - our generator wrote `Data Type`, `Length`,
  `Column Data Type`, `Read Only` (no asterisk). If the import matches by header name, none of
  these columns would be recognized.
- **Header quoting differs from data-row quoting.** Every header cell in a live export is
  quoted (`"Sequence"`, `"Read Only Record"`, ...) except the trailing blank column - a
  completely different convention from data rows, which only quote actual string-typed columns
  and leave numeric/flag columns bare. Our generator was reusing the data-row quoting logic for
  the header row too, so header cells that are bare in a data row (`Sequence`, `Pseudo Key`,
  `Required`, ...) came out unquoted in the header as well - wrong.
- **`*Read Only` and `Read Only Record` are two different flags, not one written twice.**
  Confirmed from the same live export: `*Read Only=1` appears ONLY on the 5 truly
  auto-generated system properties (`CreatedBy`, `UpdatedBy`, `CreateDate`, `RecordDate`,
  `RowPointer`) - never on any custom property, read-only or not. `Read Only Record` is the
  real read-only flag for a custom property (confirmed on `InWorkflow` and every read-only
  companion field: `ItemDescription`, `AssignedUsername`, `CloseDate`, ...). Our generator was
  writing the same `readonly` value into both columns, which would have incorrectly set
  `*Read Only=1` on every read-only custom property we import (`CloseDate`, `ClosedBy`, the
  description companion fields).

Same class of bug existed in the SQL Columns import (`ecmrs_sql_columns_import.csv`): the
trailing blank column was quoted (`""`) when the live export leaves it bare, and the header row
used the same non-quoting mistake as above.

**Lesson**: don't just check whether Application Studio *rejects* an import - a live export's
exact header/column-count/quoting also has to be diffed byte-for-byte against what the
generator produces, since a formatting mismatch (missing column, wrong header name, wrong
quoting) fails silently rather than throwing a validation error. `docs/reference/` should be
kept up to date with the freshest real export for exactly this reason.

## IDO Properties import: `Property Class` also rejects `"String"`

Same error family, different field: **"String is not a valid Property
Class."** Confirmed live while adding `SerialNum`/`LotNum`. `Property
Class` should be left blank for a plain property — confirmed from a live
IDO Properties export where all 76 existing custom properties (everything
except the 7 auto-generated system ones) have a blank `Property Class`.

## IDO Properties import: `Column Data Type` should be blank for custom properties

The generator used to default this to the generic base type (or a guessed
class like `JobBase`). **Confirmed wrong** from the same live IDO
Properties export: every one of the 76 custom properties has a **blank**
`Column Data Type`. It's only ever populated on the 7 auto-generated
system properties (`CreatedBy`/`UpdatedBy` → `UsernameType`,
`CreateDate`/`RecordDate` → `CurrentDateType`, `RowPointer` →
`RowPointerType`, `NoteExistsFlag`/`InWorkflow` → `FlagNyType`). Leave it
blank for anything new.

(The IDO Properties import's plain `Data Type` field is different from
the above and does accept generic base types — `String`, `Date`, `GUID`,
`Decimal`, `Byte` — confirmed from the same live export. It's specifically
`Column Data Type` and `Property Class` that reject `String`, not `Data
Type` itself.)

## Fixed-value dropdowns (Priority, Initial Change, QC/Eng Disposition, Status)

These cannot get their value list via CSV/Form-Sync import at all. They
need an **Inline List configured directly on the property itself in
Application Studio**, manually, per property. The form's own combo
component needs no `ComboListSource`/`PropertyClassName` for these — an
empty-looking combo with none of those attributes in the form XML is
*expected*, not a bug, until the property-level setup is done.

**Correction, confirmed live from the actual Edit Property dialog for
`Status`**: there is no separate Property Class object to create at all
in this environment. `Property Class` stays **blank**, and the value list
goes directly into that same property's own `*Inline List` field, using
the syntax `ENTRIES(value1,value2,value3,...)` (e.g.
`ENTRIES(CM,Complete,Data Input,Eng Review,Planning,Purchasing,QC
Approval)` for Status). One field, one step - not the two-step
"create a class, then point Property Class at it" process assumed
earlier in this doc. That earlier assumption was never actually confirmed
against the real dialog and turned out to be wrong.

**Editing the property alone is not enough - it must be checked in.**
Setting `*Data Type`/`*Inline List` in the Properties grid and closing the
dialog does not persist the change by itself. The IDO itself has to be
**checked in** (IDOs tab → find the IDO → Check In) before the form-save
validation sees the new value. If source control integration isn't
configured for the tenant, Check In will show an informational popup —
*"Source control integration is currently disabled in the current
configuration. The item will not be checked in to source control."* -
that's harmless, just click OK; the local check-in still applies. Skipping
this step is exactly what produced a **"Missing property data type for
ue_ecmrs.Status"** error on form save even though the property's own
`*Data Type` field visibly showed `String` in the still-open dialog - the
form was still validating against the old, not-yet-checked-in state.

Confirmed real value lists:
- `Status`: CM, Complete, Data Input, Eng Review, Planning, Purchasing, QC Approval
- `Priority`: High, Medium, Low
- `InitialChange`: Documentation, Machine, Material, Other, Process, Specification, Tooling, Variance(waiver)
- `QcDisposition`: Accept, Hold, NFF, NRS, Other, Reject, Rework, Scrap
- `EngDisposition`: NFF, NRS, Other, Rework, Scrap (subset of QcDisposition — missing Accept/Hold/Reject)
- `ReasonCode`/`CauseCode`: different mechanism from the others above - see the next section.
  Not an Inline List of our own at all; references real, existing system Property Classes
  directly.

## Reason Code / Cause Code: reference the real QCReasonCode/QCCauseCode classes directly

> **Superseded 2026-09-28 (form v2).** This did not work on `ue_ecmrs` - see "`'FP' is not a
> recognized built-in function name`" below. Kept for the history.

The signed CMR Development SOW (`Enflite - 00004 - CMR Development`) documents that SyteLine
already has real, existing Reason Codes and Cause Codes master data, categorized by a `Ref Type`
(`E`=Enterprise, `J`=In Process, `O`=Customer, `P`=Supplier, `R`=Customer RMA), with a signed
plan to add a new `Ref Type` value `C` (for CMR) and filter to it. That `RefType='C'` filtering
plan was **not** what got built (see below on why), but the underlying real classes turned out
to be directly usable without it.

**Confirmed directly from a real, live form's own XML export** (`QC_MRRs.XML`, uploaded and
inspected directly - not guessed): its `ReasonEdit`/`CauseEdit` components (`Type 27`,
`EnhancedCombo`, same as our own) carry **no `ComboListSource` at all** - just a
`PropertyClassName` tag directly on the component (`QCReasonCode` for Reason, `QCCauseCode` for
Cause). No STDOLE syntax, no IDO/property names to guess - the real system Property Class name
is the whole mechanism.

**Per direct request** ("we can use this list that exists right now... it will not always be
the same on the CMR as it is on the MRR, we are just using this list"), `eCMRs`'s own
`ReasonCode`/`CauseCode` combos now carry the same `PropertyClassName` tags directly - see
`generate_form.py`'s Quality section `LAYOUT` entry. This is a **component-level** override,
independent of the property's own Property Class (which stays blank at the IDO level, same as
every other property here) - `f(..., property_class_name="QCReasonCode")` threads a new
`PropertyClassName` XML tag through `emit_field`/`emit_control`, alongside the existing
`list_source`/`maintain_from_spec` parameters.

**What this means for "adding a new code when needed"**: since `QCReasonCode`/`QCCauseCode` are
real, shared, system-wide classes (not something eCMRs owns), a new code has to be added
wherever those classes' own values are actually maintained (whatever real SyteLine
screen/mechanism backs them - not investigated, since the immediate need was just to reference
the existing list) - not via `docs/deploy-checklist.md`'s Inline-List step, which no longer
applies to these two fields at all.

**Known, deliberate trade-off**: eCMRs' Reason/Cause Code currently shares MRR's exact list.
Per the request above, that's expected to diverge later (the SOW's own `RefType='C'` idea is
one way that could happen) - not a bug if the two lists don't match forever.

**Unconfirmed**: whether a component's `PropertyClassName` can validly reference a class
unrelated to its own bound IDO property (`ReasonCode`/`CauseCode`, both plain, Property
Class-blank String properties) the way `QCReasonCode`/`QCCauseCode` are architecturally
independent classes on `RS_QCMrrs`'s `Reason`/`Cause` properties. Directly copying real,
confirmed-working syntax from a live form is exactly the method that resolved every other
combo on this form (including twice for Job Number) - but this specific cross-IDO reference
hasn't been tested live yet. Verify after import and update this note.

## The close workflow: removed, then restored (in Implementation, not CMR Details)

The `Closed` checkbox (and its `SetCloseInfo` event handler) was originally removed from the
form because the user said it wasn't needed at the time. That left `Closed`/`CloseDate`/
`ClosedBy` all dead: `Closed` permanently `0`, `CloseDate`/`ClosedBy` marked read-only with
nothing to set them, and the form's `ORDERBY` (which used to sort on `Closed` to put open CMRs
first) simplified to just `CmrNum desc`.

**Restored later, on request, moved into the Implementation section** (not back into CMR
Details where it originally lived): the exact original `SetCloseInfo` mechanism - a plain
`Closed` checkbox with `EventToGenerate="SetCloseInfo"` wired to it, and the event handler
itself restored unchanged:

```vb
If ThisForm.Components("c_closed").Text <> "1" Then
    ThisForm.Components("c_closed_by").Text = ""
    ThisForm.Components("c_close_date").Text = ""
Else
    ThisForm.Components("c_closed_by").Text = ThisForm.UserName
    ThisForm.Components("c_close_date").Text = CStr(Today)
End If
```

This is safe to restore exactly as it was: checkbox `EventToGenerate` is a **confirmed-working**
mechanism in this tenant (unlike `SelectionEvent` on a combo, which is confirmed dead - see
Rule #1 above). `NotifyEngineering`'s button already proves `EventToGenerate` scripts fire
correctly here; `SetCloseInfo` on a checkbox toggle is the same category of mechanism. The
`ORDERBY` was restored to `ORDERBY(Closed asc, CmrNum desc)` accordingly - `Closed` is no
longer permanently `0`, so sorting on it is meaningful again.

**Still not restored, and not requested**: `GeneralReviewComplete` remains a read-only checkbox
with nothing that sets it - it was never wired to `SetCloseInfo` or anything else, before or
after this restore, and `Closed` is not gated by the `ReqX`/`XReviewComplete` checkboxes either
(despite an earlier, inaccurate schema description claiming that gating existed - it never was
implemented; `Closed` is a plain, manually-checked box).

## Dead schema: columns that exist but aren't on the form

A handful of custom columns in `generate_schema_csv.py`'s `FIELDS`/`ORPHANED_COLUMNS` still
aren't bound to any component on the current form: the 6 `*_review_complete`/
`general_review_complete` cascade flags (no cascade UI was ever built - matches the real
original form too, where these live inside a `Hidden=True` notebook container, not just
off-screen), `AdditionalChanges`, `WorkflowStatus`, and `GeneralCloseDate`/`GeneralClosedBy`.

**`GeneralCloseDate`/`GeneralClosedBy` are a confirmed intentional exclusion, not an oversight**:
both are `Hidden=True` on the real original form too (`dateCombo5`/`enhancedCombo2` in
`cmr-project`'s `QC_CMRs_Original.XML`) - never user-visible there either, so there's nothing
to "restore" here; surfacing them on our form would be adding something the original itself
deliberately hid, not fixing a gap.

`NextAssyDescription`/`VendorName`/`InternalReviewDate` used to be in this "not on the form"
list too - all three restored to the form as plain manual-entry fields (see "Auto-populating a
description field via `DefaultFrom`" above for why no auto-fill exists for the first two). The
`*_empnum` companion columns and the `*_description`/`VendorName` companion columns' ID-slot
half were restored earlier for the same reason.

These are **not removed** from the schema - the underlying SQL columns and IDO properties
already exist live from earlier imports, and dropping a live column/property is a separate,
destructive decision, not something a schema-generator refactor should do as a side effect.
Instead they're tracked explicitly in `ORPHANED_COLUMNS` (`generate_schema_csv.py`), which
prefixes each one's description with `[ORPHANED - ...]` in every export (table columns, IDO
properties, deploy checklist) so nobody mistakes "not on the form" for "not real," and so a
future contributor doesn't have to re-derive why each one is dead. If a column here gets
reused for something later, take it back out of `ORPHANED_COLUMNS`.

## Description auto-fill for Dept and Work Center: use `Validators`, not `DefaultFrom`

**Symptom**: picking a **Dept** or **Work Center** leaves **Dept Description** / **WC
Description** blank (form v1). An earlier try with `DefaultFrom="Dept(DeptDescription)"` +
`PropertyClassName="Dept"` threw *"Bad SETPROPERTIES specification in validator Dept: this cache
property OfcAddr4 not in cache"*.

**Cause**: `PropertyClassName="Dept"` brings in the `Dept` class's default validator, whose
default settings write `OfcAddr4` too - a property `ue_ecmrs` doesn't have. The description
fields had no other way to be filled.

**Update 2026-09-29 - the `Dept(...)` validator failed on TRN too**: *"internal validation error
on c_dept validator Dept, val type In Collection: Bad SETPROPERTIES specification in validator
Dept: this cache property DivName not in cache"*. The `Dept` validator always writes several
properties (`DivName`, `OfcAddr4`, ...) that the Service Orders IDO has and `ue_ecmrs` doesn't;
leaving its second argument empty doesn't stop that. **Don't use a named system validator
(`Dept`, `WcDesc`, ...) on this IDO.**

**Fix (form v2, `tools/apply_form_changes.py`)**: Infor's generic `SetPropertyFromList(<target
property>, <list column>)` validator. It copies one column of the selected dropdown row into one
property and writes nothing else. Used on the live Incidents form in this tenant
(`SetPropertyFromList(FSIncReasons.Duration, Duration)`).

| Component | Validators | List source (already there) |
|---|---|---|
| `c_dept` | `SetPropertyFromList(DeptDescription, Description)` | `SLDepts( PROPERTIES(Dept, Description) )` |
| `c_wc` | `SetPropertyFromList(WcDescription, Description)` | `SLWcs( PROPERTIES(Wc, Description) )` |

The list column (`Description`) must be in the dropdown's `PROPERTIES()`.

**Confirmed on TRN 2026-09-29**: Dept `100` → **Operations**, Work Center `BRAZE` → **Brazing**.

The target properties (`DeptDescription`, `WcDescription`) must have their IDO **Read Only**
flag cleared (Rule #1B, `docs/deploy-checklist.md`), and their form components stay bare Edit
boxes (no list source, see the ItemDescription section above).

Environments: TRN (confirmed), then production.

## `'FP' is not a recognized built-in function name.::4` on Cause Code (and an empty Reason list)

**Symptom**: opening the **Cause Code** dropdown shows *"'FP' is not a recognized built-in
function name.::4"*. **Reason Code** opens but nothing can be selected (form v1).

**Cause**: both dropdowns had no list of their own - only `PropertyClassName="QCReasonCode"` /
`"QCCauseCode"`, borrowed from the QC_MRRs form. Those classes' lists filter on QC_MRRs fields
with `FP(<field>)`. `ue_ecmrs` has no such field, so `FP(...)` isn't replaced and reaches SQL as
literal text. Pointing at these classes can't work on this IDO.

**Fix (form v2)**: `PropertyClassName` removed from `c_reason_code` / `c_cause_code`. Each
property gets its own **Inline List** with the same codes as the live QC_MRRs dropdowns
(`scripts/generate_ido_import.py` `INLINE_LISTS`, listed in `docs/deploy-checklist.md`):

- Reason: `ASMBL, DAMAGED, DELIVERY, DOCUMENT, FEATURE, FUNCTION, INTERNAL, MATERIAL, MEASURE, PURCHASE, REVISION, SUPDAM, VISUAL`
- Cause: `ENF, ENG, EXC, FUNC, HANDLE, NFF, QCM, SHIP, SHORTAGE, SUP, TOOL, UNK, VOID`

Set the Inline List on `ReasonCode` and `CauseCode` in the IDO Properties grid and **Check In**
the IDO before importing form v2. A code added in QCS later has to be added to both places.

**Update 2026-09-28: the first v2 import still showed the error.** Importing `c_cause_code`
with its `<PropertyClassName>` line removed did not clear the class on TRN - FormSync keeps a
setting that is simply missing from the file (same family as Rule #1B / #1C). Fix: the
components are now `c_reason_code_v2` / `c_cause_code_v2`, so FormSync creates them fresh with
no class. If the error still shows after that, check the **IDO property** itself: in the IDO
Properties grid, `CauseCode` and `ReasonCode` must have a blank **Property Class** (the class
may have been set there by hand at some point) - clear it and **Check In**.

**Confirmed on TRN 2026-09-29**: both dropdowns list their codes, no error (e.g. DAMAGED / EXC).

## Serial # / LOT # dropdowns are empty

**Symptom**: no values in **Serial #** or **LOT #** after picking an Item.

**Cause (most likely)**: the lists only show serials/lots **for the selected Item**
(`FILTER(Item='P(Item)')` on `SLSerials` / `SLLots`). An item that isn't serial- or
lot-tracked, or has no serials/lots yet, gives an empty list. That is expected, and you can
still type a value.

**Seen on TRN 2026-09-29**: Item `92185-001-02` - LOT # lists `20092024-000002`, Serial #
opens with an empty list and no error. An empty list with no error means the query ran and found
no serials for that item (a lot-tracked item), not a broken dropdown.

**Check**: pick an Item you know has serials (or lots) - e.g. one from a recent receipt - and open
the dropdown. To see what exists for an item, open a throw-away Dataview on `SLSerials` (or
`SLLots`) filtered on `Item = <item>`. If the Dataview has rows and the dropdown is still empty,
that's a real bug - write it up here.

## `Data length for Notify (12) is greater than effective length (10).`

**Symptom**: saving a CMR fails with this message. **PO Line** shows an Item number (e.g.
`92185-001-17`) instead of a line number.

**Cause**: the PO Line dropdown was `STDOLE SLPoItems( PROPERTIES(PoLine,Item,PoNum)
DISPLAY(2,1,3) ...)`. A dropdown writes back the **first displayed** column, so it wrote the
Item (12 characters) into `PoLine` (length 10). "Notify" is wrong in the message only because
the fields had no Caption linking them to their labels, so SyteLine used a nearby component's
name.

Also seen as *"String or binary data would be truncated in table ...ue_ecmrs, column
'po_line'. Truncated value: '92185-001-'"* - same bug, reported by SQL instead of the form.

**Fix (form v2)**: `DISPLAY(1,2,3)` again - PoLine first, Item still shown in the list. Every
bound field now has `Caption = C(<its label>)` (how Infor's forms link a field to its label),
so messages name the real field.

**Confirmed on TRN 2026-09-29**: PO Line shows the line number (e.g. `1`); save works.
Rule for every dropdown: the value you want stored must be the first column in `DISPLAY()`.

## IDO property lengths must match the SQL column lengths

**Symptom**: *"String or binary data would be truncated in table ...ue_ecmrs, column '<col>'"*
(IDO longer than SQL), or *"Data length for <field> (n) is greater than effective length (m)"*
(IDO shorter than the value).

**Cause**: when the IDO properties were created, most text properties got a default length
(20, or 100 for `PoLine`) instead of their SQL column's length. Found 2026-09-29 by comparing
the two TRN exports: 22 properties differ. Also `cause_code` was created as `char(1)` with
Default Value `(100)` - the 100 went into the wrong box.

**Decision 2026-09-29**: the text columns we own become `char(255)` (they were `char` of 1 to
160; widened on TRN 2026-09-29); columns on SyteLine data types keep their type's length. `cause_code`
(`char(1)`) then fails with *"String or binary data would be truncated ... column 'cause_code'.
Truncated value: '1'"* until it's changed.

**Fix**: follow [`length-fixes.md`](length-fixes.md), generated by
`scripts/compare_live_lengths.py` from the exports in `docs/reference/`. After fixing, export
both grids again (**SQL Columns** and **IDO Properties** → Excel), save them as
`docs/reference/ToExcel_SqlColumns_<date>.csv` / `ToExcel_IdoProperties_<date>.csv`, re-run the
script, and the IDO list should be empty.

## `Error compiling script EvHandler_SetCloseInfo_0` when ticking **Closed**

**Symptom**: ticking the **Closed** checkbox shows *"Error compiling script
EvHandler_SetCloseInfo_0"* (TRN, 2026-09-29).

**Cause**: our script set Closed By with `ThisForm.UserName`, which doesn't exist in the
scripting API, so the script never compiled. The earlier claim that this script was "unchanged,
byte-for-byte" from the original was wrong: the original never used `ThisForm.UserName`.

**Fix (form v2)**: copied the original QC_CMRs form's working pattern exactly:
- `SetCloseInfo` (checkbox event) clears or sets **Close Date** as before, but for Closed By it
  calls `ThisForm.GenerateEvent("SetClosedBy")`; `Namespace SyteLine.GlobalScripts` as in the
  original.
- New handler `SetClosedBy`, ResponseType 22: `SETPROPVALUES(ClosedBy=USERNAME())` - sets the
  property to the logged-in user. Our property is also named `ClosedBy`.

`ClosedBy` / `CloseDate` must not be Read Only at the IDO level (both are clear in the
2026-09-29 export).

**Confirmed on TRN 2026-09-29**: ticking **Closed** works. Test: Close Date = today, Closed By = your user; untick -
both clear. Save and reopen.

## `Error Message does not exist. Object:PK_ue_ecmrs, Type:17` on save

**Symptom**: saving a CMR fails with this message (TRN, 2026-09-29).

**Cause**: `PK_ue_ecmrs` is the table's primary key on `cmr_num` - the save tried to write a
CMR Num that already exists ("Error Message does not exist" only means no friendly text is set
up for that constraint). `CmrNum` is a `NumSortedString`, stored padded with leading spaces to
the IDO **Length**. Its length was changed from **10** (22 Sep export) to **20** (29 Sep). Records
from before are stored 10 wide, newer ones 20 wide. AUTONUMBER takes the highest value + 1, and
the 10-wide values always sort above the 20-wide ones (a space sorts before a digit), so it keeps
producing the same next number - which already exists 20 wide.

**Fix (decided 2026-09-29)**: drop AUTONUMBER. CMR Num is now `CMR-YYMMDD-HHMMSS` (e.g.
`CMR-260929-111742`), set by the form when you click **New** (`StdObjectNewCompleted` script, the
same pattern the Incidents form uses). The IDO **Default Value** can't do this itself: it only
takes keywords like `AUTONUMBER(...)` or `CURDATE() CURTIME()`, and can't add `CMR-` or pick the
format. In IDO Properties, `CmrNum`: **Default Value** cleared, **Data Type** `String` (not
`NumSortedString` - no padding), **Length** 255 (as set on TRN; the value is 17 characters). Leave the SQL column's 999 alone. Two CMRs
created in the same second would still clash - retry the save.

**Clean-up**: any CMR saved while the length was 20 is stored 20 wide. In the list sorted by CMR
Num those show out of order (at the bottom), and one may repeat a number used by a 10-wide
record. On TRN they're test records: delete them from the form.

**Confirmed on TRN 2026-09-29**: **New** shows `CMR-YYMMDD-HHMMSS`, and saves work.
Old test records keep their padded numbers (they sort at the end) - delete them.

## Right-click → Help: `Invalid URL string, or no help is defined for this form or field`

**Symptom**: right-clicking a field and choosing **Help** shows this message (TRN, 2026-09-29).

**Cause**: the form had no help link. Infor's forms set `<HelpFileName>` on the form (e.g.
QC_CMRs: `default.html?helpcontent=mergedProjects/sl_qcs/forms/nonmaterial/qc_cmrs.htm`); most
fields have none of their own and use the form's.

**Fix (form v2)**: the form's `HelpFileName` points to the same Infor topic as QC_CMRs, the
closest match for eCMRs. Right-click → Help on any field opens it.

**Own help pages can't be linked here (confirmed on TRN 2026-09-29)**: with the fields'
`HelpFileName` set to `file:///S:/.../index.html`, Help opened
`https://docs.infor.com/csi/latest/en-u/csbiolh/file:///S:/Engineering/Individual%20Folders/JSmith/eCMRs/index.html`.
SyteLine always puts its Infor help address in front of `HelpFileName`, so right-click Help can
only open pages on Infor's help site, so it stays on the Infor QC CMRs topic.

**Help button (2026-09-29)**: a **Help** button next to **Notify** opens the eCMRs help pages. It
raises event `OpenEcmrsHelp`, a ResponseType 39 `URL(<address>) ( )` handler - the response
Infor's own forms use to open links (tracking link on Customer Order Lines, `mailto:` on
Incidents / Service Orders). Address (`HELP_BUTTON_URL` in `tools/apply_form_changes.py`):
`file:///S:/Engineering/Individual%20Folders/JSmith/eCMRs/docs/help/index.html` - i.e. the repo
copied to `S:\Engineering\Individual Folders\JSmith\eCMRs`, with the pages in `docs\help`. After changing help text, rebuild
(`scripts/build_help.py`) and copy `docs\help` again; the form doesn't change.

**Check on TRN**: click **Help**. If nothing opens, the browser is blocking a `file:` link from the
SyteLine web page (Edge/Chrome do by default): put the folder on an internal web server or
SharePoint, change `HELP_BUTTON_URL` to its `https://` address, rebuild and re-import. Everyone
needs `S:` mapped the same way and read access to the folder.

## Dept / WC Description only fill in after **Save**

**Symptom** (team review on TRN, 2026-09-29): pick a Dept or Work Center; **Dept Description** /
**WC Description** stay empty until the record is saved.

**Cause**: the `SetPropertyFromList` validators on `c_dept` / `c_wc` run when the component is
validated, and without **Validate Immediately** that only happens on save. In the form XML it is
bit 32 of the component's `<Flags>`: every Infor component with a validator has it (Service Orders
`DeptEdit` = `33`, QC_CreateChangeRequest `DeptEdit` = `8225` = 8192 + 32 + 1). Ours had `1`.

**Fix**: `<Flags>33</Flags>` on `c_dept` and `c_wc` (`tools/apply_form_changes.py` step 14),
re-import through FormSync. In Design Mode it's the component's **Validate Immediately** box.

**Confirm**: pick a Dept: the description fills straight away, before saving. Same for Work Center.
Environments: TRN (to confirm), then production with the same file.

## Help opens a `GetFile.aspx` page ("If the following link will not open, copy the file path...")

**Symptom** (TRN, 2026-09-29): clicking Help opens a new tab at
`https://csi10f.erpsl.inforcloudsuite.com/WSWebClient/GetFile.aspx?u_addr=file%3A%2F%2FS%3A%2F...`
showing "If the following link will not open, copy the file path below and paste it into the
address bar above", the `file://S:/...` link and a **Copy Link** button.

**Cause**: SyteLine runs as an `https://` web page, and browsers (Chrome, Edge) never let a web page
open a `file:` address. The SyteLine web client knows this, so for any `file:` URL it opens its own
`GetFile.aspx` helper page instead, with the path to copy. Nothing in the form can change that: it is
the browser's security rule. (It does show the form's `URL(...)` handler ran.)

**Fix**: serve `docs/help` from an `https://` address the team can reach, then set `HELP_BUTTON_URL`
in `tools/apply_form_changes.py` to that address, rebuild and re-import. Options: an internal web
server (IIS) or an Azure Static Web App with company sign-in. SharePoint Online document libraries
download `.html` files instead of showing them, so a plain library doesn't work. Don't use a public
site: the procedures are company private. Until then, **Copy Link** and paste into the address bar
works.

**Environments**: TRN and production (same browser rule).

## Right-click → Help opening the eCMRs pages (`StdFormComponentHelp`)

> **2026-09-29:** the pages moved to the Enflite help ([Enflite/help](https://github.com/Enflite/help),
> React + Express + MongoDB). The script now builds `<HELP_SITE>/go/syteline/ecmrs/<component>`
> (`HELP_SITE` = `https://help-seven-xi.vercel.app`, the Vercel production domain, since 2026-09-30; before that `https://help-212448u20-hellojakesmiths-projects.vercel.app`, one fixed deployment, and `http://localhost:5173`, the help's dev server), and the help
> redirects to the field's page. The `docs/help/c/` pages below are the old S: drive version.
>
> **Which field was clicked**: the script tries an event parameter that names a form component
> first, then `GetCurrentComponentName()` (the focused field), and adds `?via=parm`, `?via=focus` or
> `?via=none` to the link. The help server prints one line per click
> (`help link syteline/ecmrs component=c_item via=focus -> /syteline/ecmrs/fields/item`). If it
> says `via=none`, SyteLine didn't tell the script which field: click into the field first, then
> right-click → Help, and report what the log shows.
>
> **2026-09-30, TRN: `ev=form via=none`.** SyteLine raised the form's Help for right-click a field,
> and the script found neither a parameter naming a component nor a focused component. The script
> now says which: both help events pass the event's parameters to `ENF_FindHelpField` (variable
> `EcmrsHelpParms`), and the link carries them as `&p=` plus a finer `via=`: `parm`, `focus`,
> `focusempty` (`GetCurrentComponentName()` exists but returned nothing), `nofocusapi` (the method
> doesn't exist here) or `none`. Vercel's request log lists every query value (**Search Params**).
>
> **2026-09-30, TRN: right-click a field → Help opened the eCMRs form page, not the field's.**
> Cause: the help log showed `GET /go/syteline/ecmrs` with no `?via=`, the link the form's own Help
> (`StdFormHelp`) sends, so SyteLine raised `StdFormHelp` for the right-click, not
> `StdFormComponentHelp`. Fix: `StdFormHelp` runs the same script (find the clicked component, then
> `URL(V(EcmrsHelpUrl))`), and every link says which event sent it (`&ev=field` or `&ev=form`).
> Rebuild, import on TRN, right-click a field → Help. Confirm: the field's page opens; the log line
> reads `ev=form via=focus` or `via=parm`. If it reads `via=none`, the form page says so too. TRN,
> then production.

`HelpFileName` can't do it (SyteLine prefixes Infor's help address, see above). Right-click → **Help**
raises the standard event `StdFormComponentHelp` (the form's own Help: `StdFormHelp`) - both are in
Mongoose's standard event list next to `StdFormPredisplay` etc. The form handles them itself:

1. `StdFormComponentHelp` 0: a script sets variable `EcmrsHelpUrl` to
   `.../docs/help/c/<component>.html` for the component clicked
   (`ThisForm.GetCurrentComponentName()`, late-bound in a `Try` so a missing method falls back to
   `index.html` instead of a compile error).
2. `StdFormComponentHelp` 1: `URL(V(EcmrsHelpUrl)) ( )` - the same `URL(V(...))` response Customer
   Order Lines uses for its tracking link.
3. `StdFormHelp` 0: `URL(<help>/index.html) ( )`.

`scripts/build_help.py` writes one `c/<component>.html` per component in `exports/eCMRs_v2.XML`,
each redirecting to that field's page (labels to their field, the rest to the form topic).

**Check on TRN** (not confirmed yet): right-click a field → **Help** opens that field's page. If
Infor's topic opens as well, SyteLine still runs its built-in help after ours: write that down here.
If the index page opens for every field, `GetCurrentComponentName` didn't return the clicked
component: write that down too. If nothing opens: the browser blocks the `file:` link (see above).

## "SCRIPTTEXT keyword required for InlineScript event handlers" on right-click → Help

**Symptom** (TRN, 2026-09-30): right-click a field → **Help** shows a dialog **Infor SyteLine -
eCMRs**: `SCRIPTTEXT keyword required for InlineScript event handlers`, after importing the build
where `StdFormHelp` runs the find-the-field script.

**Cause (found 2026-09-30)**: the scripts had VB comments, and a VB comment starts with an
apostrophe (`' Which component…`, `server's`). SyteLine reads `'` in an event response as a quote
(as in `FILTER(Item='P(Item)')`), so an unmatched one hides the `SCRIPTTEXT(` keyword. The
one-line `StdFormHelp` script from the first fix attempt had one too (`' Find the clicked field…`),
which is why the error stayed. None of Infor's 16 inline scripts in the Service Orders export has an
apostrophe, and neither does our working `StdObjectNewCompleted` script.

**Fix (in the XML)**: no comments in inline scripts; the build script stops with an error if one
contains `'`. The find-the-field script is also shorter (about 880 characters) and split into
`<Response>` (500 characters) and `<Response2>`, as Infor's exports store long scripts.
`StdFormHelp` step 0 is a one-line script, `ThisForm.GenerateEvent("ENF_FindHelpField")`; the
find-the-field script is the new event `ENF_FindHelpField`; step 1 opens `URL(V(EcmrsHelpUrl))`.
`tools/apply_form_changes.py`, rebuilt `exports/eCMRs_v2.XML`. Import it through **FormSync**; no
Design Mode.

**Confirm**: right-click **Item** → **Help** opens the Item page with no dialog.

**Confirmed on TRN 2026-09-30** (Enflite/eCMRs#16): the SCRIPTTEXT dialog is gone; SyteLine goes on
to open the help link (see the pop-up entry below).

**Environments**: TRN, then production with the same file. Service Orders and Incidents get the same
scripts (no apostrophes) before their first import.

## Right-click menu doesn't open (after Enflite/eCMRs#17)

**Symptom** (TRN, 2026-09-30): after importing #17, right-clicking a field shows no menu at all.

**Cause (not confirmed)**: #17 changed only the help handlers: `StdFormComponentHelp` and
`StdFormHelp` both collected their parameters into a new variable, `EcmrsHelpParms`, and raised
`ENF_FindHelpField`. Everything else was the same as #16, where the menu opened and the script ran.
`StdFormComponentHelp` is the handler tied to right-clicking a field, and it now raised another
event from inside itself.

**Fix (in the XML)**: back to #16's handlers exactly, with only `HELP_SITE` changed to the production
domain: `StdFormComponentHelp` runs the find-the-field script itself; `StdFormHelp` raises
`ENF_FindHelpField`, which runs it; step 1 of each opens `URL(V(EcmrsHelpUrl))`. Import
`exports/eCMRs_v2.XML` through **FormSync**. TRN keeps the unused `EcmrsHelpParms` variable
(FormSync keeps what the file leaves out); it does nothing. Further diagnostics go in one small
change at a time, each tested on TRN.

**Confirm**: right-click a field → the menu opens; **Help** opens the help (pop-up allowed).

## Which Help event runs, and what it knows (Infor docs, 2026-09-30)

- [`StdFormComponentHelp`](https://docs.infor.com/csi/9.01.x/en-us/csbiolh/lsm1454148059452.html): **F1**,
  **Help → Current Field**, or **What's This?** then clicking a component. Not the right-click menu.
- [`StdFormHelp`](https://docs.infor.com/csi/9.01.x/en-us/csbiolh/lsm1454148062494.html): **Help → Current
  Form**, or **What's This?** then clicking outside a component. On TRN, right-click a field → **Help**
  raised this one (`ev=form`).
- [`GetCurrentComponentName()`](https://docs.infor.com/csi/9.01.x/en-us/csbiolh/lsm1454148086019.html): the
  component that has focus, not necessarily the one right-clicked.
- [Scripts](https://docs.infor.com/csi/9.01.x/en-us/csbiolh/lsm1454148040187.html): a script reads its
  event's parameters with **`CountParameter`** and **`GetParameter`**. Our earlier scripts called
  `ParameterCount`, which isn't Infor's name, so the `Try` swallowed the error and they never saw a
  parameter.
- [Limits](https://docs.infor.com/csi/9.01.x/en-us/csbiolh/lsm1454148260301.html): inline scripts and
  response parameters are limited to 1,500 characters.

**Diagnostic (2026-09-30), `StdFormHelp` step 0 only**: reads the parameters with `CountParameter` /
`GetParameter`, asks `GetCurrentComponentName()`, and puts both in the link (`via=focus`, `focusempty`
or `nofocusapi`; `p=` the parameters, or `err`). No second event, no change to `StdFormComponentHelp`,
the grid or menus. Import only after checking that the right-click menu opens on other forms and
that **F1** in **Item** works.

## "Attempt by method ...InvokeMethod... to access method ...ScriptForm.Variables(System.String) failed"

**Symptom** (TRN, 2026-09-30, after #19): right-click a field → **Help** shows `Error during
execution of Global script class [Mongoose.GlobalScripts.EvHandler_StdFormHelp_0]` with that message.

**Cause (confirmed by the message)**: SyteLine refuses *late-bound* calls on the form, calls made
through a plain `Object` variable (`Dim f As Object = ThisForm`, then `f.Variables(...)`). #19's
`f.Variables(...)` was outside a `Try`, so it showed. The older scripts made the same kind of call
(`f.GetCurrentComponentName()`, `f.Components(p)`) inside a `Try`, so the refusal was hidden and they
always reported `via=none`: SyteLine never got to answer.

**Fix (in the XML)**: call directly, as Infor's own scripts do: `ThisForm.GetCurrentComponentName()`,
`ThisForm.Variables(...)`, and the script's own `CountParameter()` / `GetParameter(i)`. Any error text
now goes into the link as `&e=`. `StdFormHelp` step 0 only for now; the same fix applies to
`StdFormComponentHelp` and `ENF_FindHelpField` once `StdFormHelp` is confirmed.

**Confirm**: right-click **Item** → **Help** shows no error dialog; Vercel's log shows `via=`, `p=`
and `e=` for the request.

**Then (TRN, 2026-09-30, after #20)**: `Error compiling script EvHandler_StdFormHelp_0->`, with no more
detail in the dialog or the browser console. So one of the direct calls doesn't exist in SyteLine's
web scripting (`ThisForm` there is a `ScriptingDomain.ScriptForm`, not the Windows client's
`IWSForm` the help pages describe). Next import: only `ThisForm.GetCurrentComponentName()` (the
parameter calls removed). It compiles → the parameter calls were the problem; the same compile
error → `GetCurrentComponentName` is.

## "Your pop-up Blocker may be enabled" on right-click → Help

**Symptom** (TRN, 2026-09-30): right-click a field → **Help** shows **Open or Save Link**: `Your pop-up
Blocker may be enabled. To avoid this message, add this site to your exception list.` with a
**Click to open** link.

**Cause**: the help page opens in a new tab from the `URL(V(EcmrsHelpUrl))` step, after the script
step, not straight from the click, so the browser treats it as a pop-up. The form is working; this is
a browser setting, not something the XML can change.

**Fix**:
1. For now: click **Click to open** in the dialog.
2. Each user (Chrome): on the SyteLine tab, click the pop-up icon at the right end of the address
   bar → **Always allow pop-ups and redirects from …** → **Done**. Or **Settings** → **Privacy and
   security** → **Site settings** → **Pop-ups and redirects** → **Allowed to send pop-ups** → add the
   SyteLine address.
3. Everyone at once: IT allows pop-ups for the SyteLine address by browser policy (Chrome/Edge
   `PopupsAllowedForUrls`).

**Confirm**: right-click a field → **Help** opens the help page in a new tab with no dialog.

**Environments**: every browser that uses SyteLine (TRN and production are separate addresses, allow
both).

## "Dash" under the Next Assy label (shows "Next _Assy")

**Symptom** (TRN, 2026-09-29): the label left of Next Assy's description reads "Next" / "_Assy",
with "Desc:" missing.

**Cause**: the caption "Next Assy Desc:" needs three lines in its 6.5-wide, two-line-high column
(1.8), so it wraps and is cut off; the wrap shows as a dash.

**Fix**: caption only, "Assy Desc:" (fits two lines like "Vendor Name:"),
`tools/apply_form_changes.py` step 13d. Confirm: the label reads **Assy Desc:**. TRN, then production.

## General debugging order for "it's not working" reports

**Rule (team, 2026-09-30): every fix goes in the XML, never in Design Mode.** Change the build
script, rebuild `exports/eCMRs_v2.XML`, commit both, and re-import through **FormSync**. Design
Mode is only for looking (checking a property, a handler, a binding), not for changing the form.
When FormSync keeps an old setting, fix it in the file: re-import once more if only the text of a
step or property changed, or give the component or event a new name so FormSync creates it fresh
(`c_reason_code_v2`).

1. **Check our own generated files first** (`generate_form.py`'s output,
   `generate_schema_csv.py`'s `FIELDS`) before assuming it's a live
   Application-Studio-only mystery — several real bugs (the `String`
   Data Type/Property Class rejections, the stale `Read Only` flags) were
   sitting in our own generator output the whole time.
2. **Check if this exact symptom + fix is already documented here** before
   opening a fresh diagnostic. A silent form-wide lock after
   selecting/editing a field is Rule #1 above almost every time.
3. Only after both of those, treat it as a genuinely new problem and start
   isolating (does it happen on other fields too? is there truly no error
   anywhere? does a fresh re-import change anything?).
