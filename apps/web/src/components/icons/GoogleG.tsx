/**
 * GoogleG — the official Google "G" mark, inlined verbatim.
 *
 * WHY INLINE AND NOT A DEPENDENCY. ADR-027 settles `lucide` as the project's
 * icon set, but lucide ships no Google mark: the only brand glyphs it still
 * carries are three Feather leftovers (`apple`, `facebook`, `github`), and
 * those are monochrome strokes — a redrawn approximation of this logo would
 * breach Google's branding rules anyway. Pulling a whole icon package for a
 * single asset would also fight ADR-006's supply-chain quarantine for no
 * gain, so the mark lives here as source.
 *
 * TRADEMARK. This is Google's trademark, reproduced UNMODIFIED. Do not
 * recolor it (not even to `currentColor`), do not distort its aspect ratio,
 * do not crop it, and do not reuse it as a decorative icon anywhere other
 * than the Google authentication entry point. The button that carries it
 * must keep one of Google's approved strings — this app uses "Continuar con
 * Google" — and leave clear space around the mark. Reference:
 * Google Identity branding guidelines
 * (developers.google.com/identity/branding-guidelines).
 *
 * PROVENANCE. The four `d` attributes and the `0 0 48 48` viewBox below were
 * diffed byte-for-byte against the SVG that Google's own "Sign in with
 * Google" client (`accounts.google.com/gsi/client`) inlines — all four match
 * exactly. Re-run that check before changing anything here: this is a
 * trademark, so "looks right" is not the bar.
 *
 * ACCESSIBILITY. Always `aria-hidden`: the button label already says
 * "Google", so exposing the mark too would make a screen reader announce the
 * brand twice. It is decoration on top of text, never the label itself.
 *
 * NO `className` PROP, ON PURPOSE. The size is hardcoded so the rules above
 * are structural instead of merely documented: a free-form class prop would
 * let a future call site pass `w-10 h-4` and distort the mark, breaking the
 * very trademark rule this file states. There is one call site and one
 * correct size, so the prop would be speculative generality whose only
 * purchase is a way to get it wrong.
 *
 * `size-[18px]` deliberately carries a `size-` token so it opts out of
 * `button.tsx`'s `[&_svg:not([class*='size-'])]:size-4` fallback — 16px is
 * the floor for this mark and 18px sits comfortably above it inside the
 * `h-9` button.
 */
export function GoogleG() {
  return (
    <svg
      className="size-[18px]"
      viewBox="0 0 48 48"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
      />
      <path
        fill="#FBBC05"
        d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
      />
    </svg>
  );
}
