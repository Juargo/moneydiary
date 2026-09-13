import { describe, expect, it } from 'vitest';
import {
  CLAVE_PREFERENCIA_TEMA,
  TEMA_FORZADO,
  aplicarTema,
  leerPreferencia,
  resolverTema,
} from './tema';

describe('CLAVE_PREFERENCIA_TEMA', () => {
  it('usa la clave documentada en ADR-043', () => {
    expect(CLAVE_PREFERENCIA_TEMA).toBe('moneydiary:tema');
  });
});

describe('leerPreferencia', () => {
  it.each(['light', 'dark', 'system'] as const)(
    'acepta el valor almacenado %s',
    (valor) => {
      expect(leerPreferencia({ getItem: () => valor })).toBe(valor);
    },
  );

  it('cae a system cuando el valor almacenado no es reconocido', () => {
    expect(leerPreferencia({ getItem: () => 'sepia' })).toBe('system');
  });

  it('cae a system cuando no hay nada almacenado', () => {
    expect(leerPreferencia({ getItem: () => null })).toBe('system');
  });

  it('cae a system cuando no hay storage disponible', () => {
    expect(leerPreferencia(null)).toBe('system');
  });

  it('cae a system cuando getItem lanza (ej. navegación privada)', () => {
    const storage = {
      getItem: () => {
        throw new Error('SecurityError');
      },
    };
    expect(leerPreferencia(storage)).toBe('system');
  });
});

describe('resolverTema — forzado dark (S6, palanca de emergencia)', () => {
  it('TEMA_FORZADO está fijo en dark durante esta PR', () => {
    expect(TEMA_FORZADO).toBe('dark');
  });

  it.each(['light', 'dark', 'system'] as const)(
    'gana sobre la preferencia %s, tanto con OS oscuro como claro',
    (preferencia) => {
      expect(resolverTema(preferencia, true)).toBe('dark');
      expect(resolverTema(preferencia, false)).toBe('dark');
    },
  );
});

describe('aplicarTema', () => {
  function crearDocumentoFalso() {
    const clases = new Set<string>();
    const raiz = {
      classList: {
        toggle: (clase: string, forzar: boolean) => {
          if (forzar) {
            clases.add(clase);
          } else {
            clases.delete(clase);
          }
        },
        contains: (clase: string) => clases.has(clase),
      },
      style: { colorScheme: '' },
    };
    const meta = {
      content: '',
      setAttribute: (_nombre: string, valor: string) => {
        meta.content = valor;
      },
    };
    const doc = {
      documentElement: raiz,
      querySelector: () => meta,
    } as unknown as Document;
    return { doc, raiz, meta };
  }

  it('agrega la clase dark, colorScheme y theme-color al resolver dark', () => {
    const { doc, raiz, meta } = crearDocumentoFalso();
    aplicarTema(doc, 'dark');
    expect(raiz.classList.contains('dark')).toBe(true);
    expect(raiz.style.colorScheme).toBe('dark');
    expect(meta.content).toBe('#1A1917');
  });

  it('quita la clase dark y aplica light cuando resuelve light', () => {
    const { doc, raiz, meta } = crearDocumentoFalso();
    raiz.classList.toggle('dark', true);
    aplicarTema(doc, 'light');
    expect(raiz.classList.contains('dark')).toBe(false);
    expect(raiz.style.colorScheme).toBe('light');
    expect(meta.content).toBe('#EDF0F5');
  });

  it('no falla si no existe el meta theme-color', () => {
    const { doc } = crearDocumentoFalso();
    (doc as unknown as { querySelector: () => null }).querySelector = () =>
      null;
    expect(() => aplicarTema(doc, 'dark')).not.toThrow();
  });
});
