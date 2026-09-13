import { describe, expect, it, vi } from 'vitest';
import { crearControladorTema } from './controlador-tema';
import { CLAVE_PREFERENCIA_TEMA } from './tema';

interface StorageFalsoOpciones {
  lanzaAlEscribir?: boolean;
}

function crearStorageFalso(
  inicial: Record<string, string> = {},
  opciones: StorageFalsoOpciones = {},
): Storage {
  const datos = new Map(Object.entries(inicial));
  return {
    getItem: (clave: string) => datos.get(clave) ?? null,
    setItem: (clave: string, valor: string) => {
      if (opciones.lanzaAlEscribir) {
        throw new Error('QuotaExceededError');
      }
      datos.set(clave, valor);
    },
    removeItem: (clave: string) => {
      datos.delete(clave);
    },
    clear: () => datos.clear(),
    key: () => null,
    get length() {
      return datos.size;
    },
  } as Storage;
}

type ListenerOS = (evento: { matches: boolean }) => void;

function crearMatchMediaFalso(inicialOscuro: boolean) {
  let oscuro = inicialOscuro;
  const listeners = new Set<ListenerOS>();
  const mql = {
    get matches() {
      return oscuro;
    },
    addEventListener: (_tipo: string, listener: ListenerOS) => {
      listeners.add(listener);
    },
    removeEventListener: (_tipo: string, listener: ListenerOS) => {
      listeners.delete(listener);
    },
  };
  const matchMedia = vi
    .fn()
    .mockReturnValue(mql) as unknown as Window['matchMedia'];
  return {
    matchMedia,
    cambiarOS(valor: boolean) {
      oscuro = valor;
      listeners.forEach((listener) => listener({ matches: oscuro }));
    },
  };
}

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
  const documento = {
    documentElement: raiz,
    querySelector: () => meta,
  } as unknown as Document;
  return { documento, raiz, meta };
}

type ListenerStorage = (evento: Partial<StorageEvent>) => void;

function crearVentanaFalsa() {
  const listeners = new Set<ListenerStorage>();
  const ventana = {
    addEventListener: (tipo: string, listener: ListenerStorage) => {
      if (tipo === 'storage') {
        listeners.add(listener);
      }
    },
    removeEventListener: (tipo: string, listener: ListenerStorage) => {
      if (tipo === 'storage') {
        listeners.delete(listener);
      }
    },
  } as unknown as Window;
  return {
    ventana,
    emitirStorage(evento: Partial<StorageEvent>) {
      listeners.forEach((listener) => listener(evento));
    },
  };
}

describe('crearControladorTema', () => {
  it('lee la preferencia inicial de storage y aplica el tema forzado en la construcción', () => {
    const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'light' });
    const { matchMedia } = crearMatchMediaFalso(false);
    const { documento, raiz } = crearDocumentoFalso();
    const { ventana } = crearVentanaFalsa();

    const controlador = crearControladorTema({
      storage,
      matchMedia,
      documento,
      ventana,
    });

    expect(controlador.obtenerEstado().preferencia).toBe('light');
    // Invariante S6: el tema aplicado sigue forzado a dark aunque la
    // preferencia guardada sea light.
    expect(controlador.obtenerEstado().temaResuelto).toBe('dark');
    expect(raiz.classList.contains('dark')).toBe(true);
  });

  it('obtenerEstado devuelve una referencia estable entre llamadas sin cambios', () => {
    const storage = crearStorageFalso();
    const { matchMedia } = crearMatchMediaFalso(false);
    const { documento } = crearDocumentoFalso();
    const { ventana } = crearVentanaFalsa();
    const controlador = crearControladorTema({
      storage,
      matchMedia,
      documento,
      ventana,
    });

    expect(controlador.obtenerEstado()).toBe(controlador.obtenerEstado());
  });

  it('cambiarPreferencia guarda en storage, actualiza el estado y notifica a los suscriptores', () => {
    const storage = crearStorageFalso();
    const { matchMedia } = crearMatchMediaFalso(false);
    const { documento } = crearDocumentoFalso();
    const { ventana } = crearVentanaFalsa();
    const controlador = crearControladorTema({
      storage,
      matchMedia,
      documento,
      ventana,
    });
    const listener = vi.fn();
    controlador.suscribir(listener);

    controlador.cambiarPreferencia('light');

    expect(storage.getItem(CLAVE_PREFERENCIA_TEMA)).toBe('light');
    expect(controlador.obtenerEstado().preferencia).toBe('light');
    expect(controlador.obtenerEstado().temaResuelto).toBe('dark');
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('cambiarPreferencia sigue aplicando el tema (forzado) aunque falle la escritura en storage', () => {
    const storage = crearStorageFalso({}, { lanzaAlEscribir: true });
    const { matchMedia } = crearMatchMediaFalso(false);
    const { documento, raiz } = crearDocumentoFalso();
    const { ventana } = crearVentanaFalsa();
    const controlador = crearControladorTema({
      storage,
      matchMedia,
      documento,
      ventana,
    });

    expect(() => controlador.cambiarPreferencia('light')).not.toThrow();
    expect(controlador.obtenerEstado().preferencia).toBe('light');
    expect(raiz.classList.contains('dark')).toBe(true);
  });

  it('suscribir devuelve una función que deja de notificar al llamarla', () => {
    const storage = crearStorageFalso();
    const { matchMedia } = crearMatchMediaFalso(false);
    const { documento } = crearDocumentoFalso();
    const { ventana } = crearVentanaFalsa();
    const controlador = crearControladorTema({
      storage,
      matchMedia,
      documento,
      ventana,
    });
    const listener = vi.fn();
    const desuscribir = controlador.suscribir(listener);

    desuscribir();
    controlador.cambiarPreferencia('dark');

    expect(listener).not.toHaveBeenCalled();
  });
});
