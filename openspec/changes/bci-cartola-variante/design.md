# Design: bci-cartola-variante — one BCI geometry for two layouts, and no more silent empty ingestions

> SDD design artifact. Hybrid store — mirror of Engram topic `sdd/bci-cartola-variante/design`.
> Reads `openspec/changes/bci-cartola-variante/proposal.md`. This is the HOW at architectural level.
> `specs/` is written in parallel by `sdd-spec` — not touched here.
> Every line number below was read against the working tree (`/Users/jorge/dev/MoneyDiary.wt/debug-bci`,
> branch `feat/api-bci-cartola-variante`) before being written.
>
> **PII boundary (inherited, binding).** Only non-identifying page geometry crosses over from the user's real
> statement. No amount, name, account number, merchant or date from that file appears here or in any fixture.

## Technical approach

Four defects, one of them not named by the proposal, plus one structural gap.

| # | Defect | Where | Silent? |
|---|---|---|---|
| 1 | Row dates use `-`, the strategy declares `/` | `bci.strategy.ts:136` + `pdf-normalization.ts:80-88` | yes |
| 2 | **The date token is out of the `fecha` band**: measured min = p50 = **33.6**, band starts at **35** (`t.x >= xMin`, `token-grouping.ts:112`) | `bci.strategy.ts:125` | yes |
| 3 | `descripcion` starts at 134.8, band floor 145; amounts land in the `cargo`/`abono` dead zone | `bci.strategy.ts:126,132-133` | yes |
| 4 | The `PERIODO` anchor cannot match `PERIODO : …` | `bci.strategy.ts:120-123` | yes |
| 5 | Zero normalized rows is reported as success — **in both the PDF and the Excel branch** | `ejecutar-pipeline-ingesta.use-case.ts:184-197`; `excel-transaction-normalizer.service.ts:222-226` | yes |

**Defect 2 is new and it changes the plan.** The proposal's measurement table marks `fecha` as "OK". It is not:
`repartirEnColumnas` filters with `t.x >= rango.xMin` (`token-grouping.ts:112`, `xMin` inclusive / `xMax`
exclusive, `:108-110`), and `33.6 >= 35` is false. The majority of this variant's date tokens are therefore
**unassigned**, so `fila.columnas.fecha` is the empty string and `parsearFechaFila('')` returns `null`
whatever separator we teach it. Consequence for slicing: **the date-format fix alone cannot turn any row
green.** Slice 2's RED test must be a unit test on `parsearFechaFila` and on the strategy's own declaration;
only slice 3 can assert end-to-end movements. Writing slice 2's RED against the fixture's movement set would
produce a test that stays red through a correct slice-2 implementation.

Everything else follows from one decision (D-01) and one arithmetic table (D-02).

---

## D-01 — One widened band set for BCI, not two variant band sets, not runtime variant detection

**Decision.** BCI keeps exactly **one** `EstructuraPdfBanco`. Its `rangosX` is recalibrated to cover both
published layouts. No `variante` dimension is added to the strategy model, no `getEstructura(tokens)`
signature change, no header-derived geometry.

**Why the alternatives are worse, concretely.**

*Per-variant band sets (proposal option b).* `getEstructura()` is a zero-argument method consumed through
**two independent** `Map<BancoConocido, EstructuraPdfBanco>` built in **two constructors** —
`pdfjs-structure-validator.service.ts:28,37-40,55` and `pdfjs-transaction-normalizer.service.ts:36,45-50,63`.
A per-variant structure has to be *selected*, and selection needs tokens, which are not available at map
construction time. So option (b) means: a new selection concept, threaded through two services that must
choose the **same** variant for the same file, or `EstructuraPdfValidada.rangosX`
(`pdf-structure-extraction.ts:144`) describes one geometry while the normalizer parses with another. That is
two chances to disagree about *which column a peso belongs to* — a DRY violation on the single most
money-critical fact in the module. YAGNI's own sanctioned exception (`yagni` rule 4, "plugin systems with a
single plugin") is calibrated at *four* real bank implementations from day one; two layouts of one bank is
explicitly the claim the proposal already refused to grant.

*Header-derived bands (proposal option c).* Escalates to an ADR by the proposal's own dependency clause,
changes parsing for all four banks, and — decisive — is *unfalsifiable against the only evidence we have*:
we hold 2 deposit samples for this variant. Deriving band edges from header X positions replaces a number we
can audit in a diff with a number computed at runtime from a document we cannot see. That is a worse position
for ADR-015, not a better one.

*Runtime variant detection inside one strategy.* Same objection as (b) minus the type churn: it introduces a
branch whose wrong outcome is a sign inversion, and the branch signal (`SUCURSAL` header presence, header X
positions) is itself unpinned data from the same unseen documents.

**SOLID, honestly.** OCP says extend without modifying what works. Here the *thing that works* is a set of
four numbers whose only justification is measurement, and we have new measurements for the same bank. Editing
a calibrated constant with new data for the same bank is not an OCP violation — it is what calibration means.
An OCP violation would be a `switch (variante)` growing inside the shared normalizer core, which is precisely
what (b) and (c) introduce and this decision does not.

