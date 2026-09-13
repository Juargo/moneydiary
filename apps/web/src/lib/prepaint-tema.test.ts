/**
 * Parity test (D5, design.md): extrae el `<script>` inline de `index.html` y
 * lo ejecuta contra globales stubbeados, comparando el resultado con
 * `resolverTema`/`leerPreferencia` del módulo. Un script que se desincroniza
 * de `lib/tema.ts` (ej. alguien edita uno y olvida el otro) hace fallar este
 * archivo — es la única cobertura que existe sobre el texto literal del
 * script, porque no se importa como módulo (no hay bundler para `index.html`
 * en tiempo de ejecución del navegador).
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { leerPreferencia, resolverTema, TEMA_FORZADO } from './tema';

const RUTA_INDEX_HTML = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../../index.html',
);

function extraerScriptPrepaint(html: string): string {
  // Parsea el HTML en vez de usar una regex (CodeQL js/bad-tag-filter): el
  // script de pre-paint es el único `<script>` sin `src` — el otro de
  // `index.html` es `<script type="module" src="/src/main.tsx">`.
  const documento = new DOMParser().parseFromString(html, 'text/html');
  const script = Array.from(documento.querySelectorAll('script')).find(
    (elemento) => !elemento.hasAttribute('src'),
  );
  const codigo = script?.textContent ?? '';
  if (codigo.trim() === '') {
    throw new Error(
      'index.html no tiene un <script> inline de pre-paint (WT-04)',
    );
  }
  return codigo;
}

interface ResultadoDom {
  tieneClaseDark: boolean;
  colorScheme: string;
  themeColor: string;
}

function ejecutarScriptPrepaint(
  script: string,
  valorAlmacenado: string | null,
  lanzaAlLeer: boolean,
  osOscuro: boolean,
): ResultadoDom {
  let claseDark = false;
  const raizStyle = { colorScheme: '' };
  const raiz = {
    classList: {
      toggle: (clase: string, forzar: boolean) => {
        if (clase === 'dark') {
          claseDark = forzar;
        }
      },
    },
    style: raizStyle,
  };
  const meta = {
    content: '',
    setAttribute: (_nombre: string, valor: string) => {
      meta.content = valor;
    },
  };
  const documentStub = {
    documentElement: raiz,
    querySelector: () => meta,
  };
  const localStorageStub = {
    getItem: (): string | null => {
      if (lanzaAlLeer) {
        throw new Error('localStorage no disponible');
      }
      return valorAlmacenado;
    },
  };
  const matchMediaStub = () => ({ matches: osOscuro });
  const windowStub = { matchMedia: matchMediaStub };

  // El script inline vive en `index.html` sin sistema de módulos (D5,
  // design.md) — `new Function` es la única forma de ejecutar exactamente el
  // texto embebido y compararlo con `lib/tema.ts` en este mismo test.
  // (No hace falta un eslint-disable: `no-new-func` no está habilitada en
  // este repo — ver `eslint.config.js`.)
  const evaluarScript = new Function(
    'document',
    'localStorage',
    'window',
    'matchMedia',
    script,
  );
  evaluarScript(documentStub, localStorageStub, windowStub, matchMediaStub);

  return {
    tieneClaseDark: claseDark,
    colorScheme: raizStyle.colorScheme,
    themeColor: meta.content,
  };
}

describe('script de pre-paint embebido en index.html', () => {
  const html = readFileSync(RUTA_INDEX_HTML, 'utf-8');
  const script = extraerScriptPrepaint(html);

  const casosAlmacenados: Array<{
    etiqueta: string;
    valor: string | null;
    lanza: boolean;
  }> = [
    { etiqueta: 'light', valor: 'light', lanza: false },
    { etiqueta: 'dark', valor: 'dark', lanza: false },
    { etiqueta: 'system', valor: 'system', lanza: false },
    { etiqueta: 'ausente', valor: null, lanza: false },
    { etiqueta: 'invalido', valor: 'sepia', lanza: false },
    { etiqueta: 'lanza-al-leer', valor: null, lanza: true },
  ];

  describe.each(casosAlmacenados)(
    'almacenado=$etiqueta',
    ({ valor, lanza }) => {
      it.each([true, false])(
        'coincide con resolverTema cuando osOscuro=%s',
        (osOscuro) => {
          const preferenciaEsperada = leerPreferencia({
            getItem: () => {
              if (lanza) {
                throw new Error('boom');
              }
              return valor;
            },
          });
          const temaEsperado = resolverTema(preferenciaEsperada, osOscuro);

          const resultado = ejecutarScriptPrepaint(
            script,
            valor,
            lanza,
            osOscuro,
          );

          expect(resultado.tieneClaseDark).toBe(temaEsperado === 'dark');
          expect(resultado.colorScheme).toBe(temaEsperado);
          expect(resultado.themeColor).toBe(
            temaEsperado === 'dark' ? '#1A1917' : '#EDF0F5',
          );
        },
      );
    },
  );

  it('no fuerza ningún tema: TEMA_FORZADO está en null desde S7b', () => {
    expect(TEMA_FORZADO).toBeNull();
    // Con el selector desbloqueado, localStorage=light y OS=dark resuelve a
    // light — la preferencia explícita gana sobre el OS (WT-02).
    const resultado = ejecutarScriptPrepaint(script, 'light', false, true);
    expect(resultado.tieneClaseDark).toBe(false);
    expect(resultado.colorScheme).toBe('light');
    expect(resultado.themeColor).toBe('#EDF0F5');
  });
});
