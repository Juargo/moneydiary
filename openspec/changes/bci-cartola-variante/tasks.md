# Tasks: Second BCI Statement Layout + Zero-Movements Error (bci-cartola-variante)

> Grouped by Clean Architecture layer within each of the design's 5 slices (`domain <- application <-
> infrastructure`), hierarchical numbering, each phase completable in one session. Strict TDD
> (`pnpm api test`): every implementation task is RED (failing test named first) → GREEN (minimal code) →
> REFACTOR. Design decisions D-01..D-14 are BINDING — not re-litigated here. Spec requirements PDF-11, PDF-12
> and the modified PDF-02/PDF-03 are traced per phase below. Every line number was re-verified against the
> working tree (`/Users/jorge/dev/MoneyDiary.wt/debug-bci`, branch `feat/api-bci-cartola-variante`) during this
> phase (2026-09-10). Verified green baseline before any work: **273 files / 2595 tests**.
>
> **PII boundary (inherited, binding, repeat every slice).** No amount, name, account number, merchant or date
> from the real statement appears in any fixture, test name, comment or commit message. Only non-identifying
> page geometry crosses over — and it is already fully captured in design.md's D-12 table.

## Four ordering traps — encoded below, not left for `sdd-apply` to rediscover

1. **Trap 1 — the date fix alone cannot turn a row green.** `repartirEnColumnas` filters `t.x >= rango.xMin`
   (`token-grouping.ts:112`, verified). The `fecha` band starts at 35 (`bci.strategy.ts:125`, verified) and the
   new variant's date tokens measure min = p50 = 33.6 — out of band. Phase 6's RED test therefore uses a
   **synthetic token placed inside the CURRENT band** (x≈40) so it isolates the separator defect (D-04) from
   the band defect (D-03/D-02, fixed only in Phase 9-13). A RED test against the new fixture's movements would
   stay red through a correct Phase 6-8 implementation — that RED is reserved for Phase 13.
2. **Trap 2 — accepting `-` dates breaks an existing fixture.** `generar-bci-cartola-montos-grandes-test.ts:220`
   emits `t('01-05-2026 al 31-05-2026', 45.0, 561.8)` (verified) with amounts in both the cargo (`386.0`,
   `:223`) and abono (`461.0`, `:225`) bands on the SAME row. The instant Phase 7's regex change lands, that
   row parses a date and `Transaccion.crear` rejects it (cargo AND abono both non-zero) — the existing 8-move-
   ment BCI fixture assertion fails. Phase 8 is a **mandatory same-slice checkpoint**: observe this regression
   before adding the `filasIgnoradas` anchor, so the anchor is proven necessary, not speculative.
3. **Trap 3 — the `never` guards will NOT catch a missed union member.** `PdfInvalidoError`, `PdfSinTextoError`
   and every sibling domain error declare no members beyond `Error`'s, so any new error class is structurally
   assignable to them — `tsc --noEmit` stays clean even if `SinMovimientosError` is never added to
   `ProcessIngestaError`/`PreviewIngestaError`/`CommitIngestaError` (D-09, verified against
   `ingesta.routes.ts:434`/`:484` — both `_exhaustive` sites are genuinely nominal-`instanceof`-checked but
   fed from a structurally-widened union upstream that the compiler will not force). Phase 24's three
   route-level tests are the **only** detector and are marked **MERGE-BLOCKING**.
4. **Trap 4 — the zero-rows guard changes `.xlsx` behavior too, on purpose (D-07).**
   `excel-transaction-normalizer.service.ts:222-226` (verified: bare `return Result.ok(transacciones)`, no
   zero-row guard) has the identical hole. Exactly two pre-existing tests flip from documenting success to
   documenting failure: `process-ingesta.use-case.spec.ts:673` (verified —
   `"lista de transacciones vacía: persiste con total 0 y retorna ok, sin registrar FALLIDA"`) and
   `preview-ingesta.use-case.spec.ts:480` (verified —
   `"archivo con 0 filas de datos: retorna ok con totalFilas:0 y filas:[] (200 legítimo)"`). Phases 20/21 name
   both by file and line so a reviewer can tell "new specification" from "quietly rewritten expectation" —
   these two, plus the `rangosX` `toEqual` in Phase 12, are the **only three** pre-existing expectations this
   entire change is allowed to touch.

## Vitest include-glob gotcha (task-author finding, not in the design)

`apps/api/vitest.config.ts:19` is `include: ['src/**/*.spec.ts', 'test/*.spec.ts']` (verified) — **not**
`test/**/*.spec.ts`. A fixture geometry self-assertion file dropped under `test/fixtures/pdf/*.spec.ts` (the
natural-looking location, sibling to the generator script) would **silently never run** — vitest would report
0 failures because it never collected the file, and the "assertions are green from the start" claim in D-12
would be true only by omission. Phase 3 below places the self-assertion test under
`src/infrastructure/pdf/strategies/bci.strategy.spec.ts` instead — same file that already has a `tokensPagina1`
helper and per-fixture describe blocks for exactly this purpose (verified, `bci.strategy.spec.ts:10-18`).

---

## Phase 1 (Slice 1): Fixture generator — no production code (D-12)

**Traces PDF-03's new table row** ("bci — variant B (dash dates, shifted geometry)").

- [x] 1.1 Read `generar-bci-cartola-montos-grandes-test.ts` in full again (already re-verified in this phase —
      raw uncompressed content streams, `BT/Tf/Tm/Tj/ET` per token, Helvetica `/WinAnsiEncoding`, latin1, the
      backward pen-jump spacer at x=599 (`:59-77`)) before writing anything new.
- [x] 1.2 Write `apps/api/test/fixtures/pdf/generar-bci-cartola-variante-test.ts`, same structure (catalog +
      pages + content-stream objects + xref/trailer assembled by hand), reproducing the **D-12 geometry
      contract exactly**, entirely invented data:
      - Row dates `DD-MM-YYYY`, date token x = **33.6** (the out-of-band value — the fixture must prove D-03,
        do not "round" it to something safer).
      - `SUCURSAL` column, x ∈ [75.7, 83.4].
      - `descripcion` starting at **134.8**, values up to ≤220.7.
      - Charges (cargo), right-aligned, spanning **420.9 – 434.1**, including at least one token ≥430 (inside
        today's dead zone).
      - Deposits (abono), at least two, near **484 – 487**.
      - Saldo column, 555.9 – 570.6 — must remain unassigned by every `rangosX` configuration in this change.
      - Table header repeated on **every** page: `FECHA` 38.2, `SUCURSAL` 81.1, `DESCRIPCION` 195.9, `CHEQUES`
        392.1, `DEPOSITOS` 459.9, `SALDO DIARIO` 521.2.
      - `PERIODO` anchor split into 3 physical tokens: `PERIODO` | `:` | `DD-MM-YYYY al DD-MM-YYYY`.
      - **3 pages.**
      - Export `SALDO_ANTERIOR`, `TOTAL_CARGOS`, `TOTAL_ABONOS`, `SALDO_FINAL` as named constants (D-13) —
        the generator must compute a running balance that is internally consistent by construction, same
        precedent as `generar-bci-cartola-montos-grandes-test.ts:80-83`.
      - Every name, merchant, account number and amount is **invented** — no value from the real statement.
- [x] 1.3 Run `pnpm exec tsx test/fixtures/pdf/generar-bci-cartola-variante-test.ts` (from `apps/api`); commit
      both the generator script and the resulting `bci-cartola-variante-test.pdf` binary (D-12's
      committed-vs-generated-at-test-time tradeoff — same as the existing BCI fixtures).

## Phase 2 (Slice 1): Fixture self-assertions — RED first, no production code (D-12)

- [x] 2.1 RED: add a new `describe('fixture geometry — bci-cartola-variante-test.pdf (D-12 self-assertions,
      no production code)', ...)` block to `apps/api/src/infrastructure/pdf/strategies/bci.strategy.spec.ts`
      (see the vitest include-glob note above — **do not** create a new file under `test/fixtures/pdf/`).
      Reuse the existing `tokensPagina1` helper pattern to load all 3 pages' tokens via `PdfTextExtractor`
      (not filtered to page 1). Write the assertions FIRST against a file that does not exist yet if Phase 1
      hasn't landed in the same commit — otherwise this is the trustworthiness gate for everything after it,
      so treat it as RED against the fixture's own measured values:
      - At least one date token's `str` matches `/^\d{2}-\d{2}-\d{4}$/` (dash separator present).
      - Zero tokens match `/^\d{2}\/\d{2}\/\d{4}$/` (no slash dates anywhere in this fixture).
      - A date token exists at `x === 33.6` (pins the out-of-band value D-03 depends on).
      - The 6 header labels (`FECHA`, `SUCURSAL`, `DESCRIPCION`, `CHEQUES`, `DEPOSITOS`, `SALDO DIARIO`) each
        appear on all 3 pages (3 occurrences each).
      - Three separate tokens exist reading exactly `PERIODO`, `:`, and a `DD-MM-YYYY al DD-MM-YYYY` string
        (the split-anchor shape D-06 must handle).
      - At least one cargo-range token (x ∈ [420.9, 434.1]) and at least two abono-range tokens
        (x ∈ [484, 487]) exist.
- [x] 2.2 GREEN: once Phase 1's generator produces the fixture, this block should already be green — if any
      assertion fails, fix the **generator** (never loosen the assertion) until it passes.
- [x] 2.3 Run `pnpm api test -- bci.strategy` — confirm the new describe block is green and every pre-existing
      test in the same file is untouched.

---

## Phase 3 (Slice 2): Infrastructure — dash-date parsing, isolated from the band defect (D-04) — Trap 1

**Traces PDF-11** ("every movement row's date parses successfully").

- [x] 3.1 RED: `apps/api/src/infrastructure/pdf/pdf-normalization.spec.ts` — call `normalizarTransaccionesPdf`
      with a **synthetic single-row token set** (following the file's existing synthetic-token pattern) whose
      date token sits at **x=40** (inside the CURRENT `fecha` band [35, 85), so Trap 1 cannot interfere) with
      value `'22-07-2026'`, `formatoFecha: 'DD/MM/YYYY'`, and a valid cargo or abono token in-band. Assert the
      row is dropped today (0 transactions returned) because the slash-only regex does not match a dash date.
      This is the "unit test on the parser," not a fixture-level test (design.md, "Everything else follows
      from...", ¶2).
- [x] 3.2 GREEN: widen the `'DD/MM/YYYY'` case in `parsearFechaFila` (`pdf-normalization.ts:81`, verified) from
      `/(\d{2})\/(\d{2})\/(\d{4})/` to `/(\d{2})[/-](\d{2})[/-](\d{4})/` (D-04). Do **not** add a fourth
      `FormatoFechaPdf` member — BCI keeps exactly one structure, one `formatoFecha` (D-01/D-04).
- [x] 3.3 GREEN: Phase 3.1's test now passes.
- [x] 3.4 REFACTOR: update the `FormatoFechaPdf` docblock (`estructura-pdf-banco.ts:14-21`, verified) to state
      the `'DD/MM/YYYY'` member denotes the form `DD?MM?YYYY` and that BCI prints both separators across its
      two layouts.

## Phase 4 (Slice 2): Confirm the existing pins stay untouched

- [x] 4.1 Run `pnpm api test -- bci.strategy` — confirm `formatoFecha` pin (`bci.strategy.spec.ts:67`, verified)
      still reads `'DD/MM/YYYY'` and is unmodified; confirm the `xMin < xMax` pin (`:71-75`) is unmodified.
      **No `rangosX` change happens in this slice** — that is Phase 12's job, not this one.

## Phase 5 (Slice 2): Infrastructure — the mandatory same-slice checkpoint (D-05) — Trap 2

- [x] 5.1 **Checkpoint, do not skip.** Run `pnpm api test -- pdfjs-transaction-normalizer` immediately after
      Phase 3 lands. Confirm it is now RED: the existing `bci-cartola-montos-grandes-test.pdf` fixture's
      8-movement assertion (`pdfjs-transaction-normalizer.service.spec.ts:342-435`) fails with
      `EstructuraPdfInvalidaError`, because the totals-value row (`generar-...ts:220`, `'01-05-2026 al
      31-05-2026'` at x=45.0) now parses a date and carries both a cargo (`386.0`) and an abono (`461.0`)
      token. Record the exact failure (problema tipo + message) before proceeding — this is what proves the
      anchor below is necessary, not speculative.
- [x] 5.2 RED confirmed above; GREEN: add the `filasIgnoradas` anchor to `bci.strategy.ts` (after the existing
      `/^Periodo\s+Saldo Anterior\s*$/` entry, `:170`, verified), in the exact-anchor style the file already
      uses:
      ```ts
      // Fila de VALORES de la sección de totales: su columna `fecha` trae el
      // RANGO del período ("DD-MM-YYYY al DD-MM-YYYY"), no una fecha de
      // movimiento. Inerte hasta que el parser aceptó el separador "-"
      // (D-04); desde entonces parsea como fila fechada y, al traer cargo Y
      // abono, tumbaría la cartola completa. Ancla exacta: ninguna fila de
      // movimiento real trae dos fechas completas separadas por " al " en
      // esa columna.
      /^\d{2}[/-]\d{2}[/-]\d{4}\s+al\s+\d{2}[/-]\d{2}[/-]\d{4}\b/,
      ```
- [x] 5.3 Re-run `pnpm api test -- pdfjs-transaction-normalizer` — confirm both existing BCI fixtures
      (`bci-cartola-test.pdf` → **18** movements, `bci-cartola-montos-grandes-test.pdf` → **8** movements,
      verified at `:212-339` and `:342-435`) are green again with their **unchanged** documented counts. This
      IS Slice 2's real acceptance bar, per design.md D-05 — not "the new fixture's dates parse."

## Phase 6 (Slice 2): Verification

- [x] 6.1 `pnpm api test`, `pnpm api exec tsc --noEmit` — all green. Confirm the diff for this slice touches
      only: `pdf-normalization.ts`, `pdf-normalization.spec.ts`, `estructura-pdf-banco.ts` (comment-only),
      `bci.strategy.ts` (one new `filasIgnoradas` entry + comment).
- [x] 6.2 Confirm the 3 non-BCI bank suites and every other pre-existing BCI test are byte-identical in
      expectation (no other rewritten value in this slice).

---

## Phase 7 (Slice 3): Infrastructure — column geometry, the riskiest slice (D-01/D-02/D-03) — RED first

**Traces PDF-11** (correct `cargo`/`abono` column assignment per layout) **and PDF-03**'s new fixture row.

- [x] 7.1 RED: add a new describe block to `pdfjs-transaction-normalizer.service.spec.ts` for
      `bci-cartola-variante-test.pdf` asserting: (i) the exact movement count Phase 1's generator produces,
      (ii) the exact `{fecha, descripcion, cargo, abono}` multiset, (iii) `Σcargo` and `Σabono` as `BigInt`
      against the generator's exported `TOTAL_CARGOS`/`TOTAL_ABONOS` constants, (iv) the reconciliation
      identity `SALDO_ANTERIOR − Σcargo + Σabono === SALDO_FINAL` (D-13 — the only assertion that catches
      both a dropped row and a sign inversion). Confirm RED against the current (pre-Phase-8) `rangosX` — the
      new variant's date tokens are still out of band (Trap 1), so this must fail with far fewer than the
      expected movement count.

## Phase 8 (Slice 3): Infrastructure — the band change itself (D-02/D-03)

- [x] 8.1 GREEN: update `rangosX` in `bci.strategy.ts` (`:124-134`, verified) to the D-02/D-03 decided values:
      ```ts
      rangosX: [
        { col: 'fecha',       xMin:  30, xMax:  85 },   // 35 → 30 (D-03)
        { col: 'descripcion', xMin: 130, xMax: 320 },   // 145 → 130 (D-02)
        { col: 'cargo',       xMin: 360, xMax: 440 },   // 430 → 440 (D-02)
        { col: 'abono',       xMin: 450, xMax: 515 },   // 435 → 450, 500 → 515 (D-02)
      ],
      ```
      `cargo.xMin` stays **360** unchanged — no measurement asks for a change there (D-02, KISS).
- [x] 8.2 GREEN: Phase 7.1's test should now pass or come close — do not force it green by touching the test;
      if it is still red, the geometry table above is transcribed wrong, not the test.

## Phase 9 (Slice 3): Infrastructure — the mandatory invariant test (D-02)

- [x] 9.1 RED+GREEN: add a new strategy-level spec (new describe block in `bci.strategy.spec.ts`, or a
      dedicated `bci-rangos-invariante.spec.ts` sibling if the file grows unwieldy — implementer's call,
      document the choice) asserting, as arithmetic, for the 6 measured clusters in D-02's table (V1 cargo
      381.1–409.7, V1 abono 455.3–476.6, V2 cargo 420.9–434.1, V2 abono 484.4–486.6, V1 saldo 542.2–561.9, V2
      saldo 555.9–570.6):
      - Every V1 and V2 cargo sample x is inside `cargo`'s `[xMin, xMax)` and outside `abono`'s.
      - Every V1 and V2 abono sample x is inside `abono`'s `[xMin, xMax)` and outside `cargo`'s.
      - Every saldo sample x (both variants) is outside both `cargo` and `abono`.
      - `cargo.xMax < abono.xMin` (the dead zone exists).
      - `abono.xMax < 521.2` (V2's `SALDO DIARIO` header x — the thin-margin risk D-02/design-risk-2 calls
        out explicitly; this is the test that pins the 6.2 pt margin so it cannot be nudged later without
        re-measuring).

## Phase 10 (Slice 3): Infrastructure — fecha band + SUCURSAL hazard (D-03)

- [x] 10.1 RED+GREEN: a row whose `fecha` column text reads `"22-07-2026  SUCURSAL-NAME"` (date + SUCURSAL
      token both landing in the widened `fecha` band) still parses the date correctly (the unanchored regex
      from Phase 3 handles this — same pattern Santander already relies on, `santander.strategy.ts:82`,
      verified precedent cited in design D-03).
- [x] 10.2 RED+GREEN: a row containing only a SUCURSAL-shaped token (no date, no amounts) never produces a
      movement on its own.
- [x] 10.3 RED+GREEN: V1's SUCURSAL token (x ≈ 99) remains unassigned after the band change — it must fall in
      the `[85, 130)` gap between the new `fecha.xMax=85` and `descripcion.xMin=130`, not inside either
      column.
- [x] 10.4 Explicitly do **not** add a 5th `ColumnaPdf` member for `sucursal` (YAGNI, D-03 "Rejected: a fifth
      `ColumnaPdf` member") and do **not** narrow `fecha.xMax` below 85 to try to exclude SUCURSAL (D-03
      "Rejected: narrowing `fecha.xMax`").

## Phase 11 (Slice 3): Infrastructure — PERIODO anchor colon tolerance (D-06)

- [x] 11.1 RED: `bci.strategy.spec.ts` — a new scenario matching `PERIODO : 01-04-2026 al 30-04-2026` (colon
      variant, the fixture's own shape from Phase 1) against `anclasPeriodo.desde`/`.hasta` returns
      `undefined` today (the existing no-colon-only pattern does not tolerate a colon).
- [x] 11.2 GREEN: widen both anchors (`bci.strategy.ts:120-123`, verified) with the colon-tolerant shape,
      copied verbatim from the in-repo Banco de Chile precedent (`banco-chile.strategy.ts:91-92`):
      ```ts
      desde: /PERIODO\s*:?\s*(\d{2}-\d{2}-\d{4})/,
      hasta: /PERIODO\s*:?\s*\d{2}-\d{2}-\d{4}\s+al\s+(\d{2}-\d{2}-\d{4})/,
      ```
- [x] 11.3 Confirm the existing no-colon pin (`bci.strategy.spec.ts:103-111`, verified — `'PERIODO
      01-04-2026 al 30-04-2026'`) is still green, unmodified.
- [x] 11.4 Explicitly do **not** touch BCI's `fuenteAnio.kind === 'explicito'` exemption from
      `RangoFechasInvalidoError` (`bci.strategy.ts:137`; exemption logic in
      `pdf-structure-extraction.ts:117-129`, verified) — a missing period anchor stays non-fatal for BCI
      (D-06 part 2, deliberate).

## Phase 12 (Slice 3): Infrastructure — rewrite the ONE allowed pre-existing pin (D-01 tripwire 1)

- [x] 12.1 GREEN: update `bci.strategy.spec.ts:82-87`'s `rangosX` `toEqual` (verified) to the new D-02/D-03
      values, with a comment citing D-02's table as the justification — this is explicitly the one
      pre-existing expectation this whole change is allowed to rewrite, and only together with a written
      justification (design.md D-01 tripwire 1). Do not touch this test anywhere else in this change.

## Phase 13 (Slice 3): Infrastructure — header-row leak guard (D-12 hazard)

- [x] 13.1 RED-or-confirm-inert: assert no table-header fragment (`FECHA`, `SUCURSAL`, `DESCRIPCION`,
      `CHEQUES`, `DEPOSITOS`, `SALDO DIARIO`) appears in any normalized description for the new fixture. If
      this is already green (design's analysis says it likely is — non-parseable date + non-empty `cargo`
      blocks fusion), **do not add a speculative `filasIgnoradas` anchor** (YAGNI) — keep the test as a
      permanent regression guard. If it is RED, add the minimal anchor needed and document why, same style as
      Phase 5.2.

## Phase 14 (Slice 3): Infrastructure — close the loop, verify no regression

- [x] 14.1 Re-run Phase 7.1's fixture-level test — full expected movement set, correct `cargo`/`abono` sides,
      reconciliation identity all green.
- [x] 14.2 Run the full `pnpm api test` suite — confirm BOTH existing BCI fixtures (18 / 8 movements,
      unchanged) and all 3 other bank suites (BancoEstado, Banco de Chile, Santander) are byte-identical to
      before this slice.
- [x] 14.3 REFACTOR: update the `bci.strategy.ts` docblock (`:19-88`, verified) with the D-02/D-03/D-06
      numbers and a short pointer to design.md — do not duplicate the full essay, the existing docblock style
      is a few sentences per decision plus the measured ranges.

## Phase 15 (Slice 3): Manual acceptance — the real statement, never committed (D-13)

- [ ] 15.1 Run the pipeline locally against the real statement (never committed, no exception). Reconcile
      `Σcargo` / `Σabono` / movement count against the statement's own printed totals; check the balance
      identity. **Record only the boolean outcome and the row count** in the PR description — never amounts,
      names, account numbers, or descriptions.

---

## Phase 16 (Slice 4): Domain — `SinMovimientosError` (D-08)

**Traces PDF-12.**

- [ ] 16.1 RED: `apps/api/src/domain/errors/sin-movimientos.error.spec.ts` — asserts
      `new SinMovimientosError('cartola.pdf', 'BCI')` has `name === 'SinMovimientosError'`, a `readonly banco`
      property equal to `'BCI'`, and a message that contains the file name but contains **no** digits that
      could be an amount (guard against an accidental future interpolation).
- [ ] 16.2 GREEN: create `apps/api/src/domain/errors/sin-movimientos.error.ts`, shaped like
      `pdf-invalido.error.ts`/`pdf-sin-texto.error.ts` (both verified — bare `Error` subclass, constructor
      takes only identifying-but-non-sensitive params):
      ```ts
      export class SinMovimientosError extends Error {
        constructor(nombreArchivo: string, readonly banco: string) {
          super(
            `No encontramos movimientos en "${nombreArchivo}". Puede que no hayamos podido leer el ` +
            `formato de esta cartola, o que el período realmente no haya tenido movimientos. ` +
            `Si la cartola sí trae movimientos, avísanos para ajustar la lectura.`,
          );
          this.name = 'SinMovimientosError';
        }
      }
      ```
      Constructor takes `(nombreArchivo, banco)` only — no amount, row or description parameter exists to
      interpolate (structural no-PII guarantee, D-08).
- [ ] 16.3 REFACTOR: doc-comment on the error class explaining the one-message decision (D-08 — cannot
      distinguish "we could not read it" from "the month was empty," so one message names both, leads with
      the one that is our fault, never accuses the user's file).

## Phase 17 (Slice 4): Application — the pipeline guard (D-07)

- [ ] 17.1 RED: `ejecutar-pipeline-ingesta.use-case.spec.ts` — a stub `IPdfTransactionNormalizer` (or Excel
      equivalent) returning `Result.ok([])` makes `EjecutarPipelineIngestaUseCase.execute()` return
      `Result.fail(SinMovimientosError)` instead of `Result.ok({ transacciones: [], ... })`.
- [ ] 17.2 GREEN: add the guard in `ejecutar-pipeline-ingesta.use-case.ts` immediately after
      `const transacciones = normalizeResult.getValue();` (`:184`, verified) and **before** the existing debug
      log (`:187-190`, verified):
      ```ts
      if (transacciones.length === 0) {
        return Result.fail(new SinMovimientosError(archivo.originalName, banco.banco));
      }
      ```
- [ ] 17.3 GREEN: widen `EjecutarPipelineIngestaError` (`:57-67`, verified) with `SinMovimientosError`.
- [ ] 17.4 Confirm this guard fires identically for the Excel branch — no `esPdf` check around it, by design
      (D-07, Trap 4: the fix is deliberately format-agnostic, one piece of knowledge in one place).

## Phase 18 (Slice 4): Application — widen the 3 remaining error unions

- [ ] 18.1 GREEN: widen `ProcessIngestaError` (`process-ingesta.use-case.ts`, union declared after the
      docblock at `:56-69`, verified) with `SinMovimientosError`.
- [ ] 18.2 GREEN: widen `PreviewIngestaError` (`preview-ingesta.use-case.ts:70-74`, verified) with
      `SinMovimientosError`.
- [ ] 18.3 GREEN: widen `CommitIngestaError` (`commit-ingesta.use-case.ts:84-103`, verified) with
      `SinMovimientosError`, in the "Pipeline errors (400)" group alongside `PdfProtegidoError`.
- [ ] 18.4 Run `pnpm api exec tsc --noEmit` — confirm it stays **clean** with all three widened but with NO
      mapper branch added yet (Phase 24 adds those). This empirically repeats the D-09 finding: the compiler
      does not force the mapper branch, only `instanceof` narrowing at runtime does. Record the observation —
      it is the reason Phase 24's tests are merge-blocking, not decorative.

## Phase 19 (Slice 4): Application — commit registers a FALLIDA row (no carve-out, D-10)

- [ ] 19.1 RED: `commit-ingesta.use-case.spec.ts` — a stub pipeline returning
      `Result.fail(new SinMovimientosError('x.pdf', 'BCI'))` makes `CommitIngestaUseCase.execute()` call
      `ingestaFallidaWriter.registrar` **exactly once**, with `motivo: error.message` — the opposite of the
      `PdfProtegidoError` carve-out (D-10: no field to change, no retry that helps, this is a genuine terminal
      failure and the only durable trace that the user tried to import an unreadable statement).
- [ ] 19.2 GREEN: confirm the existing `runCommit()` failure branch already calls `registrarFallo` for any
      error that is NOT `PdfProtegidoError` (per the prior change's `if (!(error instanceof
      PdfProtegidoError)) await this.registrarFallo(...)` shape) — `SinMovimientosError` needs **no new
      branch**, it falls through to the default registration path. If it does not, that is itself a finding to
      fix, not a carve-out to add.

## Phase 20 (Slice 4): Application — rewrite the two pre-existing Excel-branch expectations (D-07, Trap 4)

- [ ] 20.1 **Named rewrite, not a new spec.** `process-ingesta.use-case.spec.ts:673`
      (`"lista de transacciones vacía: persiste con total 0 y retorna ok, sin registrar FALLIDA"`) — change
      the expectation from `result.isOk() === true` / `estado === 'PROCESADA'` / 0 FALLIDA calls to
      `result.isFail() === true` with `result.getError()` an instance of `SinMovimientosError`, and confirm
      `ingestaFallidaWriter.calls` now has length **1** (per Phase 19).
- [ ] 20.2 **Named rewrite, not a new spec.** `preview-ingesta.use-case.spec.ts:480`
      (`"archivo con 0 filas de datos: retorna ok con totalFilas:0 y filas:[] (200 legítimo)"`) — change the
      expectation from `result.isOk() === true` to `result.isFail() === true` with `result.getError()` an
      instance of `SinMovimientosError`.
- [ ] 20.3 Grep every other fake normalizer in the application specs
      (`process-ingesta.use-case.spec.ts:129-140,185-195`, `ejecutar-pipeline-ingesta.use-case.spec.ts:162-188`,
      `commit-ingesta.use-case.spec.ts:206-219`, `preview-ingesta.use-case.spec.ts:123-134,195-206` — line
      numbers per design.md D-07, re-verify each before touching) — confirm all of them already return a
      non-empty transaction array by default, so nothing else in the existing suite flips.

## Phase 21 (Slice 4): Infrastructure — the 3 merge-blocking route tests (D-09) — Trap 3

- [ ] 21.1 RED: `POST /api/ingestas` (one-shot) — stub `processIngesta.execute` to return
      `Result.fail(new SinMovimientosError('x.pdf', 'BCI'))`; assert the response is **400** with
      `code: 'SIN_MOVIMIENTOS'` (not 500, not a message with no `code`).
- [ ] 21.2 RED: `POST /api/ingestas/preview` — same stub/assertion shape against `previewIngesta.execute`.
- [ ] 21.3 RED: `POST /api/ingestas/commit` — same stub/assertion shape against `commitIngesta.execute`.
      **These three tests are MERGE-BLOCKING per D-09 — the slice must not merge without them, and they must
      be observed RED before Phase 22's GREEN.**

## Phase 22 (Slice 4): Infrastructure — the mapper branches

- [ ] 22.1 GREEN: add a `SinMovimientosError` branch to `aHttpError` (`ingesta.routes.ts:444-487`, verified —
      this function is reused by both the one-shot route at `:125` and the preview route at `:178`):
      ```ts
      if (error instanceof SinMovimientosError) {
        return { status: 400, message: error.message, code: 'SIN_MOVIMIENTOS' };
      }
      ```
- [ ] 22.2 GREEN: add the identical branch to `aCommitHttpError` (`ingesta.routes.ts:386-437`, verified).
- [ ] 22.3 Confirm Phase 21's three tests now pass.

## Phase 23 (Slice 4): Contract — verify, do not assume (D-11)

- [ ] 23.1 Run `pnpm api openapi:emit`; diff `apps/api/openapi.json`. `code` values appear only as free-text
      description prose today (verified: `DEMO_SOLO_LECTURA`/`PDF_PROTEGIDO` are not a closed enum anywhere
      in `openapi-document.ts`), so the expected diff is a description-string addition at most, on the
      preview/commit/one-shot 400 responses — not a new schema/enum member. If the diff is anything else,
      stop and re-check the schema file before proceeding.
- [ ] 23.2 Run `pnpm contract:sync` if the emit step changed anything; run `pnpm api openapi:check` — zero
      drift.

## Phase 24 (Slice 4): Web — verify D-11 holds, do not build a new affordance

- [ ] 24.1 Confirm (read-only, then a regression test): `SubirCartola.tsx` derives `mensajeError` from
      `previewMutation.error?.message` (`:798`, verified) and renders it verbatim in a `role="alert"` block
      for the existing `preview-error` state (`:1085-1092`, verified). Add a test in `SubirCartola.test.tsx`
      asserting a `code: 'SIN_MOVIMIENTOS'` 400 response renders `SinMovimientosError`'s message verbatim,
      through the **existing** generic error state — with **no** new `EstadoSubida` member added (D-11: no
      affordance exists for this error, a dedicated state would just duplicate the server message and drift).
- [ ] 24.2 Confirm `ApiError.tag === 'invalid'` already carries `code` and is already in
      `TAGS_ERROR_PERMANENTE` (fail-closed retry policy) — no client plumbing changes needed beyond the test
      in 24.1.

## Phase 25 (Slice 4): Verification

- [ ] 25.1 `pnpm api test`, `pnpm api exec tsc --noEmit`, `pnpm api openapi:check` — all green.
- [ ] 25.2 `pnpm web test`, `pnpm web typecheck` — all green.
- [ ] 25.3 Confirm the diff for this slice touches only: `domain/errors/sin-movimientos.error.{ts,spec.ts}`,
      `ejecutar-pipeline-ingesta.use-case.{ts,spec.ts}`, `process-ingesta.use-case.{ts,spec.ts}`,
      `preview-ingesta.use-case.{ts,spec.ts}`, `commit-ingesta.use-case.{ts,spec.ts}`, `ingesta.routes.{ts,spec.ts}`,
      `openapi.json` + `packages/api-client` (generated), `SubirCartola.test.tsx`.

---

## Phase 26 (Slice 5): Audit — read only, no strategy edits (D-14)

**Traces the proposal's audit scope. No spec requirement — documentation only.**

- [ ] 26.1 Read `banco-estado.strategy.ts`, `banco-chile.strategy.ts`, `santander.strategy.ts` in full. For
      each, determine and write down: how many real statements the bands were calibrated against (BancoEstado
      and Santander: none — confirmed by design, they were not part of the 2026-08-30 recalibration), whether
      the date format was observed or assumed, and the width of the gap between `cargo` and `abono`.

## Phase 27 (Slice 5): Documentation — 3 locations (D-14)

- [ ] 27.1 Add a comment-only block to each of the 3 strategy files with the Phase 26 findings, same location
      BCI's and Banco de Chile's provenance already lives (`bci.strategy.ts:19-21,37-50`;
      `banco-chile.strategy.ts:21-22,33-46`, verified precedent). **Bound: comments only.** Diff-check after:
      the `getEstructura()` return value must be byte-identical for all three, and their existing strategy
      specs must stay green untouched.
- [ ] 27.2 Update `apps/api/CLAUDE.md`'s fixtures table (verified current content includes the
      `bci-cartola-montos-grandes-test.pdf` row) with a new row for `bci-cartola-variante-test.pdf`, and add
      one gotchas line per audited bank under the "Notas técnicas" section, matching the existing terse style.
- [ ] 27.3 Draft one GitHub issue per bank naming a concrete risk and its trigger ("a real statement
      measurement, before any band is touched"): BancoEstado (`abono` [395,460) / `cargo` [460,500) — zero
      dead zone, `banco-estado.strategy.ts:65-70`) and Santander (`abono` 25pt wide at [495,520), 45pt dead
      zone at [450,495), `santander.strategy.ts:81-86`) at minimum, plus whatever Phase 26 found for Banco de
      Chile. **If `gh issue create` is not available in the apply session, draft the 2-3 issue bodies as an
      explicit artifact in the PR description instead of silently skipping this task** — the finding must not
      evaporate.

## Phase 28 (Slice 5): Infrastructure — the machine-checked guard (D-14)

- [ ] 28.1 RED+GREEN: a new cross-bank spec asserting, for all 4 strategies' `rangosX`, that no two bands
      overlap and that `cargo` and `abono` are disjoint. Confirm it passes for all four **today** (including
      the Slice-3-updated BCI bands). Do **not** add a stronger "minimum gap" assertion — BancoEstado would
      fail it today and fixing BancoEstado is out of scope (that fact is exactly the content of its issue in
      27.3).

## Phase 29 (Slice 5): Verification

- [ ] 29.1 `pnpm api test` — all green, including the new cross-bank spec.
- [ ] 29.2 Confirm via `git diff` that BancoEstado, Banco de Chile and Santander's `getEstructura()` return
      values are byte-identical to before this slice — only comment lines changed.

---

## Phase 30: Full change verification

- [ ] 30.1 `pnpm api test` — ≥2595 tests baseline, all green, net additions only (no expected value removed
      except the 3 named rewrites in Phases 12/20.1/20.2).
- [ ] 30.2 `pnpm api exec tsc --noEmit`, `pnpm api lint`, `pnpm web test`, `pnpm web typecheck`,
      `pnpm api openapi:check`, `pnpm build` — all green.
- [ ] 30.3 Walk the proposal's Success Criteria checklist item by item and confirm each one explicitly (both
      layouts parse with correct `cargo`/`abono` sides; both existing BCI fixtures unchanged; the 3 other bank
      suites untouched; zero-movement statements return an actionable error; the error message contains no
      statement content; no real statement or excerpt exists anywhere in the repo; audit findings are written
      down with follow-up named; full test/typecheck/contract gates green; the real statement parses end to
      end per Phase 15).
- [ ] 30.4 PII sweep: confirm no amount, name, account number, merchant string or literal date from the real
      statement appears in any diff, test name, comment or commit message across all 5 slices — reviewer
      checklist item, repeated from the proposal's binding rule.

---

# AMENDMENT — Slice 3b: right-edge rescue for BCI's `cargo` column (design.md AMENDMENT A-01, AD-01..AD-04)

> Added 2026-09-10, after Slices 1-3 shipped green (273 files / 2622 tests) and the real statement was still
> found to fail `EstructuraPdfInvalidaError` on 7 rows (sub-1000 `cargo` amounts, right-aligned, landing in the
> `[440, 450)` dead zone — **zero reached `abono`, no sign inversion**). AD-01..AD-04 in design.md are BINDING
> for everything below; not re-litigated here. Traces spec PDF-11 (correct column attribution for both
> layouts) and, indirectly, PDF-03's variant-B fixture row (the fixture gap that let a broken parser ship
> green). Phases 1-30 above are UNCHANGED — do not renumber or uncheck them. Strict TDD applies throughout:
> every implementation task is RED (failing test named first) → GREEN (minimal code) → REFACTOR. Every line
> number below was re-verified against the working tree
> (`/Users/jorge/dev/MoneyDiary.wt/debug-bci`, branch `feat/api-bci-s3-geometria`) on 2026-09-10, after Slices
> 1-3 landed. Verified green baseline before this amendment's work: **273 files / 2622 tests**.
>
> **PII boundary (inherited, binding, repeat once more).** No amount, name, account number, merchant or date
> from the real statement appears in any fixture, test name, comment or commit message. Only non-identifying
> page geometry and font metrics cross over (design.md AD-02's measured/corroborated glyph advances).

## Trap 5 — the field has to survive a manual field-by-field mapping, or the rescue is silently inert (task-author finding, not in the design)

`normalizarTransaccionesPdf` does not pass `estructura.rangosX` straight through to `agruparTokens` — it
rebuilds each entry by hand:

```ts
const rangosX: RangoColumna[] = estructura.rangosX.map((r) => ({
  col: r.col,
  xMin: r.xMin,
  xMax: r.xMax,
}));
```

(`pdf-normalization.ts:185-189`, verified). This picks exactly three fields. Adding `rescateBordeDerecho` to
`RangoX` (`estructura-pdf-banco.ts:6-11`) and to `RangoColumna` (`token-grouping.ts:4-8`) does **not** make it
cross this boundary — the object literal above drops any field it does not name, silently, with a clean
`tsc --noEmit` (the field is optional, so omitting it is not a type error). If Phase 43's fixture-level RED
test (short amounts still rejected) stays red after Phase 39-42 land, **this mapping is the first place to
check**, not the estimator or the strategy declaration. Phase 39.5 below names this explicitly as its own GREEN
step, not folded silently into a bigger one.

## Phase 39 (Slice 3a — estimator, zero strategy opts in): Infrastructure — the two-pass rescue mechanism (AD-01, AD-02)

**Traces PDF-11.** No production behavior changes in this phase for any of the 4 banks — see 39.6.

- [x] 39.1 RED: `token-grouping.spec.ts` (new file, or a new describe block if one already covers this module) —
      `anchoEstimado('123', 6)` returns a number matching `3 × 0.556 × 6 = 10.008` (3 digit advances at 6pt,
      no separators); `anchoEstimado('1.234', 6)` includes one period advance (`0.278 × 6 = 1.668`);
      `anchoEstimado('12a', 6)` returns `null` (letter `a` is not in the table — the eligibility gate, AD-02).
- [x] 39.2 GREEN: add `ANCHOS_GLIFO_1000EM` (the table in design.md AD-02, verbatim) and
      `anchoEstimado(str: string, tamanoPt: number): number | null` to `token-grouping.ts`. Do **not** reuse
      `REGEX_POSIBLE_MONTO` (`pdf-normalization.ts:48`) as the gate — it requires a `$` or a thousands
      separator and would reject the very sub-1000 amounts this amendment exists to rescue (design.md AD-02,
      explicit).
- [x] 39.3 RED: `token-grouping.spec.ts` — `repartirEnColumnas`/`agruparTokens` with a synthetic column that
      declares `rescateBordeDerecho: { xMin, xMax, tamanoFuentePt }` rescues a token whose left-edge `x` falls
      in a gap between columns but whose *estimated right edge* falls inside `rescateBordeDerecho`'s
      `[xMin, xMax)`. A token whose estimated right edge falls outside that window, or whose `anchoEstimado`
      is `null` (contains an unmeasurable character), stays unassigned — same as today.
- [x] 39.4 GREEN: add the optional `rescateBordeDerecho?: { xMin, xMax, tamanoFuentePt }` field to `RangoX`
      (`estructura-pdf-banco.ts:6-11`, verified) and to `RangoColumna` (`token-grouping.ts:4-8`, verified).
      Implement the two-pass shape design.md AD-01 specifies exactly: pass 1 collects per-column **token
      lists** instead of joining immediately (`token-grouping.ts:111-118`, verified — today's single pass);
      pass 2 iterates only columns that declare `rescateBordeDerecho` and only tokens still in
      `tokensSinAsignar` after pass 1, appending a rescued token to its column's list; the sort
      (`.sort((a,b) => a.x - b.x)`) and join (`.join(' ').trim()`) happen once, at the end, over the merged
      list. If pass 2 rescues a token into a column pass 1 already filled (should not happen given the
      catchment/window design, but must not silently corrupt data if it ever does), the column text ends up
      with two space-joined tokens and `parsearMontoPdf` fails downstream — loud, not silent (design.md AD-01,
      "Implementation shape").
- [x] 39.5 GREEN — **do not fold this into 39.4.** Update the field-by-field mapping in
      `normalizarTransaccionesPdf` (`pdf-normalization.ts:185-189`, verified) to also copy
      `rescateBordeDerecho` from `estructura.rangosX` into the `RangoColumna[]` passed to `agruparTokens`. See
      "Trap 5" above — omitting this step compiles clean and leaves the rescue silently inert end to end.
- [x] 39.6 RED-must-already-be-GREEN: a regression test asserting that for all 4 existing bank strategies
      (none declares `rescateBordeDerecho` at this point in the sequence — that only happens in Phase 40), the
      `columnas` and `tokensSinAsignar` produced by `agruparTokens` are byte-identical to before this phase.
      Zero behavior change is structural (no column has opted in, so pass 2 iterates nothing), not
      tested-into-existence — this test is the proof, not the mechanism.
- [x] 39.7 Run `pnpm api test` (full) — confirm all 2622+ pre-existing tests stay green, plus the new
      `token-grouping.spec.ts` cases. Run `pnpm api exec tsc --noEmit` — clean. Confirm the diff touches only
      `token-grouping.ts`, `token-grouping.spec.ts`, `estructura-pdf-banco.ts` (field addition, no behavior),
      `pdf-normalization.ts` (the one-line mapping addition from 39.5).

## Phase 40 (Slice 3b — BCI opts in): Infrastructure — `cargo` declares the rescue window (AD-01, AD-03)

**Traces PDF-11.**

- [x] 40.1 RED: `bci.strategy.spec.ts` — `strategy.getEstructura().rangosX` includes, for `cargo`,
      `rescateBordeDerecho: { xMin: 446, xMax: 452, tamanoFuentePt: 6 }` (design.md AD-02's window, centred on
      the measured 449.08 convergence). This means rewriting the `rangosX` `toEqual` pin
      (`bci.strategy.spec.ts:171-`, verified — the block Phase 12 already rewrote once) to carry the new
      field. Per design.md AD-04's D-01 row: this is the **second** rewrite of that one pre-existing pin, and
      this amendment is its written justification — the change's allowance rises from three pre-existing
      rewrites (Phases 12/20.1/20.2) to **four, and no more than four**.
- [x] 40.2 GREEN: add `rescateBordeDerecho: { xMin: 446, xMax: 452, tamanoFuentePt: 6 }` to BCI's `cargo` entry
      in `bci.strategy.ts` (`:161-166`, verified). Extend the `rangosX` docblock comment (`:143-160`) with the
      AD-01/AD-02/AD-03 numbers and a one-line pointer to design.md's AMENDMENT A-01 — same terse style as the
      existing D-02/D-03 block, do not duplicate the essay.
- [x] 40.3 Explicitly do **not** add `rescateBordeDerecho` to `abono`. Add a test asserting
      `estructura.rangosX.find(r => r.col === 'abono').rescateBordeDerecho` is `undefined` — AD-03's "no rescue
      window for `abono`" is a decision, not an oversight, and it is what makes "a wrong metric can reject a
      statement, it cannot move a peso from `cargo` to `abono`" true. Pin it.

## Phase 41 (Slice 3b): Infrastructure — extend the D-02 invariant test, do not rewrite it (AD-04)

- [x] 41.1 GREEN (arithmetic, no fixture needed): extend the existing invariant describe block
      (`bci.strategy.spec.ts:233-297`, verified — every existing assertion in this block stays as written) with:
      (a) each measured V2 `cargo` left-edge sample, plus a synthetic 1-, 2- and 3-digit sample, yields
      `anchoEstimado`-estimated right edge inside `[446, 452)`; (b) every V1 and V2 **saldo** sample's estimated
      right edge is **outside** `[446, 452)` (the right-edge restatement of "no phantom deposit equal to the
      running balance"); (c) `cargo.xMax < abono.xMin` still holds (the catchment exists — re-assert, do not
      assume Phase 9's assertion covers this once the field changes its meaning); (d) `abono` declares no
      `rescateBordeDerecho` (may already be covered by Phase 40.3 — do not duplicate, cross-reference).
- [x] 41.2 GREEN: the narrowest-amount invariant (explicit, per design.md AD-03's "provably wide enough, not
      just empirically empty"): a synthetic 1-digit amount's estimated right edge (449.08, the window centre)
      minus one digit advance (`3.336`) gives a left edge of **445.74**, still `4.26` pt below `abono.xMin =
      450`. Assert this as arithmetic — `rightEdgeEstimate - anchoEstimado('9', 6) < abono.xMin` shape, or the
      literal numbers with a comment citing AD-03 — so no BCI `cargo` amount of any measurable width can ever
      reach `abono` via the rescue path, and the assertion breaks (not silently drifts) if the window or the
      metric ever changes.

## Phase 42 (Slice 3b): Fixture obligation — sub-1000 amounts, right-aligned by construction (amends D-12)

**This is the gap that let Slices 1-3 ship green while the real statement was broken — reopening a committed
fixture, per the amendment's own framing.**

- [x] 42.1 Edit `generar-bci-cartola-variante-test.ts` (`:107-217`, verified — the `movimientosPlan` array and
      its hand-picked `cargo`/`abono` `x` values): add at least one **1-digit**, one **2-digit** and one
      **3-digit** `cargo` amount. Compute each amount's `x` as `bordeDerecho − anchoEstimado(str, 6)` using the
      **same** advance table Phase 39.2 put in `token-grouping.ts` (import it, do not hand-copy the numbers) —
      the fixture must *prove* the estimator, not merely coexist with it (design.md, "Fixture obligation").
      Target `bordeDerecho ≈ 449.08` so the generated `x` lands where the real statement's short amounts were
      measured.
- [x] 42.2 At least one of the new short charges must land in the **catchment** `[440, 450)` by left edge —
      reproducing the exact production failure this amendment fixes — and at least one must land inside
      `[437.6, 440)`, reproducing the 11 short amounts that happened to already work under Slice 3's shipped
      bands.
- [x] 42.3 Run `pnpm exec tsx test/fixtures/pdf/generar-bci-cartola-variante-test.ts` (from `apps/api`);
      regenerate `bci-cartola-variante-test.pdf`. Re-run and extend the self-assertion block
      (`bci.strategy.spec.ts:66-`, verified — the D-12 fixture-geometry describe block) with assertions pinning
      the new short amounts' left-edge `x` values and the 449.08 right-edge convergence across all three new
      token lengths (2-char vs 3-char vs 6-char groups agreeing to within the measured 0.01 pt spread, mirrored
      as an assertion on the *generated* fixture, not the real statement).
- [x] 42.4 Confirm the existing 18/8 movement assertions for the two V1 fixtures
      (`pdfjs-transaction-normalizer.service.spec.ts:212-339`, `:342-435`) are untouched by this regeneration —
      they read a different file.

## Phase 43 (Slice 3b): Close the loop — RED before the opt-in, GREEN after

- [x] 43.1 RED, observed in sequence: after Phase 42's regenerated fixture lands but **before** Phase 40's
      `cargo` opts in, re-run Phase 7's fixture-level test (`pdfjs-transaction-normalizer.service.spec.ts`, the
      `bci-cartola-variante-test.pdf` describe block) — confirm it now fails with `EstructuraPdfInvalidaError`
      / `TokenSinAsignarSospechoso` on the new short-amount rows. This reproduces the exact production failure
      mode before the fix lands, so the fix is proven necessary, not speculative (same discipline as Phase
      5.1's checkpoint).
- [x] 43.2 GREEN: with Phases 39-42 all landed, re-run the same test — full expected movement set (now
      including the sub-1000 amounts), correct `cargo` attribution, `Σcargo`/`Σabono` against the regenerated
      `TOTAL_CARGOS`/`TOTAL_ABONOS`, and the reconciliation identity
      `SALDO_ANTERIOR − Σcargo + Σabono === SALDO_FINAL`, all green.
- [x] 43.3 Run the full `pnpm api test` suite — confirm both V1 BCI fixtures (18/8, unchanged), all 3 other
      bank suites, and Slice 3's own fixture-level tests are byte-identical to before this amendment's work.

## Phase 44 (Slice 3b): Extend the Slice-5 cross-bank guard (amends D-14, depends on Phase 28)

- [ ] 44.1 If Phase 28 (Slice 5's cross-bank overlap spec) has already landed: extend it with one assertion —
      no strategy other than BCI declares `rescateBordeDerecho` on any column, and BCI declares it on `cargo`
      only. If Phase 28 has **not** landed yet when this phase is applied: add the assertion as part of writing
      Phase 28 itself, and cross-reference this task from there — do not create a second, parallel cross-bank
      spec file (DRY). Either order is acceptable; the assertion must exist once both phases have landed.
- [ ] 44.2 Confirm the assertion passes for all 4 strategies today.

## Phase 45 (Slice 3b): Re-verification of the real statement — raised bar (amends D-13, never committed)

- [ ] 45.1 Run the pipeline locally against the real statement (never committed, no exception — the repo is
      PUBLIC). Record only the following four booleans plus the row count in the PR description — never
      amounts, names, account numbers, descriptions or dates:
      1. `saldoAnterior − Σcargo + Σabono === saldoFinal` (catches a dropped row at 1×, a sign inversion at 2×).
      2. **All 106 movement rows parse** — no `EstructuraPdfInvalidaError`, movement count equals 106.
      3. **No row is attributed to the wrong column**, checked mechanically: for every row, the sign of the
         running-balance delta `saldoₙ − saldoₙ₋₁` agrees with the side the amount landed on (`+` ⇒ `abono`,
         `−` ⇒ `cargo`).
      4. The statement's own printed totals reconcile with `Σcargo` / `Σabono`.
      This supersedes Phase 15 as the change's real acceptance gate for the real statement — Phase 15 stays in
      the tasks above as the record of the first (incomplete) run that surfaced this amendment's root cause.

## Phase 46: Amendment verification

- [ ] 46.1 `pnpm api test` — all green, net additions only, baseline ≥2622 (the number recorded at the top of
      this amendment section), no pre-existing expected value removed except the one named rewrite in Phase
      40.1 (the fourth and final allowed rewrite of the `rangosX` `toEqual` pin).
- [ ] 46.2 `pnpm api exec tsc --noEmit`, `pnpm api lint`, `pnpm api openapi:check` — all green (no HTTP-surface
      change in this amendment, so `openapi.json` diff should be empty — confirm, do not assume).
- [ ] 46.3 Confirm via `git diff` that the diff for Phases 39-45 touches only: `token-grouping.ts`,
      `token-grouping.spec.ts` (new or extended), `estructura-pdf-banco.ts`, `pdf-normalization.ts` (the one
      mapping line from Phase 39.5), `bci.strategy.ts`, `bci.strategy.spec.ts`,
      `pdfjs-transaction-normalizer.service.spec.ts`, `generar-bci-cartola-variante-test.ts`,
      `bci-cartola-variante-test.pdf`, and, if not already present, Phase 28's cross-bank spec file.
- [ ] 46.4 PII sweep, repeated: confirm no amount, name, account number, merchant string or literal date from
      the real statement appears in any diff, test name, comment or commit message across Phases 39-45.

---

## Review Workload Forecast

Honest per-slice estimate, re-derived from the actual working tree rather than the proposal's pre-design
guess (hand-authored lines only; regenerated `openapi.json`/`types.gen.ts` excluded). The proposal's own
figure (~1450, ceiling ~1900) already assumed strict TDD's doubling; this recompute is **higher** than the
proposal for Slice 3 specifically, because D-02 turned out to require a *mandatory* new arithmetic invariant
test plus a full multiset+reconciliation test on top of the geometry edit itself — the proposal's ~320
estimate predates that discovery.

| Slice | Scope | Est. changed lines | Notes |
|---|---|---|---|
| 1 | Generator (3 pages, extra SUCURSAL column, split PERIODO, exported balance constants) + fixture self-assertions | ~470 | Comparable generator is 285 lines for 2 pages; this one has 3 pages + 1 extra column + balance bookkeeping. Self-assertion block adds ~90-110 lines to `bci.strategy.spec.ts` |
| 2 | Dash-date regex (1 line) + totals-row anchor (1 line + comment) + docblock updates + unit RED test + regression checkpoint | ~170 | Small production edit; the checkpoint (Phase 5.1) is a test-run, not new code, but the RED unit test itself (Phase 3.1) is ~40-60 lines |
| 3 | `rangosX`/`fecha` band change + PERIODO colon fix + mandatory invariant test + full fixture multiset/reconciliation test + SUCURSAL 3-case test + header-leak guard + `rangosX` toEqual rewrite | ~520 | **Riskiest and largest slice.** The invariant test (Phase 9) and the fixture-level test (Phase 7) are each 80-200 lines; the production edit itself is ~15 lines total |
| 4 | Domain error + pipeline guard + 4 union widenings + 2 mapper branches + 3 merge-blocking route tests + 2 rewritten specs + D-10 commit test + web regression test | ~380 | Roughly matches the proposal's own ~380 — this slice's shape didn't change under design |
| 5 | 3 docblock comment blocks + `CLAUDE.md` + cross-bank invariant spec + issue drafts (prose, not counted in repo diff) | ~200 | Doc-only for the strategies, but the new cross-bank spec (Phase 28) is real test code, ~60-90 lines |
| **Total (pre-amendment)** | | **~1740** | Within the proposal's stated ceiling (~1900), above its point estimate (~1450) — driven entirely by Slice 3's mandatory invariant + reconciliation tests, which the proposal's open design questions had not yet resolved when that estimate was written |

```
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High — Slices 1 and 3 individually exceed 400 changed lines
```

### Forecast delta — AMENDMENT A-01 (Phases 39-46, Slice 3b)

Added 2026-09-10, after Slices 1-3 shipped. Per design.md's "Review Workload impact" (AMENDMENT A-01 section):
two-pass `repartirEnColumnas` + advance table + `anchoEstimado` (~70 production lines), its unit spec (~120),
the `RangoX` field + the one mapping line in `pdf-normalization.ts` + BCI docblock (~30), the extended
invariant test (~70), generator changes + regeneration + new self-assertions (~100), and the second `rangosX`
`toEqual` rewrite. **≈ +390 lines.**

Unlike Slices 1 and 3, this delta is **not** taken as one lump — design.md's own recommended split gives it a
provably inert half, so the two new PRs land inside budget individually and neither needs `size:exception`:

| Sub-slice | Scope | Est. changed lines | Notes |
|---|---|---|---|
| 3a — estimator (Phase 39) | Two-pass `repartirEnColumnas`, `ANCHOS_GLIFO_1000EM`, `anchoEstimado`, the optional `RangoX`/`RangoColumna` field, the `pdf-normalization.ts` mapping fix (Trap 5), `token-grouping.spec.ts` | ~250 | Behavior change is **zero by construction** — no strategy opts in yet. The full 2622-test suite staying green (Phase 39.6/39.7) *is* the proof, not a claim. |
| 3b — BCI opts in (Phases 40-45) | `cargo`'s `rescateBordeDerecho`, extended invariant test, fixture regeneration with sub-1000 amounts + extended self-assertions, the second `toEqual` rewrite, cross-bank guard extension, docblock, re-verification | ~300 | Highest-value revert target for this amendment — restores Slice 3's shipped bands verbatim (rescue is additive-only per AD-03's asymmetry argument). |
| **Amendment total** | | **~550** (vs. ~390 estimated in design.md — the design estimate did not itemize the split's own per-PR overhead; both halves individually clear the 400-line budget) | |

```
Decision needed before apply: No — both 3a and 3b clear the 400-line budget on their own; no size:exception
needed for this amendment (contrast with Slices 1 and 3 above, which do need it)
Chained PRs recommended: Yes (3a before 3b — 3b's opt-in has no effect without 3a's mechanism)
400-line budget risk: Low for this amendment specifically
```

Chain strategy for this session is already cached as `feature-branch-chain` (per the launch brief). Slices map
1:1 onto chained PRs against the tracker branch `feat/api-bci-cartola-variante`, with the amendment inserting
two additional PRs between the original PR 3 and PR 4/5:

| PR | Ships | Verifies | Rollback boundary | Depends on |
|---|---|---|---|---|
| 1 — fixture | Generator + committed PDF + self-assertions | `pnpm api test -- bci.strategy` | Revert removes a test fixture only — zero production impact | tracker branch |
| 2 — dash dates | `parsearFechaFila` regex + totals-row anchor | `pnpm api test` (full, both existing BCI fixtures unchanged) | Revert restores `/`-only parsing; dash statements go back to yielding zero rows (Phase 17's error), not a worse state | PR 1's branch |
| 3 — geometry | `rangosX`/`fecha` band + PERIODO colon fix + invariant test | `pnpm api test` (full, all 4 banks' suites) + Phase 15 manual reconciliation | **Highest-value revert target among 1-3** — restores the 2026-08-30 bands verbatim; existing fixture assertions prove the old layout still parses. Must stay its own commit/PR per design.md, never folded into PR 2 | PR 2's branch |
| **3a — rescue estimator** *(amendment)* | Two-pass `repartirEnColumnas` + glyph table + `anchoEstimado`, no strategy opts in (Phase 39) | `pnpm api test` (full — zero behavior change is what's being verified) | Revert removes an unused mechanism only — zero production impact, since nothing opts in yet | PR 3's branch |
| **3b — BCI opts in** *(amendment)* | `cargo`'s `rescateBordeDerecho`, regenerated fixture with sub-1000 amounts, extended invariant test, re-verification against the real statement (Phases 40-45) | `pnpm api test` (full) + Phase 45's raised-bar manual reconciliation (4 booleans) | **Highest-value revert target in the whole change** — restores Slice 3's shipped bands verbatim; the rescue is additive-only (AD-03), so reverting it only re-narrows coverage, it cannot newly misattribute anything | PR 3a's branch |
| 4 — zero-rows error | Domain error + pipeline guard + 4 unions + 2 mappers + contract + web regression test | `pnpm api test` + `pnpm web test` + `pnpm api openapi:check` | Independently revertible; restores silent-success behavior. **First to revert** if production surprises us (e.g. a legitimately empty month) — it is the only user-visible change to *existing working* uploads | PR 3b's branch |
| 5 — audit | 3 docblock comments + `CLAUDE.md` + cross-bank spec + issues; **plus Phase 44's one-line extension** (no strategy but BCI declares `rescateBordeDerecho`, and only on `cargo`) if PR 3b has landed by the time PR 5 is authored — otherwise Phase 44's assertion ships as a small follow-up commit on PR 5 once PR 3b merges | `pnpm api test` (cross-bank spec + 3 untouched strategy specs) | Revert removes documentation and one guard spec — zero production impact | PR 3b's branch |

Slices 2 → 3 are strictly ordered (Trap 2's anchor lives in 2 but only 3 makes the new fixture parse end to
end). PR 3a → 3b are strictly ordered (3b's opt-in has no effect without 3a's mechanism — Trap 5 is exactly
this failure mode if the two are merged out of order or partially). Slice 4 is independent of the amendment
(design.md AD-04: D-07…D-11 untouched) and may be built off PR 3b's branch in parallel with PR 5, per
`feature-branch-chain`'s "later children target the immediate parent branch" rule (interpreted here as: PR 4
and PR 5 both target PR 3b's branch, since PR 3b is now where the tracker's geometry work is fully settled;
whichever merges to the tracker first, the other retargets). Slice 5 additionally has a soft content
dependency on PR 3b via Phase 44 (see the PR 5 row above) — this does not block PR 5 from being *authored* in
parallel, only from being *complete* before PR 3b exists.

**Decision needed before apply:** Slices 1 and 3 both exceed the 400-line budget on their own and neither
splits cleanly — Slice 1 is almost entirely mechanical generated fixture data (splitting the generator from
its self-assertions would leave an un-provable intermediate state), and Slice 3 is deliberately kept as one
commit/PR by design.md itself ("smallest diff possible, own commit, own revert" — splitting the band change
from its mandatory invariant test would mean merging an unverified band change). Recommend `size:exception`
for both PR 1 and PR 3, following the same pattern the previous change (`ingesta-pdf-password`) used for its
own oversized Slice 1. **The amendment's own PR 3a/3b split needs no such exception** — see the "Forecast
delta" above.
