# Closure Note — bci-cartola-variante

**Status**: ARCHIVED (pre-merge) — implemented 2026-09-09..2026-09-11 as a 5-slice Feature Branch Chain, verified and archived on `chore/bci-variante-archive`. NOT yet merged to `main` and NOT in production at archive time; the chain's PRs are the remaining step.

**Verify Result**: PASS WITH WARNINGS
- Implemented as a 5-slice feature-branch-chain (slices archived pre-merge; the chain was not yet merged at archive time per the launch brief).
- `sdd-verify` returned PASS WITH WARNINGS (two non-blocking warnings, both closed during apply/verify iteration).
- Gate 45 (real-statement reconciliation): PASS — 0→104 movements extracted from the real BCI variant-B statement, zero sign inversions detected, balance-identity reconciliation confirmed exact.
- Final state: `pnpm api test` → 275 files / 2673 tests, all green; `tsc --noEmit` clean.

**Open Gaps Carried Forward** (not blocking, documented for future work):
- **Audit follow-up items**: Three GitHub issues drafted in `audit-issues-draft.md` (BancoEstado headline latent defect, Banco de Chile 5pt margin, Santander unconfirmed). **Not filed** during apply — human decision required before filing to live public repo. Issues are documented and ready to file.
- **BancoEstado latent risk (headline finding)**: The audit discovered BancoEstado's `abono`/`cargo` bands are **contiguous (zero dead zone)** and **order-reversed** relative to BCI/Banco de Chile. This is unconfirmed as an active bug (no real BancoEstado PDF available) but is the highest-risk finding. Trigger: a real BancoEstado statement measurement.

---

# Proposal: bci-cartola-variante — parse the second BCI statement layout, and stop reporting zero movements as success

> SDD propose artifact. Hybrid store — mirror of Engram topic `sdd/bci-cartola-variante/proposal`.
> No `explore.md` preceded this change; the diagnosis came from an empirical stage-by-stage run of the
> project's own services against a real user statement, and every code claim below was re-verified against
> the sources cited. This is a PROPOSAL: intent, scope, approach, risk, rollback, slicing — not the spec,
> not the design, not code.
>
> **PII boundary (binding for every later phase).** The real statement that produced this diagnosis carries
> the user's name, email and account number. It MUST NOT be committed, attached, quoted, paraphrased or
> reproduced in any artifact, test, fixture, log or commit message. The only thing carried forward from it
> is non-identifying page geometry — X coordinates, token counts, date separators, header labels. Every
> fixture built here is 100 % invented data on that measured geometry (ADR-013 posture, same rule the
> existing `-test` fixtures already follow).

## Intent

**Problem.** A real BCI `CARTOLA DE CUENTA CORRIENTE` runs the entire ingestion pipeline **green** and yields
**zero transactions**. Measured stage by stage with the project's own services:

| Stage | Outcome |
|---|---|
| `PdfTextExtractor.extract` | OK — 1193 tokens, text fully legible |
| `PdfjsBankDetectorService.detect` | OK — `{banco: 'BCI', tipoCuenta: 'Cuenta Corriente'}` |
| `PdfjsStructureValidatorService.validate` | OK |
| `PdfjsTransactionNormalizerService.normalize` | **`Result.ok([])`** — zero rows |

The user sees an empty preview and no explanation. Nothing is broken loudly; everything is broken quietly.

**Three root causes, two of them BCI-specific and one structural.**

1. **Date separator.** The real statement writes row dates as `DD-MM-YYYY` (`22-07-2026`). `BciPdfStrategy`
   declares `formatoFecha: 'DD/MM/YYYY'` (`bci.strategy.ts:136`), and `parsearFechaFila`'s `'DD/MM/YYYY'`
   branch matches `/(\d{2})\/(\d{2})\/(\d{4})/` — a hard-coded slash (`pdf-normalization.ts:80-88`). It
   returns `null`, the row is dropped as "no interpretable date". Measured on the real file: **106 dates with
   `-`, 0 with `/`**. Both committed BCI fixtures and the generator
   `test/fixtures/pdf/generar-bci-cartola-montos-grandes-test.ts` use `/`, so nothing ever caught it. The
   strategy's own docblock already records that BCI uses `-` for the **period** anchor
   (`bci.strategy.ts:23-24`, `anclasPeriodo` at `:120-123`); the row dates were assumed to differ. They do
   not, in this variant.

