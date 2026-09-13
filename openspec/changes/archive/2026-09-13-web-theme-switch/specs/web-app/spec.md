# Delta for web-app

## ADDED Requirements

### Requirement: DCR-04 — Authenticated app shell uses the Clínico frío background identity

The `--background` token MUST resolve to the Clínico frío light-mode value
(measured in the design phase to satisfy WT-07), applied app-shell-wide via
the existing `bg-background` usage. The value MUST come from the theme's
`:root` block, not a hardcoded literal.

#### Scenario: App shell background resolves to the Clínico frío value

- GIVEN the authenticated web app renders in light (Clínico frío) mode
- WHEN the app shell's computed background is inspected
- THEN it resolves to `--background` as defined in `:root` for Clínico
  frío — not the previous Serene Finance `#e8f0fa`

(Previously: pinned to the exact literal `#e8f0fa`; the light identity
itself changes to Clínico frío, with values measured in the design phase.)

### Requirement: DCR-05 — Primary token uses the Clínico frío identity value

The `--primary` token MUST resolve to the Clínico frío light-mode value
(design-phase measured). Components referencing `--primary` (buttons,
headings) MUST reflect it without component-level changes.

#### Scenario: Primary-styled elements pick up the Clínico frío primary

- GIVEN a button or heading styled with the `primary` token in light mode
- WHEN its computed color/background is inspected
- THEN it resolves to `--primary` as defined in `:root` for Clínico frío —
  not the previous Serene Finance `#2260b2`

(Previously: pinned to the exact literal `#2260b2`.)

### Requirement: DCR-06 — Light and dark pairings meet WCAG 2.2 AA (ADR-018)

Every color pairing rendered in either theme (Clínico frío light, Tinta
cálida dark) — including income text on income fill, primary on background
or white, and every pairing covered by `web-theme` WT-07 — MUST meet WCAG
2.2 AA: text ≥4.5:1, non-text UI ≥3:1.

#### Scenario: Documented pairings meet AA contrast in both themes

- GIVEN the full set of themed color pairings, evaluated once per theme
- WHEN their contrast ratios are computed against that theme's own
  background/card surface
- THEN every text pairing is ≥4.5:1 and every non-text pairing is ≥3:1

(Previously: pinned three specific ratios — 6.78:1, 6.21:1, 5.40:1 — against
the single old light identity. Generalized to a per-theme threshold
obligation since exact Clínico frío/Tinta cálida values are a design-phase
output.)

### Requirement: DCR-07 — Dark mode is the Tinta cálida identity

Dark mode MUST render the Tinta cálida identity, replacing the previous
Tecno-Analítico values, and MUST meet the DCR-06 thresholds. Both `:root`
(Clínico frío) and `.dark` (Tinta cálida) MUST render without regression —
no removed rule, no broken component — and switching between them MUST NOT
alter DOM structure.

#### Scenario: Dark mode renders the Tinta cálida identity

- GIVEN the app is switched to dark
- WHEN the dashboard renders
- THEN `.dark` resolves to Tinta cálida token values (not the previous
  Tecno-Analítico values) and the layout renders without errors

#### Scenario: Switching theme does not change layout structure

- GIVEN the same page rendered once in light and once in dark
- WHEN DOM structure (excluding color/style values) is compared
- THEN the structure is unchanged

