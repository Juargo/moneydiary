# Delta for PDF Bank-Statement Ingestion — Second BCI Layout + Zero-Movements Error

> SDD spec artifact. Hybrid store — mirror of Engram topic `sdd/bci-cartola-variante/spec`.
> Deltas `openspec/specs/pdf-ingesta/spec.md`. Continues that spec's `PDF-NN` numbering from
> `PDF-11`. Behavioral requirements only — the mechanism that makes two BCI column geometries
> coexist, where the zero-rows check lives, whether a zero-row commit records a `FALLIDA`
> `Ingesta` row, and the fixture generator's implementation are all `sdd-design`'s call (see
> proposal "Open design questions"). These requirements are written to hold regardless of how
> those questions are answered.

## ADDED Requirements

### Requirement: PDF-11 — BCI parses both published statement layouts with correct money-column assignment

The system MUST parse BCI `CARTOLA DE CUENTA CORRIENTE` statements in either of its two known
published layouts: the existing layout (slash row dates, `DD/MM/YYYY`) and the newly-supported
layout (dash row dates, `DD-MM-YYYY`, with column positions shifted relative to the existing
layout). Supporting the new layout MUST NOT regress the existing layout — every fixture, movement
count, total, and excluded row documented for the existing BCI layout MUST remain unchanged.
Within each layout, a charge amount MUST always be attributed to `cargo` and a deposit amount MUST
always be attributed to `abono`; no configuration of the two layouts' column assignment MAY read
one layout's charge as a deposit or vice versa (ADR-015 money-exactness emphasis — the risk
concentrates on money, not on which layout is newer).

#### Scenario: The existing slash-date layout continues to parse unchanged

- GIVEN the existing BCI fixture(s) using `DD/MM/YYYY` row dates and their original column geometry
- WHEN the BCI pipeline runs end to end
- THEN it normalizes to the same movement count, totals, and excluded rows already documented for
  that fixture in PDF-03
- AND no previously-documented expected value for that fixture changes as a result of this change

#### Scenario: The new dash-date layout parses successfully

- GIVEN a BCI fixture using `DD-MM-YYYY` row dates and the newly-supported column geometry
- WHEN the BCI pipeline runs end to end
- THEN it normalizes to its own documented movement count, totals, and excluded rows
- AND every movement row's date parses successfully — none is dropped as "no interpretable date"

#### Scenario: Both layouts are supported without either one disabling the other

- GIVEN both the existing slash-date fixture and the new dash-date fixture
- WHEN each is ingested, in either order, with no reconfiguration between uploads
- THEN both normalize correctly and independently
- AND nothing about supporting the new layout requires disabling or degrading support for the
  existing one

#### Scenario: Charges and deposits are attributed to the correct column in each layout

| Layout | Amount type | Expected column |
|---|---|---|
| Existing (slash dates) | charge | `cargo` |
| Existing (slash dates) | deposit | `abono` |
| New (dash dates) | charge | `cargo` |
| New (dash dates) | deposit | `abono` |

- GIVEN a movement row from either layout's fixture
- WHEN normalization assigns the row's amount to `cargo` or `abono`
- THEN it lands in the column matching the table above
- AND a charge is never read as a deposit, nor a deposit as a charge, regardless of which layout
  produced the row

Note (non-requirement, carried forward for `sdd-design`, not prescriptive of a mechanism): the raw
amount-token X positions measured for the new layout overlap the existing layout's `abono` band,
and the new layout's own charge/deposit split rests on far thinner measured evidence for deposits
(2 samples) than for charges (71 samples). Whatever mechanism is chosen to make the two geometries
coexist must be evaluated against that overlap and that evidence gap — this requirement does not
pick the mechanism.

### Requirement: PDF-12 — A detected, structurally-valid statement that normalizes to zero movements is reported as an error, not a successful empty result

The system MUST treat zero normalized movements from a detected, structurally-valid bank statement
as a reportable error condition, never as a successful empty preview or commit result. The error
MUST name that no movements were found, so the outcome is actionable and diagnosable, and MUST NOT
contain statement content — no amounts, no descriptions, no PII (ADR-013). This requirement is
bank-agnostic: any of the 4 supported banks producing zero normalized rows after successful
detection and structural validation MUST trigger the same behavior, not only BCI.