**How the existing variant is guaranteed, not hoped.** Three tripwires, in order of how loudly they fire:

1. `bci.strategy.spec.ts:77-88` asserts `rangosX` with an exact `toEqual` on the full array. It fails on the
   first commit of slice 3. It is **the one pre-existing expectation this change is allowed to rewrite**,
   because it *is* the declaration of the numbers — and only together with D-02's table written into the
   test's own comment.
2. The end-to-end fixture assertions in `pdfjs-transaction-normalizer.service.spec.ts` — **18** movements for
   `bci-cartola-test.pdf` (`:212-339`) and **8** for `bci-cartola-montos-grandes-test.pdf` (`:342-435`), with
   exact amounts (`11200000n`, `310550n`), the discarded $0 row, the reconstructed multiline cluster and the
   "no description contains a header fragment" guards. **These values may not change.** If a geometry edit
   moves them, the edit is wrong.
3. A **new** arithmetic invariant test (D-02) that encodes every measured cluster as an executable assertion,
   so the numbers cannot be nudged later by anyone who has not re-measured.

## D-02 — The numbers, and why no configuration here can read a charge as a deposit

**Measured input.** Existing variant (V1), aggregate of 15 real statements, `bci.strategy.ts:37-43`; new
variant (V2), the statement measured for this change, split per column by balance delta.

| Cluster | V1 | V2 |
|---|---|---|
| fecha | 42.9 – 44.1 | 33.6 – 44.5 |
| SUCURSAL | ≈ 99 | 75.7 – 83.4 |
| descripcion | ≥ 145 (pinned incl. N° DOCUMENTO overflow ≤ 317.8) | 134.8 – 220.7 |
| **cargo** | **381.1 – 409.7** | **420.9 – 434.1** (71 samples) |
| **abono** | **455.3 – 476.6** | **484.4 – 486.6** (**2 samples**) |
| saldo | 542.2 – 561.9 | 555.9 – 570.6 |

**Decision.**

```ts
rangosX: [
  { col: 'fecha',       xMin:  30, xMax:  85 },   // 35 → 30
  { col: 'descripcion', xMin: 130, xMax: 320 },   // 145 → 130
  { col: 'cargo',       xMin: 360, xMax: 440 },   // 430 → 440
  { col: 'abono',       xMin: 450, xMax: 515 },   // 435 → 450, 500 → 515
]
```

**The separation argument (this is the money argument; read it as the answer to the proposal's headline
risk).** Amounts are right-aligned, so a token's *start* x moves **left** as the amount gets wider. Union
cargo evidence spans 381.1 – 434.1; union abono evidence spans 455.3 – 486.6. The interval **(434.1, 455.3)
contains no observed amount of either kind, in either variant** — 21.2 pt of measured emptiness. The proposal
feared a union band would invert signs; that fear was correct on the combined 420.9 – 486.6 range it had, and
it dissolves once the range is split per column. Zero measured charges fall in any abono band considered here.

Placement inside that 21.2 pt window is not arbitrary. Let `d₁ = abono.xMin − 434.1` (how far a charge must
drift right before it is read as a deposit) and `d₂ = 455.3 − cargo.xMax` (how far a deposit must drift left
before it is read as a charge). Both are maximised by pushing the two edges apart, i.e. **by making the dead
zone as wide as the coverage requirement allows**. Chosen: `cargo.xMax = 440`, `abono.xMin = 450`, giving
**d₁ = 15.9 pt** and **d₂ = 15.3 pt** — roughly three digit-widths at 9 pt Helvetica (≈ 5 pt/digit) in each
direction — with a **10 pt dead zone [440, 450)** left deliberately empty.

**The dead zone is a safety feature, not the bug.** The proposal reads the current 430–435 gap as a defect
because 36 of 57 chained charges fall in it. The gap is not the defect; its *position* is. A token in a dead
zone is unassigned, and an unassigned amount fails **loudly**: either `TokenSinAsignarSospechoso`
(`pdf-normalization.ts:249-256`, when the orphan token matches `REGEX_POSIBLE_MONTO`, `:48`) or, if it does
not match, both columns come up empty and `Transaccion.crear` rejects the row with SIN_MONTOS
(`:342-354`) — in both cases the **whole statement** is rejected with an error. A token in the *wrong* band
fails **silently**, with a peso on the wrong side. Given ADR-015, we buy loudness with coverage, not the
reverse. Consequence to state plainly: an amount narrower than anything ever observed for its variant will be
**rejected, not misread**.

**Per-edge justification.**

- `cargo.xMax 430 → 440`. Covers V2's narrowest observed charge (start 434.1) with 5.9 pt (≈ 1 digit) of
  headroom, and stays 15.3 pt below V1's widest observed deposit.
- `abono.xMin 435 → 450`. 15.9 pt above V2's narrowest observed charge; 5.3 pt (≈ 1 digit) below V1's widest
  observed deposit. Thin on the V1 side by construction — a deposit wider than any in 15 real statements
  lands in the dead zone and fails loudly.