2. **Column X bands are shifted ~25 pt right.** Measured over all 106 movement rows:

   | Column | real x (min / p50 / max) | strategy band (`bci.strategy.ts:125-133`) | verdict |
   |---|---|---|---|
   | fecha | 33.6 / 33.6 / 44.5 | `fecha` 35–85 | OK — but see the SUCURSAL hazard below |
   | sucursal | 75.7 / 75.8 / 83.4 | not modelled — **falls inside the `fecha` band** | hazard |
   | descripcion | 134.8 / 135.6 / 220.7 | `descripcion` 145–320 | starts ~10 pt below the floor |
   | amount | 420.9 / 430.7 / 486.6 | `cargo` 360–430, `abono` 435–500 | straddles both, plus the 430–435 dead zone |
   | saldo | 555.9 / 558.9 / 570.6 | outside every band | correct — deliberately ignored |

   Real table headers: `FECHA` x=38.2, `SUCURSAL` x=81.1, `DESCRIPCION` x=195.9, `CHEQUES` x=392.1,
   `DEPOSITOS` x=459.9, `SALDO DIARIO` x=521.2. The bands in the code were calibrated on 2026-08-30 against
   15 real statements that were all the **other** variant (`bci.strategy.ts:37-41`: cargos x=[381.1, 409.7],
   abonos x=[455.3, 476.6], fechas x=[42.9, 44.1], SUCURSAL x≈99). Two BCI layouts exist in the wild and the
   code models one.

3. **A statement that yields zero rows is reported as success.** This is not a BCI bug — it is a design gap
   in the pipeline. `normalizarTransaccionesPdf` returns `Result.ok([])`, `EjecutarPipelineIngestaUseCase`
   logs `totalFilas: 0` (`ejecutar-pipeline-ingesta.use-case.ts:187-190`) and returns `Result.ok`. A
   detected, structurally-valid bank statement that produced no movements is the pipeline's own strongest
   signal that its geometry model no longer matches reality — and today it is discarded. That is what turned
   a parsing bug into an unexplained empty screen, and it is what would hide the **next** layout drift in any
   of the four banks.

**Why now.** The variant is not exotic — it is what the user's own bank emitted this month, through the
preview → commit flow that is the primary ingestion path. The `ingesta-pdf-password` change that shipped the
day before is provably **not** at fault: extraction returns 1193 legible tokens, and every stage downstream
of extraction is token-only logic that cannot tell an encrypted source from a plain one.

**Success looks like.** Both BCI layouts parse. The user uploads either one and sees their movements, with
`cargo`/`abono` on the correct side. A statement that genuinely produces zero rows stops being silent: the
user gets a specific, actionable error instead of an empty screen. The three other banks are known — in
writing — to be calibrated against a single layout each, so the next drift is diagnosed in minutes instead of
an afternoon.

## Scope

### In scope

