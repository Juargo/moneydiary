# Design: Web Theme Switch (Clínico frío / Tinta cálida)

## Technical Approach

Every color the web paints becomes a CSS token that has one value in `:root` (light, Clínico frío) and another in `.dark` (dark, Tinta cálida). That includes the bucket fills, the on-wedge pie labels and the wedge separator. A theme switch is then only a class on `<html>`: no component reads theme state to pick a color. Theme state (`light | dark | system`) lives in a small external store (`useSyncExternalStore`) that the two toggles consume. An inline pre-paint script applies the resolved theme before first paint. All values come from `palette-measurements.md`. Delivery is a 7-slice chain, and light cannot be reached until every surface, the pies included, is token-driven (WT-01..09, DCR-04..07, WCFG-02).

## Architecture Decisions

| # | Decision | Alternatives rejected | Rationale |
|---|---|---|---|
| D1 | Custom `--color-*` tokens **stay in `@theme`**, with the **light** value as default. Shadcn raw vars stay in `:root` behind `@theme inline`. One unlayered `.dark {}` block overrides both families. `@theme` keeps its fonts. `--radius` stays theme-invariant in `:root`. | Move every token into `:root` behind `@theme inline`. `data-theme` attribute. | Tailwind 4 utilities for `@theme` tokens already emit `var(--color-x)`, so a runtime override works without moving about 160 lines of documented tokens. `.dark` already matches the declared `@custom-variant`. |
| D2 | `color-scheme: light` on `:root`, `color-scheme: dark` on `.dark`. The script and the controller also set `documentElement.style.colorScheme`. The `select, option` rule stays as it is: it reads `var(--card)`, so it flips on its own. | `color-scheme` only in CSS. | WT-04 names `color-scheme` as a pre-paint obligation. `dark-chrome.e2e.ts` shows the UA reads the root element. |
| D3 | **Pie labels and the separator become CSS tokens**, not `colorEtiquetaPie(bucket, theme)`. Consumers use static class maps (`fill-ahorro`, `bg-ahorro`, `fill-pie-etiqueta-ahorro`, `stroke-pie-separador`). | The proposal's theme-parameterized function. `style={{fill:'var(..)'}}`. | Fills, labels and stroke flip together in the same CSS block, so a half-applied palette cannot exist, and pies stay theme-agnostic. The old "must be literals" argument assumed fills that never followed the theme; a dedicated per-theme token is not a `--card` alias. Class assertions work in jsdom; `var()` inside inline style is unreliable there. **Deviation from the proposal; recorded in ADR-043.** |
| D4 | External store: `crearControladorTema(entorno)` factory, a global instance, and a React context whose **default value** is that instance. No provider mount is needed, and tests inject a fake. | Zustand. A mandatory context provider. Per-component `matchMedia`. | The store must follow the OS even when no toggle is mounted (e.g. `/login`). A factory with injected `storage`/`matchMedia`/`document` is fully testable in jsdom. |
| D5 | **Inline classic `<script>`** in `<head>`. It mirrors `lib/tema.ts`, and a parity test runs the script extracted from `index.html` against the module. | External `public/` script. A Vite plugin that generates the script. | No CSP exists (`vercel.json` has no `headers`; there is no CSP anywhere in `apps/web`). Inline adds no extra render-blocking request. **Trigger:** if a CSP is ever added, allow the script by its `sha256` hash (noted in ADR-043). |
| D6 | Error **text** is split off: a new `--color-error-foreground` token, and the 34 `text-destructive` usages (19 files) plus `BucketDetalleMesPage.tsx:156` migrate to it. `--destructive` stays a fill/border token with white text on it. | Keep one destructive token. Redefine `--destructive` as the text color. | In dark, no single value works for both roles. White text on the fill needs luminance L≤0.183; text on the card needs L≥0.244. Design arithmetic: `#E11D48` on `#22211E` is 3.43:1 and `#BE4E43` is ~3.34:1, both below 4.5. This AA failure already exists today (≈3.95:1 on the current card). Keeps shadcn's meaning of `destructive`; mirrors `exito-foreground`. |
| D7 | **Remove the `dark:` variants** from `ui/button.tsx` and `ui/badge.tsx`. Keep the `@custom-variant` declaration. | Keep them. Re-measure their alpha blends. | They encode shadcn slate-palette tweaks (`bg-destructive/60`, `bg-input/30`) that nobody measured. Removing them keeps what dark renders today, and keeps component classes identical across themes (DCR-07). |
| D8 | Toggles: one `SelectorTema` component built from **native radios** (`fieldset` + `legend`). It has a `compacto` variant: three 32px icon radios (Sun/Moon/Monitor, visually hidden labels). Each instance takes its `name` from `useId()`. | A cycle button (the next state is opaque). A Radix menu. | Native radios give arrow keys and checked-state announcement for free (WT-06, ADR-018). A per-instance `name` stops the Sidebar and Perfil groups from merging into one on desktop. |
| D9 | In Perfil, `Apariencia` is its **own** `SeccionConfig`, ordered: Editar perfil → Cuenta de Google → **Apariencia** → Sesión. Description: "Se aplica al instante en este dispositivo." | Put it inside `PerfilForm`. | The theme applies instantly and is not submitted by `Guardar cambios`. Account-scoped sections come first; the device-scoped ones (Apariencia, Sesión) close the page. |
| D10 | The Sidebar shortcut is injected through the existing `sidebarFooter` in `_authenticated.tsx`. `Sidebar.tsx` is not touched. | Change the `Sidebar` props. | Follows the precedent set by `ApiVersionBadge` and the logout button. |

