---
title: Evidence Standard
kind: policy
status: maintained
evidence_grade: structural
scope: Entire knowledge base
last_verified: 2026-07-21
---

# Evidence Standard

## Purpose

The KB must help an agent implement correctly without pretending to replace upstream documentation. A useful note gives a direct answer, an exact path through official material, pinned source behavior, relevant tests, and explicit uncertainty.

## Evidence grades

| Grade | Meaning | Allowed use |
|---|---|---|
| `structural` | Navigation, templates, or policy only | Organizing research |
| `documented` | Supported by current official documentation | General guidance; exact behavior still needs source verification when version-sensitive |
| `source-verified` | Checked against an exact tagged source commit | Implementation planning for that exact source revision |
| `test-verified` | Reproduced against the pinned running stack with recorded commands and results | Operational guidance for the tested deployment |
| `primary-law` | Checked against dated official statute, regulation, or administrative guidance | Legal requirements inventory, never a legal or compliance opinion |
| `project-decision` | A deliberate local choice, not an upstream fact | Project implementation only |
| `researching` | Incomplete or conflicting evidence | Navigation only; do not implement from it |

The word `verified` alone is prohibited because it hides what kind of evidence was checked.

## Claim rule

Each important claim must be visibly one of:

- **Official documentation:** linked to the exact official page and heading.
- **Pinned source:** linked to an immutable GitHub permalink containing the full commit SHA and useful line range.
- **Pinned test:** linked to an immutable official test file or test case.
- **Project decision:** linked to a decision note or stated explicitly as local policy.
- **Primary law:** linked to an official dated legal text or official administrative guidance, with applicability limits.
- **Open verification:** recorded as unresolved, with the evidence needed to resolve it.

An upstream branch URL such as `/blob/version-16/` is a discovery link, not immutable evidence. Accepted notes use `/blob/<40-character-commit>/` permalinks.

## Source precedence

1. Running pinned system, when the test and result are recorded.
2. Pinned official source and tests.
3. Current official documentation.
4. Official issue or pull-request discussion for unresolved behavior.
5. Community material only as a lead, never as final authority.

When documentation conflicts with pinned source, record the conflict. Do not silently choose the more convenient statement.

## Required structure for a reference note

1. `Direct answer`: concise explanation for the agent's immediate question.
2. `Use this when`: task boundaries.
3. `Official model`: documentation-backed concepts.
4. `Pinned implementation`: exact source behavior and symbols.
5. `Implementation runbook`: reproducible project steps.
6. `Files and commands`: concrete paths and commands.
7. `Failure modes`: observed or source-supported pitfalls.
8. `Verification`: what was checked and what remains open.
9. `Source map`: official docs, source, and tests grouped separately.

## Acceptance gate

A module is accepted only when:

- All internal links resolve.
- Every source-backed technical note has an immutable source permalink.
- Current docs and pinned source have both been checked.
- Relevant upstream tests are identified.
- Project decisions are separated from upstream behavior.
- Legal claims identify jurisdiction, effective date, official authority, and applicability boundary.
- Conflicts and missing runtime tests are explicit.
- A second agent can follow the note to the exact implementation without searching from scratch.

## Anti-copy rule

Do not reproduce documentation pages or large code blocks. Explain why a source matters, cite the exact place, and keep the official source as the detail authority.