- **A calibrated synthetic fixture for the new BCI variant**, built by a committed generator following the
  existing pattern (`generar-bci-cartola-montos-grandes-test.ts`, 285 lines, raw uncompressed content
  streams so each token's x/y is pinned to the point). It MUST reproduce the measured layout: `DD-MM-YYYY`
  row dates, the X positions in the table above, the split `PERIODO` | `:` | `DD-MM-YYYY al DD-MM-YYYY`
  anchor, the `SUCURSAL` column, and **3 pages** with the table header repeated per page. Entirely invented
  people, accounts, merchants and amounts.
- **`DD-MM-YYYY` row dates.** `FormatoFechaPdf` is a closed union of three (`estructura-pdf-banco.ts:22`)
  and `parsearFechaFila`'s `switch` has **no `default`** (`pdf-normalization.ts:71-98`) — extending the union
  breaks compilation until the case is handled. That is the safety net, not an obstacle.
- **BCI column geometry that covers both layouts** without letting either variant's amounts land in the
  other's column. The mechanism is a design decision (see Open design questions); the **constraint** is not:
  a `cargo` must never be read as an `abono`.
- **The `SUCURSAL` hazard.** In the new variant, SUCURSAL tokens (75.7–83.4) sit **inside** the current
  `fecha` band (35–85). Today `parsearFechaFila` regex-matches anywhere in the joined column text, so it is
  survivable — but it is an unmodelled token in a money-bearing row grouping, and the change must make an
  explicit, tested decision about it rather than inherit it by accident.
- **The `PERIODO` anchor for this variant.** `extraerPeriodo` runs the regexes against all tokens joined with
  spaces (`pdf-structure-extraction.ts:33-55`), so the real file reads `PERIODO : DD-MM-YYYY al DD-MM-YYYY`
  and `/PERIODO\s+(\d{2}-\d{2}-\d{4})/` does **not** match. It is harmless today only because BCI is
  `fuenteAnio: {kind: 'explicito'}` and therefore exempt from `RangoFechasInvalidoError`
  (`pdf-structure-extraction.ts:96-99`) — so the validated structure silently carries `periodo: undefined`.
  In scope: decide and test it, rather than leave a second silent hole next to the one we are closing.
- **Zero normalized rows becomes an explicit error.** A new domain error in `domain/errors/`, shaped like
  its neighbours (`Result<T,E>`, never throw — ADR-005/ADR-015), joining `EjecutarPipelineIngestaError`
  (`ejecutar-pipeline-ingesta.use-case.ts:57-67`). Both HTTP mappers end in `const _exhaustive: never`
  (`ingesta.routes.ts`), so the new member breaks compilation in both until mapped — same safety net the
  previous change relied on. The message must be actionable and must contain no statement content (ADR-013).
- **An audit — documentation only — of the other three strategies.** For BancoEstado, Banco de Chile and
  Santander: is each calibrated against a single layout, and is each date format assumed rather than
  observed? Two concrete leads already visible from the code: BancoEstado (`banco-estado.strategy.ts:65-73`,
  `abono` 395–460 / `cargo` 460–500, **zero gap** between `descripcion`, `abono` and `cargo`) and Santander
  (`santander.strategy.ts:81-89`, `abono` only 25 pt wide at 495–520, with a 45 pt dead zone at 450–495) were
  never part of the 2026-08-30 real-statement recalibration that Banco de Chile and BCI received. Findings
  get written down; **no strategy other than BCI is modified in this change.**
- Spec delta on `openspec/specs/pdf-ingesta/spec.md` (currently PDF-00..PDF-10) — exact requirement IDs and
  Given/When/Then are the spec phase's call.

### Out of scope (explicit non-goals)

- **Fixing BancoEstado, Banco de Chile or Santander.** The audit produces findings and, if warranted,
  follow-up changes with their own fixtures. Recalibrating a band without a real measurement is exactly the
  mistake that produced this bug.
- **The real user statement is never committed**, in any form, encrypted or not. No exception.
- **No generic multi-variant layout framework.** Whatever design picks, it must serve the two BCI layouts
  that exist today, not an imagined family of N (YAGNI — the four bank strategies are justified because four
  real implementations exist from day one; a variant plugin system with two known members is not the same
  claim, and design must argue it if it wants it).
- **No change to extraction, password handling, the Excel pipeline, categorization, persistence, money
  arithmetic, or the canonical transaction shape.** Nothing here touches `Transaccion`, `BigInt` handling or
  the 50/30/20 logic.
- **No Prisma migration, no schema change, no backfill.** Nothing about this change persists anything new.
- **No mobile work.** If the zero-rows error reaches the contract, mobile inherits it for free by ADR-024;
  no `apps/mobile` UI ships here.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- **`pdf-ingesta`.** Two additions after `PDF-10`, roughly: (a) BCI MUST parse **both** published layouts —
  slash and dash row dates, both column geometries — and MUST assign `cargo` and `abono` to the correct
  column in each; (b) a detected, structurally-valid statement that normalizes to **zero** movements MUST be
  reported as an error with actionable guidance, never as a successful empty result. `PDF-03`'s per-bank
  reference-target table also gains the new BCI fixture row.
- **`ingesta-management`** may need a note on whether a zero-row commit records a `FALLIDA` `Ingesta` (the
  ING-07 general rule) or is carved out like `PDF-08` does for password failures. Flagged, not decided — see
  Open design questions.

## Approach

Reproduce the variant as a fixture first, then let strict TDD drive each of the three fixes. Diagnosis is
already done; the discipline here is refusing to "fix" anything we cannot pin with a test.

1. **Fixture first (no production code).** Build the generator and the 3-page fixture, and assert the
   *fixture's own* geometry — dash dates present, no slash dates, tokens at the measured X positions, header
   repeated per page, split `PERIODO`. These assertions are green from the start and are what makes the
   later RED tests trustworthy: if the fixture drifts, they fail before the parser tests do.
2. **Date format (RED → GREEN).** A failing normalizer test against the fixture, then extend
   `FormatoFechaPdf` and `parsearFechaFila`. The exhaustive `switch` names every site that must change.
3. **Column geometry (RED → GREEN).** A failing test asserting the fixture's expected movements, totals and
   `cargo`/`abono` split, then the geometry change. **The existing pins are the backward-compatibility
   guarantee** — see below.
4. **Zero rows → error (RED → GREEN).** Domain error, pipeline check, both `_exhaustive` mappers, contract
   sync if the code is enumerated in `openapi.json`, and a user-facing message in the web app.
5. **Audit, write down, stop.** Three strategies read, findings recorded, nothing changed.

Strict TDD throughout (`strict_tdd: true`, `pnpm api test`, ADR-016). Verified green baseline before any
work: **273 files / 2595 tests**.

### How backward compatibility is guaranteed (not hoped for)

The existing BCI behavior is already pinned by three independent mechanisms, and this change treats all
three as tripwires it must clear:

1. `bci.strategy.spec.ts:82-87` asserts `rangosX` with an exact `toEqual` on the full array. **Any** band
   change fails it loudly. It may only be updated together with a written justification of the new numbers —
   never adjusted to make a test pass.
2. `bci.strategy.spec.ts:67` pins `formatoFecha` to `'DD/MM/YYYY'`, and `:71-75` asserts `xMin < xMax` for
   all four canonical columns.
3. The two existing BCI fixtures (`bci-cartola-test.pdf`, `bci-cartola-montos-grandes-test.pdf`) are
   asserted end to end in `pdfjs-transaction-normalizer.service.spec.ts`,
   `pdfjs-structure-validator.service.spec.ts` and `pdfjs-bank-detector.service.spec.ts`, with exact
   movement counts, totals and excluded rows. **Those expected values MUST NOT change in this change.** If a
   geometry edit moves them, the edit is wrong, not the fixture.

The same rule applies to the other three banks: their strategy specs and fixture assertions must stay
untouched and green. `pnpm api test` must end at ≥2595 tests, all green, with none of the pre-existing
expectations rewritten.

### Affected areas

| Area | Impact | What changes |
|---|---|---|
| `apps/api/test/fixtures/pdf/` | New | 3-page dash-date BCI fixture + its generator |
| `infrastructure/pdf/strategies/estructura-pdf-banco.ts` | Modified | `FormatoFechaPdf` gains the dash variant |
| `infrastructure/pdf/pdf-normalization.ts` | Modified | `parsearFechaFila` case (and whatever geometry hook design picks) |
| `infrastructure/pdf/strategies/bci.strategy.ts` | Modified | Bands + date format + `SUCURSAL`/`PERIODO` decisions, with docblock updated |
| `infrastructure/pdf/pdf-structure-extraction.ts` | Possibly | Only if design fixes the split `PERIODO` anchor here |
| `apps/api/src/domain/errors/` | New | Zero-movements error |
| `application/use-cases/ejecutar-pipeline-ingesta.use-case.ts` | Modified | Zero-rows check + error union member |
| `http-express/routes/ingesta.routes.ts` | Modified | Both `_exhaustive` error mappers |
| `apps/api/openapi.json`, `packages/api-client` | Possibly regenerated | `contract:sync` if the error code is enumerated |
| `apps/web` upload/preview components | Modified | Surface the new error message |
| `openspec/specs/pdf-ingesta/spec.md` | Modified | Delta (two new requirements + `PDF-03` table row) |
| `apps/api/CLAUDE.md` | Modified | New fixture in the fixtures table; audit findings |
| `banco-{estado,chile}.strategy.ts`, `santander.strategy.ts` | **Read only** | Audit — no edits |

## Open design questions (for `sdd-design` — deliberately NOT decided here)

1. **How do two column geometries coexist?** Three candidates, none free:
   (a) **widen the bands** — simplest, and the measurements suggest it may be **unsafe**: amounts are
   right-aligned, so the token's *start* x depends on the amount's width, and the new variant's amounts
   (420.9–486.6) overlap the old variant's `abono` range (455.3–476.6). A single union band pair risks
   reading one variant's charge as the other's deposit. Design must measure the new variant's per-column
   split before it can even evaluate this option;
   (b) **two BCI variants** discriminated by a layout signal (e.g. the presence of the `SUCURSAL` header, or
   the header token X positions), each with its own `rangosX` and `formatoFecha` — closest to the existing
   strategy pattern, at the cost of a second dimension in the strategy model;
   (c) **derive the bands from the measured header X positions at validation time** instead of hard-coding
   them — kills this whole class of bug, and is by far the largest change; it would need its own risk
   argument and possibly an ADR.
   The decision is design's. The **constraint is not negotiable**: no configuration may exist in which one
   layout's `cargo` can be read as the other's `abono` (ADR-015 — the risk concentrates on money).
2. **Where does the zero-rows check live, and how wide is its blast radius?**
   `EjecutarPipelineIngestaUseCase` is the obvious home, but it is shared by preview, commit and the
   one-shot endpoint **and by the Excel branch** — putting it there changes `.xlsx` behavior too. Putting it
   in the PDF normalizer limits the blast radius but leaves Excel silent. Design decides, and states which
   existing suites the choice touches.
3. **Does a zero-row commit create a `FALLIDA` `Ingesta` row?** ING-07 says every terminal commit failure is
   recorded; `PDF-08` already carves out password failures because retries would pollute history. A
   zero-row statement is arguably a genuine failed ingesta worth recording — but a user retrying the same
   file three times would get three rows. Decide explicitly.
4. **The accepted tradeoff's escape hatch — or the absence of one.** The user has settled that zero rows is
   an **error**, knowing a genuinely empty month (a real account with no movements) is then rejected too.
   Design must decide whether that is simply the accepted behavior with a message that says so, or whether
   the error text distinguishes "we could not read this file" from "this statement appears to have no
   movements". Adding a `force`/override flag is **not** on the table (YAGNI, and it re-opens a settled
   decision).