## Token Table (hex; ratios in `palette-measurements.md`)

| Token | `:root` light | `.dark` dark |
|---|---|---|
| background / foreground | #EDF0F5 / #2A2F3A | #1A1917 / #D5D0C6 |
| card, popover / *-foreground | #F9FAFC / #2A2F3A | #22211E / #D5D0C6 |
| muted / muted-foreground | #E3E7EE / #5A6270 | #2A2825 / #9A9488 |
| accent / accent-foreground | #DCE1EA / #2A2F3A | #302E2A / #D5D0C6 |
| primary / primary-foreground | #1D5FA8 / #FFFFFF | #6FB8BE / #1A1917 |
| secondary / secondary-foreground | #4F4A6B / #FFFFFF | #B0A893 / #1A1917 |
| destructive (fill) | #C1121F | #BE4E43 (product owner, 2026-09-12) |
| border / input / ring | #B6BECC / #7C8798 / #1D5FA8 | #3F3B34 / #7A7362 / #8FCDD2 |
| necesidades / gustos / ahorro / sin-categoria | #4369A2 / #782C5C / #049A78 / #2B2E32 | #77A7E5 / #BB6C90 / #47DAB4 / #696C63 |
| exceso | #C2410C | #BF9350 |
| ingreso = vinculo-activo = semaforo-verde (fill) | #DCFCE7 | #202A1E |
| semaforo-amarillo / semaforo-rojo (fill) | #F3E4C0 / #F8DCE3 | #2B2313 / #2B1F1D |
| verde ink: ingreso-, vinculo-activo-, semaforo-verde-, exito-foreground, semaforo-verde-band | #0F6B4A | #7FB77E |
| amber ink: semaforo-amarillo-foreground, -band, warning-foreground | #8A5000 | #D9A44C |
| red ink: semaforo-rojo-foreground, -band, cargo-foreground, **error-foreground (new)** | #B4143C | #D97A72 |
| warning / warning-border / warning-accent | #F5E7C4 / #B5760A / #EEDBA8 | #2B2210 / #8A6A2E / #332813 |
| pie-etiqueta-{necesidades, gustos, ahorro, sin-categoria} (new) | #FFFFFF / #FFFFFF / #0F1F1A / #FFFFFF | #1A1C1C / #1A1C1C / #1A1C1C / #F0EEE9 |
| pie-separador (new) | #FAFBFD | #100F0D |
| `<meta name="theme-color">` | #EDF0F5 | #1A1917 |

