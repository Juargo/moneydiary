import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'vitest-axe';
import { SelectorTema } from './SelectorTema';
import { ContextoControladorTema } from '@/lib/use-preferencia-tema';
import type { ControladorTema, EstadoTema } from '@/lib/controlador-tema';
import type { PreferenciaTema, TemaResuelto } from '@/lib/tema';

/**
 * SelectorTema.test.tsx (web-theme-switch PR10/S7a, ADR-043 D8/WT-06).
 *
 * Injects a fake `ControladorTema` through `ContextoControladorTema` — no
 * global side effects on the real singleton (`controladorTema` in
 * `use-preferencia-tema.ts`), and no real `localStorage`/`matchMedia`
 * involved. The fake mirrors the real controller's notify-on-change
 * contract (`cambiarPreferencia` updates `obtenerEstado()` and calls every
 * `suscribir`red listener) so `usePreferenciaTema`'s
 * `useSyncExternalStore` re-renders exactly like production.
 */

function resolverTemaFalso(preferencia: PreferenciaTema): TemaResuelto {
  return preferencia === 'dark' ? 'dark' : 'light';
}

function crearControladorFalso(
  preferenciaInicial: PreferenciaTema = 'system',
): ControladorTema {
  let estado: EstadoTema = {
    preferencia: preferenciaInicial,
    temaResuelto: resolverTemaFalso(preferenciaInicial),
  };
  const listeners = new Set<() => void>();

  return {
    obtenerEstado: () => estado,
    cambiarPreferencia: vi.fn((preferencia: PreferenciaTema) => {
      estado = {
        preferencia,
        temaResuelto: resolverTemaFalso(preferencia),
      };
      listeners.forEach((listener) => listener());
    }),
    suscribir: (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    iniciar: () => () => {},
  };
}

function renderSelector(controlador: ControladorTema, compacto = false) {
  return render(
    <ContextoControladorTema.Provider value={controlador}>
      <SelectorTema compacto={compacto} />
    </ContextoControladorTema.Provider>,
  );
}

describe('SelectorTema', () => {
  it('expone tres radios con nombre accesible Claro/Oscuro/Sistema (variante completa)', () => {
    renderSelector(crearControladorFalso());

    expect(screen.getByRole('radio', { name: 'Claro' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Oscuro' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Sistema' })).toBeInTheDocument();
  });

  it('expone tres radios con nombre accesible Claro/Oscuro/Sistema (variante compacta)', () => {
    renderSelector(crearControladorFalso(), true);

    expect(screen.getByRole('radio', { name: 'Claro' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Oscuro' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Sistema' })).toBeInTheDocument();
  });

  it('refleja la preferencia actual como radio marcado', () => {
    renderSelector(crearControladorFalso('dark'));

    expect(screen.getByRole('radio', { name: 'Oscuro' })).toBeChecked();
    expect(screen.getByRole('radio', { name: 'Claro' })).not.toBeChecked();
    expect(screen.getByRole('radio', { name: 'Sistema' })).not.toBeChecked();
  });

  it('llama a cambiarPreferencia con el valor correcto al seleccionar', async () => {
    const controlador = crearControladorFalso('system');
    renderSelector(controlador);
    const usuario = userEvent.setup();

    await usuario.click(screen.getByRole('radio', { name: 'Oscuro' }));

    expect(controlador.cambiarPreferencia).toHaveBeenCalledWith('dark');
    expect(screen.getByRole('radio', { name: 'Oscuro' })).toBeChecked();
  });

  it('navega entre opciones con flechas de teclado (grupo nativo del radio)', async () => {
    const controlador = crearControladorFalso('light');
    renderSelector(controlador);
    const usuario = userEvent.setup();

    screen.getByRole('radio', { name: 'Claro' }).focus();
    await usuario.keyboard('{ArrowRight}');

    expect(controlador.cambiarPreferencia).toHaveBeenCalledWith('dark');
    expect(screen.getByRole('radio', { name: 'Oscuro' })).toHaveFocus();
    expect(screen.getByRole('radio', { name: 'Oscuro' })).toBeChecked();
  });

  it('dos instancias en la misma página quedan en grupos de teclado separados (name distinto, D8)', async () => {
    const controladorPerfil = crearControladorFalso('light');
    const controladorSidebar = crearControladorFalso('light');
    render(
      <>
        <ContextoControladorTema.Provider value={controladorPerfil}>
          <SelectorTema />
        </ContextoControladorTema.Provider>
        <ContextoControladorTema.Provider value={controladorSidebar}>
          <SelectorTema compacto />
        </ContextoControladorTema.Provider>
      </>,
    );

    const radiosClaro = screen.getAllByRole('radio', { name: 'Claro' });
    expect(radiosClaro).toHaveLength(2);
    const [nombrePerfil, nombreSidebar] = radiosClaro.map((radio) =>
      radio.getAttribute('name'),
    );
    expect(nombrePerfil).toEqual(expect.any(String));
    expect(nombreSidebar).not.toBe(nombrePerfil);

    const usuario = userEvent.setup();
    radiosClaro[0].focus();
    await usuario.keyboard('{ArrowRight}');

    expect(controladorPerfil.cambiarPreferencia).toHaveBeenCalledWith('dark');
    expect(controladorSidebar.cambiarPreferencia).not.toHaveBeenCalled();
  });

  it('dos instancias que comparten el MISMO controlador quedan en sync (Perfil ↔ Sidebar, WT-06)', async () => {
    const controladorCompartido = crearControladorFalso('light');
    render(
      <ContextoControladorTema.Provider value={controladorCompartido}>
        <SelectorTema />
        <SelectorTema compacto />
      </ContextoControladorTema.Provider>,
    );
    const usuario = userEvent.setup();

    const [radioPerfil, radioSidebar] = screen.getAllByRole('radio', {
      name: 'Oscuro',
    });
    expect(radioPerfil).not.toBeChecked();
    expect(radioSidebar).not.toBeChecked();

    await usuario.click(radioPerfil);

    // Un solo controlador compartido: la selección hecha en la instancia
    // "Perfil" se refleja en la instancia "Sidebar" sin ninguna prop ni
    // contexto extra — es la garantía de producción (D4, `_authenticated.tsx`
    // y `PerfilPanel.tsx` consumen el mismo `controladorTema` por defecto).
    expect(radioPerfil).toBeChecked();
    expect(radioSidebar).toBeChecked();
  });

  it('no tiene violaciones de accesibilidad (variante completa)', async () => {
    const { container } = renderSelector(crearControladorFalso());

    expect(await axe(container)).toHaveNoViolations();
  });

  it('no tiene violaciones de accesibilidad (variante compacta)', async () => {
    const { container } = renderSelector(crearControladorFalso(), true);

    expect(await axe(container)).toHaveNoViolations();
  });
});
