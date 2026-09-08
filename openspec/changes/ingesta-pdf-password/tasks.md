# Tasks: Password-Protected PDF Ingestion (ingesta-pdf-password)

> Grouped by Clean Architecture layer within each of the design's 4 slices (`domain <- application <- infrastructure`),
> hierarchical numbering, each phase completable in one session. Strict TDD (`pnpm api test`): every implementation
> task is RED (failing test named first) → GREEN (minimal code) → REFACTOR. Design decisions D-01..D-11 are BINDING —
> not re-litigated here. Line numbers were re-verified against the working tree during this phase (2026-09-07).

## Review Workload Forecast

| Field | Value |
|---|---|
| Chained PRs recommended | **Yes** |
| 400-line budget risk | **High** (total ~1,150–1,300 hand-authored lines; individual slices sit close to or under the 400 cap, so the *chain* is what keeps each PR reviewable, not slice size alone) |
| Decision needed before apply | **Yes** (`delivery_strategy: ask-on-risk` per session cache — orchestrator must ask before `sdd-apply`; chain strategy, `stacked-to-main` vs `feature-branch-chain`, is also still open per the proposal) |

Honest per-slice estimate (hand-authored lines only; `openapi.json`/`types.gen.ts` regeneration excluded), revised upward from the proposal's ~900 because strict TDD means 3 dedicated test files in Slice 1 alone (constant-pin, behavioral, negative-regression) and a hand-rolled RC4-40 generator with no library help:

| Slice | Scope | Est. changed lines | Suggested PR |
|---|---|---|---|
| 1 | Domain error + extractor password/detection + encrypted fixture/generator | ~380 | PR 1 |
| 2 | 3 ports/adapters/use cases + pipeline error union + D-09 carve-out | ~300 | PR 2 (depends on PR 1) |
| 3 | HTTP contract: Zod schemas, preview error-channel fix, both `never` mappers, `contract:sync` | ~260 | PR 3 (depends on PR 2) |
| 4 | Web reactive UX: `client.ts`, 2 hooks, `SubirCartola` state machine, never-leak tests | ~300 | PR 4 (depends on PR 3) |
| **Total** | | **~1,240** | |

Roughly half of each slice is test code (ADR-015 money/access-path emphasis + strict TDD). Slices are strictly sequential — 2 depends on 1 (needs the extractor's password param and the new error class), 3 depends on 2 (needs the widened error unions to map), 4 depends on 3 (needs `code: 'PDF_PROTEGIDO'` on the wire, see Phase 12 below). This is a **Feature Branch Chain candidate**, not independent stacked slices: none of slices 2–4 is independently useful to a user without the ones before it, even though each is independently *revertible* (per the proposal's rollback plan). Chain strategy remains the orchestrator's/user's call.

### A slicing clarification not spelled out in the design (task-author note, not a re-litigation of D-01..D-11)

D-02 states the `never`-exhaustiveness guards in `aHttpError`/`aCommitHttpError` (`ingesta.routes.ts:375`, `:413`) **force** the mapping once the error unions widen. But the design's own slice table puts the union-widening in Slice 2 and "both `never` mappers" in Slice 3. Taken literally, that would leave Slice 2 with a **`tsc --noEmit` failure** at the end of the slice (the `never` guards choke on the newly-possible `PdfProtegidoError` the moment `ProcessIngestaError`/`PreviewIngestaError`/`CommitIngestaError` gain it) — which breaks "each slice green and independently revertible" (proposal, Slicing strategy). Resolution used below: Slice 2 adds a **minimal, undifferentiated 400 branch** for `PdfProtegidoError` in both mappers (just enough to keep `tsc`/tests green, no `code` yet). Slice 3 **replaces** that branch with the full `code`-discriminated mapping via `responderErrorTraducido` (D-03) and fixes the preview route's dropped-`code` bug. This preserves every substantive call the design made; it only resolves a compile-ordering gap the design didn't spell out.

---

## Phase 1 (Slice 1): Domain — new error

- [x] 1.1 RED: `apps/api/src/domain/errors/pdf-protegido.error.spec.ts` — asserts `new PdfProtegidoError('archivo.pdf', 'requiere-password')` has `name === 'PdfProtegidoError'`, a fixed message that does **not** interpolate any password value (there is no password parameter to interpolate — D-07 layer 1), and `.motivo === 'requiere-password'`; same for `'password-incorrecta'`.
- [x] 1.2 GREEN: create `apps/api/src/domain/errors/pdf-protegido.error.ts` per D-03 — `MotivoPdfProtegido = 'requiere-password' | 'password-incorrecta'`, constructor `(nombreArchivo: string, motivo: MotivoPdfProtegido)`, shaped like `pdf-invalido.error.ts`. Constructor signature has no password parameter — this is the structural control D-07 relies on, not an incidental choice.
- [x] 1.3 REFACTOR: confirm the error file follows the sibling errors' doc-comment convention (why it's a domain error, ADR-005 rationale).

## Phase 2 (Slice 1): Encrypted PDF fixture + generator