Tokens that share a hex in one row keep **separate literal declarations**: no aliasing, following the `vinculo-activo` precedent. In S1, before the palettes land, the new pie tokens carry today's values (#1a1c1c ×3, #e8e6e1, #0d0f15); in S2, `error-foreground` temporarily carries #fb7185.

## Data Flow

    index.html inline script ──► <html class="dark"?> + style.colorScheme + meta
                                          ▲
    main.tsx: controladorTema.iniciar() ──┤  matchMedia 'change' / window 'storage'
                                          │
    SelectorTema (Perfil) ─┐              │
    SelectorTema (Sidebar)─┴► usePreferenciaTema ─► controller.cambiarPreferencia
                                          │           ├─ localStorage (try/catch)
                                          └───────────┴─ aplicarTema(document)
    CSS (:root / .dark) ──► every token-driven surface, pies included (no JS)

## Interfaces / Contracts

```ts
// lib/tema.ts (pure)
export type PreferenciaTema = 'light' | 'dark' | 'system';
export type TemaResuelto = 'light' | 'dark';
export const CLAVE_PREFERENCIA_TEMA = 'moneydiary:tema';
export const TEMA_FORZADO: TemaResuelto | null; // 'dark' in S6, null from S7. Emergency lever.
export function leerPreferencia(storage: Pick<Storage, 'getItem'> | null): PreferenciaTema; // throws/invalid → 'system'
export function resolverTema(p: PreferenciaTema, osOscuro: boolean): TemaResuelto;
export function aplicarTema(doc: Document, tema: TemaResuelto): void; // class, colorScheme, theme-color meta
// lib/controlador-tema.ts
export interface EstadoTema { readonly preferencia: PreferenciaTema; readonly temaResuelto: TemaResuelto }
export interface ControladorTema {
  obtenerEstado(): EstadoTema;            // stable reference between changes
  cambiarPreferencia(p: PreferenciaTema): void;
  suscribir(listener: () => void): () => void;
  iniciar(): () => void;                  // attaches matchMedia + storage listeners
}
export function crearControladorTema(entorno: { storage: Storage | null; matchMedia?: Window['matchMedia']; documento: Document; ventana: Window }): ControladorTema;
// lib/use-preferencia-tema.ts
export function usePreferenciaTema(): EstadoTema & { cambiarPreferencia(p: PreferenciaTema): void };
// lib/bucket-colors.ts / lib/pie-colors.ts (replace COLOR_BUCKET, COLOR_EXCESO, colorEtiquetaPie, PIE_*)
export function claseRellenoBucket(bucket: string): string;  // 'fill-ahorro' | fallback 'fill-muted-foreground'
export function claseFondoBucket(bucket: string): string;    // 'bg-ahorro' | fallback 'bg-muted-foreground'
export function claseEtiquetaPie(bucket: string): string;    // 'fill-pie-etiqueta-ahorro'
export const CLASE_SEPARADOR_PIE = 'stroke-pie-separador';
```

Pre-paint script. It must not rely on the bundle, so localStorage is read inside `try` and the OS fallback is resolved outside it:

```html
<script>
  (function () {
    var p = null, forzado = 'dark'; // S6; null from S7
    try { p = localStorage.getItem('moneydiary:tema'); } catch (e) {}
    if (p !== 'light' && p !== 'dark') p = 'system';
    var osOscuro = !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    var t = forzado || (p === 'system' ? (osOscuro ? 'dark' : 'light') : p);
    var r = document.documentElement;
    r.classList.toggle('dark', t === 'dark'); r.style.colorScheme = t;
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', t === 'dark' ? '#1A1917' : '#EDF0F5');
  })();
</script>
```

The script only ever applies the resolved enum (`light`/`dark`); the raw stored value never reaches the DOM.

