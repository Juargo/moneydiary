import { afterEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { ReevaluarPatronesControl } from './ReevaluarPatronesControl';

/**
 * ReevaluarPatronesControl.test.tsx — trigger + `InlineConfirm` dialog for
 * `POST /api/transacciones/reevaluar`. Mirrors `EliminarMovimientoControl`'s
 * test shape (trigger disambiguation N/A here — one instance per page, no
 * per-row disambiguation needed) and `CategoriaFila`'s
 * pending-guards-cancel shape: unlike the delete flow, this dialog stays
 * MOUNTED across the mutation (no undo-manager hand-off) — pending disables
 * both trigger and confirm, and a failure keeps the dialog open with an
 * inline error instead of closing.
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

function mockFetchOnce(response: {
  ok: boolean;
  status: number;
  json?: () => Promise<unknown>;
}) {
  const fetchMock = vi.fn().mockResolvedValue(response);
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

const DTO_EXITO = { transaccionesEvaluadas: 40, transaccionesActualizadas: 6 };

describe('ReevaluarPatronesControl', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('renders a trigger button', () => {
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    expect(
      screen.getByRole('button', { name: /Reevaluar categorías/i }),
    ).toBeInTheDocument();
  });

  it('clicking the trigger opens an alertdialog disclosing the scope, the manual-overwrite risk, and irreversibility', async () => {
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    await user.click(
      screen.getByRole('button', { name: /Reevaluar categorías/i }),
    );

    const dialog = await screen.findByRole('alertdialog');
    expect(dialog).toHaveTextContent(/todos.*per[ií]odos/i);
    expect(dialog).toHaveTextContent(/reclasificaste a mano/i);
    expect(dialog).toHaveTextContent(/no se puede deshacer/i);
  });

  it('moves focus to the confirm button when the dialog opens', async () => {
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    await user.click(
      screen.getByRole('button', { name: /Reevaluar categorías/i }),
    );
    await screen.findByRole('alertdialog');

    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Reevaluar' })).toHaveFocus(),
    );
  });

  it('a click does NOT execute the mutation before confirmation', async () => {
    const fetchMock = mockFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(DTO_EXITO),
    });
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    await user.click(
      screen.getByRole('button', { name: /Reevaluar categorías/i }),
    );
    await screen.findByRole('alertdialog');

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('Cancelar closes the dialog without firing the request and returns focus to the trigger', async () => {
    const fetchMock = mockFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(DTO_EXITO),
    });
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    const trigger = screen.getByRole('button', {
      name: /Reevaluar categorías/i,
    });
    await user.click(trigger);
    await screen.findByRole('alertdialog');

    await user.click(screen.getByRole('button', { name: 'Cancelar' }));

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
    expect(trigger).toHaveFocus();
  });

  it('Escape closes the dialog without firing the request and returns focus to the trigger', async () => {
    const fetchMock = mockFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(DTO_EXITO),
    });
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    const trigger = screen.getByRole('button', {
      name: /Reevaluar categorías/i,
    });
    await user.click(trigger);
    await screen.findByRole('alertdialog');

    await user.keyboard('{Escape}');

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
    expect(trigger).toHaveFocus();
  });

  it('Confirmar fires POST /api/transacciones/reevaluar, closes the dialog on success, calls onReevaluado with the DTO, and returns focus to the trigger', async () => {
    const fetchMock = mockFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(DTO_EXITO),
    });
    const onReevaluado = vi.fn();
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={onReevaluado} />, {
      wrapper: crearWrapper(),
    });

    const trigger = screen.getByRole('button', {
      name: /Reevaluar categorías/i,
    });
    await user.click(trigger);
    await screen.findByRole('alertdialog');
    await user.click(screen.getByRole('button', { name: 'Reevaluar' }));

    await waitFor(() =>
      expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument(),
    );
    expect(fetchMock).toHaveBeenCalledWith('/api/transacciones/reevaluar', {
      method: 'POST',
    });
    expect(onReevaluado).toHaveBeenCalledWith(DTO_EXITO);
    expect(trigger).toHaveFocus();
  });

  it('disables both the trigger and the confirm button while the mutation is pending', async () => {
    let resolverFetch: (value: unknown) => void = () => {};
    vi.stubGlobal(
      'fetch',
      vi.fn().mockReturnValue(
        new Promise((resolve) => {
          resolverFetch = resolve;
        }),
      ),
    );
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
      wrapper: crearWrapper(),
    });

    const trigger = screen.getByRole('button', {
      name: /Reevaluar categorías/i,
    });
    await user.click(trigger);
    await screen.findByRole('alertdialog');
    await user.click(screen.getByRole('button', { name: 'Reevaluar' }));

    await waitFor(() => expect(trigger).toBeDisabled());
    expect(screen.getByRole('button', { name: 'Reevaluar' })).toBeDisabled();

    resolverFetch({
      ok: true,
      status: 200,
      json: () => Promise.resolve(DTO_EXITO),
    });
    await waitFor(() =>
      expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument(),
    );
  });

  it('on failure keeps the dialog open, shows the error inline, and does not swallow it', async () => {
    mockFetchOnce({ ok: false, status: 500 });
    const onReevaluado = vi.fn();
    const user = userEvent.setup();
    render(<ReevaluarPatronesControl onReevaluado={onReevaluado} />, {
      wrapper: crearWrapper(),
    });

    await user.click(
      screen.getByRole('button', { name: /Reevaluar categorías/i }),
    );
    await screen.findByRole('alertdialog');
    await user.click(screen.getByRole('button', { name: 'Reevaluar' }));

    const dialog = await screen.findByRole('alertdialog');
    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Ocurrió un error inesperado. Intenta nuevamente.',
      ),
    );
    expect(dialog).toBeInTheDocument();
    expect(onReevaluado).not.toHaveBeenCalled();
  });

  describe('demo session (esDemo)', () => {
    it('disables the trigger, shows an explanatory note, and clicking it does not open the dialog', async () => {
      const fetchMock = mockFetchOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(DTO_EXITO),
      });
      const user = userEvent.setup();
      render(<ReevaluarPatronesControl esDemo onReevaluado={() => {}} />, {
        wrapper: crearWrapper(),
      });

      const trigger = screen.getByRole('button', {
        name: /Reevaluar categorías/i,
      });
      expect(trigger).toBeDisabled();
      expect(screen.getByRole('note')).toHaveTextContent(/demostraci[oó]n/i);

      await user.click(trigger);

      expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
      expect(fetchMock).not.toHaveBeenCalled();
    });

    it('esDemo=false (default) leaves the trigger enabled and renders no note', () => {
      render(<ReevaluarPatronesControl onReevaluado={() => {}} />, {
        wrapper: crearWrapper(),
      });

      expect(
        screen.getByRole('button', { name: /Reevaluar categorías/i }),
      ).toBeEnabled();
      expect(screen.queryByRole('note')).not.toBeInTheDocument();
    });
  });
});
