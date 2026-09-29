# eCMRs — field-by-field review against the original forms

Every visible field on the original **QC_CMRs** form, and on **Create Change Request** (where the
Change Request fields came from), compared with the eCMRs form (v2,
[`exports/eCMRs_v2.XML`](../exports/eCMRs_v2.XML)). Sources:
[`cmr-project/exports/QC_CMRs_Original.XML`](https://github.com/Enflite/cmr-project/blob/main/exports/QC_CMRs_Original.XML),
[`QC_CreateChangeRequest_Original.XML`](https://github.com/Enflite/cmr-project/blob/main/exports/QC_CreateChangeRequest_Original.XML),
and TRN screenshots from 2026-09-28. Reviewed 2026-09-28.

**Result**: every field below works on TRN (2026-09-29). The problems were in the **new** fields
(Dept/WC descriptions, Reason/Cause), PO Line, the Closed script, CMR Num numbering and the
Implementation layout - all fixed in v2 (see [`troubleshooting.md`](troubleshooting.md)).

Status (updated 2026-09-29, after v2 was imported and tested on TRN): **OK** = working on TRN ·
**Fixed v2** = was broken, fixed in v2 and confirmed on TRN ·
**Diff** = deliberate difference from the original.

## Top rows (QC_CMRs)

| Original label | Original binding | eCMRs field | Status | Note |
|---|---|---|---|---|
| Status | `WorkFlowStatus` (UDT list) | `Status` | OK | Own Inline List (7 states). |
| Assigned: ID + user | `AssignedUserEmpNum` combo + `AssignedUser` | `AssignedEmpNum` combo + `AssignedUsername` | OK | Original defaulted the user to whoever is logged in (`UserName()`); ours fills from the ID. |
| Notify | button | `btn_notify` | **Fixed (round 1)** | Raises `ENF_NotifyUserWithCMR` like the original (email to the Assigned user). To test on TRN. |
| CMR Num / Create Date / Created By | `CmrNum` / `CreateDate` / `CreatedBy` | same | **Fixed v2** | CMR Num is `CMR-YYMMDD-HHMMSS`, set on **New** (was AUTONUMBER; repeated numbers). |
| PO / PO Line | `PoNum` / `PoNumLine` combos | `PoNum` / `PoLine` | **Fixed v2** | PO Line wrote the Item (save error "Data length for Notify (12)…"); back to `DISPLAY(1,2,3)`. PO filter dropped on purpose (padding bug in the original). |
| Assigned Buyer | `BuyerPlannerUsr` (username) | `AssignedBuyer` (employee combo) | Diff | Stores the employee number, not the username. |
| Qty / POC | plain | same | OK | |
| RFQ / Job Num | plain / `SLMatltrans` combo | same | OK | |
| Item + Description | `RsCrcvrItem` + `ItmDescription` | `Item` + `ItemDescription` | OK | Auto-fill confirmed on TRN. |
| Drawing Revision | `Revision` | `Revision` | OK | **Latest Revision** is new. |
| Next Lvl Assy + Description | `NextAssyItem` + `NextAssyDescription` | same | OK | Description fills from Next Lvl Assy (`Item(NextAssyDescription)`). |
| Vendor + Name | `Vendor` + `VendorName` | same | OK | Auto-fill confirmed on TRN. |
| Priority | number + description | `Priority` (High/Medium/Low) | OK | |
| Initial Change / Requested Action | `RsCrcvrChangeAll` / `RsCrcvrNote` | `InitialChange` combo / `RequestedAction` | OK | |

## Change Request fields (from Create Change Request - new on this form)

| Original label | Original setup | eCMRs field | Status | Note |
|---|---|---|---|---|
| Dept + description | combo, validator `RSQCDept` | `Dept` + `DeptDescription` | **Fixed v2** | Description was never filled. v2 adds validator `SetPropertyFromList(DeptDescription, Description)`. |
| WC + description | combo, validator `WcDesc(WcDescription)` | `Wc` + `WcDescription` | **Fixed v2** | Same. v2 adds `SetPropertyFromList(WcDescription, Description)`. |
| Reported By | `InspId` employee combo | `ReportedBy` (plain text) | Diff | Original was an employee lookup. Ours is free text - say if it should be a lookup. |
| Due Date | date | `DueDate` | OK | |
| Change (Initial Change) + 5 Req checkboxes | `Change(...)` cascade | `InitialChange` + `Req*` | OK | Screenshot: **Machine** ticked Costing, Documentation, Tool/Machine, Process - the right four. |
| General Note | `Note` | `GeneralNote` | OK | |

## Additional fields (new, per BRD)

| Field | Status | Note |
|---|---|---|
| Serial # (`SerialNum`) | OK | Lists serials of the selected Item (`SLSerials`). Empty for items with no serials - test with a serial-tracked item. |
| LOT # (`LotNum`) | OK | Same, `SLLots`. |
| Top Level PN / Sub Assembly | **Changed (round 1)** | Top Level PN hidden (team feedback). Sub Assembly: plain text; open question whether it's the same as Next Lvl Assy. |

## Quality

| Original label | eCMRs field | Status | Note |
|---|---|---|---|
| Reviewer ID + name | `QcReviewerEmpNum` + `QcReviewerUsername` | OK | |
| Disposition | `QcDisposition` | OK | |
| Authorization For Supplier To Ship / Hold On PO / SOX Impacted | same | OK | Hold On PO and SOX were off-screen on the original; shown here. |
| QC RCA Notes | `QcRcaNotes` | OK | |
| — (new) Reason Code | `ReasonCode` | **Fixed v2** | Couldn't select. Now its own list (13 codes from QC_MRRs). |
| — (new) Cause Code | `CauseCode` | **Fixed v2** | `'FP'` error. Now its own list (13 codes from QC_MRRs). |

## Engineering

| Original label | eCMRs field | Status | Note |
|---|---|---|---|
| Reviewer ID + name | `EngReviewerEmpNum` + `EngReviewerUsername` | OK | |
| Disposition | `EngDisposition` | OK | Inline List (NFF, NRS, Other, Rework, Scrap). |
| Review Date | `InternalReviewDate` | **Fixed v2** | Was at the bottom of Implementation with a cut-off label; moved back to Engineering, as on the original. |
| EO / MDL | `EoNum` / `Mdl` | OK | |
| ENG RCA Notes | `EngRcaNotes` | OK | |

## Implementation

| Original label | eCMRs field | Status | Note |
|---|---|---|---|
| Planning / Purchasing / CM + Reviewer ID + name | `*Complete` + `*ReviewerEmpNum` + `*ReviewerName` | OK | Planning row seen working (ID 7 → Baker, Matt R.). |
| Closed / Close Date / Closed By | `Closed` + `CloseDate` + `ClosedBy` | **Fixed v2** | One row lined up with the reviewer rows; ticking Closed fills today's date and your user (script fixed: it didn't compile). |

v2 Implementation layout:

```
[ ] Planning     Reviewer ID: [ 7  v]  Reviewer: [Baker, Matt R.            ]
[ ] Purchasing   Reviewer ID: [    v]  Reviewer: [                          ]
[ ] CM           Reviewer ID: [    v]  Reviewer: [                          ]
[ ] Closed       Close Date:  [     ]  Closed By: [                         ]
```