5. **Does the split `PERIODO` anchor get fixed?** BCI is exempt from `RangoFechasInvalidoError`, so
   `periodo: undefined` costs nothing functionally today. Fixing the regex to tolerate `:` is a two-character
   change; leaving it is a silent hole of exactly the kind this change exists to close. Small call, but make
   it deliberately.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **A widened band flips a charge into a deposit** (money sign inversion) across variants | **High** | The single most dangerous outcome here. Constraint stated above; the existing exact-value fixture assertions must stay green unchanged; design must measure the new variant's per-column split before choosing option (a) |
| Fixing BCI regresses the existing BCI layout | Med | Three independent pins (`rangosX` `toEqual`, `formatoFecha`, end-to-end fixture assertions) fail loudly; expected values may not be rewritten |
| The synthetic fixture does not faithfully reproduce the real variant, so the fix looks green and still fails in production | **High** | Fixture-geometry assertions land first, before any production code; every measurement in this proposal is reproduced explicitly; the real file is re-run manually (never committed) as the final acceptance check |
| The zero-rows error rejects a legitimately empty statement | Med | **Accepted tradeoff, chosen deliberately by the user.** Mitigated only by message quality (design question 4) |
| The zero-rows check placed in the shared pipeline changes `.xlsx` behavior unintentionally | Med | Design question 2 must name the affected suites; full `pnpm api test` is the gate |
| PII from the real statement leaks into a fixture, test name, commit message or artifact | Med | Binding rule at the top of this document; only geometry crosses over; reviewer checks it on every slice |
| The audit turns into a fix and the change balloons | Med | Audit is documentation-only by scope; any fix becomes a separate change with its own real-statement measurement |
| Contract drift if the new error code reaches `openapi.json` | Low | `contract:sync` + the existing CI drift-check |
| Slice count and TDD doubling overrun the review budget again | **High** | See Review Workload Forecast — the previous change overran its forecast by ~2.6× |