- `abono.xMax 500 → 515`. **This edge exists only because the V2 deposit band rests on two samples.** At 500
  a V2 deposit only 2.7 digits narrower than the two observed escapes the band; at 515 the margin is 5.7
  digits. The ceiling is bounded above by two independent facts: V2's `SALDO DIARIO` **header** sits at
  **521.2**, and V1's narrowest observed saldo **value** at **542.2**. 515 clears both. Raising it further is
  refused: a saldo captured into `abono` on a row whose real amount landed in a dead zone would produce a
  **phantom deposit equal to the running balance** — the single worst silent outcome available in this file.
- `cargo.xMin` **unchanged at 360**. V1's widest observed charge starts at 381.1 and `descripcion.xMax` is
  320 (which deliberately swallows the N° DOCUMENTO overflow, pinned by the original fixture,
  `bci.strategy.ts:43-46`). Nothing in the new evidence asks for a change. KISS: do not move an edge for
  which there is no measurement.
- `descripcion.xMin 145 → 130`. Covers V2's 134.8 with 4.8 pt. Safe on the left: V2's `SUCURSAL` tops out at
  83.4 and V1's sits at ≈ 99, both left-aligned (stable start x), so 130 keeps 31 pt of clearance from V1's.

**The invariant test (new, mandatory).** A strategy-level spec that asserts, as arithmetic rather than prose,
for the six clusters above: every V1 and V2 cargo sample is inside `cargo` and outside `abono`; every V1 and
V2 abono sample is inside `abono` and outside `cargo`; every saldo sample is outside both; `cargo.xMax <
abono.xMin`; `abono.xMax < 521.2`. This is what makes D-02 auditable in a diff by someone who was not here.

## D-03 — `fecha` band drops to 30; `SUCURSAL` stays deliberately unmodelled

**Decision.** `fecha.xMin 35 → 30`; `fecha.xMax` unchanged at 85; **`SUCURSAL` is not modelled as a column**
and is allowed to share the `fecha` column with the date token.

**Why 30 and not 28.** 30 covers 33.6 with 3.6 pt while leaving the two x≈28 tokens of the existing fixture
(the browser footer URL and `MONTO LINEA DE SOBREGIRO:`, `generar-bci-cartola-montos-grandes-test.ts:100,129`)
exactly where they are today — unassigned. Smallest blast radius that fixes the defect. Dates are
left-aligned, so their start x is essentially constant per layout (V2's min *is* its p50, 33.6, across 106
rows); 3.6 pt is adequate for a left-aligned column and 2 pt would not be.

**Why SUCURSAL rides in `fecha`.** In V2, `SUCURSAL` (75.7 – 83.4) is inside `fecha` [30, 85), so the joined
column text reads `"22-07-2026 SUCURSAL-NAME"` (tokens are concatenated in ascending x,
`token-grouping.ts:111-118`, so the date always comes first). `parsearFechaFila`'s regex is **deliberately
unanchored** (`pdf-normalization.ts:52-58`) for exactly this situation — Santander already fuses date and
branch into one token and its `fecha` band is deliberately wide (`santander.strategy.ts:82`, 25–90). This is
an existing, tested pattern, not a new hazard.

**Rejected: narrowing `fecha.xMax` to ~70 to exclude SUCURSAL.** It would work against today's numbers (V1
SUCURSAL ≈ 99, V2 ≤ 83.4) and it is a false promise: V2's SUCURSAL spans 7.7 pt, so we do not actually know
its left edge across statements, and a partial exclusion is worse than a documented inclusion. It would also
be a *second* unmeasured edge change in the same commit.

**Rejected: a fifth `ColumnaPdf` member.** `ColumnaPdf` (`estructura-pdf-banco.ts:4`) is the canonical schema
that `ProblemaEstructuraPdf.columna` and every strategy depend on. Adding `sucursal` ripples into four
strategies and the error taxonomy to model a field nothing consumes. YAGNI.

**Required tests.** (a) a row whose `fecha` column is `"DD-MM-YYYY  SUCURSAL-NAME"` parses the date;
(b) a SUCURSAL token never produces a movement on its own; (c) V1's SUCURSAL at ≈ 99 remains unassigned
(it sits in the [85, 130) gap and must stay there).

## D-04 — One date parser that accepts both separators; no new `FormatoFechaPdf` member

**Decision.** Widen the existing `'DD/MM/YYYY'` case regex from `/(\d{2})\/(\d{2})\/(\d{4})/` to
`/(\d{2})[/-](\d{2})[/-](\d{4})/` (`pdf-normalization.ts:81`). The union
`FormatoFechaPdf = 'DD/Mmm' | 'DD/MM' | 'DD/MM/YYYY'` (`estructura-pdf-banco.ts:22`) keeps three members;
`BciPdfStrategy.formatoFecha` stays `'DD/MM/YYYY'` (`bci.strategy.ts:136`, and its pin at
`bci.strategy.spec.ts:66-69` stays green untouched). The union's docblock (`estructura-pdf-banco.ts:14-21`)
is updated to state that this member denotes the *form* `DD?MM?YYYY` and that BCI prints both separators
across its two layouts.

