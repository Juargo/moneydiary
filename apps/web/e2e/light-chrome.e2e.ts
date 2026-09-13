import { expect, test } from '@playwright/test';
import { stubApi } from './fixtures/api-stubs';

/**
 * e2e/light-chrome.e2e.ts — mirrors `dark-chrome.e2e.ts` for the `:root`
 * default (S4, D1/D2, DCR-04/05). Light is reached by removing the class
 * in-page. Since S6, the pre-paint script AND `lib/tema.ts`'s `aplicarTema`
 * also set `documentElement.style.colorScheme` directly (D2) — an inline
 * style wins the cascade over both `:root`/`.dark`'s CSS-declared
 * `color-scheme`, so removing only the class is no longer enough to flip
 * the UA-reported scheme; the first test below also clears that inline
 * property. Same jsdom-can't-paint reasoning as `dark-chrome.e2e.ts`.
 */

test.describe('chrome claro (Clínico frío, aún inalcanzable en prod)', () => {
  test('sin la clase dark, el elemento raíz declara color-scheme: light', async ({
    page,
  }) => {
    await stubApi(page);
    await page.goto('/?periodo=2026-07');
    await page.getByText('Toca un ítem del gráfico o la leyenda').waitFor();

    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = '';
    });

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

  test('los <select> nativos pintan la cara Clínico frío sin la clase dark', async ({
    page,
  }) => {
    await stubApi(page);
    await page.goto('/buckets/Deseos?periodo=2026-07');

    await page.evaluate(() =>
      document.documentElement.classList.remove('dark'),
    );

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