- [x] 2.1 Read `generar-bci-cartola-montos-grandes-test.ts` and `generar-bancochile-cartola-montos-grandes-test.ts` in full for the committed-generator pattern (raw PDF via hand-written content streams, `writeFileSync`, regeneration instructions in the docblock) before writing anything new.
- [x] 2.2 Write `apps/api/test/fixtures/pdf/generar-protegida-test.ts`: a minimal one-page PDF (does not need real bank-statement structure — Slice 1 only exercises the extractor, not bank detection) encrypted with a **V=1/R=2 (RC4-40)** standard security handler per D-11 — MD5 via `node:crypto`, RC4 hand-rolled (~20 lines), no new npm dependency. Docblock must (a) name the fixed fake password as `PASSWORD_FIXTURE` and state it is a deliberately-fake, non-gitleaks-shaped literal, and (b) state explicitly that RC4-40 is intentionally weak/public/reproducible and must not be "fixed" by a future security pass.
- [x] 2.3 **Contingency checkpoint — do not silently skip.** Run `pnpm exec tsx test/fixtures/pdf/generar-protegida-test.ts`, then attempt to load the output with `pdfjs-dist/legacy/build/pdf.mjs` + the fixture password as the very first thing in Phase 3's RED test (3.1). If pdfjs rejects the RC4-40 handler (throws something other than `PasswordException`, or fails to decrypt even with the correct password), STOP and pivot: reimplement the generator's security handler as **V=4/R=4 (AES-128)** using `node:crypto`'s native `aes-128-cbc` (still no new dependency — Node's built-in cipher, per D-11's rejected-but-viable fallback), with crypt-filter dictionaries. Record which handler shipped in the generator docblock and in the commit message; do not leave both variants half-implemented.
  - **Result: contingency did NOT fire.** RC4-40 shipped as designed. Verified by reading the actual decrypt algorithm in `pdfjs-dist@6.2.108`'s `CipherTransformFactory` (`legacy/build/pdf.worker.mjs`) line-by-line before writing the generator, then confirmed empirically with a standalone spike script against the real fixture: no password → `PasswordException` code 1 (NEED_PASSWORD); wrong password → code 2 (INCORRECT_PASSWORD); correct password → text extracted successfully ("PDF PROTEGIDO FIXTURE"). No AES-128 pivot needed.
- [x] 2.4 Commit both `protegida-test.pdf` (binary) and the generator script, per D-11's committed-vs-generated-at-test-time tradeoff (deterministic CI, no build step added to `pnpm api test`).

## Phase 3 (Slice 1): Extractor — password support + `PasswordException` discrimination (D-04)

- [x] 3.1 RED (constant-pin / the alarm test): `pdf-text-extractor.spec.ts` — import `pdfjs-dist/legacy/build/pdf.mjs` the same way the extractor does; assert `PasswordResponses.NEED_PASSWORD` and `PasswordResponses.INCORRECT_PASSWORD` are both `typeof 'number'` and differ from each other. This test's job is to fail LOUDLY, pointing at pdfjs, if a future upgrade changes the shape D-04's detection depends on.
- [x] 3.2 RED (behavioral, 3 sub-cases against the Phase 2 fixture): `extract(buffer, name)` with no password → `Result.fail(PdfProtegidoError)` with `.motivo === 'requiere-password'`; with a wrong password → `.motivo === 'password-incorrecta'`; with the correct `PASSWORD_FIXTURE` → `Result.ok(tokens)` with the fixture's expected text content.
- [x] 3.3 RED (negative regression): re-run the existing corrupt-buffer test (`pdf-text-extractor.spec.ts`, current `PdfInvalidoError` coverage) and add an explicit assertion that a corrupt-but-not-encrypted buffer still returns `PdfInvalidoError`, not `PdfProtegidoError` — the new branch must not over-capture.
- [x] 3.4 RED (never-leak, D-07 layer 2): assert that when extraction fails with the wrong password, `result.getError().message` does **not** contain the fixture's wrong-password string anywhere (guards against a future edit that forwards pdfjs's raw rejection message).
- [x] 3.5 GREEN: modify `PdfTextExtractor.extract()` (`pdf-text-extractor.ts`) — add optional `password?: string` parameter, pass it to `getDocument({ ..., password })`, and in the `catch` at `:60-65` call the D-04 duck-typing helper (`name === 'PasswordException'` + numeric `code` compared against `pdfjsLib.PasswordResponses`, read from the same awaited module namespace — never `instanceof`, never hardcoded `1`/`2`) before falling back to today's `PdfInvalidoError`.
- [x] 3.6 GREEN: update the 3 existing extractor call sites that will break compilation once `password?` is added (none currently pass a 3rd argument, so this is additive-only — confirm no signature-order surprises). Verified: all 3 call sites (`pdfjs-bank-detector.service.ts:44`, `pdfjs-transaction-normalizer.service.ts:74`, `pdfjs-structure-validator.service.ts:66`) call with exactly 2 args — no changes needed, `tsc --noEmit` confirms.
- [x] 3.7 REFACTOR: extract the D-04 detection logic into a small named function (`motivoPassword` per the design snippet) with its own unit coverage, not inlined in the `catch`.
- [x] 3.8 Run `pnpm api test -- pdf-text-extractor` and `pnpm api exec tsc --noEmit` — green.

