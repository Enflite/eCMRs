# eCMRs — Task List

A from-scratch build: new table, new IDO, new form. Nothing here extends or joins `RS_QCCmrs`/`RS_QCCRcvrs` — see the README for why.

## Phase 0 — Carry over confirmed requirements from `cmr-project`

Not re-investigating what's already confirmed there. Pulling forward as fixed requirements, not open questions:

- [ ] **Full field list, all of it — not just the editable subset.** Stakeholder direction: eCMRs is a standalone migration, meaning every field the consolidated CMR concept needs (per `cmr-project`'s `docs/field-mapping.md`) gets carried over, but each one becomes its own real, original column on this one standalone table — never a join or reference back to `rs_cmr`/`rs_crcvr`. See `docs/field-mapping.md` for the full list.
- [ ] The Requirements checkbox cascade rule (Costing/Documentation/Material/Process/Tool-Machine, keyed off Initial Change) — the business mapping table in `cmr-project`'s `field-mapping.md` is the source of truth. The *mechanism* (`DefaultFrom: Change(RsChangeCosting, ...)`, a native Mongoose function keyed to those exact property names) is tied to the real `Change` property class on the legacy tables — **not yet confirmed whether it's available on entirely new property names on a brand-new IDO.** Treat this as unverified until tested (see Phase A).
- [ ] The Assigned/employee-lookup mechanism (`SLEmployees` list source + a `SelectionEvent` that writes a companion username field) — proven pattern, portable regardless of table.
- [ ] Job Number's real bug (leading-zero filter mismatch) — not applicable here unless eCMRs also surfaces Job Number; if it does, fix the filter clause correctly from day one instead of inheriting the bug.

## Phase A — Data model (one standalone table + IDO, zero dependencies)

**Standing rule for this whole project, per explicit stakeholder direction: no joins, no foreign keys, no dependency on any other table or IDO — including `RS_QCCRcvrs`/`rs_crcvr`.** Not even a plain `RcvrNum` reference column tying back to the receiving transaction. This is a genuinely standalone form: one table, one IDO, self-contained. If a future need for cross-referencing (CAR, receiver traceability, reporting) comes up, that's a deliberate later decision to revisit — not something to build in by default now.

- [ ] **Design the new table's schema** — see `docs/field-mapping.md`. Every column gets a real, purpose-built name (no `RsCrcvr*`/`rs_cmrUf_*` legacy naming), real data types, real lengths — not reused generic `Charfld`/`Decifld` columns, and not a join to anything.
- [ ] **Decide the primary key / numbering scheme.** Since this table has no composite key forced on it by a legacy join (unlike `RS_QCCmrs`'s `CmrNum`+`RsCrcvrRcvrNum`+`RsPriorityPriority`), this is a real chance to keep it simple — a single auto-numbering key column. Options to evaluate:
  - IDO Studio's built-in `Autonumber` property type on a single identity/sequence column — likely sufficient now that there's no composite key requirement, and would let native "New" work directly with no custom Method/stored-procedure workaround at all.
  - A new stored procedure only if `Autonumber` turns out insufficient (same atomic server-side generation pattern as `RSQC_CreateCmrSp` — **never** compute `MAX+1` client-side, same standing rule as `cmr-project`).
  - Decide before building the form — this determines whether "New" works natively or needs an event-chain workaround.
- [ ] Create the new table in Application Studio, under project `ue_ENF` (or a new dedicated project — decide naming convention for this repo).
- [ ] Create the new IDO on top of it, with the new table as its **only** base table — no secondary collections, no subcollections, no joined properties. Add a `Property` per column, set the real key.
- [ ] Test the `DefaultFrom: Change(...)` cascade function on the new IDO's own property names — confirm whether it's a generic Mongoose function available to any IDO, or specifically tied to the legacy `Change` property class. If it doesn't work, plan a scripted equivalent instead (a `StdObjectSelectCurrentCompleted`/change-event script setting the 5 checkbox properties directly) — still fully self-contained, no dependency on another table either way.
- [ ] Check In.

## Phase B — Form

- [ ] Build the `eCMRs` form from scratch — not copied from `QC_CMRs` this time, since there's no legacy layout constraint to inherit. Use `cmr-project`'s hard-won layout lessons (group Initial Change with its Requirement checkboxes, group Item/Reported By/the Create button together, keep the 5 Launch buttons/QC-review actions visually separate from the create flow) as the starting design, not a legacy shape to preserve.
- [ ] Wire New/Create using whatever Phase A's numbering decision requires.
- [ ] Wire Save/Update — should be plain native CRUD if Phase A's key design avoids `RS_QCCmrs`'s composite-key trap; confirm directly rather than assuming.
- [ ] Requirements checkboxes — build per Phase A's cascade-mechanism finding (native `DefaultFrom` if it works, scripted otherwise).
- [ ] Real `List Source`s for every combo (Item, Dept, WC, Assigned, Employee) — same real system lookups already confirmed in `cmr-project` (`SLItems`, `SLDepts`, `SLWcs`, `SLEmployees`). **Not a violation of the "no dependencies" rule**: these are read-only, standard SyteLine reference/picker lookups (the same lists any field on any form draws from), not a join or foreign key into another business table. The rule is about not structurally tying this table to `rs_cmr`/`rs_crcvr`/`RS_QCMrrs` — picking a value from a system list is fine.
- [ ] **CAR cross-referencing (`LaunchCAR`/`RS_QCMrrs.RSQC_CreateCarSp`) is explicitly out of scope for this standalone build** — it's a dependency on a different table entirely. If CAR integration is ever wanted for eCMRs, that's a deliberate future decision, not part of this migration.

## Phase C — Testing

- [ ] Create a new CMR end-to-end
- [ ] Save and reopen
- [ ] Confirm numbering has no race condition (Phase A's chosen mechanism)
- [ ] Confirm the Requirements checkbox cascade actually fires
- [ ] Confirm Assigned's employee lookup + companion username field work unchanged

## Phase D — Rollout

- [ ] Decide: does eCMRs replace `cmr-project`'s consolidated form entirely, run alongside it, or is `cmr-project` retired once eCMRs is proven? Not decided yet.
- [ ] Decide: migrate historical CMR data from `rs_cmr`/`rs_crcvr` into the new table, or start eCMRs fresh going forward with legacy history staying queryable only through the old screens/tables?
- [ ] Retire or hide `Create Change Request`/`Change Request Management`/`QC_CMRs` once eCMRs is live, per whatever Phase D above decides.
