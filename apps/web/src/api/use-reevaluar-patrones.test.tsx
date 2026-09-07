import { afterEach, describe, expect, it, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { useReevaluarPatrones } from './use-reevaluar-patrones';

/**
 * use-reevaluar-patrones.test.tsx — mirrors `use-eliminar-movimiento.test.tsx`'s
 * shape: `mutationFn` unwrap discipline + the broad, PREFIX-only 4-key
 * invalidation (`invalidarCachesMovimiento`'s exact set — see the hook's own
 * docstring for why this narrower/broader choice was made).
 */
function crearWrapper(queryClient: QueryClient) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

describe('useReevaluarPatrones', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('llama a POST /api/transacciones/reevaluar sin variables', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          transaccionesEvaluadas: 10,
          transaccionesActualizadas: 3,
        }),
    });
    vi.stubGlobal('fetch', fetchMock);
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    const { result } = renderHook(() => useReevaluarPatrones(), {
      wrapper: crearWrapper(queryClient),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith('/api/transacciones/reevaluar', {
      method: 'POST',
    });
  });

  it('resuelve el DTO en `.data` al tener éxito', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            transaccionesEvaluadas: 10,
            transaccionesActualizadas: 3,
          }),
      }),
    );
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    const { result } = renderHook(() => useReevaluarPatrones(), {
      wrapper: crearWrapper(queryClient),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual({
      transaccionesEvaluadas: 10,
      transaccionesActualizadas: 3,
    });
  });

  it('al tener éxito invalida EXACTAMENTE las 4 queries amplias (resumen, resumen-anual, detalle-bucket-mes, ingresos-mes)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            transaccionesEvaluadas: 10,
            transaccionesActualizadas: 3,
          }),
      }),
    );
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useReevaluarPatrones(), {
      wrapper: crearWrapper(queryClient),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(invalidateSpy).toHaveBeenCalledTimes(4);
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['resumen'] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['resumen-anual'] });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: ['detalle-bucket-mes'],
    });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['ingresos-mes'] });
  });

  it("NO invalida `['categorias']` — reevaluar no cambia el catálogo", async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            transaccionesEvaluadas: 10,
            transaccionesActualizadas: 3,
          }),
      }),
    );
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useReevaluarPatrones(), {
      wrapper: crearWrapper(queryClient),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidateSpy).not.toHaveBeenCalledWith({
      queryKey: ['categorias'],
    });
  });

  it('una mutación fallida no invalida ninguna caché', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 500 }),
    );
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useReevaluarPatrones(), {
      wrapper: crearWrapper(queryClient),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidateSpy).not.toHaveBeenCalled();
  });

  it('expone el ApiError tipado cuando falla, no un throw crudo', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 401 }),
    );
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    const { result } = renderHook(() => useReevaluarPatrones(), {
      wrapper: crearWrapper(queryClient),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toEqual({
      tag: 'unauthorized',
      message: 'Sin acceso.',
    });
  });
});