**Why a fourth union member is not merely unnecessary but wrong.** Under D-01 BCI has **one** structure and
therefore **one** `formatoFecha`. A `'DD-MM-YYYY'` member would force BCI to pick a separator it does not
have — the same bank prints `/` in one layout and `-` in the other. The proposal's "extend the closed union,
the exhaustive `switch` is the safety net" reasoning (`pdf-normalization.ts:71-98`, no `default`) is sound
machinery pointed at the wrong question: nothing here is a new *kind* of date.

**Precedent, one file away.** `periodoAIso` already splits on `/[/-]/` (`pdf-structure-extraction.ts:62-65`)
with the comment "los únicos dos separadores que usan los 4 bancos". The knowledge *"a Chilean bank date
part-separator may be `/` or `-`"* already exists in this module with exactly this treatment; DRY says give it
one treatment, not two.

**Blast radius: zero outside BCI.** `'DD/MM/YYYY'` is used by BCI alone — BancoEstado is `'DD/Mmm'`
(`banco-estado.strategy.ts:72`), Banco de Chile `'DD/MM'` (`banco-chile.strategy.ts:101`), Santander
`'DD/MM'` (`santander.strategy.ts:88`). The `'DD/MM'` case is **not** widened (YAGNI: no observed bank prints
`DD-MM` without a year).

**Rejected: per-variant date format.** Requires D-01(b). Rejected there.
**Rejected: renaming the member** (e.g. to `'DDsMMsYYYY'`). Touches four strategies, their specs and the
parity specs for zero behavioural gain; the docblock is already this repo's authoritative definition of what
each member means.

## D-05 — Accepting dash dates breaks the existing fixture unless the totals row is anchored out (verified)

**This is the highest-risk interaction in the change and it is not in the proposal.**

`generar-bci-cartola-montos-grandes-test.ts:220-227` emits the totals *value* row of page 3:

```
x= 45.0  "01-05-2026 al 31-05-2026"   x=296.0 "15.000.000"   x=355.3 "-"
x=386.0  "11.654.280"                 x=431.7 "+"            x=461.0 "1.895.320"
x=510.0  "="                          x=538.0 "5.241.040"
```

Today that row is inert for two independent reasons: x=45.0 is in the `fecha` band but
`parsearFechaFila('01-05-2026 al 31-05-2026', 'DD/MM/YYYY')` finds no slashes, and its non-empty `cargo`
column blocks continuation fusion (`pdf-normalization.ts:229-245`). **The moment D-04 lands, that row parses
a date** and becomes a candidate carrying both a cargo and an abono — `Transaccion.crear` rejects it and the
whole fixture fails with `EstructuraPdfInvalidaError`. The existing `filasIgnoradas` entry
`/^Periodo\s+Saldo Anterior\s*$/` (`bci.strategy.ts:170`) guards the *label* row above it, not this one.

**Decision.** Slice 2 adds one `filasIgnoradas` anchor, in the exact-anchor style the file already uses
(`bci.strategy.ts:144,153,170`):

```ts
// Fila de VALORES de la sección de totales: su columna `fecha` trae el
// RANGO del período ("DD-MM-YYYY al DD-MM-YYYY"), no una fecha de
// movimiento. Inerte hasta que el parser aceptó el separador "-" (D-04);
// desde entonces parsea como fila fechada y, al traer cargo Y abono,
// tumbaría la cartola completa. Ancla exacta: ninguna fila de movimiento
// real trae dos fechas completas separadas por " al " en esa columna.
/^\d{2}[/-]\d{2}[/-]\d{4}\s+al\s+\d{2}[/-]\d{2}[/-]\d{4}\b/,
```

`filasIgnoradas` is tested against `Object.values(fila.columnas).join(' ')` (`pdf-normalization.ts:198`) and
column insertion order follows `rangosX` (fecha first), so `^` is correct.

**Slice-2 acceptance is therefore not "the new fixture's dates parse" but "both existing BCI fixtures still
normalize to their unchanged documented counts after the parser accepts `-`".** `bci-cartola-test.pdf` is a
compressed-stream fixture whose contents cannot be inspected statically; the same test covers it.

## D-06 — The `PERIODO` anchor is fixed; BCI's period-optional exemption is kept

**Decision, part 1 — fix the regex.** Both anchors gain the colon tolerance
(`bci.strategy.ts:120-123`):

```ts
desde: /PERIODO\s*:?\s*(\d{2}-\d{2}-\d{4})/,
hasta: /PERIODO\s*:?\s*\d{2}-\d{2}-\d{4}\s+al\s+(\d{2}-\d{2}-\d{4})/,
```

Both must change: `extraerPeriodo` returns `undefined` unless **both** match
(`pdf-structure-extraction.ts:51-54`). The `\s*:?\s*` shape is copied verbatim from Banco de Chile
(`banco-chile.strategy.ts:91-92`) — an in-repo precedent, not an invention. `bci.strategy.spec.ts:103-111`
(the V1 anchor, no colon) stays green.