Accepted tradeoff, stated explicitly rather than left as a footnote: the system has no way to
distinguish "the parser failed to find movements it should have found" from "this statement
genuinely records no movements for this period." Because of that, a statement for a real account
with a genuinely empty period is also rejected by this requirement. This is a deliberate,
accepted consequence of choosing to surface zero rows as an error — not an oversight, and not
something a later reading of this spec should "fix" by silently reverting to success-with-empty-list.

#### Scenario: A statement that normalizes to zero movements returns an error

- GIVEN a bank statement whose bank is detected and whose structure validates successfully
- WHEN normalization yields zero movements
- THEN the system returns an actionable error instead of a successful empty preview or commit result
- AND the error message contains no statement content, no amounts, and no PII

#### Scenario: A genuinely empty statement is rejected by the same behavior (accepted tradeoff)

- GIVEN a real bank statement for a period that genuinely has no movements
- WHEN it is detected, validated, and normalizes to zero rows
- THEN the system reports the same zero-movements error it would report for any other cause of
  zero normalized rows
- AND this is the accepted, deliberate behavior for this case, not a defect

#### Scenario: A statement with at least one movement is unaffected

- GIVEN a bank statement that normalizes to one or more movements
- WHEN the pipeline completes
- THEN the zero-movements error is never triggered
- AND the movements are returned or persisted exactly as they were before this change

## MODIFIED Requirements

### Requirement: PDF-02 — Structure validation succeeds for the 4 known banks, groups failures, and extracts a correct period regardless of anchor punctuation

`IPdfStructureValidator` MUST produce an `EstructuraPdfValidada` (period date range, table start
page, per-column X ranges) for each fixture. A mutated or missing table header MUST return
`Result.fail(EstructuraPdfInvalidaError)` listing ALL detected problems in a single pass. A missing
period anchor MUST return `Result.fail(RangoFechasInvalidoError)` for banks that omit the year
(BancoEstado, Banco de Chile, Santander); BCI, which carries the year per row, is exempt from this
specific failure. When the period anchor text IS present in the document, the extracted period
MUST match the statement's actual dates regardless of incidental punctuation between the anchor
label and the date value (for example, a colon separator) — extraction MUST NOT depend on a
pattern narrow enough to match one bank's phrasing while silently missing another's. A
period-extraction failure for an anchor that IS present in the text MUST NOT be silently swallowed
as an undefined period; it MUST be surfaced in a way the caller can detect.

(Previously: this requirement's period-extraction guarantee was scoped only to whether the anchor
text is present or absent. A present-but-differently-punctuated anchor could fail to match the
extraction pattern and silently carry `periodo: undefined` all the way through a validated
structure, with no observable signal — masked specifically for BCI by its exemption from
`RangoFechasInvalidoError`. This change closes that gap without altering the exemption itself.)

#### Scenario: Each fixture validates to its expected period

| Fixture | Period |
|---|---|
| bancoestado-cartola-test.pdf | 01/04/2026–30/04/2026 |
| bancochile-cartola-test.pdf | 01/04/2026–30/04/2026 |
| santander-cartola-test.pdf | 01/03/2026–31/03/2026 |
| bci-cartola-test.pdf | 01/04/2026–30/04/2026 |

- GIVEN the fixture's detected bank
- WHEN `IPdfStructureValidator.validar()` runs
- THEN it returns `Result.ok(EstructuraPdfValidada)` with the matching period, table start page,
  and column X ranges

#### Scenario: Multiple structural problems are reported together

- GIVEN a fixture with both a mutated header and a missing period anchor
- WHEN validation runs
- THEN `Result.fail(EstructuraPdfInvalidaError)` lists both problems in a single error

#### Scenario: Missing period anchor is rejected for year-omitting banks

- GIVEN a BancoEstado, Banco de Chile, or Santander fixture with no `Fecha Inicio/Final` (or
  `DESDE/HASTA`) anchor
- WHEN validation runs
- THEN it returns `Result.fail(RangoFechasInvalidoError)`

