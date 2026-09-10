# Design: ingesta-pdf-password — unlock password-protected PDF statements

> SDD design artifact. Hybrid store — mirror of Engram topic `sdd/ingesta-pdf-password/design`.
> Reads from Engram `sdd/ingesta-pdf-password/proposal` (no `proposal.md` on disk). This is the HOW at
> architectural level. `specs/` is written in parallel by `sdd-spec` — not touched here.
> Every line number below was read against the working tree before being written.

## Technical approach

One optional value (`password`) threaded down an existing path, one new domain error, zero new
dependencies, zero persistence. `pdfjs-dist@6.2.108` already accepts `password` (`types/src/display/api.d.ts:38`)
and already throws `PasswordException` with `PasswordResponses.{NEED_PASSWORD,INCORRECT_PASSWORD}`
(`types/src/shared/util.d.ts:330-339`). Today `pdf-text-extractor.ts:60-65` throws that information away by
flattening every load failure to `PdfInvalidoError`. We stop discarding it.

---

## D-01 — Port signature: trailing `password?: string`, not a carrier object, not a VO

**Decision.** Add a trailing optional parameter to the three port methods:
`IPdfBankDetector.detect(buffer, originalName, password?)` (`pdf-bank-detector.port.ts:17-27`),
`IPdfStructureValidator.validate(buffer, banco, password?)` (`pdf-structure-validator.port.ts:44-54`),
`IPdfTransactionNormalizer.normalize(buffer, banco, password?)` (`pdf-transaction-normalizer.port.ts:18-28`).
**Only `detect`'s error union widens** (see D-03/D-06); the other two unions stay byte-identical.

**Rationale (ISP).** ISP is about consumers depending on members they do not use. A *trailing optional*
parameter imposes no obligation on any caller or implementer — every existing call site and every existing
test double keeps compiling untouched, which is also the backward-compatibility requirement. The interface
is not widened in the ISP sense; it is extended at zero cost to existing consumers.

**Rationale (YAGNI).** A carrier object (`PdfLecturaOptions`) buys nothing today: it would arrive as a
trailing optional parameter anyway, so it is the same signature plus one indirection, for one field with
one producer. A domain VO `ClavePdf` is worse — a VO earns its keep by holding an invariant, and a PDF
password has none (any string is legal; the bank decides). A VO also *adds* a leak surface (`toString`)
where D-07 needs the opposite. Sanctioned escape hatch per `yagni`: if a second option ever appears
(e.g. a per-bank parse hint), that is the 2nd strike — abstract on the 3rd, with real data.

**Rejected.** Options object (speculative indirection); domain VO (no invariant, leak surface);
a mutable extractor field / constructor arg (would make the three shared adapter instances stateful and
request-coupled — worst of the three).

## D-02 — Deprecated `POST /ingestas` gets the error variant, NOT the password field

**Decision.** Split the question the compiler already answers two different ways.

- *Error-union membership is forced.* `ProcessIngestaUseCase` delegates to the shared pipeline and does
  `return Result.fail(pipelineResult.getError())` (`process-ingesta.use-case.ts:186-191`). The moment
  `EjecutarPipelineIngestaError` (`ejecutar-pipeline-ingesta.use-case.ts:52-61`) gains the new member,
  line 190 stops compiling unless `ProcessIngestaError` (`:56-66`) gains it too — and then `aHttpError`'s
  `const _exhaustive: never` (`ingesta.routes.ts:413`) forces the 400 mapping. Not optional. Skipping it
  is a compile error, not a style choice.
- *The request field is not forced.* `ingesta-upload.schema.ts:14-21` stays unchanged; the one-shot route
  (`ingesta.routes.ts:90-117`) never reads a password.

**Consequence, checked not assumed.** The contract stays consistent (no endpoint advertises a field it
ignores) and a locked PDF through the deprecated route gets a strictly better message than today's
"corrupt" — it just cannot be unlocked there. This *also* removes `ingesta-upload.schema.ts` from the
proposal's affected-areas table.

