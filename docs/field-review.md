# eCMRs — field-by-field review against the original forms

Every visible field on the original **QC_CMRs** form, and on **Create Change Request** (where the
Change Request fields came from), compared with the eCMRs form (v2,
[`exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML)). Sources:
[`cmr-project/exports/QC_CMRs_Original.XML`](https://github.com/Enflite/cmr-project/blob/main/exports/QC_CMRs_Original.XML),
[`QC_CreateChangeRequest_Original.XML`](https://github.com/Enflite/cmr-project/blob/main/exports/QC_CreateChangeRequest_Original.XML),
and TRN screenshots from 2026-09-28. Reviewed 2026-09-28.

**Result**: the fields carried over from QC_CMRs match the original and work. The problems were
in the **new** fields (Dept/WC descriptions, Reason/Cause, Serial/Lot) and in the Implementation
layout. All of them are addressed in v2, except Serial/Lot, which needs a check with a
serial/lot-tracked item (see below).

Status: **OK** = matches and seen working on TRN · **Fixed v2** = changed in v2, check on TRN ·
**Check** = needs a TRN test · **Diff** = deliberate difference from the original.

## Top rows (QC_CMRs)

| Original label | Original binding | eCMRs field | Status | Note |
|---|---|---|---|---|
| Status | `WorkFlowStatus` (UDT list) | `Status` | OK | Own Inline List (7 states). |
| Assigned: ID + user | `AssignedUserEmpNum` combo + `AssignedUser` | `AssignedEmpNum` combo + `AssignedUsername` | Check | Original defaulted the user to whoever is logged in (`UserName()`); ours fills from the ID. |
| Notify | button | `btn_notify` | Diff | Placeholder message only - no notification sent yet. |
| CMR Num / Create Date / Created By | `CmrNum` / `CreateDate` / `CreatedBy` | same | OK | |
| PO / PO Line | `PoNum` / `PoNumLine` combos | `PoNum` / `PoLine` | OK | PO filter dropped on purpose (padding bug in the original). |
| Assigned Buyer | `BuyerPlannerUsr` (username) | `AssignedBuyer` (employee combo) | Diff | Stores the employee number, not the username. |
| Qty / POC | plain | same | OK | |
| RFQ / Job Num | plain / `SLMatltrans` combo | same | OK | |
| Item + Description | `RsCrcvrItem` + `ItmDescription` | `Item` + `ItemDescription` | OK | Auto-fill confirmed on TRN. |
| Drawing Revision | `Revision` | `Revision` | OK | **Latest Revision** is new. |
| Next Lvl Assy + Description | `NextAssyItem` + `NextAssyDescription` | same | Check | Description fill (`Item(NextAssyDescription)`) not yet seen on TRN. |
| Vendor + Name | `Vendor` + `VendorName` | same | OK | Auto-fill confirmed on TRN. |
| Priority | number + description | `Priority` (High/Medium/Low) | OK | |
| Initial Change / Requested Action | `RsCrcvrChangeAll` / `RsCrcvrNote` | `InitialChange` combo / `RequestedAction` | OK | |

## Change Request fields (from Create Change Request - new on this form)

| Original label | Original setup | eCMRs field | Status | Note |
|---|---|---|---|---|
| Dept + description | combo, validator `RSQCDept` | `Dept` + `DeptDescription` | **Fixed v2** | Description was never filled. v2 adds validator `Dept(DeptDescription,)`. |
| WC + description | combo, validator `WcDesc(WcDescription)` | `Wc` + `WcDescription` | **Fixed v2** | Same. v2 adds `WcDesc(WcDescription)`. |
| Reported By | `InspId` employee combo | `ReportedBy` (plain text) | Diff | Original was an employee lookup. Ours is free text - say if it should be a lookup. |
| Due Date | date | `DueDate` | OK | |
| Change (Initial Change) + 5 Req checkboxes | `Change(...)` cascade | `InitialChange` + `Req*` | OK | Screenshot: **Machine** ticked Costing, Documentation, Tool/Machine, Process - the right four. |
| General Note | `Note` | `GeneralNote` | OK | |

## Additional fields (new, per BRD)

| Field | Status | Note |
|---|---|---|
| Serial # (`SerialNum`) | Check | Lists serials of the selected Item (`SLSerials`). Empty for items with no serials - test with a serial-tracked item. |
| LOT # (`LotNum`) | Check | Same, `SLLots`. |
| Top Level PN / Sub Assembly | OK | Plain text. Open question: is Sub Assembly the same as Next Lvl Assy? |

## Quality

| Original label | eCMRs field | Status | Note |
|---|---|---|---|
| Reviewer ID + name | `QcReviewerEmpNum` + `QcReviewerUsername` | Check | Same pattern as the Implementation rows, which work on TRN. |
| Disposition | `QcDisposition` | OK | |
| Authorization For Supplier To Ship / Hold On PO / SOX Impacted | same | OK | Hold On PO and SOX were off-screen on the original; shown here. |
| QC RCA Notes | `QcRcaNotes` | OK | |
| — (new) Reason Code | `ReasonCode` | **Fixed v2** | Couldn't select. Now its own list (13 codes from QC_MRRs). |
| — (new) Cause Code | `CauseCode` | **Fixed v2** | `'FP'` error. Now its own list (13 codes from QC_MRRs). |

## Engineering

| Original label | eCMRs field | Status | Note |
|---|---|---|---|
| Reviewer ID + name | `EngReviewerEmpNum` + `EngReviewerUsername` | Check | |
| Disposition | `EngDisposition` | Check | Inline List still to set (deploy checklist). |
| Review Date | `InternalReviewDate` | **Fixed v2** | Was at the bottom of Implementation with a cut-off label; moved back to Engineering, as on the original. |
| EO / MDL | `EoNum` / `Mdl` | OK | |
| ENG RCA Notes | `EngRcaNotes` | OK | |

## Implementation

| Original label | eCMRs field | Status | Note |
|---|---|---|---|
| Planning / Purchasing / CM + Reviewer ID + name | `*Complete` + `*ReviewerEmpNum` + `*ReviewerName` | OK | Planning row seen working (ID 7 → Baker, Matt R.). |
| Closed / Close Date / Closed By | `Closed` + `CloseDate` + `ClosedBy` | **Fixed v2** (layout) | Now one row lined up with the reviewer rows. Check that ticking **Closed** fills date and name. |

v2 Implementation layout:

```
[ ] Planning     Reviewer ID: [ 7  v]  Reviewer: [Baker, Matt R.            ]
[ ] Purchasing   Reviewer ID: [    v]  Reviewer: [                          ]
[ ] CM           Reviewer ID: [    v]  Reviewer: [                          ]
[ ] Closed       Close Date:  [     ]  Closed By: [                         ]
```
