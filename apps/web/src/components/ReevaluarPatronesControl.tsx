import { useRef, useState } from 'react';
import { useReevaluarPatrones } from '@/api/use-reevaluar-patrones';
import type { ReevaluarCategoriasDto } from '@/api/types';
import { Button } from '@/components/ui/button';
import { InlineConfirm } from '@/components/ui/inline-confirm';

const MENSAJE_DEMO_REEVALUAR =
  'Estás en una cuenta de demostración. Crea una cuenta real para reevaluar categorías.';

/**
 * ReevaluarPatronesControl — trigger + confirmation dialog for
 * `POST /api/transacciones/reevaluar`, mounted once inside
 * `BucketDetalleMesPage`'s header, next to `PeriodoSelector`.
 *
 * Built directly on `InlineConfirm` (`EliminarMovimientoControl`/
 * `ReclasificarCategoriaControl`'s shell) rather than
 * `ConfirmarImpactoDialog` — that component's `fraseDeImpacto` copy shapes
 * are catalog-impact specific (eliminar / cambiar-bucket) and there's no
 * per-row disambiguation need here (one instance per page, not one per
 * row).
 *
 * Unlike `EliminarMovimientoControl` (which hands off to `undo-manager` and
 * closes immediately), this dialog stays MOUNTED across the mutation —
 * `CategoriaFila`/`ConfirmarImpactoDialog`'s shape instead: `pending`
 * disables the confirm button, the trigger itself is ALSO disabled while
 * pending (`disabled={esDemo || mutacion.isPending}`, same as
 * `CategoriaFila`'s delete trigger) so a stray click on the still-rendered,
 * non-modal trigger underneath can't call `mutacion.reset()` mid-flight,
 * and `cancelar()` guards Escape/Cancelar against firing while pending
 * (`InlineConfirm`'s `cancelDisabled` only disables the BUTTON — Escape
 * still calls `onCancel` unconditionally, so the guard has to live in the
 * handler too, same reasoning as `ConfirmarImpactoDialog.cancelar()`). A
 * failed attempt is shown INLINE via `InlineConfirm`'s own `error` slot —
 * the dialog does not close, so the user can retry in place without
 * re-reading the confirmation copy.
 *
 * Only a SUCCESSFUL confirm closes the dialog; the caller (`onReevaluado`)
 * turns the result into the page's own `role="status"` announcement
 * (`BucketDetalleMesPage`'s shared `anuncio` region) — this control has no
 * opinion on how the outcome is announced.
 *
 * Focus: `InlineConfirm` moves focus to the confirm button on open. Every
 * closing path — Cancelar, Escape, OR a successful confirm — returns focus
 * to THIS component's own trigger (`NuevaCategoriaDesdeFilaForm`'s
 * "restore focus to the trigger on close" precedent, generalized to the
 * success path too): unlike `EliminarMovimientoControl`'s per-row trigger,
 * this page-level trigger never unmounts on success, so there is always a
 * live target to focus.
 *
 * `esDemo` disables the trigger proactively and shows an explanatory note
 * — same UI-honesty precedent as `MENSAJE_DEMO_ELIMINAR`
 * (`BucketDetalleMesPage`): the server would reject a demo request with
 * `DEMO_SOLO_LECTURA` regardless (`postReevaluarCategorias`'s docstring),
 * this just avoids the round-trip.
 */
export function ReevaluarPatronesControl({
  esDemo = false,
  onReevaluado,
}: {
  readonly esDemo?: boolean;
  readonly onReevaluado: (resultado: ReevaluarCategoriasDto) => void;
}) {
  const triggerRef = useRef<HTMLButtonElement>(null);
  const [abierto, setAbierto] = useState(false);
  const mutacion = useReevaluarPatrones();

  function abrir() {
    mutacion.reset();
    setAbierto(true);
  }

  function cerrar() {
    setAbierto(false);
    triggerRef.current?.focus();
  }

  function cancelar() {
    if (mutacion.isPending) {
      return;
    }
    cerrar();
  }

  function confirmar() {
    mutacion.mutate(undefined, {
      onSuccess: (resultado) => {
        cerrar();
        onReevaluado(resultado);
      },
    });
  }

  // Same narrowing-capture reasoning as `NuevaCategoriaDesdeFilaForm`'s
  // `errorActual`: `mutacion.isError`/`mutacion.error` are independent
  // fields on the hook's return value, so `tsc` cannot carry the
  // `isError`-implies-`error !== null` narrowing across to a later read.
  const errorActual = mutacion.isError ? mutacion.error : null;

  return (
    <div className="flex flex-col items-start gap-1">
      <Button
        ref={triggerRef}
        type="button"
        variant="outline"
        size="sm"
        disabled={esDemo || mutacion.isPending}
        onClick={abrir}
      >
        Reevaluar categorías
      </Button>
      {esDemo && (
        <p role="note" className="text-xs text-muted-foreground">
          {MENSAJE_DEMO_REEVALUAR}
        </p>
      )}
      {abierto && (
        <InlineConfirm
          title="Reevaluar categorías"
          titleVisible
          confirmLabel="Reevaluar"
          destructive
          onConfirm={confirmar}
          onCancel={cancelar}
          pending={mutacion.isPending}
          cancelDisabled={mutacion.isPending}
          error={errorActual?.message ?? null}
          className="w-full max-w-md gap-2 p-3 text-xs"
        >
          {/* Tres frases, tres párrafos: qué alcanza, qué pisa, y que no hay
              vuelta atrás. Un único bloque denso entierra la consecuencia
              destructiva en el medio, que es justo lo que el usuario tiene
              que leer antes de confirmar. Sin mayúsculas de énfasis: el peso
              lo lleva la estructura, no el grito. */}
          <p>
            Vuelve a aplicar tus reglas de clasificación sobre todos tus
            movimientos, de todos los períodos.
          </p>
          <p>
            Los que coincidan con un patrón se sobrescriben, incluidos los que
            reclasificaste a mano. Los que no coincidan con ningún patrón quedan
            sin cambios.
          </p>
          <p>Esta acción no se puede deshacer.</p>
        </InlineConfirm>
      )}
    </div>
  );
}