**Load-bearing detail.** `aHttpError` is shared: the preview route calls it at `ingesta.routes.ts:144`
with a `PreviewIngestaError` (`preview-ingesta.use-case.ts:62-71`), which is assignable only because it is
a subset of `ProcessIngestaError`. Preview therefore *cannot* gain the capability without
`ProcessIngestaError` gaining the member — unless preview grows its own mapper, which we reject (DRY: one
error→status table for one taxonomy).

## D-03 — One domain error with a discriminator, not two sibling classes

**Decision.** `apps/api/src/domain/errors/pdf-protegido.error.ts`, shaped like its siblings
(`pdf-invalido.error.ts`, `pdf-sin-texto.error.ts`):

```ts
export type MotivoPdfProtegido = 'requiere-password' | 'password-incorrecta';

export class PdfProtegidoError extends Error {
  constructor(nombreArchivo: string, readonly motivo: MotivoPdfProtegido) { /* … */ }
}
```

**Rationale.** Both cases are the same knowledge ("this PDF is locked") in two sub-states, and both map to
**400** — the status carries no distinction, so status does not motivate two classes. Two classes would
cost 8 union entries (pipeline + process + preview + commit) and 4 `instanceof` branches across the two
`never`-guarded mappers (`aCommitHttpError` `:342-378`, `aHttpError` `:385-416`); one class costs 4 and 2.
The client-visible distinction rides on the response `code`, which the existing
`ErrorTraducido.code` channel already carries (`responder-error-traducido.ts:11-20`, `:51-55`, precedent
`DEMO_SOLO_LECTURA`): one `instanceof` branch reads `error.motivo` and emits
`PDF_PROTEGIDO` or `PDF_PASSWORD_INCORRECTA`.

**On the password-oracle objection — stated, then dismissed.** It does not apply here, and the reason is
specific, not hand-waved: the caller already holds a valid session *and* is supplying the ciphertext in the
same request. The encrypted file is not a server-side asset — the attacker already has the bytes locally
and can brute-force them offline at many orders of magnitude better throughput than through this endpoint.
Distinguishing "needs a password" from "wrong password" therefore discloses nothing the caller does not
already possess. (The objection *would* bite if we ever decrypted a stored, server-side file. Trigger
noted: revisit if a stored-file decrypt endpoint is ever added.)

**Preview route gap (must fix).** `ingesta.routes.ts:144-146` currently does
`res.status(status).json({ message })` — it **drops `code`**. Preview must route through
`responderErrorTraducido` like the mutation surfaces do, or the reactive UI has nothing machine-readable to
branch on. This is the single change that makes D-08 possible.

## D-04 — Detecting `PasswordException` across the dynamic ESM import

**Decision.** Duck-type on `name` + numeric `code`, comparing against constants read from **the same module
namespace object we just awaited** — never hardcoded `1`/`2`, never `instanceof`.

```ts
const pdfjsLib = await import('pdfjs-dist/legacy/build/pdf.mjs'); // pdf-text-extractor.ts:47
// …in the catch:
function motivoPassword(e: unknown, R: { NEED_PASSWORD: number; INCORRECT_PASSWORD: number }) {
  if (!(e instanceof Error) || e.name !== 'PasswordException') return null;
  const code = (e as { code?: unknown }).code;
  if (code === R.NEED_PASSWORD) return 'requiere-password' as const;
  if (code === R.INCORRECT_PASSWORD) return 'password-incorrecta' as const;
  return null; // → falls through to PdfInvalidoError, i.e. today's behavior
}
```

**Why not `instanceof pdfjsLib.PasswordException`.** Two independent reasons. (1) The shipped type is
`declare const PasswordException_base: any` (`util.d.ts:330-335`) — TS gives zero help, so the check would
be `any`-typed anyway. (2) pdfjs reconstructs rejection reasons across the worker-message boundary
(`wrapReason`); prototype identity survives only because Node currently runs the *fake* worker in-realm. A
future pdfjs/Node change to that setup silently breaks `instanceof` and regresses to `PdfInvalidoError` —
exactly the failure mode we are asked to prevent. `name` + numeric `code` is what pdfjs preserves across
that boundary. Duck-typing is also already this file's idiom (`'str' in item`, `pdf-text-extractor.ts:77`).

**How a pdfjs upgrade fails LOUDLY (three tests, one of them the alarm).**

