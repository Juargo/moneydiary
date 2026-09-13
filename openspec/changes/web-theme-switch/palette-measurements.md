# Palette Measurements — web-theme-switch

Bounded measurement pass feeding the design phase. All ratios computed with the WCAG relative-luminance formula (`contrast()` in `/Users/jorge/.claude/jobs/50994895/tmp/vp.mjs`) and OKLab ΔE×100 (`deltaE()`, same file; Machado-Oliveira-Fernandes 2009 severity-1.0 for protan/deutan). Categorical checks via `validate(palette, {mode, surface, pairs:'all'})`. No value below was estimated — every ratio in this document is a script output. Scratch scripts live under `/Users/jorge/.claude/jobs/50994895/tmp/theme-measure*.mjs` and `search-sincat*.mjs`.

Thresholds used throughout: text 4.5:1 AA, non-text/graphical-object 3:1, categorical normal-vision floor ΔE≥15 (hard gate), CVD floor ΔE≥6 / target ΔE≥8 (6–8 legal only with a secondary encoding — this app already carries one: bucket legends/labels are never color-only).

## Light theme — "Clínico frío"

Surfaces: `background` #EDF0F5, `card` #F9FAFC.

| Token | Value | Against | Ratio | Pass |
|---|---|---|---|---|
| background | #EDF0F5 | — | — | anchor |
| foreground | #2A2F3A | background | 11.74:1 | PASS |
| foreground | #2A2F3A | card | 12.84:1 | PASS |
| card | #F9FAFC | — | — | anchor |
| card-foreground | #2A2F3A (= foreground) | card | 12.84:1 | PASS |
| popover | #F9FAFC (= card) | — | — | derived |
| popover-foreground | #2A2F3A (= foreground) | popover | 12.84:1 | PASS |
| muted | #E3E7EE | — | — | anchor |
| muted-foreground | #5A6270 | card | 5.89:1 | PASS |
| muted-foreground | #5A6270 | muted | 4.96:1 | PASS |
| muted-foreground | #5A6270 | background | 5.38:1 | PASS |
| accent | #DCE1EA | — | — | anchor |
| accent-foreground | #2A2F3A (= foreground) | accent | 10.22:1 | PASS |
| primary | #1D5FA8 | — | — | anchor |
| primary-foreground | **#FFFFFF** | primary | 6.45:1 | PASS |
| secondary | #4F4A6B | — | — | anchor |
| secondary-foreground | **#FFFFFF** | secondary | 8.32:1 | PASS |
| destructive | **#C1121F** | — | — | derived |
| destructive on-fill text | #FFFFFF | destructive | 6.22:1 | PASS |
| border (decorative) | #B6BECC | card | 1.79:1 | N/A — decorative, no floor |
| border (decorative) | #B6BECC | background | 1.64:1 | N/A — decorative, no floor |
| input | #7C8798 | card | 3.48:1 | PASS |
| input | #7C8798 | background | 3.18:1 | PASS |
| ring | #1D5FA8 | card | 6.18:1 | PASS |
| ring | #1D5FA8 | background | 5.65:1 | PASS |

Custom tokens:

| Token | Value | Against | Ratio | Pass |
|---|---|---|---|---|
| ingreso (fill) | **#DCFCE7** | — | — | derived |
| ingreso-foreground | **#0F6B4A** (reused semáforo-verde anchor) | ingreso | 5.93:1 | PASS |
| vinculo-activo | #DCFCE7 (literal dup of ingreso) | — | — | derived |
| vinculo-activo-foreground | #0F6B4A (literal dup) | vinculo-activo | 5.93:1 | PASS |
| semaforo-verde (fill) | **#DCFCE7** (shared w/ ingreso) | — | — | derived |
| semaforo-verde-foreground | #0F6B4A (PO anchor) | semaforo-verde | 5.93:1 | PASS |
| semaforo-verde-band | #0F6B4A (reused as non-text fill) | card | 6.24:1 | PASS |
| semaforo-verde-band | #0F6B4A | background | 5.71:1 | PASS |
| semaforo-amarillo (fill) | **#F3E4C0** | — | — | derived |
| semaforo-amarillo-foreground | #8A5000 (PO anchor) | semaforo-amarillo | 5.16:1 | PASS |
| semaforo-amarillo-band | #8A5000 | card | 6.23:1 | PASS |
| semaforo-amarillo-band | #8A5000 | background | 5.69:1 | PASS |
| semaforo-rojo (fill) | **#F8DCE3** | — | — | derived |
| semaforo-rojo-foreground | #B4143C (PO anchor) | semaforo-rojo | 5.26:1 | PASS |
| semaforo-rojo-band | #B4143C | card | 6.47:1 | PASS |
| semaforo-rojo-band | #B4143C | background | 5.92:1 | PASS |
| warning (fill) | **#F5E7C4** | — | — | derived |
| warning-foreground | #8A5000 (reused semáforo-amarillo anchor) | warning | 5.30:1 | PASS |
| warning-foreground | #8A5000 | card | 6.23:1 | PASS |
| warning-border | **#B5760A** | background | 3.31:1 | PASS |
| warning-border | #B5760A | warning fill | 3.08:1 | PASS |
| warning-accent (hover) | **#EEDBA8** | — | — | derived |
| warning-foreground | #8A5000 | warning-accent | 4.75:1 | PASS |
| exito-foreground | #0F6B4A (= ingreso-foreground) | card | 6.24:1 | PASS |
| exito-foreground | #0F6B4A | background | 5.71:1 | PASS |
| cargo-foreground | #B4143C (= semaforo-rojo-foreground) | card | 6.47:1 | PASS |
| cargo-foreground | #B4143C | background | 5.92:1 | PASS |
| cargo-foreground ≠ destructive | #B4143C vs #C1121F | — | distinct literals | confirmed |
| exceso (fill, unconsumed) | **#C2410C** | card | 4.96:1 | PASS |
| exceso | #C2410C | background | 4.53:1 | PASS |

`color-scheme: light`; `<meta name="theme-color">` = `#EDF0F5` (background).

## Dark theme — "Tinta cálida"

Surfaces: `background` #1A1917, `card` #22211E.

| Token | Value | Against | Ratio | Pass |
|---|---|---|---|---|
| background | #1A1917 | — | — | anchor |
| foreground | #D5D0C6 | background | 11.43:1 | PASS |
| foreground | #D5D0C6 | card | 10.48:1 | PASS |
| card | #22211E | — | — | anchor |
| card-foreground | #D5D0C6 (= foreground) | card | 10.48:1 | PASS |
| popover | #22211E (= card) | — | — | derived |
| popover-foreground | #D5D0C6 (= foreground) | popover | 10.48:1 | PASS |
| muted | #2A2825 | — | — | anchor |
| muted-foreground | #9A9488 | card | 5.34:1 | PASS |
| muted-foreground | #9A9488 | muted | 4.88:1 | PASS |
| muted-foreground | #9A9488 | background | 5.83:1 | PASS |
| accent | #302E2A | — | — | anchor |
| accent-foreground | #D5D0C6 (= foreground) | accent | 8.82:1 | PASS |
| primary | #6FB8BE | — | — | anchor |
| primary-foreground | **#1A1917** (= background, "ground ink") | primary | 7.76:1 | PASS |
| secondary | #B0A893 | — | — | anchor |
| secondary-foreground | **#1A1917** (= background) | secondary | 7.42:1 | PASS |
| destructive | **#E11D48** (reused shipped value; scoped exception, see WARN) | — | — | derived |
| destructive on-fill text | #FFFFFF | destructive | 4.70:1 | PASS |
| border (decorative) | #3F3B34 | card | 1.45:1 | N/A — decorative, no floor |
| border (decorative) | #3F3B34 | background | 1.58:1 | N/A — decorative, no floor |
| input | #7A7362 | card | 3.42:1 | PASS |
| input | #7A7362 | background | 3.73:1 | PASS |
| ring | #8FCDD2 | card | 9.07:1 | PASS |
| ring | #8FCDD2 | background | 9.90:1 | PASS |