## Rollback plan

Low-risk by construction: **no Prisma migration, no schema change, no backfill, nothing new persisted.**
Every slice reverts with `git revert` of its merge commit, with no data repair and no state to unwind.

- **Fixture slice**: reverting removes a test fixture and its generator. Zero production impact.
- **Date-format slice**: reverting restores `'DD/MM/YYYY'`-only parsing. Dash-date statements go back to
  yielding zero rows — the pre-change behavior, not a worse one.
- **Geometry slice**: the highest-value revert target. Reverting restores the 2026-08-30 bands verbatim, and
  the existing fixture assertions prove the old layout still parses. This is why the geometry change must be
  its **own** commit, not folded into the date fix.
- **Zero-rows slice**: independently revertible; reverting restores the silent-success behavior. Because this
  slice is the only user-visible behavior change on **existing** working uploads, it is the one to revert
  first if production surprises us (e.g. a user with a legitimately empty month).
- If a slice touching the contract is reverted, re-run `contract:sync` so `openapi.json` and
  `packages/api-client` return to the committed state; CI's drift-check catches a half-revert.

## Slicing strategy

Chain strategy for this session is `feature-branch-chain`: a tracker branch accumulates integration, PR #1
targets the tracker, each later PR targets the previous PR's branch. Strict TDD per slice
(`pnpm api test`), each slice green and independently revertible.

