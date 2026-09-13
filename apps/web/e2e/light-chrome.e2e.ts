import { expect, test } from '@playwright/test';
import { stubApi } from './fixtures/api-stubs';

/**
 * e2e/light-chrome.e2e.ts — mirrors `dark-chrome.e2e.ts` for the `:root`
 * default (S4, D1/D2, DCR-04/05). Since S7b (PR11) the selector is live and
 * light is reachable: no preference is stored (default `system`), so
 * `page.emulateMedia({ colorScheme: 'light' })` before navigating drives the
 * pre-paint script to resolve `light` for real — no in-page DOM
 * manipulation needed anymore. Same jsdom-can't-paint reasoning as
 * `dark-chrome.e2e.ts`.
 */

test.describe('chrome claro (Clínico frío)', () => {
  test('con OS claro y sin preferencia guardada, el elemento raíz declara color-scheme: light', async ({
    page,
  }) => {
    await stubApi(page);
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/?periodo=2026-07');
    await page.getByText('Toca un ítem del gráfico o la leyenda').waitFor();

    const esquema = await page.evaluate(
      () => getComputedStyle(document.documentElement).colorScheme,
    );
    expect(esquema).toBe('light');

    const fondo = await page.evaluate(
      () => getComputedStyle(document.body).backgroundColor,
    );
    expect(fondo).toBe('rgb(237, 240, 245)');

    const tarjeta = await page
      .locator('[class*="bg-card"]')
      .first()
      .evaluate((el) => getComputedStyle(el).backgroundColor);
    expect(tarjeta).toBe('rgb(249, 250, 252)');
  });

  test('los <select> nativos pintan la cara Clínico frío con OS claro', async ({
    page,
  }) => {
    await stubApi(page);
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/buckets/Deseos?periodo=2026-07');

    const select = page.locator('select').first();
    await select.waitFor();

    const fondo = await select.evaluate(
      (el) => getComputedStyle(el).backgroundColor,
    );

    expect(fondo).not.toBe('rgba(0, 0, 0, 0)');
    expect(fondo).not.toBe('transparent');

    expect(fondo).toBe('rgb(249, 250, 252)'); // Clínico frío card
  });
});
