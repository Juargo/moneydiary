import { useMutation, useQueryClient } from '@tanstack/react-query';
import { postReevaluarCategorias } from './client';
import type { ApiError } from './client';
import type { ReevaluarCategoriasDto } from './types';
import { invalidarCachesMovimiento } from './movimientos-invalidacion';

/**
 * useReevaluarPatrones — `useMutation` para `POST /api/transacciones/reevaluar`.
 * `mutationFn` mirrors `useEliminarMovimiento`/`useRegistrarMovimiento`:
 * calls `postReevaluarCategorias`, unwraps `ApiResult`, or throws
 * `result.error` so TanStack Query exposes a typed `ApiError` on
 * `mutation.error` (never a raw throw). No mutation variables — the
 * endpoint takes no request body (re-runs the caller's OWN catalog against
 * their OWN transactions).
 *
 * Invalidation: reuses `invalidarCachesMovimiento`'s exact 4-key PREFIX set
 * (`resumen`, `resumen-anual`, `detalle-bucket-mes`, `ingresos-mes`) instead
 * of `use-reclasificar-categoria.ts`'s narrower `periodo`/`bucket`-scoped
 * keys. That narrower hook can build an EXACT key because its caller
 * already knows which single period/bucket it's reclassifying into. This
 * mutation has no such argument — a re-evaluation can rewrite the
 * categoria/bucket of ANY transaction, in ANY period, across the caller's
 * ENTIRE history (it iterates every transaction, not just the one visible
 * period) — so only a broad, prefix-only invalidation is correct, the same
 * reasoning `categorias-invalidacion.ts`'s `invalidarCatalogoYDashboard`
 * documents for its own prefix keys.
 *
 * `invalidarCachesMovimiento` ALREADY IS that exact broad 4-key set (see
 * its own docstring: the same set `useRegistrarMovimiento` inlines,
 * extracted once the 3rd occurrence appeared) — reusing it here instead of
 * hand-rolling a near-identical list a 4th time is the direct DRY
 * consequence of that already-established rule, not a new decision.
 *
 * Deliberately NOT `invalidarCatalogoYDashboard` (`categorias-invalidacion.ts`):
 * that profile ALSO invalidates `['categorias']`, which is correct for a
 * mutation that changes the catalog itself (create/rename/re-bucket/delete
 * categoria or patrón). Re-evaluating existing patterns against existing
 * transactions never touches the catalog — only which transactions match
 * it — so invalidating `['categorias']` here would just be an unnecessary
 * refetch of data that provably did not change.
 */
export function useReevaluarPatrones() {
  const queryClient = useQueryClient();

  return useMutation<ReevaluarCategoriasDto, ApiError, void>({
    mutationFn: async () => {
      const result = await postReevaluarCategorias();
      if (!result.ok) {
        throw result.error;
      }
      return result.value;
    },
    onSuccess: () => invalidarCachesMovimiento(queryClient),
  });
}
