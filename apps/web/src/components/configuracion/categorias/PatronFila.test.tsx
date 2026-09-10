import { afterEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import type { PatronDto } from '@/api/types';
import { PatronFila } from './PatronFila';

/**
 * PatronFila.test.tsx (US-043 PR #4, design.md §1/Q9b, WCTG-04, WCTG-09,
 * WCTG-13) — one pattern row. `matchType` `<select>` + `patron` `<input>`,
 * both `<label>`-associated, immediate per-row commits — never batched.
 * Delete fires with NO dialog (a pattern carries no impact).
 *
 * **Redesign (judgment-day, 2026-08-14, see `PatronFila`'s own docblock)**:
 * an EXISTING row (`patron` prop present) commits on blur-or-Enter, same as
 * before. A NOT-YET-CREATED row (`patron` prop absent) commits ONLY on an
 * explicit confirm (Enter, or picking `matchType` once `Patrón` already has
 * text) — `blur` never commits it, regardless of where focus goes next.
 * Several tests below were rewritten because they pinned the PREVIOUS
 * (defective) "blur creates a new row" mechanism — see each test's comment
 * for what changed and why.
 */
function crearWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

const PATRON: PatronDto = {
  id: 'pat-1',
  categoriaId: 'cat-1',
  patron: 'netflix',
  matchType: 'CONTAINS',
  prioridad: 100,
};

describe('PatronFila — fila existente', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('renderiza patrón y tipo de coincidencia, ambos label-associated', () => {
    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    expect(screen.getByLabelText('Patrón')).toHaveValue('netflix');
    expect(screen.getByLabelText('Tipo de coincidencia')).toHaveValue(
      'CONTAINS',
    );
    expect(
      screen.getByRole('option', { name: 'CONTIENE' }),
    ).toBeInTheDocument();
  });

  it('un matchType que el web no reconoce (fuera de MATCH_TYPES) NO se pierde: la fila sigue renderizando y el valor sin reconocer viaja INTACTO en un commit que solo edita el texto (design.md Q2b/Q4c, ADR-024: el servidor es la autoridad de validez, el web nunca lo rechaza como parse failure — revert judgment-day PR #4 de la unión cerrada MatchType en el estado local, que contradecía esta decisión sin que `esPatronDto` la reforzara en runtime)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);
    const patronConMatchTypeDesconocido: PatronDto = {
      ...PATRON,
      matchType: 'ALGO_QUE_EL_WEB_NO_CONOCE',
    };

    render(
      <PatronFila
        categoriaId="cat-1"
        patron={patronConMatchTypeDesconocido}
        esDemo={false}
      />,
      { wrapper: crearWrapper() },
    );

    // The row still renders — an unrecognised `matchType` never throws or
    // hides the row.
    const input = screen.getByLabelText('Patrón');
    expect(input).toHaveValue('netflix');

    // Editing ONLY the pattern text and committing must send the
    // unrecognised `matchType` back UNCHANGED — never coerced/defaulted to
    // one of the three literals the web happens to know about.
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.blur(input);

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
        credentials: 'same-origin',
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          patron: 'spotify',
          matchType: 'ALGO_QUE_EL_WEB_NO_CONOCE',
        }),
      }),
    );
  });

  it('blur después de editar Patrón commitea EXACTAMENTE un PATCH /api/patrones/:id y llama a onAnunciar("Patrón guardado.") (mecanismo 2, judgment-day round 2: el aria-live vive ahora en PatronesSection — ver PatronesSection.test.tsx)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);
    const onAnunciar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        patron={PATRON}
        esDemo={false}
        onAnunciar={onAnunciar}
      />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.blur(input);

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
        credentials: 'same-origin',
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ patron: 'spotify', matchType: 'CONTAINS' }),
      }),
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
    await waitFor(() =>
      expect(onAnunciar).toHaveBeenCalledWith('Patrón guardado.'),
    );
  });

  it('Enter (sin blur previo) también commitea', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'disney' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
      credentials: 'same-origin',
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ patron: 'disney', matchType: 'CONTAINS' }),
    });
  });

  it('elegir un nuevo Tipo de coincidencia commitea inmediatamente, sin esperar blur', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    await user.selectOptions(
      screen.getByLabelText('Tipo de coincidencia'),
      'REGEX',
    );

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
      credentials: 'same-origin',
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ patron: 'netflix', matchType: 'REGEX' }),
    });
  });

  it('REGEX pre-validation es un HINT, no un gate: una regex inválida muestra role="status" pero blur SIGUE commiteando', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    await user.selectOptions(
      screen.getByLabelText('Tipo de coincidencia'),
      'REGEX',
    );
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    fetchMock.mockClear();

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: '(unclosed' } });

    expect(await screen.findByRole('status')).toBeInTheDocument();

    fireEvent.blur(input);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
      credentials: 'same-origin',
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ patron: '(unclosed', matchType: 'REGEX' }),
    });
  });

  it('el icono de eliminar dispara DELETE /api/patrones/:id sin diálogo', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    await user.click(screen.getByRole('button', { name: /eliminar patrón/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
        credentials: 'same-origin',
        method: 'DELETE',
      }),
    );
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
  });

  it('un error de commit (400 PATRON_INVALIDO) renderiza mensajeDeErrorCatalogo en role="alert"', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ code: 'PATRON_INVALIDO' }),
      }),
    );

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    // A non-empty value here — a BLANK value must not even reach the
    // server (see "un valor vacío ... NO commitea" below), so this test
    // exercises a genuine server-side rejection instead.
    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'ab' } });
    fireEvent.blur(input);

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'El patrón debe tener entre 1 y 200 caracteres.',
    );
  });

  it('un valor vacío (o solo espacios) en Patrón NO commitea: sin request, sin error (fila existente)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.blur(input);

    // No `waitFor` timeout to eat — assert synchronously that the guard
    // never even reaches the mutation, then confirm nothing shows up async.
    expect(fetchMock).not.toHaveBeenCalled();
    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('un segundo commit disparado mientras el PRIMER PATCH está en vuelo (actualizar.isPending) NO dispara un segundo PATCH, y Patrón/Tipo de coincidencia quedan deshabilitados mientras tanto (judgment-day round 2 CRITICAL: evita perder una segunda edición en silencio)', async () => {
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const onAnunciar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        patron={PATRON}
        esDemo={false}
        onAnunciar={onAnunciar}
      />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.blur(input);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

    // In-flight assertion BEFORE resolving (deferred promise, not
    // `mockResolvedValue`) — both fields must be disabled while THIS row's
    // own mutation is in flight, otherwise a second edit here would update
    // local state, `commit()` would silently drop it on `filaOcupada`, and
    // the field would keep showing an unsent edit reported as "saved".
    expect(screen.getByLabelText('Patrón')).toBeDisabled();
    expect(screen.getByLabelText('Tipo de coincidencia')).toBeDisabled();

    fireEvent.keyDown(input, { key: 'Enter' });

    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolverFetch({ ok: true, status: 200 });
    await waitFor(() =>
      expect(onAnunciar).toHaveBeenCalledWith('Patrón guardado.'),
    );
    expect(screen.getByLabelText('Patrón')).not.toBeDisabled();
    expect(screen.getByLabelText('Tipo de coincidencia')).not.toBeDisabled();
  });

  it('un blur con el MISMO valor y matchType que el último commit conocido NO dispara un PATCH (dirty check, judgment-day round 2)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    // No edit at all — blur with the value exactly as loaded from `patron`.
    fireEvent.blur(screen.getByLabelText('Patrón'));

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('tras un PATCH exitoso, un blur posterior con el MISMO valor ya guardado no repite el PATCH (dirty check idempotente)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.blur(input);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

    // Same value as just committed — an incidental second blur (e.g. focus
    // bounced away and back) must not repeat the request.
    fireEvent.blur(input);

    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('una fila EXISTENTE NO renderiza el botón Confirmar patrón: ahí el blur ya commitea, un segundo disparador sería redundante (issue #600, alcance acotado a la fila sin crear)', () => {
    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    expect(
      screen.queryByRole('button', { name: 'Confirmar patrón' }),
    ).not.toBeInTheDocument();
  });

  it('sesión demo: Patrón, Tipo de coincidencia y el botón eliminar quedan deshabilitados (WCTG-11)', () => {
    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo />, {
      wrapper: crearWrapper(),
    });

    expect(screen.getByLabelText('Patrón')).toBeDisabled();
    expect(screen.getByLabelText('Tipo de coincidencia')).toBeDisabled();
    expect(
      screen.getByRole('button', { name: /eliminar patrón/i }),
    ).toBeDisabled();
  });

  it('escribir texto y Tab hacia el botón eliminar SÍ commitea el PATCH en una fila EXISTENTE (judgment-day CRITICAL, redesign PR #4: Tab no es un clic — perder la edición sin avisar era el hallazgo de la ronda 2)', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    await user.type(screen.getByLabelText('Patrón'), '-plus');
    await user.tab();

    expect(
      screen.getByRole('button', { name: /eliminar patrón/i }),
    ).toHaveFocus();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
      credentials: 'same-origin',
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ patron: 'netflix-plus', matchType: 'CONTAINS' }),
    });
  });

  it('escribir texto y hacer CLIC en eliminar en una fila EXISTENTE NO dispara un PATCH antes del DELETE — solo el DELETE (el clic no debe commitear una edición que el usuario está a punto de descartar junto con la fila)', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    await user.type(screen.getByLabelText('Patrón'), '-plus');
    await user.click(screen.getByRole('button', { name: /eliminar patrón/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
      credentials: 'same-origin',
      method: 'DELETE',
    });
  });

  it('limpiar el texto de un patrón EXISTENTE a vacío y perder el foco revierte la vista al último valor comprometido, en vez de quedar vacío para siempre divergido del servidor (redesign, judgment-day PR #4)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: '' } });
    fireEvent.blur(input);

    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Patrón')).toHaveValue('netflix');
  });

  it('cuando el prop patron cambia (refetch en background) SIN edición local pendiente, Patrón y Tipo de coincidencia se resincronizan a la verdad del servidor (redesign, judgment-day PR #4, causa estructural #1)', () => {
    const { rerender } = render(
      <PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />,
      { wrapper: crearWrapper() },
    );

    expect(screen.getByLabelText('Patrón')).toHaveValue('netflix');

    rerender(
      <PatronFila
        categoriaId="cat-1"
        patron={{ ...PATRON, patron: 'disney', matchType: 'STARTS_WITH' }}
        esDemo={false}
      />,
    );

    expect(screen.getByLabelText('Patrón')).toHaveValue('disney');
    expect(screen.getByLabelText('Tipo de coincidencia')).toHaveValue(
      'STARTS_WITH',
    );
  });

  it('si el usuario tiene una edición local SIN GUARDAR, un refetch en background NO la sobrescribe', () => {
    const { rerender } = render(
      <PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />,
      { wrapper: crearWrapper() },
    );

    fireEvent.change(screen.getByLabelText('Patrón'), {
      target: { value: 'en-progreso' },
    });

    rerender(
      <PatronFila
        categoriaId="cat-1"
        patron={{ ...PATRON, patron: 'disney' }}
        esDemo={false}
      />,
    );

    expect(screen.getByLabelText('Patrón')).toHaveValue('en-progreso');
  });

  it('un Enter SIN cambios (dirty-check no-op) no deja el flag de restaurar foco pegado en true: una edición real commiteada por blur DESPUÉS no roba el foco (judgment-day round 3 CRITICAL: el flag solo se limpiaba en el useEffect y en alCambiarMatchType, nunca en los early-return de commit())', async () => {
    // Deferred promise (not `mockResolvedValue`) — the mutation MUST stay
    // observably in-flight (`accionesBloqueadas` true across a render) so
    // the focus-restoration `useEffect` gets a genuine false→true→false
    // transition to react to; an already-resolved mock can collapse both
    // transitions into a single render and never exercise the effect.
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón') as HTMLInputElement;
    const focoSpy = vi.spyOn(input, 'focus');

    // Enter with NO edit — the dirty check in `commit()` bails BEFORE any
    // `fetch` call, so `accionesBloqueadas` never even starts cycling for
    // this press.
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(fetchMock).not.toHaveBeenCalled();

    // A later, real edit committed via ordinary blur — NOT Enter — DOES
    // start a mutation this time.
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.blur(input);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(input).toBeDisabled();
    expect(focoSpy).not.toHaveBeenCalled();

    resolverFetch({ ok: true, status: 200 });

    // The fields re-enable once the blur-triggered PATCH resolves — the
    // focus-restoration effect must NOT fire, because this commit was
    // never Enter-driven.
    await waitFor(() => expect(input).not.toBeDisabled());
    expect(focoSpy).not.toHaveBeenCalled();
  });

  it('cambiar Tipo de coincidencia mientras Patrón está vacío en una fila EXISTENTE revierte AMBOS campos al último valor comprometido, no solo el texto — y un blur posterior con el par revertido no dispara un PATCH fantasma (judgment-day round 3 CRITICAL: la guarda de valor vacío solo revertía `valor`, dejando `matchType` avanzado sin confirmar)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: '' } });

    const select = screen.getByLabelText('Tipo de coincidencia');
    fireEvent.change(select, { target: { value: 'REGEX' } });

    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Patrón')).toHaveValue('netflix');
    expect(screen.getByLabelText('Tipo de coincidencia')).toHaveValue(
      'CONTAINS',
    );

    // The dirty-check baseline must ALSO be back to the confirmed pair —
    // otherwise the next blur sees an unchanged `valor` but a changed
    // `matchType` and fires a PATCH sending the OLD text under the NEW
    // match type, a pair the user never confirmed together.
    fireEvent.blur(input);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('mousedown en Eliminar SIN que un clic real lo siga (arrastre fuera del target de 24×24) recupera y commitea la edición que el blur había dejado pendiente, en vez de perderla en silencio (judgment-day round 3 WARNING: clicEliminarEnCursoRef se limpiaba en el blur asumiendo que un clic real vendría después)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón');
    const boton = screen.getByRole('button', { name: /eliminar patrón/i });

    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.mouseDown(boton);
    fireEvent.blur(input);

    // The blur alone must not commit yet — a genuine click might still
    // land right after and discard the row, making the commit pointless.
    expect(fetchMock).not.toHaveBeenCalled();

    // No `click` ever follows (the pointer released elsewhere) — the
    // recovery must fire once the gesture is known to have ended.
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones/pat-1', {
      credentials: 'same-origin',
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ patron: 'spotify', matchType: 'CONTAINS' }),
    });
  });

  it('si la fila se desmonta ANTES de que el timer de recuperación diferida (mousedown en Eliminar seguido de arrastre fuera del target) se dispare, el commit diferido se cancela: cero request (judgment-day PR #4 WARNING: el `setTimeout` no tenía cleanup — un `commit()` diferido podía disparar un PATCH real contra una fila de la que el usuario ya navegó)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal('fetch', fetchMock);

    const { unmount } = render(
      <PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón');
    const boton = screen.getByRole('button', { name: /eliminar patrón/i });

    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.mouseDown(boton);
    fireEvent.blur(input);

    // The deferred recovery timer is now scheduled (see the sibling test
    // above), but the row unmounts — e.g. `Cancelar` navigated away —
    // before the macrotask that would replay `commit()` ever runs.
    unmount();

    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('un Enter que dispara un PATCH llama a input.focus() una vez que el input se re-habilita (redesign, judgment-day PR #4, causa estructural #4: un navegador real pierde el foco al deshabilitar un control enfocado; jsdom no reproduce ese auto-blur de forma confiable, así que este test verifica el fix real — la llamada a `.focus()` guiada por el ref — en vez de `document.activeElement`)', async () => {
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón') as HTMLInputElement;
    const focoSpy = vi.spyOn(input, 'focus');
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(input).toBeDisabled();
    expect(focoSpy).not.toHaveBeenCalled();

    resolverFetch({ ok: true, status: 200 });

    await waitFor(() => expect(input).not.toBeDisabled());
    await waitFor(() => expect(focoSpy).toHaveBeenCalledTimes(1));
  });

  it('si el propio PATCH de la fila resuelve MIENTRAS un bloqueo EXTERNO (bloqueado=true, p.ej. un diálogo de confirmación abierto en EditarCategoria) sigue activo, la intención de restaurar foco se descarta — NO se roba el foco de vuelta a Patrón cuando el bloqueo externo se libera después (judgment-day PR #4 WARNING: la intención pertenece solo al ciclo de vida de la mutación PROPIA de esta fila, nunca a un bloqueo impuesto desde afuera)', async () => {
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const { rerender } = render(
      <PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón') as HTMLInputElement;
    const focoSpy = vi.spyOn(input, 'focus');
    fireEvent.change(input, { target: { value: 'spotify' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(input).toBeDisabled();

    // An external dialog opens elsewhere on the screen WHILE this row's own
    // PATCH is still in flight — mirrors `EditarCategoria` passing
    // `bloqueado={dialogo !== null}` down to every `PatronFila`.
    rerender(
      <PatronFila
        categoriaId="cat-1"
        patron={PATRON}
        esDemo={false}
        bloqueado
      />,
    );

    // The row's own PATCH resolves while the external block is STILL up —
    // the input must stay disabled (the external block, not this row's own
    // mutation, is now the reason) and focus must NOT be restored yet.
    resolverFetch({ ok: true, status: 200 });
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(screen.getByLabelText('Patrón')).toBeDisabled();
    expect(focoSpy).not.toHaveBeenCalled();

    // The external dialog closes (e.g. the user pressed Escape, and
    // `EditarCategoria` already synchronously focused ITS OWN `Guardar`/
    // `Eliminar` button) — this row must not steal that focus back.
    rerender(<PatronFila categoriaId="cat-1" patron={PATRON} esDemo={false} />);

    expect(screen.getByLabelText('Patrón')).not.toBeDisabled();
    expect(focoSpy).not.toHaveBeenCalled();
  });
});

describe('PatronFila — fila nueva (sin patrón todavía creado)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('arranca vacía, y el primer commit EXPLÍCITO (Enter) dispara POST /api/patrones con categoriaId y luego llama a onDescartar (redesign, judgment-day PR #4 — blur ya NO commitea una fila sin crear, ver el test siguiente)', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    expect(screen.getByLabelText('Patrón')).toHaveValue('');

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'uber' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(onDescartar).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones', {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        categoriaId: 'cat-1',
        patron: 'uber',
        matchType: 'CONTAINS',
      }),
    });
  });

  it('blur en una fila SIN crear (el foco se va a CUALQUIER lugar, no solo al botón eliminar) NO dispara POST — la creación exige un confirm explícito (redesign, judgment-day PR #4, reemplaza el mecanismo de la ronda 2 que ató la creación a un blur ambiguo)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'uber' } });
    fireEvent.blur(input);

    // No `waitFor` timeout to eat — synchronous assertion, then confirm
    // nothing shows up async either.
    expect(fetchMock).not.toHaveBeenCalled();
    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(onDescartar).not.toHaveBeenCalled();
    // The typed text stays put — the user can still confirm it with Enter,
    // or discard the whole row with Eliminar.
    expect(screen.getByLabelText('Patrón')).toHaveValue('uber');
  });

  it('eliminar una fila NO creada todavía llama a onDescartar sin emitir ninguna request', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    await user.click(screen.getByRole('button', { name: /eliminar patrón/i }));

    expect(onDescartar).toHaveBeenCalledTimes(1);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('elegir un Tipo de coincidencia ANTES de escribir texto NO dispara POST (valor vacío no commitea)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    const select = screen.getByLabelText('Tipo de coincidencia');
    fireEvent.change(select, { target: { value: 'REGEX' } });

    expect(fetchMock).not.toHaveBeenCalled();
    expect(onDescartar).not.toHaveBeenCalled();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('un segundo commit disparado mientras el PRIMER POST está en vuelo (Enter, luego cambiar Tipo de coincidencia ANTES de que resuelva) NO dispara un segundo POST — regresión del hallazgo crítico de judgment-day (trigger actualizado a Enter: blur ya no crea, redesign PR #4)', async () => {
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'uber' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

    // The FIRST `POST` is still pending (`resolverFetch` not yet called) —
    // `idCreado` stays `undefined` for this whole window. Picking a
    // different `matchType` here used to fire a SECOND `POST` because
    // `commit()` had no `crear.isPending` guard.
    const select = screen.getByLabelText('Tipo de coincidencia');
    fireEvent.change(select, { target: { value: 'REGEX' } });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(onDescartar).not.toHaveBeenCalled();

    resolverFetch({ ok: true, status: 201 });
    await waitFor(() => expect(onDescartar).toHaveBeenCalledTimes(1));
    // Still exactly one request — `onSuccess` only ever fired once.
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('escribir texto y luego hacer CLIC en eliminar en una fila SIN crear NO commitea el patrón: cero POST, la fila se descarta de inmediato (redesign PR #4: blur NUNCA commitea una fila sin crear, así que ni siquiera hace falta distinguir el clic del botón — reemplaza el mecanismo `relatedTarget` de la ronda 2, que resolvía esto ad-hoc solo para ESTE caso)', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    // `user.type` (not `fireEvent.change`) so the input genuinely holds
    // focus, matching the real "type, then click the trash icon" gesture —
    // a real click always blurs the previously-focused element first.
    await user.type(screen.getByLabelText('Patrón'), 'uber');
    await user.click(screen.getByRole('button', { name: /eliminar patrón/i }));

    expect(fetchMock).not.toHaveBeenCalled();
    expect(onDescartar).toHaveBeenCalledTimes(1);
  });

  it('escribir texto y luego tabular FUERA del input (a Confirmar, y de ahí a Eliminar) tampoco commitea en una fila SIN crear — blur nunca commitea una fila sin crear, independientemente de a dónde vaya el foco (contraste: en una fila EXISTENTE, Tab SÍ commitea — ver "PatronFila — fila existente")', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    await user.type(screen.getByLabelText('Patrón'), 'uber');

    // El orden de tabulación de una fila SIN crear es
    // `Patrón → Confirmar → Eliminar` (issue #600: `Confirmar patrón` se
    // renderiza antes que la papelera). Tabular hasta CUALQUIERA de los dos
    // dispara el `blur` del input, y ninguno de esos blur commitea.
    await user.tab();
    expect(
      screen.getByRole('button', { name: 'Confirmar patrón' }),
    ).toHaveFocus();
    expect(fetchMock).not.toHaveBeenCalled();

    await user.tab();
    expect(
      screen.getByRole('button', { name: /eliminar patrón/i }),
    ).toHaveFocus();
    expect(fetchMock).not.toHaveBeenCalled();
    expect(onDescartar).not.toHaveBeenCalled();
  });

  it('eliminar mientras el POST de creación está en vuelo (disparado por un Enter AJENO al clic de eliminar) queda bloqueado hasta que resuelve, y la fila se descarta igual al resolver — escenario distinto de la race del clic, cubierto arriba (trigger actualizado a Enter: blur ya no crea, redesign PR #4)', async () => {
    const user = userEvent.setup();
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón');
    fireEvent.change(input, { target: { value: 'uber' } });
    // An explicit Enter confirm, UNRELATED to the delete button (blur alone
    // never creates a not-yet-created row any more — see the tests above).
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

    const boton = screen.getByRole('button', { name: /eliminar patrón/i });
    expect(boton).toBeDisabled();

    await user.click(boton);
    expect(onDescartar).not.toHaveBeenCalled();

    resolverFetch({ ok: true, status: 201 });
    await waitFor(() => expect(onDescartar).toHaveBeenCalledTimes(1));
    expect(onDescartar).toHaveBeenCalledTimes(1);
  });
  it('renderiza un botón Confirmar patrón visible: el gesto de confirmación explícito deja de ser SOLO la tecla Enter (issue #600 — el usuario escribía el patrón, apretaba el Guardar de identidad y no pasaba nada, porque ese Guardar no toca patrones y el blur nunca crea una fila)', () => {
    render(<PatronFila categoriaId="cat-1" esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    expect(
      screen.getByRole('button', { name: 'Confirmar patrón' }),
    ).toBeInTheDocument();
  });

  it('clic en Confirmar patrón dispara EXACTAMENTE un POST /api/patrones y luego onDescartar + onAnunciar — el mismo commit que Enter, por un camino visible (issue #600)', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();
    const onAnunciar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        onAnunciar={onAnunciar}
      />,
      { wrapper: crearWrapper() },
    );

    await user.type(screen.getByLabelText('Patrón'), 'Alcancía');
    await user.click(screen.getByRole('button', { name: 'Confirmar patrón' }));

    await waitFor(() => expect(onDescartar).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones', {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        categoriaId: 'cat-1',
        patron: 'Alcancía',
        matchType: 'CONTAINS',
      }),
    });
    expect(onAnunciar).toHaveBeenCalledWith('Patrón guardado.');
  });

  it('Confirmar patrón arranca deshabilitado con Patrón vacío y se habilita al escribir: un botón que no hace nada al tocarlo es exactamente el defecto que este arreglo cierra (issue #600)', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const confirmar = screen.getByRole('button', { name: 'Confirmar patrón' });
    expect(confirmar).toBeDisabled();

    // Solo espacios sigue siendo "no hay nada que commitear" — misma regla
    // que la guarda de valor vacío de `commit()`.
    await user.type(screen.getByLabelText('Patrón'), '   ');
    expect(confirmar).toBeDisabled();

    await user.type(screen.getByLabelText('Patrón'), 'Alcancía');
    expect(confirmar).toBeEnabled();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('sesión demo: Confirmar patrón queda deshabilitado aunque haya texto (WCTG-11, misma condición que el resto de la fila)', () => {
    render(<PatronFila categoriaId="cat-1" esDemo={true} />, {
      wrapper: crearWrapper(),
    });

    expect(
      screen.getByRole('button', { name: 'Confirmar patrón' }),
    ).toBeDisabled();
  });

  it('un segundo clic en Confirmar patrón mientras el PRIMER POST está en vuelo NO dispara un segundo POST (misma garantía que ya tenía el camino de Enter — accionesBloqueadas)', async () => {
    const user = userEvent.setup();
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<{ ok: boolean; status: number }>((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    await user.type(screen.getByLabelText('Patrón'), 'Alcancía');
    const confirmar = screen.getByRole('button', { name: 'Confirmar patrón' });
    await user.click(confirmar);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(confirmar).toBeDisabled();

    await user.click(confirmar);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolverFetch({ ok: true, status: 201 });
    await waitFor(() => expect(onDescartar).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it('un POST rechazado por el servidor (400 PATRON_INVALIDO) desde Confirmar patrón renderiza role="alert", CONSERVA el texto tipeado, re-habilita el botón para reintentar y NO descarta la fila (review de fiabilidad, issue #600: el modo de falla vecino al bug reportado — que el patrón desaparezca en silencio — no estaba cubierto para la creación, solo para el PATCH)', async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ code: 'PATRON_INVALIDO' }),
      }),
    );
    const onDescartar = vi.fn();

    render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
      />,
      { wrapper: crearWrapper() },
    );

    await user.type(screen.getByLabelText('Patrón'), 'Alcancía');
    await user.click(screen.getByRole('button', { name: 'Confirmar patrón' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'El patrón debe tener entre 1 y 200 caracteres.',
    );
    // La fila SIGUE viva con el texto puesto: el usuario puede corregir y
    // reintentar sin volver a escribir todo.
    expect(onDescartar).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Patrón')).toHaveValue('Alcancía');
    expect(
      screen.getByRole('button', { name: 'Confirmar patrón' }),
    ).toBeEnabled();
  });

  it('un POST fallido desde Confirmar patrón devuelve el foco al input una vez re-habilitado, igual que el camino de Enter (review de fiabilidad, issue #600: el botón se deshabilita mientras la mutación vuela, lo que en un navegador real tira el foco a <body> — dejar la ruta VISIBLE peor que el atajo invisible sería exactamente al revés de lo que arregla este cambio)', async () => {
    const user = userEvent.setup();
    // Promesa CONTROLADA a mano, no un mock que resuelve al instante: el
    // `useEffect` que restaura el foco tiene deps `[filaOcupada,
    // bloqueadoTotal]`, así que solo corre cuando `filaOcupada` CAMBIA. Con
    // un mock inmediato React batchea `isPending` true→false en un único
    // render, la dep nunca cambia y el efecto no se dispara — un artefacto
    // del test, no del navegador. Mismo idioma que el test del camino de
    // Enter ("un Enter que dispara un PATCH llama a input.focus()...").
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
      json: () => Promise<{ code: string }>;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    const input = screen.getByLabelText('Patrón') as HTMLInputElement;
    await user.type(input, 'Alcancía');
    // Mismo criterio que el test del camino de Enter: jsdom no reproduce el
    // auto-blur de deshabilitar un control enfocado, así que se verifica la
    // llamada real a `.focus()` guiada por el ref, no `document.activeElement`.
    const focoSpy = vi.spyOn(input, 'focus');
    await user.click(screen.getByRole('button', { name: 'Confirmar patrón' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    // Mientras vuela: fila ocupada, sin foco robado todavía.
    expect(input).toBeDisabled();
    expect(focoSpy).not.toHaveBeenCalled();

    resolverFetch({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ code: 'PATRON_INVALIDO' }),
    });

    expect(await screen.findByRole('alert')).toBeInTheDocument();
    await waitFor(() => expect(focoSpy).toHaveBeenCalled());
  });

  it('Confirmar patrón SIGUE disparando el POST con una REGEX inválida: la pre-validación es un hint, no un compuerta (ADR-024 — el motor RegExp del navegador no es el del servidor; guarda de regresión contra agregar `|| regexInvalida` al disabled del botón)', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);

    render(<PatronFila categoriaId="cat-1" esDemo={false} />, {
      wrapper: crearWrapper(),
    });

    await user.selectOptions(
      screen.getByLabelText('Tipo de coincidencia'),
      'REGEX',
    );
    await user.type(screen.getByLabelText('Patrón'), '(sin cerrar');

    expect(screen.getByRole('status')).toHaveTextContent(
      'Esa expresión regular podría no ser válida.',
    );
    const confirmar = screen.getByRole('button', { name: 'Confirmar patrón' });
    expect(confirmar).toBeEnabled();

    await user.click(confirmar);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones', {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        categoriaId: 'cat-1',
        patron: '(sin cerrar',
        matchType: 'REGEX',
      }),
    });
  });

  it('un bloqueo EXTERNO (bloqueado=true, p.ej. un diálogo de confirmación abierto en EditarCategoria) deshabilita Confirmar patrón igual que al resto de la fila (paridad WCTG-11)', () => {
    render(<PatronFila categoriaId="cat-1" esDemo={false} bloqueado={true} />, {
      wrapper: crearWrapper(),
    });

    expect(
      screen.getByRole('button', { name: 'Confirmar patrón' }),
    ).toBeDisabled();
  });
});

