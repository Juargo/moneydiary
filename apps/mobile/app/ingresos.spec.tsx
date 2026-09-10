/**
 * ingresos route spec — T-16 RED (US-056, D-12/D-18/MDET-06)
 *
 * Three route-machine cases:
 * 1. useLocalSearchParams seeds periodo state from query param
 * 2. Arrow press steps periodo state → re-fetch fires
 * 3. back Pressable calls router.back
 *
 * Architecture: ingresos.tsx is a thin wrapper that reads params, owns local
 * periodo state, and passes them to IngresosMesScreen. The screen owns the
 * fetch lifecycle and useFocusEffect. This mirrors the M1 pattern
 * (bucket/[bucket].tsx → BucketDetalleScreen).
 *
 * **Esperar la PANTALLA, no el PEDIDO (issue #618, 2026-09-10)**: estos casos
 * hacían `await waitFor(() => expect(mockFetchIngresosMes).toHaveBeenCalled())`
 * y seguían. Ese `waitFor` se satisface en cuanto el fetch SE LLAMA — la
 * promesa todavía no resolvió, el estado sigue en `loading`, y en esa fase la
 * pantalla renderiza sólo el botón de volver y el spinner: el selector de
 * período NO existe. Bajo carga (la suite corriendo junto a otros workspaces)
 * la promesa tardaba lo suficiente como para que el caso terminara antes de
 * tiempo, RNTL desmontara el árbol en su `afterEach`, y el `setEstado` huérfano
 * resolviera después contra un árbol muerto — de ahí los `act(...)` warnings y
 * el `render function has not been called` del caso siguiente. Reproducido 1 de
 * 6 corridas bajo carga concurrente.
 *
 * La regla que dejan: esperar SIEMPRE al elemento que se va a usar (`findBy*`),
 * nunca a un mock intermedio. `findBy*` reintenta hasta que el árbol se asienta,
 * así que cada caso termina con su propio estado ya resuelto y no le hereda
 * resaca al que sigue.
 *
 * Y todos hacen `await render(...)`, no `render(...)` pelado. En RNTL 14 el
 * `screen` global recién queda poblado cuando el árbol commitea, un tick
 * después: sin ese `await`, la primera lectura de `screen` da
 * `render function has not been called` — verificado acá quitándoselo y
 * viendo fallar los tres casos. (Las queries que antes devolvía `render()`
 * ya no existen en v14, así que `screen` es el único camino.)
 */

import {
  act,
  render,
  screen,
  fireEvent,
  waitFor,
} from '@testing-library/react-native';
import type { ApiResult } from '../src/api/client';
import type { IngresosMesDto } from '../src/domain/detalle.types';

import IngresosMesPage from './ingresos';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

const mockFetchIngresosMes = jest.fn<
  Promise<ApiResult<IngresosMesDto>>,
  [string?]
>();

jest.mock('../src/api/client', () => ({
  ...jest.requireActual('../src/api/client'),
  fetchIngresosMes: (periodo?: string) => mockFetchIngresosMes(periodo),
}));

const mockRouterBack = jest.fn();
const mockUseLocalSearchParams = jest.fn<{ periodo?: string }, []>();

jest.mock('expo-router', () => {
  const { useEffect } = jest.requireActual('react');
  return {
    useRouter: () => ({ back: mockRouterBack }),
    useLocalSearchParams: () => mockUseLocalSearchParams(),
    useFocusEffect: (callback: () => void) => {
      useEffect(() => {
        callback();
      }, [callback]);
    },
  };
});

// ---------------------------------------------------------------------------
// Fixture
// ---------------------------------------------------------------------------

function makeDto(overrides: Partial<IngresosMesDto> = {}): IngresosMesDto {
  return {
    conteo: 2,
    total: '500000',
    transacciones: [
      {
        id: 'ing-r1',
        descripcion: 'Sueldo',
        fecha: '2026-07-01',
        monto: '500000',
        origen: 'BancoEstado',
      },
    ],
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ingresos route', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('useLocalSearchParams seeds periodo state from query param', async () => {
    mockUseLocalSearchParams.mockReturnValue({ periodo: '2026-07' });
    mockFetchIngresosMes.mockResolvedValue({ ok: true, value: makeDto() });

    await render(<IngresosMesPage />);

    expect(await screen.findByTestId('ingresos-mes-header')).toBeTruthy();
    expect(mockFetchIngresosMes).toHaveBeenCalledWith('2026-07');
  });

  it('periodo state steps on SelectorPeriodoMes arrow press → re-fetch fires', async () => {
    jest.useFakeTimers({
      doNotFake: [
        'hrtime',
        'nextTick',
        'performance',
        'queueMicrotask',
        'requestAnimationFrame',
        'cancelAnimationFrame',
        'requestIdleCallback',
        'cancelIdleCallback',
        'setImmediate',
        'clearImmediate',
        'setInterval',
        'clearInterval',
        'setTimeout',
        'clearTimeout',
      ],
      now: new Date('2026-08-15T12:00:00.000Z'),
    });

    try {
      mockUseLocalSearchParams.mockReturnValue({ periodo: '2026-07' });
      mockFetchIngresosMes.mockResolvedValue({ ok: true, value: makeDto() });

      await render(<IngresosMesPage />);

      // `findByRole`, no `waitFor(fetch fue llamado)` + `getByRole`: el
      // control sólo existe en la fase `data`, así que hay que esperar a la
      // PANTALLA, no al PEDIDO (ver el comentario del bloque, issue #618).
      const prevBtn = await screen.findByRole('button', {
        name: 'Mes anterior',
      });
      expect(mockFetchIngresosMes).toHaveBeenCalledWith('2026-07');

      jest.clearAllMocks();
      mockFetchIngresosMes.mockResolvedValue({ ok: true, value: makeDto() });

      await act(async () => {
        fireEvent.press(prevBtn);
      });

      await waitFor(() => {
        expect(mockFetchIngresosMes).toHaveBeenCalledWith('2026-06');
      });
      // El re-fetch ya salió, pero su promesa sigue en vuelo: sin esperar a
      // que el árbol vuelva a la fase `data`, este caso termina con un
      // `setEstado` pendiente que resuelve contra un árbol ya desmontado
      // (issue #618 — es exactamente la resaca que rompía al caso siguiente).
      expect(await screen.findByTestId('ingresos-mes-header')).toBeTruthy();
    } finally {
      jest.useRealTimers();
    }
  });

  it('back Pressable calls router.back', async () => {
    mockUseLocalSearchParams.mockReturnValue({ periodo: '2026-07' });
    mockFetchIngresosMes.mockReturnValue(new Promise(() => {}));

    await render(<IngresosMesPage />);

    // Este caso se queda a propósito en la fase `loading` (el fetch nunca
    // resuelve), y el botón de volver existe en las TRES fases.
    const backBtn = await screen.findByRole('button', {
      name: 'Volver al resumen',
    });
    fireEvent.press(backBtn);

    expect(mockRouterBack).toHaveBeenCalledTimes(1);
  });
});