Custom tokens:

| Token | Value | Against | Ratio | Pass |
|---|---|---|---|---|
| ingreso (fill) | **#202A1E** | — | — | derived |
| ingreso-foreground | **#7FB77E** (reused semáforo-verde anchor) | ingreso | 6.36:1 | PASS |
| vinculo-activo | #202A1E (literal dup) | — | — | derived |
| vinculo-activo-foreground | #7FB77E (literal dup) | vinculo-activo | 6.36:1 | PASS |
| semaforo-verde (fill) | **#202A1E** (shared w/ ingreso) | — | — | derived |
| semaforo-verde-foreground | #7FB77E (PO anchor) | semaforo-verde | 6.36:1 | PASS |
| semaforo-verde-band | #7FB77E (reused as non-text fill) | card | 6.88:1 | PASS |
| semaforo-verde-band | #7FB77E | background | 7.51:1 | PASS |
| semaforo-amarillo (fill) | **#2B2313** | — | — | derived |
| semaforo-amarillo-foreground | #D9A44C (PO anchor) | semaforo-amarillo | 6.92:1 | PASS |
| semaforo-amarillo-band | #D9A44C | card | 7.18:1 | PASS |
| semaforo-amarillo-band | #D9A44C | background | 7.83:1 | PASS |
| semaforo-rojo (fill) | **#2B1F1D** | — | — | derived |
| semaforo-rojo-foreground | #D97A72 (PO anchor) | semaforo-rojo | 5.30:1 | PASS |
| semaforo-rojo-band | #D97A72 | card | 5.35:1 | PASS |
| semaforo-rojo-band | #D97A72 | background | 5.84:1 | PASS |
| warning (fill) | **#2B2210** | — | — | derived |
| warning-foreground | #D9A44C (reused semáforo-amarillo anchor) | warning | 6.99:1 | PASS |
| warning-foreground | #D9A44C | card | 7.18:1 | PASS |
| warning-border | **#8A6A2E** | background | 3.50:1 | PASS |
| warning-border | #8A6A2E | warning fill | 3.12:1 | PASS |
| warning-accent (hover) | **#332813** | — | — | derived |
| warning-foreground | #D9A44C | warning-accent | 6.44:1 | PASS |
| exito-foreground | #7FB77E (= ingreso-foreground) | card | 6.88:1 | PASS |
| exito-foreground | #7FB77E | background | 7.51:1 | PASS |
| cargo-foreground | #D97A72 (= semaforo-rojo-foreground) | card | 5.35:1 | PASS |
| cargo-foreground | #D97A72 | background | 5.84:1 | PASS |
| cargo-foreground ≠ destructive | #D97A72 vs #E11D48 | — | distinct literals | confirmed |
| exceso (fill, unconsumed) | **#BF9350** | card | 5.75:1 | PASS |
| exceso | #BF9350 | background | 6.28:1 | PASS |

`color-scheme: dark`; `<meta name="theme-color">` = `#1A1917` (background).

### Role interpretation flagged for design-phase sign-off

The prompt's PO anchors gave one hex per semáforo state (`#0F6B4A/#8A5000/#B4143C` light, `#7FB77E/#D9A44C/#D97A72` dark) without saying whether it names the chip **fill** or the chip **foreground**. Measurement settled it empirically: white text on the light anchors passes AA (6.5–6.8:1) but black text fails (3.1–3.2:1); the reverse holds for the dark anchors (black/ink text 7.0–9.4:1, white text fails at 2.2–3.0:1). Both directions are numerically valid in isolation, but only one is architecturally consistent with what's already shipped: the current dark identity uses a **deep/pale tint fill + a distinct, brighter/darker ink text**, and reuses that exact ink literal across `ingreso-foreground`/`vinculo-activo-foreground`/`exito-foreground`/`semaforo-verde-foreground` (all `#4ade80` today). Treating the PO anchors as the **-foreground ink** (mirroring that precedent, and mirroring the retired light "Serene Finance" identity's own `*-100`-fill/`*-700`-text pattern per `index.css`'s docstring) reproduces that exact reuse pattern with real numbers and required inventing only the fill tints (not the inks). This is the recommendation below; if the design phase intended the anchors as literal FILLS with white/black text instead, flag it and this document's derived fill tints are the values to discard, not the anchors.

