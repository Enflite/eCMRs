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

**Net result**: there is currently no reliable way to auto-populate a
companion field from a combo selection in this tenant. Fields that used to
attempt this are now either plain manual-entry fields, or (better, where
the target property is big enough) the combo binds directly to the
property that holds the value you actually want — see the `Username`
pattern below.

## Binding a combo directly to return `Username` instead of `EmpNum`

To make a combo return an employee's `Username` (a real email address in
this tenant, e.g. `gcaraway@enflite.com`) instead of their `EmpNum`,
without any auto-populate script: rebind the combo's own `DataSource` to
the `Username`-holding property, and reorder the `ComboListSource`'s
`PROPERTIES()` list so `Username` is listed **first**.

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
- `ReasonCode`/`CauseCode`: same pattern, added to the Quality section, but shipped with an
  **empty** Inline List - no real values confirmed yet (see next section for why not, and what
  the real alternative would have been).

## Reason Code / Cause Code: used our own Inline List, not SyteLine's real master tables

The signed CMR Development SOW (`Enflite - 00004 - CMR Development`) documents that SyteLine
already has real, existing Reason Codes and Cause Codes master tables, each row categorized by
a `Ref Type` (`E`=Enterprise, `J`=In Process, `O`=Customer, `P`=Supplier, `R`=Customer RMA), and
the SOW's own plan was to add a new `Ref Type` value `C` (for CMR) to those real tables, then
filter the CMR form's dropdowns to `RefType='C'`.

**That real mechanism was not used.** Per direct request, `ReasonCode`/`CauseCode` instead use
the same fixed-value-dropdown pattern as `Status`/`Priority`/`Disposition` above - Property
Class blank, Inline List set directly on the property in Application Studio - since eCMRs
already owns its own IDO/table and this avoids needing to go confirm the real Reason
Codes/Cause Codes IDO names and `RefType='C'` filter syntax live (the same kind of confirmation
`Job Number` needed twice before landing on the right answer - see `SLMatltrans`/`RefNum`
above).

**Trade-off worth knowing**: this means CMR's reason/cause codes live in their own separate list,
disconnected from whatever reason/cause codes the rest of the SyteLine system uses (RMAs, etc.)
- there's no shared vocabulary, and someone adding a code for CMR purposes here has to do it
twice if the same code should also exist in the real system-wide tables. If that turns out to
matter, switching to the real tables later is possible but requires the same live-confirmation
step described above.

The Inline List ships **empty** - no real Reason Code/Cause Code values have been provided yet.
Add them directly on the `ReasonCode`/`CauseCode` properties in Application Studio
(`ENTRIES(value1,value2,...)`, same syntax as the others) whenever the team has a real list -
tracked in `docs/deploy-checklist.md`.

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

21 of the 71 custom columns in `generate_schema_csv.py`'s `FIELDS` aren't bound to any
component on the current form - the `*_empnum` companion columns (superseded by the
Username-binding pattern above), the `*_description`/`VendorName` companion columns
(superseded when `SelectionEvent` was found dead), the 5 `*_review_complete` cascade flags (no
cascade UI was ever built), and a handful never placed on the layout at all
(`AdditionalChanges`, `GeneralNote`, `WorkflowStatus`, `GeneralCloseDate`, `GeneralClosedBy`).

These are **not removed** from the schema - the underlying SQL columns and IDO properties
already exist live from earlier imports, and dropping a live column/property is a separate,
destructive decision, not something a schema-generator refactor should do as a side effect.
Instead they're tracked explicitly in `ORPHANED_COLUMNS` (`generate_schema_csv.py`), which
prefixes each one's description with `[ORPHANED - ...]` in every export (table columns, IDO
properties, deploy checklist) so nobody mistakes "not on the form" for "not real," and so a
future contributor doesn't have to re-derive why each one is dead. If a column here gets
reused for something later, take it back out of `ORPHANED_COLUMNS`.

## General debugging order for "it's not working" reports

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