| # | Test | Fails when |
|---|---|---|
| 1 | **Constant-pin** (alarm): import pdfjs the same way; assert `PasswordResponses.NEED_PASSWORD` and `.INCORRECT_PASSWORD` are both `number` and differ | pdfjs renames/removes the namespace or changes the type → RED with an unmistakable message pointing at the library, not at our code |
| 2 | **Behavioral**, against the encrypted fixture: no password → `requiere-password`; wrong → `password-incorrecta`; correct → `Result.ok(tokens)` | detection silently regresses to `PdfInvalidoError` |
| 3 | **Negative regression**: corrupt buffer still → `PdfInvalidoError` | the new branch over-captures |

Test 2 is the net; test 1 exists so the *cause* is obvious instead of a mysterious behavioral failure.

## D-05 — Validator and normalizer forward the password but do NOT widen their error unions

**Decision.** `PdfjsStructureValidatorService` and `PdfjsTransactionNormalizerService` pass `password` to
their own `PdfTextExtractor` and keep returning `EstructuraPdfInvalidaError | RangoFechasInvalidoError`.

**Rationale.** Both already **swallow** every extractor error into
`EstructuraPdfInvalidaError(banco, [{tipo:'PdfIlegible'}])` (`pdfjs-structure-validator.service.ts:66-71`,
`pdfjs-transaction-normalizer.service.ts:74-79`). That masking is harmless *only* because of the pipeline
invariant in D-06: detect runs first with the same password, so a password failure can never reach stage 2
or 3. Widening two more unions for an unreachable branch is textbook YAGNI.
**Invariant to record in code comments:** if any future caller invokes the validator or normalizer without a
preceding `detect`, the masking returns and a locked PDF reads as "malformed structure".

## D-06 — Fast failure: one parse, not three

**Verified, not assumed.** `ejecutar-pipeline-ingesta.use-case.ts:131-142` runs `detectPdfBankUseCase`
first and returns on failure *before* validate/normalize. So a wrong or missing password costs **one**
parse and surfaces from stage 1 — the "3× re-parse now fails 3 times" worry does not materialize. The
accepted 3× re-parse (documented at `pdfjs-transaction-normalizer.service.ts:20-26`; three independent
`new PdfTextExtractor()` at `:27`, `:27`, `:35`) is **out of scope** and is not refactored here; it only
costs on the *success* path, exactly as today.

## D-07 — The password cannot reach an error message (constraint, not intention)

Four layers, the first of which is structural:

1. **Unrepresentable.** `PdfProtegidoError`'s constructor takes `(nombreArchivo, motivo)`. The password is
   not a parameter, so interpolating it is a compile error. This is the actual control.
2. The extractor never forwards the raw pdfjs message either — it constructs its own, as the file already
   does for `PdfInvalidoError`.
3. **No logging channel.** The password is never placed in a `logger.*` context object. Pipeline logging
   emits `{banco, totalFilas}` only (`ejecutar-pipeline-ingesta.use-case.ts:178-181`). ADR-033 Pino
   redaction is a *backstop*, never the primary control.
4. **No echo path.** The route reads `req.body.password` into a local and passes it on;
   `responderErrorTraducido` emits only `{message, code, indice}` (`:51-55`).

Test: assert the thrown error's `message` does not contain the fixture password, and (D-09) that the
FALLIDA writer — the one component that *persists* `.message` — was never called.

## D-08 — Contract: optional multipart text field on preview + commit only

`password` joins `previewIngestaRequestSchema` (`ingesta-preview.schema.ts:11-18`) and
`commitIngestaRequestSchema` (`ingesta-commit.schema.ts:19-35`) as
`z.string().optional().describe(...)` — copying the `edits` precedent verbatim (`:26-34`). Zod →
`openapi.json` → `packages/api-client` via `pnpm contract:sync`; CI `openapi:check` catches a half-sync.