## Bucket palette ("Brote") — recheck against final surfaces

### Light (fills are PO anchors, unchanged)

| Bucket | Fill | vs card | vs background | Label | Label vs fill |
|---|---|---|---|---|---|
| Necesidades | #4369A2 | 5.32:1 PASS | 4.86:1 PASS | #FFFFFF | 5.55:1 PASS |
| Deseos | #782C5C | 8.69:1 PASS | 7.95:1 PASS | #FFFFFF | 9.08:1 PASS |
| Ahorro | #049A78 | 3.41:1 PASS (tight) | 3.12:1 PASS (tight) | #0F1F1A | 4.79:1 PASS |
| Sin categoría | #2B2E32 | 13.06:1 PASS | 11.94:1 PASS | #FFFFFF | 13.64:1 PASS |

Categorical `validate(pairs:'all')`, surface `#F9FAFC`: Lightness-band/Chroma-floor FAIL (expected — those checks assume a generic categorical ramp, not a deliberately near-black neutral 4th slot; not applicable here). **CVD separation: pass** (worst all-pairs Sin categoría↔Deseos protan ΔE 8.6, ≥ target 8.0). **Normal-vision floor: pass** (worst pair 17.0, ≥ 15.0 hard floor). **Contrast vs surface: pass** (all 4 ≥ 3:1).

Salience check: Ahorro's own contrast (3.41/3.12) is the *lowest margin* of the three spend buckets but its relative luminance (computed below) is the highest, and its label uses the darkest ink of the set (#0F1F1A) — consistent with "most salient."

### Dark — Sin categoría fill required an adjustment (anchor measurement failed)

The PO's shipped dark Sin categoría fill `#686663` was documented as measured only against the **old** Tecno-Analítico card `#11131A`. Re-measured against the new Tinta cálida `card` `#22211E`:

| Bucket | Fill | vs card (Tinta cálida) | vs background |
|---|---|---|---|
| Necesidades | #77A7E5 | 6.47:1 PASS | 7.06:1 PASS |
| Deseos | #BB6C90 | 4.34:1 PASS | 4.74:1 PASS |
| Ahorro | #47DAB4 | 9.17:1 PASS | 10.00:1 PASS |
| Sin categoría | **#686663 → 2.81:1 FAIL** | — | 3.07:1 PASS |

**Adjustment 1 (fill):** `#686663` → **`#696C63`** (R+1, G+6, B unchanged — a near-imperceptible, hue-neutral nudge). This was not a single-variable fix: a naive uniform-lightness lighten to clear the card floor (e.g. `#6D6B68`, tested first) pushes the color close enough to Deseos' plum that the **categorical normal-vision floor fails** (ΔE 14.9, below the 15.0 hard gate) — an anchor-fixing-anchor regression. A brute-force search over the RGB neighborhood for the closest point satisfying all four constraints simultaneously (≥3:1 vs card, ≥3:1 vs background, ≥15.0 ΔE-normal vs Deseos, ≥6.0 ΔE-CVD vs Deseos, ≥4.5:1 for whichever on-wedge label survives) converged on `#696C63`:

| Check | Result |
|---|---|
| vs card | 3.01:1 PASS |
| vs background | 3.28:1 PASS |
| ΔE normal vs Deseos (closest neighbor) | 15.8 PASS (≥15.0) |
| ΔE protan vs Deseos | 7.7 — floor band (6.0–8.0), legal with existing label/legend secondary encoding |
| ΔE deutan vs Deseos | 10.8 PASS |
| ΔE vs Necesidades / Ahorro | 22.5 / 30.3 — comfortable |

