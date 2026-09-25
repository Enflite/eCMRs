# eCMRs — Deploy Checklist

Generated from the schema by `scripts/generate_deploy_checklist.py` - re-run it
after adding a field to either tracking dict below, don't hand-edit this file.
See `docs/troubleshooting.md` for why each category exists.

**After every item below**: editing a property in the IDO Properties grid does
not persist by itself - the IDO itself must be Check In'd (IDOs tab -> find the
IDO -> Check In) before the change takes effect, even with no source control
configured (a "Source control integration is currently disabled" popup is
harmless - click OK, the local check-in still applies). Skipping this produced a
real "Missing property data type" error on form save. See
`docs/troubleshooting.md`.

## Read Only must be manually unchecked

Form Sync re-import never touches an existing property's Read Only flag.

- [ ] `AssignedUsername` (assigned_username) - Combo binds here directly (Username-first list source) - was a read-only companion.
- [ ] `QcReviewerUsername` (qc_reviewer_username) - Combo binds here directly (Username-first list source) - was a read-only companion.
- [ ] `EngReviewerUsername` (eng_reviewer_username) - Combo binds here directly (Username-first list source) - was a read-only companion.
- [ ] `PlanningReviewerName` (planning_reviewer_name) - Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.
- [ ] `PurchasingReviewerName` (purchasing_reviewer_name) - Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.
- [ ] `CmReviewerName` (cm_reviewer_name) - Combo binds here directly (Username-first list source), holds a Username despite the property's own name - was a read-only companion.
- [ ] `DeptDescription` (dept_description) - Now a plain manually-typed field - the DefaultFrom auto-fill it was designed for is permanently abandoned (confirmed live-breaking). Was a read-only auto-populated companion.
- [ ] `WcDescription` (wc_description) - Now a plain manually-typed field - the DefaultFrom auto-fill it was designed for is permanently abandoned (confirmed live-breaking). Was a read-only auto-populated companion.
- [ ] `ItemDescription` (item_description) - DefaultFrom="Item(ItemDescription)" on Item confirmed live-working once this property's Read Only flag is cleared - locked the whole form (Rule #1B) until fixed. Was a read-only auto-populated companion.
- [ ] `VendorName` (vendor_name) - DefaultFrom="VendNum(VendorName)" added to Vendor, extending the confirmed-working Item/EmpNum pattern - needs this property's Read Only flag cleared the same way. Was designed as a read-only auto-populated companion.
- [ ] `NextAssyDescription` (next_assy_description) - DefaultFrom="Item(NextAssyDescription)" added to NextAssyItem, same pattern as VendorName above - needs this property's Read Only flag cleared. Was designed as a read-only auto-populated companion.

## Inline List must be manually configured

Cannot be pushed via CSV/Form Sync import at all - set the property's own
`*Inline List` field directly to the `ENTRIES(...)` value below. `Property
Class` stays blank - there is no separate class to create in this
environment (confirmed live on Status; see docs/troubleshooting.md).

- [ ] `Status` - Inline List: `ENTRIES(CM,Complete,Data Input,Eng Review,Planning,Purchasing,QC Approval)`
- [ ] `Priority` - Inline List: `ENTRIES(High,Medium,Low)`
- [ ] `InitialChange` - Inline List: `ENTRIES(Documentation,Machine,Material,Other,Process,Specification,Tooling,Variance(waiver))`
- [ ] `QcDisposition` - Inline List: `ENTRIES(Accept,Hold,NFF,NRS,Other,Reject,Rework,Scrap)`
- [ ] `EngDisposition` - Inline List: `ENTRIES(NFF,NRS,Other,Rework,Scrap)`