**Multer claim — VERIFIED, not assumed.** `.single('file')` parses non-file fields into `req.body`
(commit already relies on it at `ingesta.routes.ts:175-178`), and busboy's default `fieldSize` is
**1 MiB** (`busboy@1.6.0/lib/types/multipart.js:251-253`) when `limits.fieldSize` is absent. So
`subirArchivo()` (`:266-287`, `fileSize` only — used by preview) accepts the field with **no
reconfiguration**, and `subirArchivoConEdits()` (`:296-333`, `fieldSize: 256 KB`) is comfortably above a
password. The only asymmetry: `subirArchivo()` has no `LIMIT_FIELD_VALUE` → 400 mapping, so a >1 MiB
password field would 500. Mitigation (one guard clause, KISS): the preview handler rejects a `password`
over a fixed character cap with 400 before use. Do **not** duplicate the `LIMIT_FIELD_VALUE` block into
`subirArchivo()` — that would change behavior for the one-shot route too, which D-02 keeps untouched.
Never put an example password in a `.describe()`.

## D-09 — The FALLIDA carve-out, and why the `never` guards will not save us

**Decision.** The branch lives at `commit-ingesta.use-case.ts:210-218`, at the single call site that turns
a pipeline failure into a history row:

```ts
if (pipelineResult.isFail()) {
  const error = pipelineResult.getError();
  if (!(error instanceof PdfProtegidoError)) {
    await this.registrarFallo(input.userId, input.fileReader.getOriginalName(), error.message);
  }
  return Result.fail(error);
}
```

**Why there and nowhere else.**

| Candidate location | Rejected because |
|---|---|
| Inside `registrarFallo` (`:449-472`) | SRP: the helper's one job is "write a FALLIDA row". It would also silently affect the outer-catch caller at `:188`, a *different* situation (mid-flight explosion after the pipeline already succeeded — unreachable for a locked PDF) |
| The `IRegistrarIngestaFallidaWriter` adapter | ADR-005 violation: infrastructure deciding a product rule, invisible to the use case that owns the policy |
| The route handler | Too late — the write has already happened by the time the route sees the error |
| `EjecutarPipelineIngestaUseCase` | It knows nothing about `Ingesta` rows; writes are deliberately excluded from the shared pipeline (its D-01) |

**⚠ The `never` guards will NOT catch a missed carve-out.** `const _exhaustive: never` at
`ingesta.routes.ts:375` and `:413` proves only that every error variant is *mapped to a status*. It says
nothing about whether a row was written on the way out. A missing carve-out compiles, typechecks, lints
clean, and returns the correct 400 with the correct message — while quietly writing one `Ingesta` row per
password attempt. The **only** detector is a test asserting `ingestaFallidaWriter.registrar` was **not**
called. That test is mandatory in the same slice as the carve-out; the carve-out must not merge without it.

**One-shot deliberately excluded.** `ProcessIngestaUseCase` registers FALLIDA the same way
(`process-ingesta.use-case.ts:124`) and is **not** carved out: without a password field (D-02) there is
exactly one attempt, so it cannot pollute history the way three commit retries would, and today it already
records that file as invalid. Registered as debt with an explicit trigger (`yagni`, the 11.6 idiom):
**if `POST /ingestas` ever gains the password field, the carve-out moves with it.**

## D-10 — Web: reactive reveal, ephemeral state, same `File`

**State machine.** `EstadoSubida` (`SubirCartola.tsx:62-69`) gains one member: `'preview-protegido'`.

```
idle ─(pick)→ previsualizando ─(ok)→ preview-listo ─→ committing → exito
                    │                                      └─(protegido)→ preview-protegido
                    ├─(400 PDF_PROTEGIDO|PDF_PASSWORD_INCORRECTA)→ preview-protegido
                    │        └─(type password + Reintentar, SAME `archivo`)→ previsualizando
                    └─(other fail)→ preview-error
```

A real member, not a hidden sub-branch of `preview-error`, because `MENSAJE_POR_ESTADO` is a
`Record<EstadoSubida, string>` (`:77-88`) that is deliberately type-exhaustive — a new member *forces* the
copy to be written. Overloading `preview-error` would defeat the repo's own mechanism and make the machine
lie. The requerida-vs-incorrecta nuance stays in a small separate state field, not a second machine state:
one word of copy does not justify doubling every switch.

