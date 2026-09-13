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
  it('lee la preferencia inicial de storage y aplica el tema resuelto en la construcción', () => {
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
    expect(controlador.obtenerEstado().temaResuelto).toBe('light');
    expect(raiz.classList.contains('dark')).toBe(false);
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

    controlador.cambiarPreferencia('dark');

    expect(storage.getItem(CLAVE_PREFERENCIA_TEMA)).toBe('dark');
    expect(controlador.obtenerEstado().preferencia).toBe('dark');
    expect(controlador.obtenerEstado().temaResuelto).toBe('dark');
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('cambiarPreferencia sigue aplicando el tema aunque falle la escritura en storage (WT-03)', () => {
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

    expect(() => controlador.cambiarPreferencia('dark')).not.toThrow();
    expect(controlador.obtenerEstado().preferencia).toBe('dark');
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

  describe('iniciar()', () => {
    it('sigue el cambio de OS cuando la preferencia es system, actualizando el tema aplicado', () => {
      const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'system' });
      const { matchMedia, cambiarOS } = crearMatchMediaFalso(false);
      const { documento, raiz } = crearDocumentoFalso();
      const { ventana } = crearVentanaFalsa();
      const controlador = crearControladorTema({
        storage,
        matchMedia,
        documento,
        ventana,
      });
      const listener = vi.fn();
      controlador.suscribir(listener);
      controlador.iniciar();

      expect(controlador.obtenerEstado().temaResuelto).toBe('light');
      expect(raiz.classList.contains('dark')).toBe(false);

      cambiarOS(true);

      expect(listener).toHaveBeenCalledTimes(1);
      expect(controlador.obtenerEstado().preferencia).toBe('system');
      expect(controlador.obtenerEstado().temaResuelto).toBe('dark');
      expect(raiz.classList.contains('dark')).toBe(true);
    });

    it('ignora un cambio de OS cuando la preferencia es explícita', () => {
      const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'light' });
      const { matchMedia, cambiarOS } = crearMatchMediaFalso(false);
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
      controlador.iniciar();

      cambiarOS(true);

      expect(listener).not.toHaveBeenCalled();
      expect(controlador.obtenerEstado().preferencia).toBe('light');
    });

    it('no falla si matchMedia no está disponible en el entorno', () => {
      const storage = crearStorageFalso();
      const { documento } = crearDocumentoFalso();
      const { ventana } = crearVentanaFalsa();
      const controlador = crearControladorTema({
        storage,
        matchMedia: undefined,
        documento,
        ventana,
      });

      expect(() => controlador.iniciar()).not.toThrow();
    });

    it('reacciona a un evento storage de la clave de tema y aplica el tema resuelto', () => {
      const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'light' });
      const { matchMedia } = crearMatchMediaFalso(false);
      const { documento, raiz } = crearDocumentoFalso();
      const { ventana, emitirStorage } = crearVentanaFalsa();
      const controlador = crearControladorTema({
        storage,
        matchMedia,
        documento,
        ventana,
      });
      controlador.iniciar();
      const listener = vi.fn();
      controlador.suscribir(listener);

      storage.setItem(CLAVE_PREFERENCIA_TEMA, 'dark');
      emitirStorage({ key: CLAVE_PREFERENCIA_TEMA });

      expect(controlador.obtenerEstado().preferencia).toBe('dark');
      expect(raiz.classList.contains('dark')).toBe(true);
      expect(listener).toHaveBeenCalledTimes(1);
    });

    it('reacciona a un evento storage con key null (clear) releyendo storage', () => {
      const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'dark' });
      const { matchMedia } = crearMatchMediaFalso(false);
      const { documento } = crearDocumentoFalso();
      const { ventana, emitirStorage } = crearVentanaFalsa();
      const controlador = crearControladorTema({
        storage,
        matchMedia,
        documento,
        ventana,
      });
      controlador.iniciar();

      storage.clear();
      emitirStorage({ key: null });

      // Storage vacío cae al default (light), no a `system` — ver tema.ts.
      expect(controlador.obtenerEstado().preferencia).toBe('light');
    });

    it('ignora eventos storage de otras claves', () => {
      const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'light' });
      const { matchMedia } = crearMatchMediaFalso(false);
      const { documento } = crearDocumentoFalso();
      const { ventana, emitirStorage } = crearVentanaFalsa();
      const controlador = crearControladorTema({
        storage,
        matchMedia,
        documento,
        ventana,
      });
      controlador.iniciar();
      const listener = vi.fn();
      controlador.suscribir(listener);

      emitirStorage({ key: 'otra-clave-cualquiera' });

      expect(listener).not.toHaveBeenCalled();
    });

    it('la función de limpieza devuelta remueve ambos listeners (matchMedia y storage)', () => {
      const storage = crearStorageFalso({ [CLAVE_PREFERENCIA_TEMA]: 'system' });
      const { matchMedia, cambiarOS } = crearMatchMediaFalso(false);
      const { documento } = crearDocumentoFalso();
      const { ventana, emitirStorage } = crearVentanaFalsa();
      const controlador = crearControladorTema({
        storage,
        matchMedia,
        documento,
        ventana,
      });
      const listener = vi.fn();
      controlador.suscribir(listener);
      const limpiar = controlador.iniciar();

      limpiar();
      cambiarOS(true);
      emitirStorage({ key: CLAVE_PREFERENCIA_TEMA });

      expect(listener).not.toHaveBeenCalled();
    });
  });
});
