import { expect, test } from '@playwright/test';
import { stubApi } from './fixtures/api-stubs';

/**
 * e2e/tema.e2e.ts — WT-02/WT-04/WT-05 runtime proof (S7b, PR11, design.md
 * Testing Strategy "Runtime" row). jsdom cannot exercise a real reload, a
 * real live `prefers-color-scheme` flip, or a real second tab — this is the
 * only layer that can. Uses the sidebar's compact `SelectorTema` (mounted on
 * every `_authenticated` route via `_authenticated.tsx`'s `sidebarFooter`,
 * D10) as the live UI surface for the persisted-choice and cross-tab
 * scenarios; its input is `sr-only` (D8), so `.check({ force: true })` is
 * used — the element has a non-zero (1×1, clipped) box and IS visible to
 * Playwright (same reasoning as `mobile-header.e2e.ts`'s sr-only h1), but
 * two co-located sr-only radios can shadow each other's hit-target, so
 * `force` skips that check while still dispatching the click on the real
 * `<input>`.
 */

const RUTA_HOME = '/?periodo=2026-07';

async function esperarHomeListo(page: import('@playwright/test').Page) {
  await page.getByText('Toca un ítem del gráfico o la leyenda').waitFor();
}

test.describe('runtime del tema (persistencia, OS en vivo, cross-tab)', () => {
  test('elegir Oscuro persiste tras el reload, con la clase aplicada antes de que #root se pinte (WT-03/WT-04)', async ({
    page,
  }) => {
    await stubApi(page);
    await page.goto(RUTA_HOME);
    await esperarHomeListo(page);

    await page.getByRole('radio', { name: 'Oscuro' }).check({ force: true });
    await expect(page.locator('html')).toHaveClass(/dark/);

    // The inline pre-paint script runs synchronously in <head>, before body
    // parsing — by construction it has already applied the class by the
    // time `domcontentloaded` fires, while the module script that mounts
    // React (deferred, in <body>) has not necessarily run yet. Capturing
    // state right here is the only way to observe "no flash" instead of
    // just its end result.
    await page.reload({ waitUntil: 'domcontentloaded' });
    const estadoTemprano = await page.evaluate(() => ({
      tieneClaseDark: document.documentElement.classList.contains('dark'),
      colorScheme: getComputedStyle(document.documentElement).colorScheme,
      rootVacio: document.getElementById('root')?.children.length === 0,
    }));
    expect(estadoTemprano.tieneClaseDark).toBe(true);
    expect(estadoTemprano.colorScheme).toBe('dark');
    expect(estadoTemprano.rootVacio).toBe(true);

    // And the fully-mounted app confirms the persisted choice too.
    await esperarHomeListo(page);
    await expect(page.getByRole('radio', { name: 'Oscuro' })).toBeChecked();
  });

  test('bajo preferencia system, un cambio de OS en vivo actualiza el tema sin reload (WT-02)', async ({
    page,
  }) => {
    await stubApi(page);
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto(RUTA_HOME);
    await esperarHomeListo(page);

    await expect(page.locator('html')).not.toHaveClass(/dark/);
    await expect(page.getByRole('radio', { name: 'Sistema' })).toBeChecked();

    await page.emulateMedia({ colorScheme: 'dark' });
    await expect(page.locator('html')).toHaveClass(/dark/);

    await page.emulateMedia({ colorScheme: 'light' });
    await expect(page.locator('html')).not.toHaveClass(/dark/);
  });

  test('cross-tab: cambiar el tema en una pestaña actualiza la otra vía storage (WT-05)', async ({
    context,
  }) => {
    const paginaA = await context.newPage();
    const paginaB = await context.newPage();
    await stubApi(paginaA);
    await stubApi(paginaB);

    await paginaA.goto(RUTA_HOME);
    await esperarHomeListo(paginaA);
    await paginaB.goto(RUTA_HOME);
    await esperarHomeListo(paginaB);

    await paginaA.getByRole('radio', { name: 'Oscuro' }).check({ force: true });
    await expect(paginaA.locator('html')).toHaveClass(/dark/);

    await expect(paginaB.locator('html')).toHaveClass(/dark/);
    await expect(paginaB.getByRole('radio', { name: 'Oscuro' })).toBeChecked();
  });
});
