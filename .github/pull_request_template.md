## Summary

<!-- What changes and why. One concern per PR. -->

## Type

- [ ] feat
- [ ] fix
- [ ] docs
- [ ] refactor
- [ ] test
- [ ] chore

## Risk

- Data sensitivity: <!-- none / config / accounting data -->
- Breaking change: <!-- no / yes — what breaks -->
- Blast radius: <!-- which DocTypes, reports, or companies are affected -->

## Rollback

<!-- How to undo this if it goes wrong (revert, patch, restore). -->

## Compliance

- [ ] Does NOT change a statutory output (CoA, statement layout, VAT logic), OR
- [ ] Changes a statutory output — it is effective-dated and needs accountant sign-off.

## Verification

- [ ] `bench migrate` runs clean on a dev site
- [ ] Tests pass for the changed area (cover the failure mode)
- [ ] `git status` shows only source files — no secrets or data
- [ ] Docs updated for any documented surface this changes

## Linked

<!-- Issue / ADR (docs/adr/NNNN-*.md) -->