**Adjustment 2 (label):** the shipped `PIE_LABEL_FILL_LIGHT` (`#e8e6e1`) no longer clears 4.5:1 on the adjusted fill (4.26:1 FAIL). Nudged to **`#F0EEE9`** → 4.61:1 PASS. `PIE_LABEL_FILL` (`#1a1c1c`, dark label) still fails on this bucket (3.20:1) — Sin categoría still takes the light label exclusively, unchanged role.

Final dark bucket categorical validation (surface `#22211E`, `pairs:'all'`): Lightness-band/Chroma-floor FAIL (expected, same reasoning as light). **CVD separation: floor** (worst pair Sin categoría↔Deseos protan ΔE 7.7 — inside 6–8, legal only with the mandatory secondary encoding this app already has). **Normal-vision floor: pass** (worst pair 15.8). **Contrast vs surface: pass** (all 4 ≥ 3:1, Sin categoría at 3.01:1 is the tightest margin in the set — recommend a manual eyeball check before shipping).

On-wedge labels (card-independent, re-verified against the *unchanged* three fills + the adjusted Sin categoría fill):

| Bucket | Fill | Dark label #1a1c1c | Light label #F0EEE9 |
|---|---|---|---|
| Necesidades | #77A7E5 | 6.88:1 PASS | 1.99:1 FAIL |
| Deseos | #BB6C90 | 4.61:1 PASS | 2.97:1 FAIL |
| Ahorro | #47DAB4 | 9.75:1 PASS | 1.41:1 FAIL |
| Sin categoría | #696C63 | 3.20:1 FAIL | 4.61:1 PASS |

Role assignment unchanged from shipped: Necesidades/Deseos/Ahorro take the dark label, Sin categoría alone takes the light label.

### Mini-pie fills vs the selected-month `ingreso` tint

| Bucket | Fill | Light: vs ingreso #DCFCE7 | Dark: vs ingreso #202A1E |
|---|---|---|---|
| Necesidades | — | 5.06:1 PASS | 6.10:1 PASS |
| Deseos | — | 8.27:1 PASS | 4.09:1 PASS |
| Ahorro | — | 3.24:1 PASS | 8.63:1 PASS |
| Sin categoría | — | 12.42:1 PASS | **2.85:1 FAIL (WARN)** |

Dark Sin categoría's fill (already the tightest-margin bucket) drops just under 3:1 when the cell it sits in is the `bg-ingreso` selected-month tint instead of `bg-card`. Not a hard requirement in this task's token list (only fill-vs-card/background is specified), flagged as a relief case for the design phase — the 1px `PIE_WEDGE_STROKE` separator around every wedge still gives it a boundary regardless.

## Wedge separator (`PIE_WEDGE_STROKE`)

The old literal (`#0d0f15`) was tuned to sit between the old Tecno-Analítico `background`/`card` (`#090a0f`/`#11131a`) and cannot be reused — Tinta cálida's base is both warmer and lighter.

| Theme | New value | vs card | vs background | vs Necesidades | vs Deseos | vs Ahorro | vs Sin categoría |
|---|---|---|---|---|---|---|---|
| Light | **#FAFBFD** | 1.01:1 | 1.10:1 | 5.36:1 | 8.77:1 | 3.44:1 | 13.17:1 |
| Dark | **#100F0D** | 1.19:1 | 1.09:1 | 7.70:1 | 5.16:1 | 10.91:1 | 3.58:1 |

Both clear the ≥3:1 non-text floor against every fill (Ahorro is the tightest in light, Sin categoría the tightest in dark — same buckets that are tightest against the surfaces too) while sitting close enough to their own card/background (≈1.0–1.3:1) to read as "vanishing." Against the selected-month `ingreso` tint: light stroke vs `#DCFCE7` = 1.06:1; dark stroke vs `#202A1E` = 1.26:1 — both still near-invisible there too, so the separator's appearance doesn't change when a wedge sits on the highlighted cell.

## Donut focus-indicator derivation (`DistribucionPie.tsx`)

