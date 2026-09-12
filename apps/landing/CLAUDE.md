# apps/landing — Notas técnicas (gotchas)

Conocimiento no obvio de la landing — durable, no derivable de un vistazo. Arquitectura, convenciones y ADRs viven en el `CLAUDE.md` raíz y en `docs/adr/`.

- **Tailwind 4 CSS-first:** la utility `rounded` a secas lee el token `--radius` — el nombre `--radius-DEFAULT` se ignora en silencio y `rounded` cae al fallback de 4px sin error de build. Al tocar tokens de `@theme`, verificar el mapping en el CSS de `dist/`.
- **Tipografía:** DM Sans (cuerpo) + Plus Jakarta Sans (títulos) con tinta `#022030` — excepción scoped documentada en `DESIGN.md` (las apps siguen en Inter).
- **Header sticky:** exige `scroll-mt-*` en los targets de anchors (`#como-funciona`, `#main`).
