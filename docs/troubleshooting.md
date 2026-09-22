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
  `DK00084716` (zero-padded). Deferred, not fixed — the real fixed
  length/format was never confirmed enough to build a padding rule.
- **PO Number**: `FILTER(PoNum=FP(PoNum))` (self-referencing) never
  matched anything, because real PO Numbers are zero-padded with a
  variable-length prefix (confirmed real examples: `RD00000021`,
  `INT0120033` — different prefix lengths, same total length, no single
  padding rule could reconstruct either from partial input).

**Fix used for PO Number**: drop the `FILTER()` entirely and list every
row via `STDOLE SLPoItems(...)` with no filter — same pattern already
proven working for `Item`/`Work Center`/`Dept`/`Vendor` on this form. The
`EnhancedCombo`'s own client-side type-ahead handles narrowing it down
instead of a server-side exact match.

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
need a **Property Class + Inline List configured directly on the property
in Application Studio**, manually, per property. The form's own combo
component needs no `ComboListSource`/`PropertyClassName` for these — an
empty-looking combo with none of those attributes in the form XML is
*expected*, not a bug, until the property-level setup is done.

Two separate steps are required and both have been missed before:
1. Create the Inline List (the actual value set).
2. Set that property's own `Property Class` field to point at a class
   carrying that list — a list existing on its own, unlinked, does nothing.

Confirmed real value lists:
- `Status`: CM, Complete, Data Input, Eng Review, Planning, Purchasing, QC Approval
- `Priority`: High, Medium, Low
- `InitialChange`: Documentation, Machine, Material, Other, Process, Specification, Tooling, Variance(waiver)
- `QcDisposition`: Accept, Hold, NFF, NRS, Other, Reject, Rework, Scrap
- `EngDisposition`: NFF, NRS, Other, Rework, Scrap (subset of QcDisposition — missing Accept/Hold/Reject)

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