Re-derived per theme, same method as the shipped comment (an outline's bounding box crosses neighboring wedges, so a single ring color must be checked against every fill, not just the surface).

**Light** — ring `#1D5FA8` vs bucket fills: Necesidades 1.16:1, Deseos 1.41:1, Ahorro 1.81:1, Sin categoría 2.11:1 — **all FAIL** the 3:1 floor (ring vs card 6.18:1 / vs background 5.65:1 both pass fine, so the ring is only a problem where the bbox crosses a fill). Luminances: Necesidades 0.139, Deseos 0.066, Ahorro 0.245, Sin categoría 0.027, background 0.869, card 0.955. Solving for a single opaque tone that clears 3:1 against Ahorro (lightest fill) AND card AND Sin categoría (darkest fill) simultaneously: clearing card/background from below caps the tone at luminance ≤0.285; clearing Ahorro from below requires ≤0.048; clearing Sin categoría (luminance 0.027, itself already near black) requires either ≥0.181 (impossible together with ≤0.048) or a negative luminance (impossible). **The interval is empty** — light theme needs the same two-tone treatment as dark.

**Dark** — ring `#8FCDD2` vs bucket fills: Necesidades 1.40:1, Deseos 2.09:1, Ahorro 1.01:1, Sin categoría (adjusted fill #696C63) **3.01:1 PASS** — all others FAIL. Luminances (final, post-adjustment): Necesidades 0.372, Deseos 0.233, Ahorro 0.548, Sin categoría 0.146, background 0.0098, card 0.0152. Clearing 3:1 against Ahorro (lightest) caps a tone at ≤0.149; clearing background from above requires ≥0.129; clearing Sin categoría (0.146) requires either ≥0.539 or ≤0.015. The window [0.129, 0.149] required by background/Ahorro does not overlap either branch of the Sin categoría constraint → **still empty**, even after the fill's own adjustment moved it slightly lighter (0.133→0.146, which only tightened the conflict).

**Resolution (both themes, mirrors the shipped two-tone pattern):** the indicator carries two tones covering where the other fails —
- the theme's `--ring` (blue #1D5FA8 light / teal #8FCDD2 dark) on the outline's bbox rectangle for the stretches over `card`/`background` (6.18–9.90:1, comfortable), and
- the wedge's own `PIE_WEDGE_STROKE` thickened on focus, tracing the real wedge shape, for the stretches over the fill itself (3.44–13.17:1 light, 3.58–10.91:1 dark, per the table above).

No single-tone shortcut exists in either theme; do not collapse this back to one ring color without re-running this derivation.

## Adjusted anchors (summary)

| Token | Old (PO anchor) | New | Why |
|---|---|---|---|
| Dark `--color-sin-categoria` (bucket fill) | #686663 | **#696C63** | Fails 3:1 vs the new Tinta cálida card (2.81:1); a naive lightness-only fix (#6D6B68) then fails the categorical normal-vision floor vs Deseos (14.9 < 15.0). Minimal RGB nudge (+1R, +6G) clears both. |
| Dark `PIE_LABEL_FILL_LIGHT` | #e8e6e1 | **#F0EEE9** | No longer clears 4.5:1 (4.26:1) against the adjusted Sin categoría fill above; nudged lighter to 4.61:1. |
| Dark `PIE_WEDGE_STROKE` | #0d0f15 | **#100F0D** | Not a PO anchor, but the value cannot survive the base-surface swap (old base #090a0f/#11131a → new #1A1917/#22211E); re-derived from scratch. |
| Light `PIE_WEDGE_STROKE` | #ffffff (old, pre-Tecno "Serene Finance") | **#FAFBFD** | Not a PO anchor; re-derived for the new light surfaces (near-white but not pure white, consistent with "avoid pure white cards"). |

Everything else in the anchor list (`background`, `card`, `muted`, `accent`, `border`, `foreground`, `muted-foreground`, `primary`, `secondary`, `ring`, `input`, all four bucket fills in both themes, and the semáforo verde/amarillo/rojo hexes reinterpreted as -foreground ink per the role note above) measured clean and is used as-is.

## Remaining WARN / relief cases for design-phase review

1. Dark bucket CVD separation sits in the 6–8 "floor" band (worst pair Sin categoría↔Deseos, protan ΔE 7.7) rather than clearing the 8.0 target — legal only because the app never relies on color alone (legend text, `ETIQUETA_BUCKET` labels). Do not remove those secondary encodings without re-deriving this.
2. Dark Sin categoría's own contrast vs card (3.01:1) and vs the selected-month `ingreso` tint (2.85:1, FAIL) are the tightest margins in the whole set — recommend an eyeball check in the actual app before shipping, not just the computed numbers.
3. Hue proximity between Ahorro (jade, the "most salient" bucket) and the semáforo-verde/ingreso green family: light ΔE(normal) 14.4 (just under the 15.0 categorical floor), dark ΔE(normal) 10.1. These are different tokens for different UI roles (donut wedge vs. status/success text) so the strict adjacent-categorical gate doesn't formally apply, but a reader could perceive them as "the same green" side by side — this is exactly the hue-collision risk called out in the task brief. Not fixed here; flagged for explicit design-phase judgment (e.g., cooling one of the two hues slightly).
4. `exceso` (unconsumed today) sits perceptually close to other reds already in the palette — light ΔE vs destructive 6.2, vs semáforo-rojo-foreground 9.2; dark ΔE vs semáforo-rojo-foreground 9.6 (re-tuned from an initial #CC8563 candidate at 4.4, which was too close). If a future feature ever shows `exceso` next to `semaforo-rojo` or `destructive` in the same view, re-validate before shipping.
5. Dark `destructive` (#E11D48, reused shipped value) is a more saturated red than the rest of the low-chroma Tinta cálida ramp — a deliberate, scoped exception (danger colors conventionally stay legible/saturated). A compliant low-chroma alternative exists if the design phase wants strict adherence instead: `#BE4E43` (white text 4.82:1 AA).
6. `border` has no numeric floor in this task's contract (explicitly "decorative") — the low ratios reported for it (light 1.79:1/1.64:1, dark 1.45:1/1.58:1) are informational, not failures.
7. Light `input` vs `muted` (not a required pair per this task's token list, only vs card/background was required) sits at 2.93:1, under 3:1 — informational only.

## Addendum — destructive and error-text pairs (orchestrator measurement, 2026-09-12)

Closes the design's Open Question "measurement pass before S2/S3". WCAG ratios computed with the validator's `contrast()`; tints are alpha composites over the card.

| Theme | Pair | Ratio | Pass |
|---|---|---|---|
| light | error-foreground #B4143C on card #F9FAFC / on background #EDF0F5 | 6.47 / 5.92 | yes |
| light | white on destructive #C1121F | 6.22 | yes |
| light | destructive #C1121F as invalid-input border vs card / background | 5.96 / 5.45 | yes |
| light | error-foreground on bg-destructive/10 over card (#F3E3E6) | 5.45 | yes |
| dark | error-foreground #D97A72 on card #22211E / on background #1A1917 | 5.35 / 5.84 | yes |
| dark | white on destructive #BE4E43 / #E11D48 | 4.82 / 4.70 | yes |
| dark | destructive as invalid-input border vs card: #BE4E43 / #E11D48 | 3.34 / 3.43 | yes |
| dark | destructive as invalid-input border vs background: #BE4E43 / #E11D48 | 3.65 / 3.74 | yes |
| dark | error-foreground on bg-destructive/10 over card: #BE4E43 tint #322622 / #E11D48 tint #352122 | 4.86 / 5.01 | yes |
| dark | destructive (#BE4E43 / #E11D48) used as TEXT on card | 3.34 / 3.43 | no — confirms D6 (separate error-foreground) |
| today | #E11D48 as text on Tecno card #11131A / background #090A0F | 3.95 / 4.21 | no — pre-existing AA failure |
| light / dark | exceso #C2410C / #BF9350 vs card | 4.96 / 5.75 | yes |

Both dark destructive candidates pass every fill/border/tint pair; the choice is aesthetic (product owner).