## Flagged Items: Resolution

| Item | Resolution |
|---|---|
| (a) Semáforo anchors | **Confirmed as `-foreground` ink**, with derived tint fills. This matches the shipped fill+ink pattern and `SemaforoHeroCard`'s `bg-semaforo-verde-foreground` dot. |
| (b) Jade vs green | The one real adjacency is the `ResumenAnual` selected month: `bg-ingreso` plus a `border-ingreso-foreground` border around a mini pie with a jade wedge. The hero dot and the donut sit in separate cards; the legend's Ingresos row has no dot. **No palette change.** The (d) card ring also separates the two spatially. DESIGN.md gets a rule: jade and the income green are never neighbors in a categorical set. |
| (c) Dark destructive | Once D6 moves error text off it, `--destructive` is only a fill/border, so the "must stay saturated to read" argument no longer holds. **Recommend `#BE4E43`**: white text 4.82:1 and it fits the low-chroma ramp. It is a product-owner confirmation (Open Question 1). |
| (d) Sin categoría vs ingreso tint | Wrap the mini pie in `ResumenAnual` with `rounded-full bg-card p-0.5`, unconditionally, following the IDEAL-inset cut-out precedent. The wedge edge then touches the card (3.01:1 PASS), not the tint (2.85:1). The pie stays inside its `h-16 w-16` box, so there is no layout shift. |
| (e) shadcn `dark:` classes | Remove them (D7) in S3, the slice where `.dark` first gets applied. |
| Focus indicator | The two-tone approach stays in both themes, with both intervals empty. The bbox outline uses `outline-ring` (#1D5FA8 / #8FCDD2). The on-wedge tone is the thickened `stroke-pie-separador` (3.44–13.17:1 light, 3.58–10.91:1 dark). It flips through tokens, so no theme branch. The call-site comment gets rewritten per theme. |

## File Changes

| File | Action | Description |
|---|---|---|
| `apps/web/src/index.css` | Modify | Light defaults, `.dark` block, new pie and error tokens, `color-scheme` split, docstrings |
| `apps/web/index.html` | Modify | `theme-color` meta; static `class="dark"` (S3), then the inline script (S5) |
| `apps/web/src/main.tsx` | Modify | `controladorTema.iniciar()` |
| `apps/web/src/lib/{tema,controlador-tema,use-preferencia-tema}.ts` (+tests) | Create | Runtime |
| `apps/web/src/lib/prepaint-tema.test.ts` | Create | Script ↔ module parity matrix |
| `apps/web/src/components/SelectorTema.tsx` (+test) | Create | Radiogroup, full and `compacto` variants |
| `apps/web/src/test/contraste-tokens.test.ts` | Create | Parses `index.css`; asserts both themes define every token and meet the measured pair thresholds |
| `apps/web/src/lib/{bucket-colors,pie-colors}.ts` (+tests) | Modify | Class helpers; fix the stale docstring claiming the view-model consumes it |
| `DistribucionPie`, `MiniDistribucionPie`, `LeyendaGasto`, `CategoriasPanel`, `ResumenAnual` (+tests) | Modify | Token classes; mini-pie card ring |
| `configuracion/perfil/PerfilPanel.tsx`, `routes/_authenticated.tsx` | Modify | Apariencia section; sidebar shortcut |
| `components/ui/button.tsx`, `badge.tsx` | Modify | Drop `dark:` variants |
| 19 files using `text-destructive`, `BucketDetalleMesPage.tsx:156` | Modify | → `text-error-foreground` |
| `e2e/dark-chrome.e2e.ts`; `e2e/light-chrome.e2e.ts`, `e2e/tema.e2e.ts` | Modify / Create | Chrome per theme; persistence, no flash, live OS follow, cross-tab |
| `docs/adr/ADR-043-tema-claro-oscuro-web.md`, `docs/adr/README.md`, `CLAUDE.md`, `DESIGN.md` | Create / Modify | Decision record and identities |

`resumen-view-model` and `Sidebar.tsx` are not touched.

## Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit | Resolution matrix; bad or throwing storage; forced mode | Plain `tema.test.ts` |
| Unit | Controller: OS follow only under `system`; `storage` events (matching key and `null`); a failing write still applies the theme; DOM application | Injected fakes |
| Unit | Pre-paint parity | Read `index.html`, run the inline script with `new Function` against stubbed globals, compare with `resolverTema` |
| Unit | Tokens | `contraste-tokens.test.ts`: every themed token exists in both blocks; WCAG ratios ≥ thresholds for the pairs in `palette-measurements.md`. A half-applied palette fails CI. |
| Component | Pies, legend, categorías | Class assertions, no hex (WT-09 import check on the view-model) |
| Component | SelectorTema | Radio roles and names, arrow keys via user-event, two instances stay in sync, `vitest-axe` on both variants |
| E2E | Chrome per theme | `dark-chrome` (card `rgb(34, 33, 30)`); `light-chrome` (root `light`, select face `rgb(249, 250, 252)`) |
| E2E | Runtime | `tema.e2e.ts`: reload restores the choice with the class present at `DOMContentLoaded` while `#root` is still empty; `emulateMedia` live follow; two pages cross-tab |

## Slice Plan (each ≤400 changed lines; light unreachable until S6)

| Slice | Content | Visible change | Rollback |
|---|---|---|---|
| S1 | ADR-043 (+README, CLAUDE.md rows); pie/bucket tokenization using today's values; class helpers; token-relative tests | None | Revert |
| S2 | `error-foreground` token (Tecno value #fb7185) + migrate 34 sites + `BucketDetalleMesPage:156` | Error text becomes AA | Revert |
| S3 | `.dark` block = Tinta cálida; static `<html class="dark">`; D7; mini-pie ring; `dark-chrome` update; dark half of the token test | Dark repaint | Revert (Tecno defaults still in `:root`) |
| S4 | `:root`/`@theme` defaults = Clínico frío; `color-scheme: light`; `light-chrome.e2e` (removes the class in-page); light half of the token test; index.css docstring rewrite | None (unreachable) | Revert |
| S5 | DESIGN.md rewrite | Docs | Revert |
| S6 | Runtime + pre-paint script with `forzado='dark'` + meta + parity tests | None | Revert, or keep the lever |
| S7 | `SelectorTema`, Apariencia, sidebar shortcut, `forzado=null`, `tema.e2e`; chrome specs move to `colorScheme` emulation | Switch live | Set `TEMA_FORZADO`/`forzado` to `'dark'` (one-line hotfix) or revert |

S2 and S7 are the slices most at risk of going over budget; `sdd-tasks` may split them (for example, S7a Perfil, S7b sidebar and e2e).

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification or process-integration boundary. The only untrusted input is the localStorage value. It is checked against an allowlist and never reaches the DOM (only the resolved enum is applied).

## Migration / Rollout

No data migration. A leftover localStorage key is harmless after a revert (nothing reads it).

## Open Questions

- [x] **Product owner:** dark `--destructive` fill → `#BE4E43` (decided 2026-09-12).
- [x] **Measurement pass:** closed — see the addendum in `palette-measurements.md`. Dark `#BE4E43` as text on card is 3.34:1 (fails, confirming D6); white on it 4.82:1; as invalid border 3.34:1 vs card / 3.65:1 vs background; `error-foreground` on its `/10` tint 4.86:1. Light `#C1121F`: white 6.22:1, border 5.96:1, tint text 5.45:1. All pairs used by the design pass.
- [x] **Spec reconciliation:** closed — `specs/web-app/spec.md` WCFG-02 now orders Editar perfil → Cuenta de Google → Apariencia → Sesión and scopes `Guardar cambios` to Editar perfil (aligned with D9 and the shipped `PerfilForm`).
- [ ] Before S7, check the dark Sin categoría fill in the running app (3.01:1 vs card is the tightest margin).
