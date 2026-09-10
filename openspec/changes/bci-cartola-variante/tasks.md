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

- [ ] 1.1 Read `generar-bci-cartola-montos-grandes-test.ts` in full again (already re-verified in this phase —
      raw uncompressed content streams, `BT/Tf/Tm/Tj/ET` per token, Helvetica `/WinAnsiEncoding`, latin1, the
      backward pen-jump spacer at x=599 (`:59-77`)) before writing anything new.
- [ ] 1.2 Write `apps/api/test/fixtures/pdf/generar-bci-cartola-variante-test.ts`, same structure (catalog +
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
- [ ] 1.3 Run `pnpm exec tsx test/fixtures/pdf/generar-bci-cartola-variante-test.ts` (from `apps/api`); commit
      both the generator script and the resulting `bci-cartola-variante-test.pdf` binary (D-12's
      committed-vs-generated-at-test-time tradeoff — same as the existing BCI fixtures).

## Phase 2 (Slice 1): Fixture self-assertions — RED first, no production code (D-12)

- [ ] 2.1 RED: add a new `describe('fixture geometry — bci-cartola-variante-test.pdf (D-12 self-assertions,
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
- [ ] 2.2 GREEN: once Phase 1's generator produces the fixture, this block should already be green — if any
      assertion fails, fix the **generator** (never loosen the assertion) until it passes.
- [ ] 2.3 Run `pnpm api test -- bci.strategy` — confirm the new describe block is green and every pre-existing
      test in the same file is untouched.

---

## Phase 3 (Slice 2): Infrastructure — dash-date parsing, isolated from the band defect (D-04) — Trap 1

**Traces PDF-11** ("every movement row's date parses successfully").

- [ ] 3.1 RED: `apps/api/src/infrastructure/pdf/pdf-normalization.spec.ts` — call `normalizarTransaccionesPdf`
      with a **synthetic single-row token set** (following the file's existing synthetic-token pattern) whose
      date token sits at **x=40** (inside the CURRENT `fecha` band [35, 85), so Trap 1 cannot interfere) with
      value `'22-07-2026'`, `formatoFecha: 'DD/MM/YYYY'`, and a valid cargo or abono token in-band. Assert the
      row is dropped today (0 transactions returned) because the slash-only regex does not match a dash date.
      This is the "unit test on the parser," not a fixture-level test (design.md, "Everything else follows
      from...", ¶2).
- [ ] 3.2 GREEN: widen the `'DD/MM/YYYY'` case in `parsearFechaFila` (`pdf-normalization.ts:81`, verified) from
      `/(\d{2})\/(\d{2})\/(\d{4})/` to `/(\d{2})[/-](\d{2})[/-](\d{4})/` (D-04). Do **not** add a fourth
      `FormatoFechaPdf` member — BCI keeps exactly one structure, one `formatoFecha` (D-01/D-04).
- [ ] 3.3 GREEN: Phase 3.1's test now passes.
- [ ] 3.4 REFACTOR: update the `FormatoFechaPdf` docblock (`estructura-pdf-banco.ts:14-21`, verified) to state
      the `'DD/MM/YYYY'` member denotes the form `DD?MM?YYYY` and that BCI prints both separators across its
      two layouts.

## Phase 4 (Slice 2): Confirm the existing pins stay untouched

- [ ] 4.1 Run `pnpm api test -- bci.strategy` — confirm `formatoFecha` pin (`bci.strategy.spec.ts:67`, verified)
      still reads `'DD/MM/YYYY'` and is unmodified; confirm the `xMin < xMax` pin (`:71-75`) is unmodified.
      **No `rangosX` change happens in this slice** — that is Phase 12's job, not this one.

## Phase 5 (Slice 2): Infrastructure — the mandatory same-slice checkpoint (D-05) — Trap 2

- [ ] 5.1 **Checkpoint, do not skip.** Run `pnpm api test -- pdfjs-transaction-normalizer` immediately after
      Phase 3 lands. Confirm it is now RED: the existing `bci-cartola-montos-grandes-test.pdf` fixture's
      8-movement assertion (`pdfjs-transaction-normalizer.service.spec.ts:342-435`) fails with
      `EstructuraPdfInvalidaError`, because the totals-value row (`generar-...ts:220`, `'01-05-2026 al
      31-05-2026'` at x=45.0) now parses a date and carries both a cargo (`386.0`) and an abono (`461.0`)
      token. Record the exact failure (problema tipo + message) before proceeding — this is what proves the
      anchor below is necessary, not speculative.
- [ ] 5.2 RED confirmed above; GREEN: add the `filasIgnoradas` anchor to `bci.strategy.ts` (after the existing
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
- [ ] 5.3 Re-run `pnpm api test -- pdfjs-transaction-normalizer` — confirm both existing BCI fixtures
      (`bci-cartola-test.pdf` → **18** movements, `bci-cartola-montos-grandes-test.pdf` → **8** movements,
      verified at `:212-339` and `:342-435`) are green again with their **unchanged** documented counts. This
      IS Slice 2's real acceptance bar, per design.md D-05 — not "the new fixture's dates parse."

## Phase 6 (Slice 2): Verification

- [ ] 6.1 `pnpm api test`, `pnpm api exec tsc --noEmit` — all green. Confirm the diff for this slice touches
      only: `pdf-normalization.ts`, `pdf-normalization.spec.ts`, `estructura-pdf-banco.ts` (comment-only),
      `bci.strategy.ts` (one new `filasIgnoradas` entry + comment).
- [ ] 6.2 Confirm the 3 non-BCI bank suites and every other pre-existing BCI test are byte-identical in
      expectation (no other rewritten value in this slice).

---

## Phase 7 (Slice 3): Infrastructure — column geometry, the riskiest slice (D-01/D-02/D-03) — RED first

**Traces PDF-11** (correct `cargo`/`abono` column assignment per layout) **and PDF-03**'s new fixture row.

- [ ] 7.1 RED: add a new describe block to `pdfjs-transaction-normalizer.service.spec.ts` for
      `bci-cartola-variante-test.pdf` asserting: (i) the exact movement count Phase 1's generator produces,
      (ii) the exact `{fecha, descripcion, cargo, abono}` multiset, (iii) `Σcargo` and `Σabono` as `BigInt`
      against the generator's exported `TOTAL_CARGOS`/`TOTAL_ABONOS` constants, (iv) the reconciliation
      identity `SALDO_ANTERIOR − Σcargo + Σabono === SALDO_FINAL` (D-13 — the only assertion that catches
      both a dropped row and a sign inversion). Confirm RED against the current (pre-Phase-8) `rangosX` — the
      new variant's date tokens are still out of band (Trap 1), so this must fail with far fewer than the
      expected movement count.

## Phase 8 (Slice 3): Infrastructure — the band change itself (D-02/D-03)

- [ ] 8.1 GREEN: update `rangosX` in `bci.strategy.ts` (`:124-134`, verified) to the D-02/D-03 decided values:
      ```ts
      rangosX: [
        { col: 'fecha',       xMin:  30, xMax:  85 },   // 35 → 30 (D-03)
        { col: 'descripcion', xMin: 130, xMax: 320 },   // 145 → 130 (D-02)
        { col: 'cargo',       xMin: 360, xMax: 440 },   // 430 → 440 (D-02)
        { col: 'abono',       xMin: 450, xMax: 515 },   // 435 → 450, 500 → 515 (D-02)
      ],
      ```
      `cargo.xMin` stays **360** unchanged — no measurement asks for a change there (D-02, KISS).
- [ ] 8.2 GREEN: Phase 7.1's test should now pass or come close — do not force it green by touching the test;
      if it is still red, the geometry table above is transcribed wrong, not the test.

## Phase 9 (Slice 3): Infrastructure — the mandatory invariant test (D-02)

- [ ] 9.1 RED+GREEN: add a new strategy-level spec (new describe block in `bci.strategy.spec.ts`, or a
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

- [ ] 10.1 RED+GREEN: a row whose `fecha` column text reads `"22-07-2026  SUCURSAL-NAME"` (date + SUCURSAL
      token both landing in the widened `fecha` band) still parses the date correctly (the unanchored regex
      from Phase 3 handles this — same pattern Santander already relies on, `santander.strategy.ts:82`,
      verified precedent cited in design D-03).
- [ ] 10.2 RED+GREEN: a row containing only a SUCURSAL-shaped token (no date, no amounts) never produces a
      movement on its own.
- [ ] 10.3 RED+GREEN: V1's SUCURSAL token (x ≈ 99) remains unassigned after the band change — it must fall in
      the `[85, 130)` gap between the new `fecha.xMax=85` and `descripcion.xMin=130`, not inside either
      column.
- [ ] 10.4 Explicitly do **not** add a 5th `ColumnaPdf` member for `sucursal` (YAGNI, D-03 "Rejected: a fifth
      `ColumnaPdf` member") and do **not** narrow `fecha.xMax` below 85 to try to exclude SUCURSAL (D-03
      "Rejected: narrowing `fecha.xMax`").

## Phase 11 (Slice 3): Infrastructure — PERIODO anchor colon tolerance (D-06)

- [ ] 11.1 RED: `bci.strategy.spec.ts` — a new scenario matching `PERIODO : 01-04-2026 al 30-04-2026` (colon
      variant, the fixture's own shape from Phase 1) against `anclasPeriodo.desde`/`.hasta` returns
      `undefined` today (the existing no-colon-only pattern does not tolerate a colon).
- [ ] 11.2 GREEN: widen both anchors (`bci.strategy.ts:120-123`, verified) with the colon-tolerant shape,
      copied verbatim from the in-repo Banco de Chile precedent (`banco-chile.strategy.ts:91-92`):
      ```ts
      desde: /PERIODO\s*:?\s*(\d{2}-\d{2}-\d{4})/,
      hasta: /PERIODO\s*:?\s*\d{2}-\d{2}-\d{4}\s+al\s+(\d{2}-\d{2}-\d{4})/,
      ```
- [ ] 11.3 Confirm the existing no-colon pin (`bci.strategy.spec.ts:103-111`, verified — `'PERIODO
      01-04-2026 al 30-04-2026'`) is still green, unmodified.
- [ ] 11.4 Explicitly do **not** touch BCI's `fuenteAnio.kind === 'explicito'` exemption from
      `RangoFechasInvalidoError` (`bci.strategy.ts:137`; exemption logic in
      `pdf-structure-extraction.ts:117-129`, verified) — a missing period anchor stays non-fatal for BCI
      (D-06 part 2, deliberate).

## Phase 12 (Slice 3): Infrastructure — rewrite the ONE allowed pre-existing pin (D-01 tripwire 1)

- [ ] 12.1 GREEN: update `bci.strategy.spec.ts:82-87`'s `rangosX` `toEqual` (verified) to the new D-02/D-03
      values, with a comment citing D-02's table as the justification — this is explicitly the one
      pre-existing expectation this whole change is allowed to rewrite, and only together with a written
      justification (design.md D-01 tripwire 1). Do not touch this test anywhere else in this change.

## Phase 13 (Slice 3): Infrastructure — header-row leak guard (D-12 hazard)

- [ ] 13.1 RED-or-confirm-inert: assert no table-header fragment (`FECHA`, `SUCURSAL`, `DESCRIPCION`,
      `CHEQUES`, `DEPOSITOS`, `SALDO DIARIO`) appears in any normalized description for the new fixture. If
      this is already green (design's analysis says it likely is — non-parseable date + non-empty `cargo`
      blocks fusion), **do not add a speculative `filasIgnoradas` anchor** (YAGNI) — keep the test as a
      permanent regression guard. If it is RED, add the minimal anchor needed and document why, same style as
      Phase 5.2.

## Phase 14 (Slice 3): Infrastructure — close the loop, verify no regression

- [ ] 14.1 Re-run Phase 7.1's fixture-level test — full expected movement set, correct `cargo`/`abono` sides,
      reconciliation identity all green.
- [ ] 14.2 Run the full `pnpm api test` suite — confirm BOTH existing BCI fixtures (18 / 8 movements,
      unchanged) and all 3 other bank suites (BancoEstado, Banco de Chile, Santander) are byte-identical to
      before this slice.
- [ ] 14.3 REFACTOR: update the `bci.strategy.ts` docblock (`:19-88`, verified) with the D-02/D-03/D-06
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
| **Total** | | **~1740** | Within the proposal's stated ceiling (~1900), above its point estimate (~1450) — driven entirely by Slice 3's mandatory invariant + reconciliation tests, which the proposal's open design questions had not yet resolved when that estimate was written |

```
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High — Slices 1 and 3 individually exceed 400 changed lines
```

Chain strategy for this session is already cached as `feature-branch-chain` (per the launch brief). Slices map
1:1 onto 5 chained PRs against the tracker branch `feat/api-bci-cartola-variante`:

| PR | Ships | Verifies | Rollback boundary | Depends on |
|---|---|---|---|---|
| 1 — fixture | Generator + committed PDF + self-assertions | `pnpm api test -- bci.strategy` | Revert removes a test fixture only — zero production impact | tracker branch |
| 2 — dash dates | `parsearFechaFila` regex + totals-row anchor | `pnpm api test` (full, both existing BCI fixtures unchanged) | Revert restores `/`-only parsing; dash statements go back to yielding zero rows (Phase 17's error), not a worse state | PR 1's branch |
| 3 — geometry | `rangosX`/`fecha` band + PERIODO colon fix + invariant test | `pnpm api test` (full, all 4 banks' suites) + Phase 15 manual reconciliation | **Highest-value revert target** — restores the 2026-08-30 bands verbatim; existing fixture assertions prove the old layout still parses. Must stay its own commit/PR per design.md, never folded into PR 2 | PR 2's branch |
| 4 — zero-rows error | Domain error + pipeline guard + 4 unions + 2 mappers + contract + web regression test | `pnpm api test` + `pnpm web test` + `pnpm api openapi:check` | Independently revertible; restores silent-success behavior. **First to revert** if production surprises us (e.g. a legitimately empty month) — it is the only user-visible change to *existing working* uploads | PR 3's branch |
| 5 — audit | 3 docblock comments + `CLAUDE.md` + cross-bank spec + issues | `pnpm api test` (cross-bank spec + 3 untouched strategy specs) | Revert removes documentation and one guard spec — zero production impact | PR 3's branch (independent of PR 4) |

Slices 2 → 3 are strictly ordered (Trap 2's anchor lives in 2 but only 3 makes the new fixture parse end to
end). Slices 4 and 5 are independent of the BCI fixes and of each other — both may be built off PR 3's branch
in parallel once it merges into the tracker, per `feature-branch-chain`'s "later children target the immediate
parent branch" rule (interpreted here as: PR 4 and PR 5 both target PR 3's branch, since PR 3 is where the two
diverge; whichever merges to the tracker first, the other retargets).

**Decision needed before apply:** Slices 1 and 3 both exceed the 400-line budget on their own and neither
splits cleanly — Slice 1 is almost entirely mechanical generated fixture data (splitting the generator from
its self-assertions would leave an un-provable intermediate state), and Slice 3 is deliberately kept as one
commit/PR by design.md itself ("smallest diff possible, own commit, own revert" — splitting the band change
from its mandatory invariant test would mean merging an unverified band change). Recommend `size:exception`
for both PR 1 and PR 3, following the same pattern the previous change (`ingesta-pdf-password`) used for its
own oversized Slice 1.
