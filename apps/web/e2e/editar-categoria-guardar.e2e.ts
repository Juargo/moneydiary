import { expect, test } from '@playwright/test';
import { stubApi } from './fixtures/api-stubs';

/**
 * e2e/editar-categoria-guardar.e2e.ts — el botón `Guardar` de la pantalla de
 * editar categoría, apretado como lo aprieta una persona.
 *
 * Por qué existe este archivo: toda la cobertura de esa pantalla vive en
 * `EditarCategoria.test.tsx` y dispara el guardado con
 * `fireEvent.submit(document.getElementById('form-identidad'))`, NUNCA con un
 * click en el botón. El propio comentario del bloque lo dice: "jsdom's
 * `form=`-attribute submit-button activation on a plain `userEvent.click` is
 * not something to bet a suite on". Es una decisión razonable sobre jsdom,
 * pero deja un hueco: `Guardar` está FUERA del `<form>` y se asocia por el
 * atributo HTML `form="form-identidad"` (§1/Q3b mecanismo 1), y nadie verifica
 * nunca que esa asociación realmente dispare el submit. Un botón desconectado
 * pasaría las ~1800 pruebas de `apps/web` sin que ninguna se pusiera roja.
 *
 * Playwright cierra ese hueco porque corre Chromium de verdad: el atributo
 * `form` lo resuelve el navegador, no un polyfill.
 *
 * Stub-everything (D-11, ver el docblock de `fixtures/api-stubs.ts`): sin
 * backend real. El PATCH se intercepta y se observa — lo que se afirma es que
 * el click LO PRODUCE, no qué hace el servidor con él.
 */

test.describe('editar categoría — el botón Guardar', () => {
  test('un click en Guardar emite el PATCH de identidad (el atributo form= dispara el submit)', async ({
    page,
  }) => {
    await stubApi(page);

    const patches: Array<{ url: string; body: string | null }> = [];
    await page.route('**/api/categorias/*', async (route) => {
      if (route.request().method() !== 'PATCH') {
        await route.continue();
        return;
      }
      patches.push({
        url: route.request().url(),
        body: route.request().postData(),
      });
      await route.fulfill({ status: 200, json: { ok: true } });
    });

    await page.goto('/configuracion/categorias/cat-1');

    const nombre = page.getByLabel('Nombre', { exact: true });
    await expect(nombre).toHaveValue('Supermercado');

    await nombre.fill('Supermercado renombrado');

    const guardar = page.getByRole('button', { name: 'Guardar' });
    await expect(guardar).toBeEnabled();
    await guardar.click();

    // El corazón del caso: el click tiene que haber producido el PATCH. Si el
    // botón quedara desasociado del form, esta espera vence y el resto del
    // archivo no llega a correr — que es exactamente la señal que falta hoy.
    await expect
      .poll(() => patches.length, {
        message:
          'el click en Guardar no emitió ningún PATCH a /api/categorias/:id',
      })
      .toBeGreaterThan(0);

    expect(patches[0].url).toContain('/api/categorias/cat-1');
    expect(JSON.parse(patches[0].body ?? '{}')).toMatchObject({
      nombre: 'Supermercado renombrado',
    });
  });

  test('un click en Guardar confirma además el patrón nuevo pendiente (issue #600)', async ({
    page,
  }) => {
    await stubApi(page);

    const posts: Array<string | null> = [];
    await page.route('**/api/patrones', async (route) => {
      if (route.request().method() !== 'POST') {
        await route.continue();
        return;
      }
      posts.push(route.request().postData());
      await route.fulfill({ status: 201, json: { ok: true } });
    });
    await page.route('**/api/categorias/*', async (route) => {
      if (route.request().method() !== 'PATCH') {
        await route.continue();
        return;
      }
      await route.fulfill({ status: 200, json: { ok: true } });
    });

    await page.goto('/configuracion/categorias/cat-1');

    await page.getByRole('button', { name: 'Agregar patrón' }).click();
    // La fila nueva es la última: se escribe el patrón y NO se confirma —
    // ni Enter, ni "Confirmar patrón". Sólo `Guardar`, que es el gesto que
    // perdía el patrón en silencio antes del fix de #600.
    await page.getByLabel('Patrón', { exact: true }).last().fill('jumbo');

    await page.getByRole('button', { name: 'Guardar' }).click();

    await expect
      .poll(() => posts.length, {
        message:
          'el click en Guardar no emitió el POST del patrón nuevo pendiente',
      })
      .toBeGreaterThan(0);

    expect(JSON.parse(posts[0] ?? '{}')).toMatchObject({
      categoriaId: 'cat-1',
      patron: 'jumbo',
    });
  });
});