/**
 * `confirmarAlGuardar` (issue #600 follow-up, 2026-09-09) — `Confirmar
 * patrón` (PR #601) gave the explicit confirm a VISIBLE surface, but the
 * user reported back that they pressed `Guardar` again, which is what
 * anyone reaches for when they want to save. `EditarCategoria` bumps a
 * counter on every `Guardar` click and threads it down to not-yet-created
 * rows ONLY (`PatronesSection`'s docblock) — a CHANGE in the number is the
 * signal, not a specific value, mirroring `alCambiarMatchType`/
 * `confirmarFilaNueva`'s own calls into the SAME `commit()`.
 */
describe('PatronFila — confirmarAlGuardar (issue #600 follow-up: Guardar confirma patrones nuevos pendientes)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('un cambio en confirmarAlGuardar con Patrón no vacío dispara EXACTAMENTE un POST /api/patrones y luego onDescartar — el mismo commit que Enter/Confirmar patrón, ahora también alcanzable desde Guardar', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    const { rerender } = render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        confirmarAlGuardar={0}
      />,
      { wrapper: crearWrapper() },
    );
    fireEvent.change(screen.getByLabelText('Patrón'), {
      target: { value: 'Alcancía' },
    });

    rerender(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        confirmarAlGuardar={1}
      />,
    );

    await waitFor(() => expect(onDescartar).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones', {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        categoriaId: 'cat-1',
        patron: 'Alcancía',
        matchType: 'CONTAINS',
      }),
    });
  });

  it('confirmarAlGuardar con Patrón vacío NO dispara ningún POST — el guard de valor vacío de commit() se mantiene intacto aunque el disparador sea Guardar', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    const { rerender } = render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        confirmarAlGuardar={0}
      />,
      { wrapper: crearWrapper() },
    );

    rerender(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        confirmarAlGuardar={1}
      />,
    );

    expect(fetchMock).not.toHaveBeenCalled();
    expect(onDescartar).not.toHaveBeenCalled();
  });

  it('confirmarAlGuardar en sesión demo NO dispara ningún POST aunque haya texto — accionesBloqueadas (esDemo) cubre también esta superficie nueva (WCTG-11)', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    // `fireEvent.change` en vez de `userEvent.type`: el campo YA está
    // deshabilitado en esDemo (paridad con el resto de la fila, `PatronesSection.
    // test.tsx` ya fija que "Agregar patrón" queda deshabilitado en demo, así
    // que ninguna fila nueva llega a existir en la UI real). Este test aísla
    // el guard de `accionesBloqueadas` en sí mismo — la segunda línea de
    // defensa — no el camino de UI.
    const { rerender } = render(
      <PatronFila categoriaId="cat-1" esDemo={true} confirmarAlGuardar={0} />,
      { wrapper: crearWrapper() },
    );
    fireEvent.change(screen.getByLabelText('Patrón'), {
      target: { value: 'Alcancía' },
    });

    rerender(
      <PatronFila categoriaId="cat-1" esDemo={true} confirmarAlGuardar={1} />,
    );

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('confirmarAlGuardar no roba el foco — a diferencia de Enter/Confirmar patrón, este gesto no ocurrió en el input Patrón, sino en el botón Guardar de otra sección', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);

    const { rerender } = render(
      <PatronFila categoriaId="cat-1" esDemo={false} confirmarAlGuardar={0} />,
      { wrapper: crearWrapper() },
    );
    const input = screen.getByLabelText('Patrón') as HTMLInputElement;
    const focoSpy = vi.spyOn(input, 'focus');
    fireEvent.change(input, { target: { value: 'Alcancía' } });

    rerender(
      <PatronFila categoriaId="cat-1" esDemo={false} confirmarAlGuardar={1} />,
    );

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(focoSpy).not.toHaveBeenCalled();
  });

  it('un confirmarAlGuardar que llega MIENTRAS el POST disparado por Enter sigue en vuelo no pisa la intención de restaurar foco de ese Enter: si el POST termina en error, el foco SIGUE volviendo a Patrón (regresión judgment-day, 2026-09-09: el efecto pisaba `restaurarFocoPatronRef` a `false` incondicionalmente, incluso cuando `commit()` iba a no-opear por `accionesBloqueadas` — la mutación en vuelo, que SÍ es dueña de esa intención, nunca llegaba a limpiarla porque ya la encontraba en `false`)', async () => {
    let resolverFetch: (value: {
      ok: boolean;
      status: number;
      json: () => Promise<{ code: string }>;
    }) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolverFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const onDescartar = vi.fn();

    const { rerender } = render(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        confirmarAlGuardar={0}
      />,
      { wrapper: crearWrapper() },
    );

    const input = screen.getByLabelText('Patrón') as HTMLInputElement;
    const focoSpy = vi.spyOn(input, 'focus');

    // Enter confirma la fila nueva — el POST queda en vuelo (promesa
    // controlada, no resuelta todavía) y `restaurarFocoPatronRef` queda en
    // `true`.
    fireEvent.change(input, { target: { value: 'uber' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(input).toBeDisabled();

    // Con el POST original TODAVÍA sin resolver, el usuario hace clic en el
    // Guardar de otra sección — `confirmarAlGuardar` cambia y dispara el
    // efecto nuevo. `commit()` no-opea aquí (`accionesBloqueadas` por el
    // POST en vuelo), así que la intención de restaurar foco de ese Enter
    // no debe perderse.
    rerender(
      <PatronFila
        categoriaId="cat-1"
        esDemo={false}
        onDescartar={onDescartar}
        confirmarAlGuardar={1}
      />,
    );

    // El POST original falla — la fila sigue viva con su error.
    resolverFetch({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ code: 'PATRON_INVALIDO' }),
    });

    expect(await screen.findByRole('alert')).toBeInTheDocument();
    expect(onDescartar).not.toHaveBeenCalled();
    // El foco vuelve al input Patrón una vez que la fila se rehabilita — si
    // el efecto de `confirmarAlGuardar` hubiera pisado la intención, esta
    // llamada nunca ocurriría.
    await waitFor(() => expect(focoSpy).toHaveBeenCalled());
  });

  it('DOS filas nuevas con texto pendiente, confirmadas por UN solo cambio de confirmarAlGuardar, disparan UN POST por fila — cada fila tiene su propio ref/efecto, sin interferencia entre ellas', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 201 });
    vi.stubGlobal('fetch', fetchMock);
    const onDescartarUno = vi.fn();
    const onDescartarDos = vi.fn();

    const { rerender } = render(
      <>
        <PatronFila
          categoriaId="cat-1"
          esDemo={false}
          onDescartar={onDescartarUno}
          confirmarAlGuardar={0}
        />
        <PatronFila
          categoriaId="cat-1"
          esDemo={false}
          onDescartar={onDescartarDos}
          confirmarAlGuardar={0}
        />
      </>,
      { wrapper: crearWrapper() },
    );

    const [inputUno, inputDos] = screen.getAllByLabelText('Patrón');
    fireEvent.change(inputUno, { target: { value: 'uber' } });
    fireEvent.change(inputDos, { target: { value: 'lyft' } });

    rerender(
      <>
        <PatronFila
          categoriaId="cat-1"
          esDemo={false}
          onDescartar={onDescartarUno}
          confirmarAlGuardar={1}
        />
        <PatronFila
          categoriaId="cat-1"
          esDemo={false}
          onDescartar={onDescartarDos}
          confirmarAlGuardar={1}
        />
      </>,
    );

    await waitFor(() => expect(onDescartarUno).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(onDescartarDos).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones', {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        categoriaId: 'cat-1',
        patron: 'uber',
        matchType: 'CONTAINS',
      }),
    });
    expect(fetchMock).toHaveBeenCalledWith('/api/patrones', {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        categoriaId: 'cat-1',
        patron: 'lyft',
        matchType: 'CONTAINS',
      }),
    });
  });
});
