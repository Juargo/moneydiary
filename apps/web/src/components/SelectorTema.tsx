import { useId } from 'react';
import { Monitor, Moon, Sun } from 'lucide-react';
import { cn } from '@/lib/utils';
import { usePreferenciaTema } from '@/lib/use-preferencia-tema';
import type { PreferenciaTema } from '@/lib/tema';

/**
 * SelectorTema — radiogroup nativo para la preferencia de tema (web-theme-
 * switch WT-01/WT-06, ADR-043 D8). Tres `<input type="radio">` reales dentro
 * de un `fieldset`/`legend`: las flechas de teclado y el anuncio del estado
 * "seleccionado" los da gratis el navegador/AT — no hay `role="radio"`
 * simulado a mano.
 *
 * El input queda `sr-only` en ambas variantes; el `<label>` que lo envuelve
 * es la superficie visual (texto en la completa, ícono en la `compacto`) y
 * usa `has-[:checked]`/`has-[:focus-visible]` para reflejar el estado sin JS
 * extra.
 *
 * `name` sale de `useId()` por instancia, no de una constante del módulo:
 * dos `SelectorTema` en la misma página (Perfil y, desde PR11, el Sidebar)
 * deben quedar en grupos de teclado separados — las flechas de un grupo no
 * deben mover la selección del otro (D8's rationale).
 */
const OPCIONES: ReadonlyArray<{
  readonly valor: PreferenciaTema;
  readonly etiqueta: string;
  readonly Icono: typeof Sun;
}> = [
  { valor: 'light', etiqueta: 'Claro', Icono: Sun },
  { valor: 'dark', etiqueta: 'Oscuro', Icono: Moon },
  { valor: 'system', etiqueta: 'Sistema', Icono: Monitor },
];

export function SelectorTema({
  compacto = false,
}: { readonly compacto?: boolean } = {}) {
  const { preferencia, cambiarPreferencia } = usePreferenciaTema();
  const nombreGrupo = useId();

  return (
    <fieldset className="m-0 flex flex-col gap-2 border-0 p-0">
      <legend
        className={cn(
          'p-0 text-sm font-medium text-foreground',
          compacto && 'sr-only',
        )}
      >
        Tema
      </legend>
      <div className={cn('flex gap-2', compacto && 'gap-1')}>
        {OPCIONES.map(({ valor, etiqueta, Icono }) => (
          <label
            key={valor}
            className={cn(
              'flex cursor-pointer items-center gap-2 rounded-md border border-input px-3 py-2 text-sm text-foreground has-[:checked]:border-ring has-[:checked]:bg-accent has-[:checked]:text-accent-foreground has-[:focus-visible]:ring-[3px] has-[:focus-visible]:ring-ring/50',
              compacto && 'size-8 justify-center gap-0 p-0',
            )}
          >
            <input
              type="radio"
              name={nombreGrupo}
              value={valor}
              checked={preferencia === valor}
              onChange={() => cambiarPreferencia(valor)}
              className="sr-only"
            />
            <Icono aria-hidden="true" className="size-4 shrink-0" />
            <span className={cn(compacto && 'sr-only')}>{etiqueta}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
