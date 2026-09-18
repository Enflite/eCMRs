# eCMRs — Field Mapping

The full field list for the new standalone table, carried forward from everything confirmed in `cmr-project`'s `docs/field-mapping.md` — but every field here is its **own original column** on the new table. No `RsCrcvr*` names, no `rs_cmrUf_*` names, no joins, no reference back to `rs_cmr`/`rs_crcvr`/any other table. This is a full migration of the CMR concept onto independent storage, not a rebind of existing columns.

Status vocabulary: **Planned** (in this list, not yet built), **Built**, **Tested**.

| Field | New column (proposed) | Type | List Source (system lookup, not a join) | Notes | Status |
|---|---|---|---|---|---|
| CMR Num | `cmr_num` | Autonumber / Integer (key) | — | See `task-list.md` Phase A — numbering mechanism still to be decided (`Autonumber` property type, preferred now that there's no composite-key constraint). | Planned |
| Priority | `priority` | String (`High`/`Medium`/`Low`) or a small lookup list | Could reuse `RS_QCPriority`'s values as a static/inline list, or define eCMRs' own — decide during build. | Real property class + `EnhancedCombo`, `Required`. | Planned |
| Item | `item` | String | `STDOLE SLItems( PROPERTIES(Item, Description) )` | Standard system lookup — fine per the "no dependencies" rule (read-only picker, not a join). | Planned |
| Initial Change | `initial_change` | String (fixed 8-value list: Documentation/Machine/Material/Other/Process/Specification/Tooling/Variance(waiver)) | Inline list, not a query — matches the real `Change` property class's own behavior. | Drives the Requirements checkbox cascade — see below. | Planned |
| Requested Action | `requested_action` | Multiline text | — | | Planned |
| Dept | `dept` | String | `STDOLE SLDepts( PROPERTIES(Dept, Description) )` | | Planned |
| Work Center | `wc` | String | `STDOLE SLWcs( PROPERTIES(Wc, Description) )` | | Planned |
| Reported By | `reported_by` | String (EmpNum) | `STDOLE SLEmployees( PROPERTIES(EmpNum, Name) )` | | Planned |
| Due Date | `due_date` | Date | — | | Planned |
| Serial Number | `serial_number` | String | — | Free-text for now, same as `cmr-project`'s decision — a real `SL.SLSerials`-backed validated version is a possible later upgrade, not required for this migration. | Planned |
| Lot Number | `lot_number` | String | — | Same as Serial Number. | Planned |
| Assigned | `assigned_empnum` / `assigned_username` | String / String | `STDOLE SLEmployees( PROPERTIES(EmpNum,Name,Username) )` | Two columns, same proven pattern as `cmr-project`'s Assigned field: a `SelectionEvent` on the EmpNum combo writes the matching `Username` into the companion column. | Planned |
| Status | `status` | String | Small fixed/inline list (Open/Closed/etc. — confirm real values wanted) | | Planned |
| Created By | `created_by` | String (EmpNum or Username) | `STDOLE SLEmployees( PROPERTIES(EmpNum, Name) )` | | Planned |
| Create Date | `create_date` | DateTime | — | Default to now on creation. | Planned |
| Closed By | `closed_by` | String | `STDOLE SLEmployees( PROPERTIES(EmpNum, Name) )` | | Planned |
| Close Date | `close_date` | Date | — | | Planned |
| Closed (flag) | `closed` | Boolean | — | | Planned |
| Requirement: Costing | `req_costing` | Boolean | — | Cascades off `initial_change` — see below. | Planned |
| Requirement: Documentation | `req_documentation` | Boolean | — | Cascades off `initial_change`. | Planned |
| Requirement: Material | `req_material` | Boolean | — | Cascades off `initial_change`. | Planned |
| Requirement: Process | `req_process` | Boolean | — | Cascades off `initial_change`. | Planned |
| Requirement: Tool/Machine | `req_tool_machine` | Boolean | — | Cascades off `initial_change`. | Planned |

## Requirements checkbox cascade (carried forward from `cmr-project`)

Same business rule, same mapping table — confirmed real, not inferred:

| Initial Change | Costing | Documentation | Material | Process | Tool/Machine |
|---|:---:|:---:|:---:|:---:|:---:|
| Documentation | | ✓ | | | |
| Machine | ✓ | ✓ | | ✓ | ✓ |
| Material | ✓ | ✓ | | | |
| Other | | | | | |
| Process | ✓ | ✓ | | ✓ | ✓ |
| Specification | ✓ | ✓ | | ✓ | ✓ |
| Tooling | | | | | ✓ |
| Variance(waiver) | ✓ | ✓ | | ✓ | ✓ |

On the legacy tables, this is enforced by a native `DefaultFrom: Change(RsChangeCosting, RsChangeProcess, RsChangeDocumentation, RsChangeToolmachine, RsChangeMaterial)` function tied to the real `Change` property class. **Unverified whether this same built-in function works against entirely new property names on a brand-new IDO** (see `task-list.md` Phase A) — if it doesn't, build a scripted equivalent (an event fired on `initial_change` changing, setting the 5 `req_*` properties directly) — still fully self-contained, no dependency on any other table either way.

## Explicitly not carried over (out of scope for this standalone build)

- **Job Number** (`rs_cmrUf_ENF_CMR_JobNum`) — tied to `SLMatltrans`/receiving data; not part of this migration unless specifically requested.
- **CAR cross-referencing** — a dependency on `RS_QCMrrs`, a different table entirely. Out of scope per the "no dependencies" rule.
- **Any receiver reference (`RcvrNum`)** — no column for this at all. eCMRs does not link back to `RS_QCCRcvrs`/`rs_crcvr` in any way.