#### Scenario: BCI's period anchor is extracted regardless of colon punctuation between label and date

- GIVEN a BCI statement whose period anchor reads `PERIODO : <start> al <end>` (a colon between
  the label and the date, rather than whitespace only)
- WHEN `IPdfStructureValidator.validar()` runs
- THEN the validated structure's period matches `<start>`–`<end>`
- AND the period is not `undefined`

#### Scenario: A period-extraction failure is never silent

- GIVEN a statement whose period anchor text is present but does not match the extraction pattern
  for any accepted punctuation variant
- WHEN validation runs
- THEN the validated structure does not silently carry an undefined period as if extraction had
  succeeded
- AND the caller has an observable signal that period extraction failed

### Requirement: PDF-03 — Normalization emits the canonical shape with exact money and matches per-bank reference targets

`IPdfTransactionNormalizer` MUST emit `{ fecha: 'YYYY-MM-DD', descripcion, cargo, abono }` with
`cargo`/`abono` as `number`, computed without floating-point arithmetic, shape-compatible with the
Excel normalizer output — so `PersistTransactionsUseCase`, categorization, and consolidation stay
untouched. Each fixture MUST normalize to its documented period, totals, and filtered-row set.

#### Scenario: Amounts parse as exact integer CLP

- GIVEN a PDF cell containing `$1.580.000`
- WHEN the normalizer parses the amount
- THEN the result is the integer `1580000`
- AND no floating-point arithmetic is used

#### Scenario: Each fixture normalizes to its reference targets

| Fixture | Period | Signals |
|---|---|---|
| bancoestado | 01/04/2026–30/04/2026 | Cargos $135.010 / Abonos $150.000; 2 pages concatenated; year 2026 inferred |
| bancochile | 01/04/2026–30/04/2026 | SALDO INICIAL/FINAL rows excluded |
| santander | 01/03/2026–31/03/2026 | descriptions merged from word-by-word X tokens (e.g. `Transf a Tercero Maria Ejemplo`); Resumen de Comisiones excluded |
| bci | 01/04/2026–30/04/2026 | 2 pages concatenated; browser footer (URL + print date) excluded; year explicit per row; multiline continuations stitched into one row |
| bci — variant B (dash dates, shifted geometry) | synthetic, invented by the fixture generator — not fixed here | `DD-MM-YYYY` row dates; 3 pages, table header repeated per page; `SUCURSAL` column present; `cargo`/`abono` attributed correctly per PDF-11 |

- GIVEN the fixture's validated structure
- WHEN normalization runs
- THEN the output's period, totals, and excluded rows match the table
- AND the movement count matches the real normalizer output verified against the fixture (exact
  count is asserted by the implementation test against the actual fixture, not fixed here)

#### Scenario: Month regression across the period increments the inferred year

- GIVEN a BancoEstado, Banco de Chile, or Santander statement whose period spans a year boundary
  (December → January)
- WHEN a row's month is earlier than the previous row's month
- THEN the inferred year for that row, and all following rows, increments by 1
- AND BCI rows use their explicit per-row year instead of inference

## Non-Goals

| Excluded | Reason |
|----------|--------|
| Fixing BancoEstado, Banco de Chile, or Santander column bands or date assumptions | This change audits those three strategies and documents findings only; recalibrating a band without a real measurement is the exact mistake that produced this bug — any fix is a separate, later change with its own real-statement measurement |
| A generic multi-variant layout framework | YAGNI — two known BCI layouts exist today, not an open-ended family; the four bank strategies are separately justified because four real implementations exist from day one |
| Any change to `.xlsx` ingestion | This change is scoped to the PDF pipeline only |
| Reprocessing statements already uploaded, or auditing past uploads for silent data loss | Assumed unnecessary; affected users retry the specific files after the fix ships |
| A `force`/override flag to bypass the zero-movements error | Not on the table — it would re-open the settled tradeoff decision (a genuinely empty statement is rejected) |
| Committing, quoting, or reproducing the real user statement that produced this diagnosis, in any form | Binding PII rule for this change (ADR-013); only invented data on measured, non-identifying geometry crosses over |
