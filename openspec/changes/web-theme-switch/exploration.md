## Exploration: apps/web light/dark theme switch (Clínico frío ↔ Tinta cálida)

> Materialized by the orchestrator from Engram `sdd/web-theme-switch/explore` (observation #1232); the explore phase had no file-write capability. Content unchanged.

### Current State

`apps/web/src/index.css` declares Tailwind 4 tokens in two blocks: a compile-time `@theme` block (fonts, bucket fills, ingreso/vinculo-activo/semáforo/warning/exito/cargo pairs — 20+ custom tokens) and a `:root` block with shadcn tokens (background/foreground/card/popover/primary/secondary/muted/accent/destructive/border/input/ring, `--radius: 0rem`), remapped into Tailwind utilities via a second `@theme inline` block. `@custom-variant dark (&:is(.dark *))` is declared but nothing ever applies `.dark` — dark is hardcoded as the only identity (`color-scheme: dark` on `:root`, DESIGN.md titled "Tecno-Analítico (Dark Mode)", index.css docstring says "there is no theme toggle"). No theme store, no `prefers-color-scheme` read, no FOUC guard, no `theme-color` meta. `bucket-colors.ts` and `pie-colors.ts` are deliberately theme-immune literal hex modules — their docstrings state they must be re-measured, never auto-derived, whenever the surface tokens they're read against change. Prisma `User` has no preference column. `PerfilPanel.tsx`/`SeccionConfig` already establishes the settings-surface pattern; `Sidebar.tsx` has an existing `footer` slot (used today for `ApiVersionBadge`, injected from `_authenticated.tsx`) that composes without touching `Sidebar`'s own props contract.

### Affected Areas

- `apps/web/src/index.css` — token architecture change: `@theme` (compile-time) tokens that need to vary by theme must migrate into `:root`/`.dark` (runtime); `:root` becomes light values, new `.dark` block added; `color-scheme` must become dynamic.
- `apps/web/src/lib/bucket-colors.ts`, `apps/web/src/lib/pie-colors.ts` — theme-immune literals feeding SVG `fill`/inline `style`; need a per-theme resolution path. The pure `resumen-view-model` does not import them (verified: it imports only `formatear-monto`, `porcentaje` and API types); colors are resolved at the presentation layer in `DistribucionPie.tsx`/`MiniDistribucionPie.tsx`/`LeyendaGasto.tsx`/`CategoriasPanel.tsx`.
- `apps/web/src/components/DistribucionPie.tsx` — two-tone focus indicator derived from a hand-solved luminance interval against dark-only bucket fills/background; must be re-derived per theme.
- `apps/web/index.html` — needs pre-paint theme script (avoid FOUC) and `<meta name="theme-color">`.
- New: a theme hook/context (no `src/stores/` exists yet) and a toggle UI component.
- `apps/web/src/components/app-shell/Sidebar.tsx` (footer slot) and/or `apps/web/src/components/configuracion/perfil/PerfilPanel.tsx` (`SeccionConfig`) — plausible toggle placement, both composable without prop-contract changes.
- `apps/web/src/components/ui/button.tsx`, `badge.tsx` — dormant `dark:` utility classes; once `.dark` applies they activate and need re-validation.
- `apps/web/src/components/BucketDetalleMesPage.tsx:156` — untokenized `text-red-600` (PerfilPanel already fixed the same class of bug by moving to `text-destructive`).
- ~15 unit test files pinning hex literals + 6 `vitest-axe` files + `apps/web/e2e/dark-chrome.e2e.ts` (hardcodes `colorScheme === 'dark'` and `rgb(17, 19, 26)` for `--card`).
- `DESIGN.md` (repo root, title "Tecno-Analítico (Dark Mode)") and lack of any theming ADR.
- Prisma `User` model — no preference field exists; adding one is a schema/migration decision, not free.

### Approaches

**1. Token architecture**
- A. `:root` (light) + `.dark` class override — Tailwind's documented pattern, works directly with the already-declared `@custom-variant dark (&:is(.dark *))`, and is what shadcn's stock `button.tsx`/`badge.tsx` `dark:` classes assume. Pros: zero new Tailwind config, activates dormant `dark:` utilities, trivial FOUC guard (`classList.add('dark')` before paint). Cons: every token inside `@theme` that must vary by theme has to move to `:root`/`.dark` — a real migration. Effort: Medium.
- B. `data-theme="light|dark"` attribute selector — same runtime mechanics. Cons: `@custom-variant dark` is already wired to `.dark` and shadcn's dormant classes assume `.dark`; no concrete benefit with only two themes. Effort: Medium (same migration, plus undoing existing wiring).
- C. `@media (prefers-color-scheme)` only, no manual override — zero JS, but does not satisfy the explicit user-facing switch requirement and cannot persist an explicit choice. Effort: Low but doesn't meet the ask.
- **Recommendation: A** (`:root` + `.dark`). Tokens identical across themes (fonts, `--radius: 0rem`) can stay theme-invariant.

**2. Theme-immune literals (bucket/pie colors)**
- A. CSS custom properties read via `var(--color-necesidades)` etc. in SVG `fill` and inline `style` — single source of truth in `index.css`, flips automatically on `.dark`; `COLOR_BUCKET` keeps only the bucket-key → CSS var mapping. Viable because the view-model does not consume colors.
- B. JS resolver keyed by the active theme returning plain hex — easy to unit test, but duplicates value maintenance and threads a theme argument through every call site.
- **Recommendation: A for flat bucket fills** (move `--color-necesidades` etc. into `:root`/`.dark` with the measured light and dark Brote values); **B for `PIE_LABEL_FILL`/`PIE_LABEL_FILL_LIGHT`/`PIE_WEDGE_STROKE`**, which are already per-bucket conditional logic (`colorEtiquetaPie`) — add a theme parameter (`colorEtiquetaPie(bucket, theme)`).
- `DistribucionPie.tsx`'s two-tone focus indicator: the "empty interval" proof must be re-derived for both Clínico frío and Tinta cálida surfaces.

**3. Theme state & preference**
- Default: **system** (`prefers-color-scheme`) on first visit.
- Options: **three-way (light/dark/system)** — a binary toggle cannot express "follow OS". Cost delta: one extra state + one `matchMedia` listener.
- Persistence: **localStorage only, no `User` column/API.** ADR-024: theme is presentation, not domain data. A synced preference is additive later (register as deferred debt, trigger: "user asks for cross-device theme sync").
- FOUC guard: inline `<script>` in `index.html` `<head>` reading `localStorage` (fallback `matchMedia('(prefers-color-scheme: dark)')`) and setting `classList`/`color-scheme` before first paint.
- Cross-tab sync: `storage` event listener (~5 lines).
- Store choice: a small dedicated hook/context (e.g. `useSyncExternalStore`) rather than the first Zustand store in the codebase — KISS/YAGNI; revisit on a second unrelated global client-state need.

**4. Toggle placement/UX**
- A. Sidebar footer slot — always visible on desktop; `BottomTabs` (mobile width) has no equivalent slot.
- B. Configuración/PerfilPanel as a new `SeccionConfig` — consistent with other account-level preferences, reachable on desktop and mobile width, no new component contract.
- **Recommendation: B primary**, optional compact mirror in the Sidebar footer (explicit yes/no for the owner). A11y: real `<button>`/radiogroup with `aria-checked`/`aria-pressed`, visible focus ring, accessible name announcing the current state (ADR-018, `vitest-axe`).

**5. Missing palette values (design-phase input; WCAG 2.2 AA 4.5:1 text / 3:1 non-text, both themes)**
- `card-foreground`, `popover-foreground`, `primary-foreground`, `secondary-foreground`, `accent-foreground` — no value in either design sheet.
- `destructive` + on-fill text for both themes (shadcn hardcodes `text-white` on `bg-destructive`).
- `--color-ingreso` / `--color-ingreso-foreground` — no light value.
- `--color-vinculo-activo` (+ foreground) — literal, non-aliased; needs its own light measurement.
- Semáforo: `--color-semaforo-{verde,amarillo,rojo}` + `-foreground` + `-band` — 9 tokens, no light value.
- Warning: `--color-warning`, `-border`, `-foreground`, `-accent` — 4 tokens, no light value.
- `--color-exito-foreground`, `--color-cargo-foreground` — no light value; each non-aliased.
- `PIE_WEDGE_STROKE`, `PIE_LABEL_FILL`, `PIE_LABEL_FILL_LIGHT` — re-derive against Clínico frío and Tinta cálida surfaces (shipped dark Brote was measured against the old Tecno card #11131A).
- `DistribucionPie.tsx` two-tone focus derivation — re-solve per theme.
- Shipped Sin categoría dark fill #686663 must be re-measured against Tinta cálida card #22211E.
- `--input`, `--ring`, `--border` — light sheet values exist (input #7C8798, border #B6BECC, ring #1D5FA8) but need the same verified 3:1 non-text treatment the current dark identity documents.

**6. Tests & CI**
- A. Per-theme projects for the whole suite — doubles CI for little value outside e2e.
- B. Token-relative unit assertions (import the constant instead of pinning hex) — theme-safe by construction; contrast still needs a design-review sign-off.
- C. Mirror `dark-chrome.e2e.ts` as `light-chrome.e2e.ts`.
- **Recommendation: B where feasible + C.** `vitest-axe` files need no structural change.

**7. Docs/ADR**
- DESIGN.md title and the `index.css` "dark is the ONLY theme" docstring must be rewritten.
- No ADR covers theming. **Recommend a new ADR** (next number, e.g. ADR-043) recording the two identities, the `:root`+`.dark` mechanism, default=system, localStorage-only persistence, and toggle placement.

**8. Rollout & slicing (chained PRs, ~400-line budget)**
1. Infra + token restructure, no visual change — move varying `@theme` tokens into `:root`, `.dark` mirrors current dark values 1:1, FOUC script + theme hook (theme still forced dark).
2. `.dark` = Tinta cálida (re-measured semáforo/warning/ingreso/pie tokens against #22211E); update `dark-chrome.e2e.ts`.
3. `:root` = Clínico frío + toggle UI (Configuración, tri-state) + persistence + system default.
4. Theme-immune literals per theme (`bucket-colors.ts`/`pie-colors.ts`, `DistribucionPie` re-derivation, `BucketDetalleMesPage.tsx:156` fix).
5. Docs + ADR + test hardening (DESIGN.md, token-relative tests, `light-chrome.e2e.ts`).

**9. Risks / traps verified in code**
- Half-revert/half-apply ships green: pie tests assert literals, not contrast against the current card (documented in `index.css`).
- `button.tsx`/`badge.tsx` `dark:` classes execute for the first time once `.dark` applies — treat as new UI.
- `BucketDetalleMesPage.tsx:156` `text-red-600` will not flip with the theme.
- `resumen-view-model` purity currently respected; keep it.
- Scope creep toward API-synced theme would be an uncosted schema migration — close it off explicitly.
- `dark-chrome.e2e.ts` breaks when dark `--card` changes to `#22211E` (`rgb(34, 33, 30)`).
- Zustand-vs-hook sets precedent for the first global client state in `apps/web`.

### Recommendation

`:root` + `.dark`, a small theme hook/context with localStorage-only persistence and `system` default, a tri-state switch in Configuración/PerfilPanel, CSS-var bucket fills plus a theme-parameterized label/stroke function, and a five-slice chained rollout (inert migration → dark repaint → light + toggle → theme-immune literals → docs/ADR).

### Ready for Proposal

Yes, conditionally — the owner must confirm: default theme, switch cardinality, persistence scope, toggle placement (and Sidebar mirror), state management, and the new ADR.