**Decision, part 2 — a missing period stays non-fatal for BCI.** `fuenteAnio: {kind:'explicito'}`
(`bci.strategy.ts:137`) exempts BCI from `RangoFechasInvalidoError` (`pdf-structure-extraction.ts:117-129`),
and `resolverAnios` takes the year from each row (`pdf-normalization.ts:454-458`). Reversing the exemption
would make **any** BCI layout whose period anchor we have not yet seen fail wholesale — trading a harmless
`undefined` for a hard rejection, which is the exact opposite of what this change exists to do. ADR-015
concentrates risk on money and access; a missing period cannot mis-state a peso.

**The tripwire is a test, not an error.** The right instrument for a metadata field is an assertion, not a
rejection: the fixture spec asserts `evaluarEstructura(...).getValue().periodo` equals the expected
`{desde, hasta}` ISO pair for the new fixture *and* for the existing one. A regex that stops matching then
fails a named test instead of silently yielding `undefined`. **Trigger recorded** (`yagni`, the 11.6 idiom):
the first consumer that reads BCI's `periodo` re-opens the exemption.

## D-07 — The zero-rows check lives in `EjecutarPipelineIngestaUseCase`, and it changes `.xlsx` too — deliberately

**Decision.** One guard, in the application layer, immediately after the normalize stage and before the
existing debug log (`ejecutar-pipeline-ingesta.use-case.ts:184-190`):

```ts
if (transacciones.length === 0) {
  return Result.fail(new SinMovimientosError(archivo.originalName, banco.banco));
}
```