- **Slice 1 — the calibrated fixture.** Generator + 3-page dash-date fixture + assertions on the fixture's
  own geometry. No production code. Ends green.
- **Slice 2 — dash row dates.** RED against the fixture, then `FormatoFechaPdf` + `parsearFechaFila` + the
  BCI strategy's `formatoFecha`. Resolves nothing about geometry.
- **Slice 3 — column geometry.** RED on expected movements/totals/`cargo`-`abono` split, then the geometry
  change, plus the `SUCURSAL` and `PERIODO` decisions and the strategy docblock. Resolves design questions
  1 and 5. **The riskiest slice — smallest diff possible, own commit, own revert.**
- **Slice 4 — zero rows is an error.** Domain error, pipeline check, both `_exhaustive` mappers, contract
  sync if needed, web message. Resolves design questions 2, 3 and 4.
- **Slice 5 — audit of the other three banks.** Read-only; findings into `apps/api/CLAUDE.md` and/or the
  spec, plus follow-up items for anything that warrants its own change. No strategy edits.

## Review Workload Forecast

Honest estimate, hand-authored lines only (regenerated `openapi.json` / `types.gen.ts` excluded). **The
previous change (`ingesta-pdf-password`) forecast ~900 lines and overran by roughly 2.6×, largely because
strict TDD doubles every slice — each production edit arrives with its RED test.** These numbers already
carry that multiplier instead of discovering it again mid-apply:

| Slice | Est. changed lines | Notes |
|---|---|---|
| 1 — fixture generator + fixture + geometry assertions | ~450 | The comparable generator is 285 lines for 2 pages; this one is 3 pages with an extra column |
| 2 — dash row dates | ~160 | Small production edit, several parser tests |
| 3 — column geometry | ~320 | Small production edit, heavy test surface (both variants, both money columns) |
| 4 — zero rows → error | ~380 | Domain + application + 2 mappers + contract + web, each with tests |
| 5 — audit (documentation only) | ~140 | Prose, no code |
| **Total** | **~1450** | Ceiling ~1900 if design picks option (c) — header-derived geometry |

Slice 1 alone exceeds the 400-line budget, and it is almost entirely mechanical generated-content data; the
other slices fit. Roughly half of slices 2–4 is test code by construction (strict TDD + the ADR-015 emphasis
on money paths).

```
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
```

