# Archive Report: bci-cartola-variante

**Date Archived**: 2026-09-11
**Status**: COMPLETED — Merged specs and moved to archive
**Git Operations Pending**: `git rm -r openspec/changes/bci-cartola-variante/` (cleanup old location)

## Merge Summary

### Delta Specs Merged into Live Spec
**File**: `openspec/specs/pdf-ingesta/spec.md`

#### Modifications Performed

1. **PDF-02 (Structure validation requirement)** — MODIFIED
   - Added explanatory text about period-extraction punctuation tolerance (colon handling)
   - Added NEW scenarios:
     - "BCI's period anchor is extracted regardless of colon punctuation between label and date"
     - "A period-extraction failure is never silent"
   - Live spec scenarios before: 3 → After: 5

2. **PDF-03 (Normalization reference targets table)** — MODIFIED
   - Added new row for the new BCI variant:
     - Fixture: `bci — variant B (dash dates, shifted geometry)`
     - Period: synthetic, invented by the fixture generator
     - Signals: `DD-MM-YYYY` row dates; 3 pages, table header repeated per page; `SUCURSAL` column present; `cargo`/`abono` attributed correctly per PDF-11

3. **PDF-11 (BCI parses both layouts)** — ADDED
   - 4 scenarios covering: existing layout unchanged, new dash-date layout, both coexistent, correct column attribution

4. **PDF-12 (Zero-movements error)** — ADDED
   - 3 scenarios covering: zero movements returns error, genuinely empty statements rejected (accepted tradeoff), statements with movements unaffected

### Scenario Count Verification
- **Live spec before merge**: 32 scenarios (PDF-00 through PDF-10)
- **PDF-02 modification added**: 2 new scenarios (from original 3)
- **PDF-03 modification**: 0 new scenarios (reference table only)
- **PDF-11 added**: 4 new scenarios
- **PDF-12 added**: 3 new scenarios
- **Live spec after merge**: 32 + 2 + 4 + 3 = **41 scenarios**

**Proof of no dropped requirements**: All pre-existing 32 scenarios remain. Only additions and modifications to PDF-02/PDF-03 as specified in the delta.

## Archive Operations

### Folder Move
- **From**: `openspec/changes/bci-cartola-variante/`
- **To**: `openspec/changes/archive/2026-09-11-bci-cartola-variante/`
- **Status**: Files created in archive location

### Files in Archive
- [x] `proposal.md` — with Closure Note prepended
- [x] `design.md` — complete design document (70+ pages, includes AMENDMENT A-01)
- [x] `tasks.md` — complete tasks breakdown (50+ pages, includes Phases 39-46 for amendment)
- [x] `specs/pdf-ingesta/spec.md` — delta spec
- [x] `audit-issues-draft.md` — drafted GitHub issues (BancoEstado, Banco de Chile, Santander)
- [x] `archive-report.md` — this file

## Change Summary

**bci-cartola-variante**: Parse the second BCI statement layout (dash-date variant-B) and stop reporting zero movements as success

- **5-slice feature-branch-chain**: Slices 1-3 focus on BCI geometry and dating; Slice 4 adds zero-movements error; Slice 5 audits the three sibling banks
- **Delivered**: 2026-09-09/2026-09-10 (pre-merge archive)
- **Verify result**: PASS WITH WARNINGS — both warnings closed, gate 45 (real-statement reconciliation) PASS
- **Final test count**: 275 files / 2673 tests green; `tsc --noEmit` clean
- **Amendment A-01** (right-edge rescue for `cargo` column): Delivered 2026-09-10 after Slices 1-3 revealed fixture gap. Phases 39-46 ship in Slices 3a/3b.

## Observation IDs (for Engram Traceability)

When this change was previously saved to Engram during proposal/spec/design/tasks/verify phases, it used:

- `sdd/bci-cartola-variante/proposal` — topic_key for proposal phase
- `sdd/bci-cartola-variante/spec` — topic_key for spec phase
- `sdd/bci-cartola-variante/design` — topic_key for design phase (includes AMENDMENT A-01)
- `sdd/bci-cartola-variante/tasks` — topic_key for tasks phase (includes Phases 39-46)
- `sdd/bci-cartola-variante/verify-report` — topic_key for verify phase

This archive report is saved as:
- `sdd/bci-cartola-variante/archive-report` — topic_key for archive phase

## Open Items Carried Forward

1. **Three GitHub issues drafted** (not filed): `audit-issues-draft.md` contains issue bodies for BancoEstado, Banco de Chile, and Santander auditing findings. Human decision required before filing to the live public repo. Trigger: real statement measurement for each bank.

2. **BancoEstado latent risk (headline finding)**: `abono`/`cargo` bands are contiguous (zero dead zone) and reversed relative to BCI. Unconfirmed as an active bug but flagged as highest-risk finding. Trigger: real BancoEstado PDF statement measurement.

## Cleanup Note

**Files in original location NOT yet removed**:
- `openspec/changes/bci-cartola-variante/` — old folder still exists
- To complete the archive, run: `git rm -r openspec/changes/bci-cartola-variante/`
- This will be done by the human who commits the archive changes

## Verification Checklist

- [x] Delta specs merged into live spec (PDF-02 modified, PDF-03 modified, PDF-11 added, PDF-12 added)
- [x] No pre-existing scenarios dropped (scenario count: 32 → 41, all additions accounted for)
- [x] All artifacts copied to archive folder with 2026-09-11 date prefix
- [x] Closure note added to archived proposal.md
- [x] Archive report created documenting the merge and move
- [x] Old change folder ready for cleanup (git rm pending)