**Where the password lives.** `const [password, setPassword] = useState('')` in `SubirCartola`, cleared in
the same three reset paths that already clear `edits`/`previewData` — `procesarArchivoSeleccionado`
(`:443`), `handleDescartar` (`:668`), `handleSubirOtra` (`:711`). Retry needs no re-pick: `archivo` is set
at `:482` and cleared *only* in those three paths, so a failed preview preserves the selected `File`.

**Never `localStorage`/`sessionStorage`** — three independent reasons: (a) both are origin-scoped and
outlive the component, so any XSS or any later script on the origin reads verbatim a key that decrypts the
user's full financial history; (b) they survive logout, leaking to the next user of a shared machine;
(c) it is a credential for a *third party* (the bank's file) — commonly a RUT or a reused password — so the
blast radius exceeds MoneyDiary. React state dies with the tab and is never serialized. The input is
`type="password"` with `autoComplete="off"`, outside any autofillable `<form>`, and never rendered with a
server-echoed `defaultValue`.

**Client plumbing.** `previewIngesta(file, password?)` (`client.ts:1185-1270`) and
`postCommitIngesta(file, edits, password?)` (`:1336-1342`) append `password` **only when non-empty**, so
empty string is indistinguishable from absent and backward compat holds. `ApiError`'s `'invalid'` variant
(`client.ts:33-58`) gains `code?: string`, mirroring exactly what was already done for `'server'` at `:49`
— additive, established precedent, no behavior change. `'invalid'` stays in `TAGS_ERROR_PERMANENTE`
(`retry-policy.ts:16-19`): a protected-PDF 400 must not be auto-retried; the user retries by typing.
Hook variables change `File` → `{file, password?}` (`use-preview-ingesta.ts:22-32`) and gain `password?`
(`use-commit-ingesta.ts:25-49`).

## D-11 — Encrypted fixture: hand-rolled RC4-40, committed alongside its generator

**Decision.** `apps/api/test/fixtures/pdf/protegida-test.pdf` + committed generator
`generar-protegida-test.ts`, following the two existing precedents exactly
(`generar-bci-cartola-montos-grandes-test.ts`, `generar-bancochile-…`): raw PDF written by hand, regenerated
with `pnpm exec tsx test/fixtures/pdf/generar-protegida-test.ts`.

Standard security handler **V=1 / R=2 (RC4-40)**: MD5 from `node:crypto`, RC4 as ~20 lines of pure JS.
**No new dependency** — decisive, because `.npmrc` enforces a 7-day quarantine and ADR-021 gates SCA, so a
fixture-only dependency would be disproportionate. AES-128 (V=4/R=4) would use Node's native cipher but
needs crypt-filter dictionaries for no additional test value. RC4-40 being cryptographically dead is
*desirable* here (weak, public, reproducible) — the generator docblock must say so, so a future security
review does not "fix" the fixture. The password is an obviously-fake kebab literal named
`PASSWORD_FIXTURE`, declared in the generator docblock and re-declared in the spec (not a gitleaks shape).

**Committed vs generated at test time.** Commit both. Trade-off, stated: the committed binary keeps
`pnpm api test` with no generation step and CI deterministic, at the cost of a small opaque blob that only
the generator explains; generating at test time removes the blob but adds a build step to every run and
makes a broken generator look like a broken extractor. Precedent + KISS win.

---

## Slices (strict TDD — RED first, each independently revertible)

| Slice | Scope | First RED test |
|---|---|---|
| 1 | `pdf-protegido.error.ts`, extractor password + D-04 detection, fixture + generator | protected PDF, no password → `PdfProtegidoError('requiere-password')` |
| 2 | 3 ports/adapters/use cases (D-01/D-05), pipeline input + union, **D-09 carve-out** | pipeline stub returns `PdfProtegidoError` → `registrarFallo` **not** called |
| 3 | Zod schemas, preview via `responderErrorTraducido` (D-03), both `never` mappers, `contract:sync` | `POST /preview` with locked PDF → 400 + `code: 'PDF_PROTEGIDO'` |
| 4 | `client.ts`, 2 hooks, `SubirCartola` state machine | no password field on `idle`; appears after a `PDF_PROTEGIDO` 400; retry reuses the same `File` |

## Open questions

- None blocking. All three proposal questions are resolved (D-01, D-02, D-03).
