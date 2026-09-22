# eCMRs — Deploy Checklist

Generated from the schema by `scripts/generate_deploy_checklist.py` - re-run it
after adding a field to either tracking dict below, don't hand-edit this file.
See `docs/troubleshooting.md` for why each category exists.

## Read Only must be manually unchecked

Form Sync re-import never touches an existing property's Read Only flag.

- [ ] `AssignedUsername` (assigned_username) - Combo binds here directly (Username-first list source) - was a read-only companion.
- [ ] `QcReviewerUsername` (qc_reviewer_username) - Combo binds here directly (Username-first list source) - was a read-only companion.
- [ ] `EngReviewerUsername` (eng_reviewer_username) - Combo binds here directly (Username-first list source) - was a read-only companion.
- [ ] `PlanningReviewerName` (planning_reviewer_name) - Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.
- [ ] `PurchasingReviewerName` (purchasing_reviewer_name) - Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.
- [ ] `CmReviewerName` (cm_reviewer_name) - Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.

## Property Class + Inline List must be manually configured

Cannot be pushed via CSV/Form Sync import at all - two steps each: create
the Inline List, then set the property's own Property Class to point at it.

- [ ] `Status` - Property Class `ue_CmrStatusType`, values: CM,Complete,Data Input,Eng Review,Planning,Purchasing,QC Approval
- [ ] `Priority` - Property Class `ue_CmrPriorityType`, values: High,Medium,Low
- [ ] `InitialChange` - Property Class `ue_CmrInitialChangeType`, values: Documentation,Machine,Material,Other,Process,Specification,Tooling,Variance(waiver)
- [ ] `QcDisposition` - Property Class `ue_CmrQcDispositionType`, values: Accept,Hold,NFF,NRS,Other,Reject,Rework,Scrap
- [ ] `EngDisposition` - Property Class `ue_CmrEngDispositionType`, values: NFF,NRS,Other,Rework,Scrap

