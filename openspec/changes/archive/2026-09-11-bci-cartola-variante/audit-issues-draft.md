# Audit issue drafts (Slice 5, Phase 27.3, design.md D-14)

> These 3 issues were **drafted but not filed** via `gh issue create` — `gh` was
> authenticated and available in this apply session, but filing a public
> GitHub issue is a one-way action on the live repo that this session did not
> have explicit instruction to perform. This file is the "explicit artifact"
> the task requires so the finding does not evaporate. To file them for real:
>
> ```bash
> gh issue create --repo Juargo/MoneyDiary --title "<title>" --body-file <(sed -n '/^## Body: <title>$/,/^---$/p' openspec/changes/bci-cartola-variante/audit-issues-draft.md)
> ```
>
> or simply copy each body below into `gh issue create --title "..." --body "..."`.

---

## Issue 1 (headline finding) — BancoEstado: `abono`/`cargo` bands are contiguous, zero dead zone, order reversed

**Trigger:** a real BancoEstado statement measurement, before any band is touched.

**Body:**

`BancoEstadoPdfStrategy.getEstructura().rangosX` (`apps/api/src/infrastructure/pdf/strategies/banco-estado.strategy.ts`) declares:

```ts
{ col: 'abono', xMin: 395, xMax: 460 },
{ col: 'cargo', xMin: 460, xMax: 500 },
```

`abono.xMax === cargo.xMin === 460`. Per the reasoning in `design.md` D-02 (see `bci-cartola-variante` change), a dead zone between the two money columns is what turns a wrong-band amount into a **loud rejection** instead of a **silent sign inversion**. BancoEstado has **no dead zone at all** — and its column order is reversed relative to BCI/Banco de Chile (`abono` on the left, `cargo` on the right).

If BancoEstado's PDF money columns are right-aligned the way BCI's and Banco de Chile's are confirmed to be (measured, `design.md` AMENDMENT A-01) — which is plausible since Chilean bank statement generators share layout conventions — then a short amount landing exactly on the shared boundary would be attributed to the **wrong column with no error raised at all**. This is strictly worse than the bug `bci-cartola-variante` fixes: that bug failed loudly (`EstructuraPdfInvalidaError`); this one, if it exists, would not fail at all.

**Status: unconfirmed.** No real BancoEstado PDF statement is available to this project, and the repo's synthetic fixture (`Últimos_Movimientos_CuentaRUT_test.xlsx` is Excel, not PDF, so there isn't even a PDF fixture) uses left-aligned token positions that cannot expose this defect either way.

**Next step:** the first time a real BancoEstado PDF statement becomes available, run the reconciliation-identity check documented in `design.md` D-13 (`saldoAnterior − Σcargo + Σabono === saldoFinal`) against it. If it fails, this is confirmed as an active money bug, not a theoretical one, and should be triaged with the same urgency as the BCI defect this change fixes.

**Labels (suggested):** `bug` (if you want to track it as a defect) or `tech-debt` (if you prefer to track it as unconfirmed risk), `area:pdf-ingesta`, `bank:banco-estado`.

---

## Issue 2 — Banco de Chile: 5pt dead zone, the thinnest healthy margin

**Trigger:** a real Banco de Chile statement measurement showing a value close to either edge, before any band is touched.

**Body:**

`BancoChilePdfStrategy.getEstructura().rangosX` (`apps/api/src/infrastructure/pdf/strategies/banco-chile.strategy.ts`) declares:

```ts
{ col: 'cargo', xMin: 360, xMax: 445 },
{ col: 'abono', xMin: 450, xMax: 530 },
```

5pt dead zone `[445, 450)` — the thinnest margin among the 3 banks that have one at all (BCI: 10pt after `bci-cartola-variante`; Santander: 45pt). Independently verified in the Slice 5 audit against one real Banco de Chile statement: the balance-reconciliation identity reconciled exactly, so this is **not an active bug**, but the margin is measurably thinner than its siblings.

**Next step:** if a future real statement shows an amount whose left-edge x falls inside or very close to `[445, 450)`, re-measure and consider whether the band needs widening — following the same discipline as `bci-cartola-variante`'s AMENDMENT A-01 (measure first, never widen speculatively).

**Labels (suggested):** `tech-debt`, `area:pdf-ingesta`, `bank:banco-chile`.

---

## Issue 3 (lowest priority, for completeness) — Santander: unusually wide 45pt dead zone, but never systematically recalibrated

**Trigger:** a real Santander statement measurement, before any band is touched.

**Body:**

`SantanderPdfStrategy.getEstructura().rangosX` (`apps/api/src/infrastructure/pdf/strategies/santander.strategy.ts`) declares:

```ts
{ col: 'cargo', xMin: 395, xMax: 450 },
{ col: 'abono', xMin: 495, xMax: 520 },
```

45pt dead zone — the widest of the 4 banks, structurally safe against sign inversion. However, unlike BCI and Banco de Chile, Santander's money-column bands were **never part of the 2026-08-30 recalibration effort against multiple real statements** — they rest on the original synthetic fixture alone. Independently verified in the Slice 5 audit against one real Santander statement: it opened and detected correctly, with no incident, though that sample had few real amounts to exercise the bands.

This is the lowest-priority of the 3 findings — the 45pt margin makes a sign inversion effectively impossible without an amount far wider than anything ever observed in this module — but it is recorded here for completeness per `design.md` D-14.

**Labels (suggested):** `tech-debt`, `area:pdf-ingesta`, `bank:santander`.