(Previously: asserted dark was untouched by this change — "Only light-mode
`:root` tokens change" / "`.dark` theme MUST continue to render without
regression." Superseded: dark is now itself the changed identity.)

## MODIFIED Requirements

### Requirement: WCFG-02 — Perfil layout matches the verbatim visual contract (CA-02)

The Perfil screen MUST render, in order: the shared `Configuración` `<h1>`
owned by the layout route; a vertical section-tab list whose `Perfil` entry
carries `aria-current="page"` and whose `Categorías` entry is a real, active
`<Link>` to `/configuracion/categorias`; the panel's own `Editar perfil`
heading, one level below the shared `<h1>`; four `SeccionConfig` blocks in
this exact order — `Editar perfil` (`Nombre`/`Email`, `Cambiar password`
with `Password actual`/`Password nueva`, and a right-aligned `Guardar
cambios` button scoped to this block), `Cuenta de Google`, `Apariencia`,
`Sesión`. `Guardar cambios` MUST submit only the identity/password fields;
it MUST NOT submit the Apariencia choice. The `Apariencia` block MUST apply
the selected theme instantly, on the current device, without a save action;
MUST carry the description "Se aplica al instante en este dispositivo.";
MUST use the same divided-block visual pattern as its siblings; and MUST
contain the theme toggle described by `web-theme` WT-06 (keyboard-operable,
accessible name and current-state). The Google block MUST render exactly
one of two structurally symmetric states, driven by `me.googleVinculado`.

#### Scenario: The shared heading precedes the panel heading

- GIVEN an authenticated session on `/configuracion`
- WHEN the page renders
- THEN the `Configuración` heading is the page's top-level heading and
  `Editar perfil` is one level below it, inside the routed panel

#### Scenario: The Categorías tab is no longer inert

- GIVEN an authenticated session on `/configuracion`
- WHEN the user activates the `Categorías` tab
- THEN it navigates to `/configuracion/categorias` — a real `<Link>`, never
  disabled, without `aria-disabled`

#### Scenario: The four blocks render in the fixed order, Guardar cambios scoped to the first

- GIVEN an authenticated session on `/configuracion`
- WHEN the page renders
- THEN the blocks appear in order `Editar perfil`, `Cuenta de Google`,
  `Apariencia`, `Sesión`, and the `Guardar cambios` button renders only
  inside `Editar perfil`, right-aligned within that block — no block after
  it carries a save action

#### Scenario: Apariencia applies the theme instantly, without Guardar cambios

- GIVEN the Apariencia block renders
- WHEN the user selects a different theme option
- THEN the choice applies immediately to the current device without
  activating `Guardar cambios`, and the block exposes the theme toggle
  described by `web-theme` WT-06 (keyboard-operable, accessible name and
  current-state)

#### Scenario: Linked state renders the green pill and Desvincular

- GIVEN `me.googleVinculado` is `true`
- WHEN the Cuenta de Google block renders
- THEN it shows the pill `Vinculada: {me.email}` and a `Desvincular` button

#### Scenario: Not-linked state renders the neutral pill and Vincular

- GIVEN `me.googleVinculado` is `false`
- WHEN the Cuenta de Google block renders
- THEN it shows a neutral `No vinculada` pill and a `Vincular con Google`
  button, in the same layout position `Desvincular` would occupy

(Previously: the page's first heading was `Editar perfil` and `Categorías`
was an inert placeholder — both already superseded by WCTG-01/§1 and
retained here. Immediately before this change, the panel had exactly three
`SeccionConfig` blocks — `Editar perfil`, `Cuenta de Google`, `Sesión` —
with `Guardar cambios` already scoped to `Editar perfil`, and no
appearance/theme control. `web-theme` inserts a fourth block, `Apariencia`,
between `Cuenta de Google` and `Sesión` — design decision D9 — and confirms
`Guardar cambios` stays scoped to `Editar perfil`, never submitting the
device-local theme choice.)

## REMOVED Requirements

### Requirement: DCR-04 — Authenticated app shell uses the pale-blue background token

(Reason: web-theme-switch replaces the retired single light/dark identity values with the measured Clínico frío / Tinta cálida themes; the requirement keeps its ID and is re-added above under its new title.)

(Migration: none — same ID, rewritten requirement in ADDED above.)

### Requirement: DCR-05 — Primary token is `#2260b2` in light mode

(Reason: web-theme-switch replaces the retired single light/dark identity values with the measured Clínico frío / Tinta cálida themes; the requirement keeps its ID and is re-added above under its new title.)

(Migration: none — same ID, rewritten requirement in ADDED above.)

### Requirement: DCR-06 — New color pairings meet WCAG 2.2 AA (ADR-018)

(Reason: web-theme-switch replaces the retired single light/dark identity values with the measured Clínico frío / Tinta cálida themes; the requirement keeps its ID and is re-added above under its new title.)

(Migration: none — same ID, rewritten requirement in ADDED above.)

### Requirement: DCR-07 — Dark mode is unaffected

(Reason: web-theme-switch replaces the retired single light/dark identity values with the measured Clínico frío / Tinta cálida themes; the requirement keeps its ID and is re-added above under its new title.)

(Migration: none — same ID, rewritten requirement in ADDED above.)