Delivery strategy for this session is `ask-on-risk`, so this needs an explicit call before apply. The five
slices map onto five chained PRs under `feature-branch-chain`; slice 1 will likely need a `size:exception`
on the generator, or a split of the generator from its assertions. Slices 2 → 3 are strictly ordered; slices
4 and 5 are independent of the BCI fixes and of each other.

## Dependencies

- `pdfjs-dist` — already installed, no version change, no new dependency.
- **No new ADR required.** This change lives inside ADR-009's PDF pipeline and respects ADR-005 layering,
  ADR-015's money emphasis, ADR-013's no-PII rule, and ADR-016's TDD posture. **Exception:** if design picks
  option (c) — deriving column bands from measured header positions at validation time — that is a change of
  parsing strategy for all four banks and escalates to an ADR **before** any code.
- No relationship to `ingesta-pdf-password` beyond sharing files; that change is explicitly cleared of
  causing this bug.

## Success criteria

- [x] The new dash-date, shifted-geometry BCI fixture normalizes to its full expected movement set, with
      `cargo` and `abono` on the correct sides and exact integer CLP amounts.
- [x] Both existing BCI fixtures still normalize to their **unchanged** documented counts, totals and
      excluded rows — no expected value in any pre-existing test was rewritten.
- [x] BancoEstado, Banco de Chile and Santander suites are untouched and green.
- [x] A detected, structurally-valid statement that normalizes to zero movements returns a specific,
      actionable error — never a successful empty preview.
- [x] The error message contains no statement content, no amounts and no PII.
- [x] No real user statement, or any excerpt of one, exists anywhere in the repository.
- [x] Audit findings for the other three banks are written down, with any follow-up work named.
- [x] `pnpm api test` ≥ 2595 tests, all green; `pnpm web test`, `tsc --noEmit`, and the `openapi.json`
      drift-check green.
- [x] The real statement (run manually, never committed) parses end to end.

## Proposal question round

Written here rather than asked live, because this phase ran as a delegated executor with no direct channel
to the user. Four product questions that would sharpen the proposal, plus the assumptions this document
made in their absence. None of them re-open the three settled decisions.

1. **Silent-failure blast radius (impact).** Has this variant been uploaded before? Any earlier month that
   produced an empty preview and was abandoned — or worse, committed as a zero-movement `Ingesta` — is data
   the user is currently missing. Should this change include a "which past uploads were silently lost" check,
   or is the assumption that nothing was ever committed from a broken parse?
   *Assumed*: no history repair is needed; the user simply retries the affected files after the fix.
2. **The empty-month message (product outcome).** When a statement genuinely has no movements, what should
   the user read? The settled decision is "error", but the wording is the entire product surface of this
   change. Should the message claim "we could not read this file", or admit "this statement appears to have
   no movements — if that's wrong, tell us"?
   *Assumed*: one message covering both, phrased so it does not accuse the user's file of being broken.
3. **Audit follow-through (decision gap).** The audit is documentation-only by scope — but where do the
   findings need to land to actually get acted on, and what is the trigger? A note in `apps/api/CLAUDE.md`
   is durable but passive; GitHub issues create real backlog pressure.
   *Assumed*: findings into `apps/api/CLAUDE.md`, plus an issue per bank that shows a concrete risk.
4. **Acceptance bar (business rule).** Is "parses without error" enough to call this done, or must the parsed
   totals be reconciled against the statement's own printed totals — the strongest available proof that no
   movement was dropped and no charge was read as a deposit?
   *Assumed*: the manual acceptance check on the real file reconciles totals, not just row counts.

## Next

`sdd-spec` and `sdd-design` can run in parallel.

**Design must** settle the five open questions — above all question 1, and it must do so with the new
variant's **per-column** amount X split measured, not inferred from the combined 420.9–486.6 range in this
proposal. It must state, in writing, why its chosen configuration cannot read one layout's `cargo` as the
other's `abono`.

**Spec must** write the `pdf-ingesta` delta in Given/When/Then with RFC 2119 keywords: BCI parses both
published layouts with correct column assignment; zero normalized movements is an error, never a success;
and the new fixture's row in the `PDF-03` reference-target table. It must also state the accepted tradeoff
(a genuinely empty statement is rejected) as an explicit, testable requirement rather than a footnote.
