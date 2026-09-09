# Delta for Ingesta Management — Password-Protected PDF Carve-Out

> SDD spec artifact. Hybrid store — mirror of Engram topic `sdd/ingesta-pdf-password/spec`.
> Deltas `openspec/specs/ingesta-management/spec.md`. Narrow, single-requirement carve-out
> required for consistency with the `pdf-ingesta` delta in this same change (requirement PDF-08):
> without this modification, ING-07's "every terminal pipeline failure" wording would be false
> once password-protected-PDF handling ships.

## MODIFIED Requirements

### Requirement: ING-07 — Early pipeline failures are recorded with direct userId isolation

The system MUST persist a `FALLIDA` `Ingesta` row for every terminal pipeline failure, including
failures before an `Account` is resolved (invalid extension, unrecognized bank), **except** a
commit-time failure caused by a password-protected PDF with no password supplied, or with an
incorrect password (`pdf-ingesta` PDF-08). That specific case is a client-correctable input
validation error, not a recorded ingesta outcome, and MUST NOT create any `Ingesta` row — neither
`FALLIDA` nor `PROCESADA`. Every other terminal failure category is unaffected by this exception
and continues to be recorded exactly as before. Each recorded row MUST carry `userId` (NOT NULL,
from the authenticated request) directly on `Ingesta`, independent of `accountId`.
`accountId`/`banco` MAY be null. `motivoFallo` MUST be set. The invariant
`estado = PROCESADA ⟹ accountId IS NOT NULL` MUST hold.

(Previously: this requirement stated, without exception, that every terminal pipeline failure is
recorded as a `FALLIDA` row. This change carves out the new password-protected-PDF validation
error, which must NOT be recorded at all.)

#### Scenario: Unrecognized-bank upload is recorded as FALLIDA (unchanged)

- GIVEN an authenticated user uploads a cartola whose bank cannot be detected
- WHEN the upload completes
- THEN a row exists with `estado=FALLIDA`, `userId` set, `banco=null`, `nombreArchivo` set, and a
  descriptive `motivoFallo`

#### Scenario: Invalid-extension upload is recorded as FALLIDA (unchanged)

- GIVEN a user uploads a `.docx` file
- WHEN validation rejects it
- THEN a `FALLIDA` row is recorded with `nombreArchivo` and a `motivoFallo` describing the invalid
  extension

#### Scenario: A password-protected PDF failure at commit is NOT recorded (new exception)

- GIVEN a user submits a password-protected PDF to commit with no password, or with an incorrect
  password, any number of times
- WHEN each attempt completes
- THEN no `Ingesta` row — `FALLIDA` or otherwise — is created for any of those attempts

## Non-Goals

| Excluded | Reason |
|----------|--------|
| Any change to failure categories other than password-protected PDFs | This is a single, narrow exception; every other `FALLIDA` recording behavior is unchanged |
| A new `EstadoIngesta` value for "rejected input" | The absence of a row is itself the signal; no new enum value is introduced |
