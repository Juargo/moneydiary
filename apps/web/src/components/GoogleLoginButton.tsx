import { useGoogleLoginVisible } from '@/api/capabilities';
import { Button } from '@/components/ui/button';
import { GoogleG } from '@/components/icons/GoogleG';

/**
 * GoogleLoginButton — a top-level `<a href>` navigation to
 * `GET /api/auth/google` (AUTH-17). This MUST stay a real anchor doing a
 * full-page navigation, never an `onClick` handler issuing `fetch`/
 * `window.location`: the backend's Sec-Fetch guard on the initiate route
 * requires a genuine top-level document navigation to send the
 * `Sec-Fetch-*` headers it checks (same reasoning as the landing page's
 * demo link, `apps/landing/src/config.ts`).
 *
 * Visibility is driven entirely by `GET /api/auth/capabilities`
 * (design.md §4.5) — the kill switch lives server-side (Render env vars),
 * never a build-time flag — via the shared `useGoogleLoginVisible()` hook
 * (`@/api/capabilities`), the single source of truth `routes/login.tsx`'s
 * auth-path divider also reads so the two can never disagree. While the
 * capability answer is still loading, an invisible placeholder reserves the
 * button's footprint so the layout does not jump once the answer arrives (no
 * flash of a dead button); once resolved to `false`, or on any fetch failure
 * (fail-closed), nothing is rendered at all.
 *
 * The official Google mark (`components/icons/GoogleG`) sits before the
 * label. It is `aria-hidden`, so the accessible name stays exactly
 * "Continuar con Google" — one of Google's approved strings — and a screen
 * reader does not announce the brand twice. `Button`'s base `gap-2` provides
 * the clear space the mark requires; the button keeps the app's own
 * `outline` variant rather than Google's stock button chrome, which their
 * guidelines allow as long as the mark itself is unmodified.
 */
export function GoogleLoginButton() {
  const { isPending, visible } = useGoogleLoginVisible();

  if (isPending) {
    return <div aria-hidden="true" className="h-9 w-full" />;
  }

  if (!visible) {
    return null;
  }

  return (
    <Button asChild variant="outline" className="w-full">
      <a href="/api/auth/google">
        <GoogleG />
        Continuar con Google
      </a>
    </Button>
  );
}