**Why not the PDF normalizer core.** Two pre-existing tests pin `Result.ok([])` **as correct** at that level
and would have to be rewritten:
`pdf-normalization.spec.ts:678-699` ("una cartola BCI cuyas filas fechadas son TODAS '0' literal se importa
vacía (`Result.ok([])`), sin error estructural") and `normalize-transactions.use-case.spec.ts:68-85`. The
proposal forbids rewriting pre-existing expectations. They are also *right*: "this page produced no rows" is
a legitimate outcome of a pure geometric function; "this ingestion produced no movements" is a product rule.
Different layers, different knowledge — SRP.

**Why not per-caller.** Three callers (`ProcessIngesta`, `PreviewIngesta`, `CommitIngesta`) → the same rule in
three places, and a fourth caller added later inherits the silence. Straight DRY violation.

**The Excel branch changes too, and that is the point.** Verified, not assumed:
`excel-transaction-normalizer.service.ts:222-226` returns `Result.ok(transacciones)` with **no** zero-row
guard, so `.xlsx` has the identical silent-success hole. The knowledge — *a detected, structurally valid
statement that yields no movements is not a successful ingestion* — is **one** piece of knowledge. Splitting
it by file format would be the DRY failure the proposal's own risk table warns about, in the other direction.

**Blast radius, named and small (grepped, not estimated).** Exactly **two** pre-existing tests encode the
behaviour being reversed, both on the Excel branch:

| Suite | Test | Fate |
|---|---|---|
| `process-ingesta.use-case.spec.ts:673-676` | *"lista de transacciones vacía: persiste con total 0 y retorna ok, sin registrar FALLIDA"* | **rewritten** — now expects `Result.fail(SinMovimientosError)` |
| `preview-ingesta.use-case.spec.ts:480-482` | *"archivo con 0 filas de datos: retorna ok con totalFilas:0 y filas:[] (200 legítimo)"* | **rewritten** — now expects a 400 |

Every other fake normalizer in the application specs returns a non-empty `TXS` by default
(`process-ingesta.use-case.spec.ts:129-140,185-195`, `ejecutar-pipeline-ingesta.use-case.spec.ts:162-188`,
`commit-ingesta.use-case.spec.ts:206-219`, `preview-ingesta.use-case.spec.ts:123-134,195-206`), so nothing
else flips. These two rewrites are **the change's own new specification**, not pre-existing values being
adjusted to make a test pass — a reviewer must be able to tell those apart, which is why they are listed here
by name and line.

**Also affected, by construction:** `ingesta.routes.spec.ts`, `app.ingesta.spec.ts` (new status/code cases),
and `apps/web` (`client.test.ts`, `SubirCartola.test.tsx`). `pnpm api test` + `pnpm web test` is the gate.

## D-08 — `SinMovimientosError`: one error, one message, 400 + `SIN_MOVIMIENTOS`

**Decision.** `apps/api/src/domain/errors/sin-movimientos.error.ts`, shaped like `pdf-invalido.error.ts` and
`pdf-sin-texto.error.ts`:

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

`PdfSinTextoError`'s own docblock already names this failure mode — *"la forma controlada de rechazar ese
caso en vez de fallar silenciosamente con cero movimientos"* (`pdf-sin-texto.error.ts:5-7`). This error
finishes the sentence that file started.

**One message, not two (proposal question 4).** We **cannot distinguish** "we could not read it" from "the
month was empty" — that missing information is the whole problem. Two messages, or two `code`s, would be a
lie the client would branch on. One message names both possibilities, leads with the one that is our fault,
and does not accuse the user's file. The **wording is the entire product surface of this change**.

**Status 400, `code: 'SIN_MOVIMIENTOS'`.** Every client-file validation error in both mappers is already 400
(`ingesta.routes.ts:419-433`, `:471-483`) and `ErrorTraducido.code` is the established machine-readable
channel (`responder-error-traducido.ts:11-20,51-55`). 422 is rejected: it would be a new pattern for one
error, and on the web side 400 is what maps to `ApiError.tag === 'invalid'`, which is in
`TAGS_ERROR_PERMANENTE` — a 422 risks being auto-retried by the retry policy, which for an error that no
retry can fix is exactly wrong.

**No PII, structurally.** The constructor takes `(nombreArchivo, banco)` only — no amount, no row, no
description can be interpolated because none is a parameter. `nombreArchivo` is the established precedent
(`pdf-invalido.error.ts:11-14`, `pdf-sin-texto.error.ts:10-13`).

## D-09 — The `never` guards will NOT force the four unions. Route tests will. (Corrected mechanism.)

The previous change's design claimed the compiler forces a new error variant through
pipeline → `ProcessIngestaError` → `aHttpError`'s `const _exhaustive: never`. **That claim is wrong, and the
reason is not the one usually cited.**

- `instanceof` narrowing is **nominal** in TypeScript (`isTypeDerivedFrom` walks the base-type chain), so
  once a member reaches a union, `const _exhaustive: never = error` (`ingesta.routes.ts:434`, `:484`)
  **does** fire if it is unmapped. That part works.
- **Assignability is structural, and that is where the chain breaks.** `PdfInvalidoError`,
  `PdfSinTextoError` and `RangoFechasInvalidoError` declare no members beyond `Error`'s. Any new error class
  is therefore assignable to them — extra properties never block assignability. So
  `return Result.fail(pipelineResult.getError())` in `ProcessIngestaUseCase` / `CommitIngestaUseCase` /
  `PreviewIngestaUseCase` **keeps compiling** after `EjecutarPipelineIngestaError` (`:57-67`) gains
  `SinMovimientosError`, because every source member is assignable to *some* target member. Adding a
  discriminating field to the new class does **not** help — extra properties are allowed in the assignable
  direction.

**Consequence if we trust the compiler.** The member never reaches `ProcessIngestaError`, the `never` guard
never sees it, and at runtime the `instanceof` chain in `aHttpError` matches nothing and falls through to
`return { status: 500, message: 'Error inesperado' }` (`ingesta.routes.ts:486`). A carefully worded 400
becomes an opaque 500, with a green typecheck.

**Decision.** Widen all four unions **by checklist**, and detect a miss with tests that exercise the wire, not
with the type system:

| Union | Site |
|---|---|
| `EjecutarPipelineIngestaError` | `ejecutar-pipeline-ingesta.use-case.ts:57-67` |
| `ProcessIngestaError` | `process-ingesta.use-case.ts` |
| `PreviewIngestaError` | `preview-ingesta.use-case.ts` |
| `CommitIngestaError` | `commit-ingesta.use-case.ts:88-99` |

**Mandatory in the same slice:** one route-level test per surface — `POST /api/ingestas/preview`,
`POST /api/ingestas/commit`, `POST /api/ingestas` — asserting **400** and **`code: 'SIN_MOVIMIENTOS'`**.
A missed union widening yields 500 / no `code` → RED. These three tests are the only real detector; the slice
must not merge without them.

## D-10 — A zero-movement commit DOES register a FALLIDA `Ingesta` (no carve-out)

**Decision.** No carve-out at `commit-ingesta.use-case.ts:215-226`. `SinMovimientosError` follows the ING-07
default and writes a FALLIDA row like every other pipeline failure.

**Why this differs from `PdfProtegidoError`'s carve-out.** That carve-out exists because a password prompt
*invites* retries: three attempts at one file that will eventually succeed would write three rows for one
success. A zero-movement file offers **no field to change and no retry that helps** — the row is a genuine
terminal failure. It is also the *only durable trace* that a user tried to import a statement we could not
read: exactly the signal whose absence turned this bug into an afternoon of diagnosis. The message persisted
into that row is `error.message`, which by D-08 carries only the file name and bank.

**Trigger recorded.** If ingesta history shows users repeatedly re-uploading the same zero-row file, revisit.

## D-11 — Web: no new state, no new copy — the server message already reaches the user (verified)

**Decision.** `apps/web` needs **no** `EstadoSubida` member and **no** new string. Verified:
`SubirCartola.tsx:798-802` derives `mensajeError` from `previewMutation.error?.message`, and `:1083-1094`
renders it verbatim in a `role="alert"` for `estado === 'preview-error'`. The domain message from D-08 is
displayed as written.

**Why not a dedicated state** (the `preview-protegido` precedent, `SubirCartola.tsx:63-73`). That member
earned itself because it unlocks an **affordance** — a password field and a retry with the same `File`. There
is no affordance here: nothing the user can type changes the outcome. A state member whose only content is a
canned status line would duplicate the server message and start drifting from it. YAGNI + DRY.

**Contract.** `code: 'SIN_MOVIMIENTOS'` reaches `openapi.json` only if error codes are enumerated there; run
`pnpm contract:sync` and let the CI drift-check decide. `ApiError.tag === 'invalid'` already carries `code`
and is already in `TAGS_ERROR_PERMANENTE` — no client plumbing changes.

## D-12 — Fixture: committed PDF + committed generator, geometry asserted before any production code

**Decision.** `apps/api/test/fixtures/pdf/bci-cartola-variante-test.pdf` **and**
`generar-bci-cartola-variante-test.ts`, both committed, following
`generar-bci-cartola-montos-grandes-test.ts` exactly: raw uncompressed content streams, `BT/Tf/Tm/Tj/ET` per
token, Helvetica `/WinAnsiEncoding`, latin1, and the **backward pen-jump spacer at x=599** (`:59-77`) without
which pdfjs merges adjacent runs and destroys the per-token x.

**Committed vs generated at test time — tradeoff stated.** Commit both. The committed binary keeps
`pnpm api test` free of a generation step and CI deterministic, at the cost of an opaque blob only the
generator explains. Generating at test time removes the blob but adds a build step to every run and makes a
broken generator look like a broken extractor. Two in-repo precedents plus KISS decide it.

**Geometry contract the generator MUST reproduce** (all data invented; only these positions are carried over):

| Element | Requirement |
|---|---|
| Row dates | `DD-MM-YYYY`, x = **33.6** (the out-of-band value — the fixture must prove D-03) |
| SUCURSAL | x ∈ [75.7, 83.4] |
| descripcion | starts at **134.8**, ≤ 220.7 |
| Charges | right-aligned, spanning **420.9 – 434.1**, including at least one at ≥ 430 (today's dead zone) |
| Deposits | at least two, near **484 – 487** |
| Saldo | 555.9 – 570.6 (must stay unassigned) |
| Table header | `FECHA` 38.2, `SUCURSAL` 81.1, `DESCRIPCION` 195.9, `CHEQUES` 392.1, `DEPOSITOS` 459.9, `SALDO DIARIO` 521.2 — repeated on every page |
| Period anchor | split into three tokens: `PERIODO` \| `:` \| `DD-MM-YYYY al DD-MM-YYYY` |
| Pages | 3 |

**Slice 1 asserts the fixture against itself** — dash dates present, zero slash dates, tokens at the x values
above, header repeated per page, split `PERIODO` — and those assertions are green from the start. They are
what makes the later RED tests trustworthy: if the fixture drifts, they fail *before* the parser tests do.

**Header-row hazard, to be resolved by test.** V2's header row puts `SUCURSAL` between `FECHA` and
`DESCRIPCION`, so the joined row text is `"FECHA SUCURSAL DESCRIPCION …"` and the existing filter
`/^FECHA\s+DESCRIPCION/` (`bci.strategy.ts:144`) does **not** match it. Analysis says it is inert (no
parseable date, non-empty `cargo` column blocks fusion), but the `N° DE` leak (`:145-153`) is precedent that
this analysis is easy to get wrong. Slice 3 asserts *no header fragment appears in any description*; whatever
`filasIgnoradas` anchor that requires gets added, and none is added speculatively.

## D-13 — Acceptance bar is **reconciliation**, not "it parses"

**Decision.** A parse that silently reads 60 of 106 rows is the same class of failure this change exists to
fix, so row-count-and-no-error is not the bar. Both fixtures and the real statement are accepted on the
**balance identity**:

```
saldoAnterior − Σcargo + Σabono === saldoFinal
```

*Automated (the fixture).* The generator already computes a consistent running balance and totals section by
construction (`generar-bci-cartola-montos-grandes-test.ts:80-83` is the precedent); the new generator declares
`SALDO_ANTERIOR`, `TOTAL_CARGOS`, `TOTAL_ABONOS`, `SALDO_FINAL` as exported constants, and the normalizer spec
asserts (i) exact movement count, (ii) the exact `{fecha, descripcion, cargo, abono}` multiset, (iii) `Σcargo`
and `Σabono` as `BigInt` against those constants, and (iv) the identity above. **(iv) is the only assertion
that catches both a dropped row and a sign inversion** — an inverted charge moves the identity by 2× the
amount, a dropped row by 1×.

*Manual (the real statement, never committed).* Run the pipeline locally, reconcile `Σcargo` / `Σabono` /
count against the statement's own printed totals, and check the identity. **Record only the boolean outcome
and the row count in the PR — never the amounts.**

## D-14 — Where the audit findings live so they get acted on

The audit stays documentation-only: **no `rangosX`, regex, `formatoFecha` or any `getEstructura()` return
value of BancoEstado, Banco de Chile or Santander is modified.** Findings land in three places with three
different jobs, because one is not enough:

1. **The strategy docblock of each bank — comment-only edits.** This is where BCI's and Banco de Chile's
   calibration provenance already lives (`bci.strategy.ts:19-21,37-50`; `banco-chile.strategy.ts:21-22,33-46`)
   and it is the only location the next person to edit a band is guaranteed to read. Each of the three gains a
   short block: *how many real statements the bands were calibrated against (Santander and BancoEstado: none
   — they were not part of the 2026-08-30 recalibration), whether the date format was observed or assumed,
   and the width of the gap between its money columns.* **Bound:** comments only; the reviewer verifies the
   returned object is byte-identical and the three untouched strategy specs stay green.
2. **`apps/api/CLAUDE.md`** — a gotchas line per bank plus the new fixture row in the fixtures table. Durable
   agent/onboarding context.
3. **One GitHub issue per bank that shows a concrete risk** — today that is BancoEstado (`abono` [395, 460)
   and `cargo` [460, 500) are **contiguous: zero dead zone**, `banco-estado.strategy.ts:65-70` — under D-02's
   reasoning this bank has *no* loud-failure buffer between its two money columns) and Santander (`abono` is
   **25 pt wide** at [495, 520) with a **45 pt dead zone** at [450, 495), `santander.strategy.ts:81-86`).
   Each issue names its trigger: *a real statement measurement, before any band is touched.*

**Plus one machine-checked guard, so the finding cannot rot.** A new cross-bank spec asserting, for all four
strategies, that no two `rangosX` bands overlap and that `cargo` and `abono` are disjoint. It passes for all
four today (bands are `[xMin, xMax)`, `token-grouping.ts:108-112`) and it fails the day someone widens a band
into its neighbour. A stronger assertion — *a minimum gap between `cargo` and `abono`* — is deliberately
**not** added: BancoEstado would fail it today and fixing BancoEstado is out of scope. That fact is the
content of its issue.

---

## Slices (strict TDD — RED first, each independently revertible, `feature-branch-chain`)

| # | Scope | First RED test | Notes |
|---|---|---|---|
| 1 | Generator + 3-page fixture + geometry self-assertions (D-12) | fixture geometry: dash dates present, 0 slash dates, date token at x=33.6, header repeated ×3, split `PERIODO` | No production code. Likely needs `size:exception` or a generator/assertions split |
| 2 | `parsearFechaFila` `[/-]` (D-04), union docblock, **totals-row `filasIgnoradas` anchor (D-05)** | `parsearFechaFila('22-07-2026', 'DD/MM/YYYY')` → `{22,7,2026}`; **and** both existing BCI fixtures still normalize to 18 / 8 unchanged | RED must be a unit test, **not** the new fixture's movements (D-03) |
| 3 | `rangosX` (D-02), `fecha`/SUCURSAL (D-03), `PERIODO` anchor (D-06), docblock, invariant test | new fixture → full expected movement set, correct `cargo`/`abono` sides, reconciliation identity (D-13) | **Riskiest slice.** Smallest diff, own commit, own revert |
| 4 | `SinMovimientosError`, pipeline guard, 4 unions, both mappers, 2 rewritten specs (D-07/D-08/D-09/D-10) | `POST /preview` with a zero-row file → 400 + `code: 'SIN_MOVIMIENTOS'` (not 500) | Only user-visible change to **existing working uploads** → first to revert if production surprises us |
| 5 | Audit (D-14) — docblock comments, `CLAUDE.md`, 3 issues, cross-bank overlap spec | overlap spec green for all four banks | No `getEstructura()` return value changes |

Slices 2 → 3 are strictly ordered (D-05 lives in 2 but only 3 makes the new fixture parse). Slices 4 and 5
are independent of the BCI fixes and of each other.

## Open questions

None blocking. All five proposal questions are resolved: 1 → D-01/D-02/D-03, 2 → D-07, 3 → D-10, 4 → D-08,
5 → D-06.

## Risks this design accepts, in writing

1. **The new variant's deposit band rests on two samples.** 484.4 – 486.6 over a near-expense-only month
   (71 charges, 2 deposits). Any deposit-band number for this variant is close to a guess. D-02 responds by
   (a) putting 15.9 pt between the highest observed charge and the deposit floor, so a *wrong* deposit band
   cannot swallow a charge, and (b) widening the ceiling to 515 so a narrower-than-observed deposit still
   lands in-band. Residual: a deposit narrower than ~5.7 digits below the two samples is **rejected loudly**,
   not misread. That is the intended failure mode and it will look like a bug report, not like bad data.
2. **`abono.xMax = 515` is 6.2 pt from V2's `SALDO DIARIO` header (521.2).** The header lives on an
   undated row and is inert, but the margin is thin and pinned by the invariant test.
3. **The synthetic fixture may not faithfully reproduce the real variant.** Only the manual reconciliation
   run on the real file (D-13) can close this, and it must be repeated after slice 3.
4. **D-07 changes `.xlsx` behaviour.** Deliberate, and bounded to two named tests — but it is a behaviour
   change to a path this change never otherwise touches.
5. **The compiler will not force the four union widenings (D-09).** The three route tests are the only
   detector. If they are dropped from the slice, the failure mode is a silent 500.