## Phase 4 (Slice 1): Verification

- [x] 4.1 `pnpm api test`, `pnpm api exec tsc --noEmit`, `pnpm api lint` — all green. No other file outside domain/errors, infrastructure/pdf, and test/fixtures/pdf should be touched in this slice (self-contained per the proposal's slicing strategy). Confirmed via `git status`: only `domain/errors/pdf-protegido.error.{ts,spec.ts}`, `infrastructure/pdf/pdf-text-extractor.{ts,spec.ts}`, `test/fixtures/pdf/{generar-protegida-test.ts,protegida-test.pdf}`.
- [x] 4.2 Confirm no existing PDF fixture test (`bancochile-cartola-test.pdf` etc.) regressed — unlocked-PDF behavior must be byte-identical (PDF-09). Full suite: 268 files / 2517 tests, all passing (baseline was 267/2508 — net +1 file, +9 tests, 0 regressions).

---

## Phase 5 (Slice 2): Application — port signatures (D-01)

- [x] 5.1 RED: for each of the 3 port interfaces, add/update a compile-level or behavioral test asserting a caller can pass a trailing `password?: string` with no effect on existing call sites that omit it (backward-compat check — trailing optional parameter). Folded into the Phase 6 adapter RED tests (forwarding tests + the pre-existing "delega" tests updated to assert the new trailing `undefined` arg) — a separate port-only test file would just re-test the same TS structural contract already exercised there.
- [x] 5.2 GREEN: widen `IPdfBankDetector.detect(buffer, originalName, password?)` (`pdf-bank-detector.port.ts:17-27`) — **also widen this port's error union** to include `PdfProtegidoError` (only `detect`'s union widens, per D-01/D-05 — bank detection runs first in the pipeline and is the only stage that can surface the password error, since D-06 guarantees a password failure never reaches stage 2/3).
- [x] 5.3 GREEN: widen `IPdfStructureValidator.validate(buffer, banco, password?)` (`pdf-structure-validator.port.ts:44-54`) — error union **stays byte-identical** (D-05: masked into `EstructuraPdfInvalidaError`, unreachable in practice).
- [x] 5.4 GREEN: widen `IPdfTransactionNormalizer.normalize(buffer, banco, password?)` (`pdf-transaction-normalizer.port.ts:18-28`) — error union **stays byte-identical**, same D-05 rationale.
- [x] 5.5 Add an inline code comment at both the validator and the normalizer service (D-05's "invariant to record in code comments"): if either is ever called without a preceding `detect`, the masking returns and a locked PDF reads as malformed structure. Landed as doc-comments on the two PORT interfaces themselves (`pdf-structure-validator.port.ts`, `pdf-transaction-normalizer.port.ts`) rather than the service files — the invariant is a contract property of the interface, and both service implementations share the identical masking code inherited from before this change.

## Phase 6 (Slice 2): Infrastructure — 3 adapters forward the password

- [x] 6.1 RED: `pdfjs-bank-detector.service.spec.ts` — `detect(buffer, name, password)` forwards `password` to its internal `PdfTextExtractor.extract()` (spy/fake), and against the Phase 2 fixture returns `Result.fail(PdfProtegidoError)`/`Result.ok` per the same 3 sub-cases as Phase 3.2. Confirmed RED (2 failing for the right reason — wrong-password assertion and correct-password assertion, since forwarding didn't exist yet).
- [x] 6.2 GREEN: `PdfjsBankDetectorService.detect()` (`pdfjs-bank-detector.service.ts:35-44`) passes `password` through to `this.extractor.extract(buffer, originalName, password)`.
- [x] 6.3 RED: `pdfjs-structure-validator.service.spec.ts` — `validate(buffer, banco, password)` forwards `password`; when the extractor fails for any reason (including password), it still collapses to `EstructuraPdfInvalidaError` (D-05 — unchanged masking, verified NOT to have grown a new branch). Confirmed RED via the `AnclaFaltante`-vs-`PdfIlegible` distinction (correct password → extraction succeeds → different problema tipo).
- [x] 6.4 GREEN: `PdfjsStructureValidatorService.validate()` (`pdfjs-structure-validator.service.ts:66`) passes `password` to `this.extractor.extract(buffer, ..., password)`.
- [x] 6.5 RED: `pdfjs-transaction-normalizer.service.spec.ts` — same forwarding assertion as 6.3 for `normalize()`. Confirmed RED, same technique.
- [x] 6.6 GREEN: `PdfjsTransactionNormalizerService.normalize()` (`pdfjs-transaction-normalizer.service.ts:74`) passes `password` to its own `this.extractor.extract(buffer, ..., password)`.

## Phase 7 (Slice 2): Application — 3 wrapper use cases pass through

- [x] 7.1 RED+GREEN: `DetectPdfBankUseCase.execute(buffer, originalName, password?)` (`detect-pdf-bank.use-case.ts:26-42`) forwards to `this.pdfBankDetector.detect(buffer, originalName, password)`; widen its own return-type union to include `PdfProtegidoError` (mirrors the port change in 5.2). Also updated the pre-existing "delega" test's `toHaveBeenCalledWith` to expect the trailing `undefined` (now always forwarded).
- [x] 7.2 RED+GREEN: `ValidatePdfStructureUseCase.execute(buffer, banco, password?)` (`validate-pdf-structure.use-case.ts:27-35`) forwards `password`; return type **unchanged** (D-05). Same pre-existing-test update.
- [x] 7.3 RED+GREEN: `NormalizePdfTransactionsUseCase.execute(buffer, banco, password?)` (`normalize-pdf-transactions.use-case.ts:23-31`) forwards `password`; return type **unchanged** (D-05). Same pre-existing-test update.

## Phase 8 (Slice 2): Application — pipeline input + error union

- [x] 8.1 RED: `ejecutar-pipeline-ingesta.use-case.spec.ts` — given a stub `IPdfBankDetector` that returns `Result.fail(PdfProtegidoError)`, `EjecutarPipelineIngestaUseCase.execute({ fileReader, password })` returns `Result.fail(PdfProtegidoError)` (fast failure — D-06, only stage 1 runs), and the password is forwarded to `detectPdfBankUseCase.execute(buffer, name, password)`.
- [x] 8.2 RED: with a stub detector that succeeds, assert `password` is ALSO forwarded to `validatePdfStructureUseCase.execute(buffer, banco, password)` and `normalizePdfTransactionsUseCase.execute(buffer, banco, password)` — the "3× re-parse, one password" invariant, tested end to end per the proposal's risk table (not just at the extractor).
- [x] 8.3 GREEN: add `password?: string` to `EjecutarPipelineIngestaInput` (`ejecutar-pipeline-ingesta.use-case.ts:29-31`); thread it through `runPipeline()`'s 3 conditional calls (`:131-142` detect, `:149-157` validate, `:163-171` normalize — only the PDF branches take it, the Excel branches are untouched by construction since Excel has no password concept).
- [x] 8.4 GREEN: add `PdfProtegidoError` to `EjecutarPipelineIngestaError` (`:52-61`).
- [x] 8.5 GREEN: widen `ProcessIngestaError` (`process-ingesta.use-case.ts:56-66`) and `PreviewIngestaError` (`preview-ingesta.use-case.ts:62-71`) to include `PdfProtegidoError`. **Finding, task-author judgment applied:** the task text says this is "forced" by `Result.fail(pipelineResult.getError())` no longer type-checking — VERIFIED FALSE. `Result<T,E>`'s `_error` field is private, and TS's structural-compatibility check for two instantiations of the same generic class still allows `Result<never, WiderE>` to satisfy `Result<X, NarrowerE>` here because `PdfProtegidoError` (Error + `motivo`) structurally satisfies `PdfInvalidoError` (bare `Error`, no extra fields) — `tsc --noEmit` stayed clean with NEITHER union widened. Widened both anyway per D-02's explicit intent and because Phase 8.6's `instanceof PdfProtegidoError` branch needs the type to be a real member of the union for correct exhaustiveness enforcement (without it, a real regression — PdfProtegidoError silently falling through to the generic 500 branch — would NOT be caught by `tsc`). Per D-02 (confirmed by 9.5 below), thread `password?` through `PreviewIngestaInput` ONLY, NOT `ProcessIngestaInput` — the one-shot endpoint deliberately does not gain the field.
- [x] 8.6 GREEN: add a **minimal, undifferentiated 400 branch** for `PdfProtegidoError` to `aHttpError` (`ingesta.routes.ts`) — this IS compiler-forced (confirmed: `tsc` failed with `TS2322: Type 'PdfProtegidoError' is not assignable to type 'never'` at the `_exhaustive` line before adding the branch). `aCommitHttpError`'s branch deferred to Phase 9.2/9.3 (its union doesn't widen until `CommitIngestaError` does). No `code` field yet; Slice 3 (Phase 13) replaces this branch with the full D-03 mapping.
- [x] 8.7 Run `pnpm api exec tsc --noEmit` after 8.5–8.6 — green (0 errors).

## Phase 9 (Slice 2): Application — commit's carve-out and password threading (D-09) — MERGE-BLOCKING

- [x] 9.1 RED — **the mandatory carve-out test, must exist before the carve-out code and must not be skipped or deferred:** in `commit-ingesta.use-case.spec.ts`, wire a stub pipeline that returns `Result.fail(new PdfProtegidoError('x.pdf', 'password-incorrecta'))`, call `CommitIngestaUseCase.execute()`, and assert **`ingestaFallidaWriter.registrar` was NOT called** (spy/fake writer, assert `.mock.calls.length === 0` or fake-writer call count). Also assert the use case still returns `Result.fail(PdfProtegidoError)` (the 400 path is unaffected — only the persistence side-effect is carved out). **CONFIRMED RED before the carve-out existed** — `expected [ { userId: 'user-123', …(2) } ] to have a length of +0 but got 1` — failed for exactly the right reason (FALLIDA was being registered unconditionally). Test name/location: `commit-ingesta.use-case.spec.ts`, describe `"(d) D-09 — PdfProtegidoError does NOT register a FALLIDA row"`, test `"el pipeline falla con PdfProtegidoError → NO se llama a ingestaFallidaWriter.registrar, y el commit igual retorna Fail(PdfProtegidoError)"`. Landed in the SAME commit as 9.2 (merge-blocking gate honored).
- [x] 9.2 GREEN: in `commit-ingesta.use-case.ts`'s `runCommit()`, changed the pipeline-failure branch to the `if (!(error instanceof PdfProtegidoError)) await this.registrarFallo(...)` shape exactly as specified, per D-09's decided location (NOT inside `registrarFallo`, NOT the adapter, NOT the route, NOT the shared pipeline use case).
- [x] 9.3 RED+GREEN: widened `CommitIngestaError` to include `PdfProtegidoError`; added `password?: string` to `CommitIngestaInput` and forwarded it to `this.ejecutarPipelineUseCase.execute({ fileReader, password: input.password })`. Same structural-typing finding as 8.5 applies (tsc did not force this widening either) — widened anyway for the same correctness reason, and added the matching minimal 400 branch to `aCommitHttpError` (mirrors 8.6 — without it a `PdfProtegidoError` would silently fall through to the generic 500 `_exhaustive` branch at runtime since it's a distinct class from every other member checked via `instanceof`).
- [x] 9.4 RED: repeated-attempts test added (`"3 intentos consecutivos con password incorrecta → 0 filas FALLIDA registradas (spec PDF-08)"`) — calls `commit-ingesta` 3 times with the same stub pipeline failure, asserts `registrar` was never called across all 3. Also added a 4th regression test confirming a NON-password failure (`BancoNoReconocidoError`) still registers exactly 1 FALLIDA row — proves the carve-out doesn't over-apply.
- [x] 9.5 RED+GREEN: `ProcessIngestaUseCase` (one-shot) is **deliberately excluded** from the carve-out per D-09 — added a comment at its own `registrarFallo` call site (`process-ingesta.use-case.ts`) referencing this decision and the YAGNI trigger. No behavior change; `ProcessIngestaInput` does NOT gain a `password` field (D-02) — documentation-only touch.

## Phase 10 (Slice 2): Verification

- [x] 10.1 `pnpm api test`, `pnpm api exec tsc --noEmit` — green (268 files / 2536 tests, 0 tsc errors). Confirmed both mapper functions compile with only the minimal 400 branch from 8.6/9.3 (no `code` yet — intentionally deferred to Slice 3).
- [x] 10.2 Re-ran the full existing PDF and Excel ingestion test suites — no regression (baseline 268/2517 at the start of Slice 2 → 268/2536 at the end, +19 tests, 0 regressions). PDF-09's "absent password ⇒ byte-identical" guarantee verified by the explicit "sin password → undefined forwarded" tests added at every layer (adapters, wrapper use cases, pipeline, preview, commit).

---

## Phase 11 (Slice 3): Infrastructure — Zod contract schemas (D-08)

- [x] 11.1 RED: `ingesta-preview.schema.spec.ts` — `previewIngestaRequestSchema` accepts an object with an optional `password` string field alongside `file`, mirroring the `edits` precedent in `ingesta-commit.schema.ts:26-34`. Confirmed RED via `result.data.password` assertion (a bare `success:true` would pass trivially — `z.object()` strips unknown keys by default, so the value-preservation check is what actually proves the field is part of the schema).
- [x] 11.2 GREEN: add `password: z.string().optional().describe(...)` to `previewIngestaRequestSchema` (`ingesta-preview.schema.ts:11-18`). Per D-08: never put an example password in `.describe()`.
- [x] 11.3 RED+GREEN: same addition to `commitIngestaRequestSchema` (`ingesta-commit.schema.ts:19-35`). Same RED technique.
- [x] 11.4 Confirmed `ingesta-upload.schema.ts` is **NOT** touched (D-02 — the deprecated one-shot route does not gain the password field).

## Phase 12 (Slice 3): Infrastructure — fix the preview error channel (MUST land before Slice 4)

> **Hard ordering dependency, called out explicitly per the launch brief.** `ingesta.routes.ts:144-146` currently does
> `const { status, message } = aHttpError(result.getError()); res.status(status).json({ message })` — it drops `code`
> entirely. Slice 4's reactive UI branches on `code: 'PDF_PROTEGIDO' | 'PDF_PASSWORD_INCORRECTA'`; without this fix,
> the UI has nothing machine-readable to key off. This phase MUST be complete and merged before Phase 17 begins.

- [x] 12.1 RED-equivalent (characterization guard, see note): `ingesta.routes.spec.ts` — `POST /api/ingestas/preview` with a non-DEMO, non-locked failure (`ExtensionNoPermitidaError`) still returns `{ message }` with **no** `code` key present. **Finding**: this assertion is NOT genuinely RED on its own — the *current* code (`res.status(status).json({ message })`) already drops `code` unconditionally for every variant, and `responderErrorTraducido` also omits `code` when the translator returns none, so the observable body is identical before and after 12.2 for every error EXCEPT `PdfProtegidoError`. The real RED signal for this phase only appears once combined with Phase 13's `code`-bearing branches (see 13.1 note) — landed together in the same commit as a result.
- [x] 12.2 GREEN: changed the preview route handler (`ingesta.routes.ts`) from the raw `res.status(status).json({ message })` to `responderErrorTraducido(res, req, aHttpError(result.getError()))` — same pattern already used by the one-shot and commit routes. Confirmed `responderErrorTraducido`'s existing behavior for a mapper result with no `code` field is unchanged (regression guard above stays green).
- [x] 12.3 Ran the full `ingesta.routes.spec.ts` suite — no other preview scenario's response shape regressed (268 files / 2547 tests green).

## Phase 13 (Slice 3): Infrastructure — full D-03 error mapping (replaces the Slice 2 stub)

- [x] 13.1 RED (this IS the genuine RED for Phases 12+13 combined — see 12.1 note): `ingesta.routes.spec.ts` — `POST /api/ingestas/preview` with a stubbed `PdfProtegidoError('cartola.pdf', 'requiere-password')` → 400 + `code: 'PDF_PROTEGIDO'`; with `'password-incorrecta'` → 400 + `code: 'PDF_PASSWORD_INCORRECTA'`. Confirmed RED (9 failing tests, right reason — `res.body.code` was `undefined` because both the Slice 2 minimal branch and the pre-fix route dropped it). **Scope note**: the correct-password→200 full-pipeline sub-case from the original task text is NOT exercised at this route-spec layer (the use case is stubbed here, by design — the real pipeline unlock path is already covered by Phase 3's extractor-level and Phase 6/8's adapter/pipeline-level tests); adding it here would just re-assert that a stub returns what it's told to return.
- [x] 13.2 GREEN: replaced the Phase 8.6 minimal branch in `aHttpError` with the discriminated mapping: `error instanceof PdfProtegidoError` → `{ status: 400, message: error.message, code: error.motivo === 'requiere-password' ? 'PDF_PROTEGIDO' : 'PDF_PASSWORD_INCORRECTA' }`.
- [x] 13.3 RED+GREEN: same replacement in `aCommitHttpError`, same 2 sub-cases mirrored at the commit route. **Scope note**: the "confirm no `Ingesta` row exists after the two failure sub-cases via `GET /api/ingestas`" cross-check from the original task text is NOT re-tested here — at this route-spec layer `commitIngesta` is a stub with no real writer behind it, so there is nothing to query; the actual no-FALLIDA-row guarantee is Phase 9's `commit-ingesta.use-case.spec.ts` D-09 tests (already merge-blocking, already green), which is the correct layer for that assertion.
- [x] 13.4 RED+GREEN: read `req.body.password` in both the preview and commit handlers and forwarded it into `deps.previewIngesta.execute({ ..., password })` / `deps.commitIngesta.execute({ ..., password })`. Explicit tests confirm both "password forwarded when present" and "undefined forwarded when absent" (PDF-09 byte-identical guarantee) for both routes.
- [x] 13.5 RED+GREEN (D-08 multer guard clause): added `MAX_PASSWORD_LENGTH = 500` character cap check on `req.body.password` in the preview handler only (`subirArchivo()` has no `LIMIT_FIELD_VALUE` → 400 mapping, unlike `subirArchivoConEdits()`) — rejects with 400 before use if the field exceeds the cap, use case never called. Did **not** duplicate the `LIMIT_FIELD_VALUE` multer-error block into `subirArchivo()` itself (D-02). **Documented nuance** (code comment on the constant): this cap *mitigates*, not eliminates, the 500 risk — a password field beyond busboy's ~1 MiB default fieldSize still fails during multer's own parsing, before the handler code (and this cap check) ever runs; closing that fully would require the forbidden `LIMIT_FIELD_VALUE` block. Not applied to the commit handler — its own multer instance already has a `LIMIT_FIELD_VALUE` mapping (256 KB) covering any oversized text field, so there is no equivalent 500 risk to mitigate there (YAGNI — no duplicate guard added).
- [x] 13.6 RED (D-07 layer 4, never-leak at the wire): both the `password-incorrecta` tests (preview + commit) and the length-cap test assert the submitted password value (or the oversized string) never appears anywhere in `JSON.stringify(res.body)`.

## Phase 14 (Slice 3): Contract regeneration — explicit task, not a side effect

- [x] 14.1 Ran `pnpm api openapi:emit`; diff-reviewed `apps/api/openapi.json` — confirmed only the preview/commit request schemas gained the optional `password` property, nothing else drifted.
- [x] 14.2 Ran `pnpm contract:sync` — regenerated `packages/api-client/src/types.gen.ts` (and `index.ts`, touched by the generator) — committed.
- [x] 14.3 Ran `pnpm api openapi:check` — zero drift (exits clean against the just-emitted `openapi.json`).

## Phase 15 (Slice 3): Verification

- [x] 15.1 `pnpm api test`, `pnpm api exec tsc --noEmit`, `pnpm api openapi:check` — all green. `pnpm web typecheck` also confirmed green after `contract:sync` (see apply-progress for exact counts).
- [x] 15.2 Confirmed `ingesta-upload.schema.ts` and the one-shot route (`ingesta.routes.ts`, `POST /ingestas`) are functionally untouched except for the (already-forced, Slice 2) error-union widening — no new request field, no new behavior (D-02). `git diff` for this slice touches only: the 2 preview/commit schema files + specs, `ingesta.routes.ts` + spec, and the Phase 14 contract-regeneration outputs.

---

## Phase 16 (Slice 4): Web — `ApiError` gains `code?` on the `'invalid'` tag

- [x] 16.1 RED: a `client.ts` unit test (or type-level test) asserting the `'invalid'` `ApiError` variant accepts an optional `code?: string`, mirroring the existing `'server'` variant's `code?: string` at `client.ts:49`. Landed as runtime tests (17.3) plus a `tsc --noEmit` RED confirmed via `TS2353` before the widening.
- [x] 16.2 GREEN: widen the `'invalid'` member of `ApiError` (`client.ts:33-58`) to `{ tag: 'invalid'; message: string; code?: string }` — additive, no existing producer breaks.

## Phase 17 (Slice 4): Web — client functions gain optional `password`

> Depends on Phase 12 (preview error channel) and Phase 13 (full `code` mapping) — do not start until both are merged.

- [x] 17.1 RED: `client.test.ts` — `previewIngesta(file, password)` appends `password` to the `FormData` **only when non-empty** (empty string indistinguishable from absent — backward compat); `previewIngesta(file)` (no 2nd arg) sends no `password` field at all (byte-identical to today). Confirmed RED (4 failures, right reason — feature didn't exist).
- [x] 17.2 GREEN: `previewIngesta(file: File, password?: string)` (`client.ts:1101-1103`) — conditionally `formData.append('password', password)`.
- [x] 17.3 RED+GREEN: on the 400 branch of `previewIngesta` (`client.ts:1123-1147`), extract `body.code` (in addition to the existing `body.message` extraction) into the returned `ApiError`'s new `code` field.
- [x] 17.4 RED+GREEN: same two changes (optional `password` param + `code` extraction on 400) for `postCommitIngesta` (`client.ts:1252-1300`).

## Phase 18 (Slice 4): Web — retry policy stays fail-closed for the new error

- [x] 18.1 RED: `retry-policy.test.ts` (new file) — confirm `'invalid'` (the tag `PDF_PROTEGIDO`/`PDF_PASSWORD_INCORRECTA` responses use) remains in `TAGS_ERROR_PERMANENTE` — a protected-PDF 400 must never be auto-retried by TanStack Query; the user retries by typing a password, not by the retry machinery.
- [x] 18.2 Confirmed: no production code change needed — the test passed immediately (regression guard held after 16.2's widening).

## Phase 19 (Slice 4): Web — hooks

- [x] 19.1 RED+GREEN: `usePreviewIngesta()` (`use-preview-ingesta.ts`) — mutation variable type changed from `File` to `{ file: File; password?: string }`, forwards both to `previewIngesta(file, password)`.
- [x] 19.2 RED+GREEN: `useCommitIngesta()` (`use-commit-ingesta.ts`) — added `password?: string` to the mutation variables type, forwarded to `postCommitIngesta(file, edits, password)`.
- [x] 19.3 Updated every existing call site of `previewMutation.mutate(seleccionado)` (was a bare `File`) for the new `{ file, password }` shape, including `handleCategoriaCreada`'s re-eval call and the 3 hook-level tests that called `mutate(archivoDePrueba())` directly.

## Phase 20 (Slice 4): Web — `SubirCartola` reactive state machine (D-10)

- [x] 20.1 RED: `SubirCartola.test.tsx` — no password `<input>` is rendered on initial mount (`idle` state) — PDF-10's first scenario.
- [x] 20.2 RED: submitting a locked PDF with no password, mocking `usePreviewIngesta` to reject with `{ tag: 'invalid', code: 'PDF_PROTEGIDO', message: '...' }`, transitions to a new `'preview-protegido'` state and reveals a password `<input type="password" autoComplete="off">`, **without** re-prompting the file picker — the previously-selected `File` object is still referenced (asserted via the retained selected-file readout).
- [x] 20.3 RED: typing a password and clicking "Reintentar" re-submits the SAME `archivo` (`File` reference) plus the typed password — asserted `previewMutation.mutate` was called with `{ file: <same object identity>, password: <typed value> }`.
- [x] 20.4 RED: a `PDF_PASSWORD_INCORRECTA` response (vs `PDF_PROTEGIDO`) is distinguishable in the rendered copy — implemented as `motivoPassword`, a value DERIVED from `previewMutation.error.code` (not a `useState`), since TanStack Query already resets `.error` on every new `mutate()` call — one less piece of state to manually clear, same "small field, not a second machine state" intent as D-10.
- [x] 20.5 RED: `MENSAJE_POR_ESTADO`'s `Record<EstadoSubida, string>` exhaustiveness — TypeScript enforces this at compile time (confirmed by the type error before 20.6's GREEN); a runtime test also asserts the rendered status text for `preview-protegido` differs from `preview-error`'s.
- [x] 20.6 GREEN: added `'preview-protegido'` to `EstadoSubida` and its entry in `MENSAJE_POR_ESTADO`.
- [x] 20.7 GREEN: added `const [password, setPassword] = useState('')`; the requiere-vs-incorrecta distinction is the DERIVED `motivoPassword` from 20.4 (no second `useState` needed — see that entry). `password` is cleared in the same 3 reset paths that already clear `edits`/`previewData` — `procesarArchivoSeleccionado`, `handleDescartar`, `handleSubirOtra`.
- [x] 20.8 GREEN: `estado`'s derivation now branches to `'preview-protegido'` when `previewMutation.isError && motivoPassword !== null` (i.e. `error.code` is `'PDF_PROTEGIDO'` or `'PDF_PASSWORD_INCORRECTA'`), falling through to the existing generic `'preview-error'` branch for every other code.
- [x] 20.9 GREEN: rendered the password field via the existing `CampoTexto` primitive (`type="password" autoComplete="off"`, real `<label>`, `aria-describedby` pointing at the role="alert" message) only in the `'preview-protegido'` state, inside a `<section>` (not a `<form>`), never with a server-echoed value.
- [x] 20.10 GREEN: "Reintentar" calls `handleReintentarPassword`, which calls `previewMutation.mutate({ file: archivo, password })` reusing the retained `archivo` reference (no re-pick).
- [x] 20.11 GREEN: `password` is threaded through to the commit call site (`commitMutation.mutate({ file: archivo, edits, password }, ...)`) so a password typed at preview also works at commit without retyping (PDF-09's second scenario) — also threaded through the `handleCategoriaCreada` preview re-eval call, since a re-run of a previously-unlocked PDF must re-supply the same password (the design's slice list didn't call this out explicitly, but it follows directly from D-06's "backend re-parses every call" invariant).

## Phase 21 (Slice 4): Never-leak constraint at the browser boundary (D-07 layer 4, PDF-07/PDF-10)

- [x] 21.1 RED: a test types a password into the revealed prompt and clicks "Reintentar", then asserts `Storage.prototype.setItem` was never called with a value containing the password AND that `JSON.stringify({...sessionStorage})` never contains it. (`localStorage` itself is `undefined` in this project's jsdom test environment — the shared-prototype spy still covers it; a `localStorage`-specific assertion was dropped after confirming this via `TypeError: Cannot read properties of undefined`.)
- [x] 21.2 RED: confirms the existing `guardarBorrador`/draft-recovery mechanism does **not** serialize `password` into the draft object — types a password, lets preview succeed (the draft-write effect only fires on a successful preview), then asserts the raw `sessionStorage.getItem('md:borrador-revision:v1')` string never contains the typed password.
- [x] 21.3 Confirmed: no new production code was needed beyond Phase 20's React-state-only implementation — both regression guards passed once 20.7-20.11 landed correctly (D-10 held).

## Phase 22 (Slice 4): Verification

- [x] 22.1 `pnpm web test` (141 files / 1791 tests, all green), `pnpm web typecheck` (clean), `pnpm --filter @moneydiary/web lint` (clean after `--fix` for prettier formatting) — all green.
- [x] 22.2 `pnpm api test` (268 files / 2547 tests, unchanged from Slice 3's baseline — this slice touched zero `apps/api` files), `pnpm api exec tsc --noEmit` (clean) — no backend regression.
- [ ] 22.3 **NOT performed** — manual smoke check against a running dev server requires interactive browser access this session did not have. Flagged as a risk/follow-up: a human (or a future Playwright/E2E pass) should upload the Phase 2 fixture (`apps/api/test/fixtures/pdf/protegida-test.pdf`, password `PASSWORD_FIXTURE`) through `pnpm web dev` + `pnpm api dev` before merging to `main`, confirming the prompt appears, the correct password unlocks preview → commit exactly once, and no re-pick is required.
- [x] 22.4 Re-confirmed the proposal's Success Criteria checklist item by item — all 7 items hold: (1) locked PDF → protected error, never `PdfInvalidoError` (Slice 1/3); (2) correct password completes preview AND commit, typed once (Slice 2/4); (3) wrong password → no `Ingesta` row (Slice 2 D-09 carve-out); (4) password never in log/error/response/DB/browser storage (D-07 layers 1-4, this slice's 21.1/21.2); (5) unlocked PDF and `.xlsx` paths unchanged (baselines preserved: api 268/2547, web 141/1791, both only additive); (6) no password field until API reports protected (20.1); (7) `pnpm api test`/`pnpm web test`/`tsc --noEmit` all green (`openapi.json` drift-check unchanged since this slice touched no backend/contract files — last verified clean in Slice 3).
