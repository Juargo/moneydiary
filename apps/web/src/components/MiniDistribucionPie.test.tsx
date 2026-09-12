import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { MiniDistribucionPie } from './MiniDistribucionPie';
import type { TajadaGasto } from '@/domain/distribucion-gasto';

// US-030 Slice C (task 30.12): compact, non-interactive, decorative pie for
// the annual grid. Reuses pie-geometry directly (no duplicated arc math) —
// see the component's docstring for why this is a thin wrapper rather than a
// `compact` flag threaded through `DistribucionPie`.
const tajadas: ReadonlyArray<TajadaGasto> = [
  { bucket: 'Necesidades', porcentaje: 50, fraccion: 0.5 },
  { bucket: 'Deseos', porcentaje: 30, fraccion: 0.3 },
  { bucket: 'Ahorro', porcentaje: 20, fraccion: 0.2 },
];

describe('MiniDistribucionPie', () => {
  it('renders one slice per tajada with its resolved color', () => {
    render(<MiniDistribucionPie tajadas={tajadas} />);
    const fills = screen
      .getAllByTestId('mini-pie-slice')
      .map((el) => el.getAttribute('fill'));
    // Brote bucket palette (2026-09-12): steel blue→Necesidades, plum→Gustos, jade→Ahorro.
    expect(fills).toEqual(['#77A7E5', '#BB6C90', '#47DAB4']);
  });

  // WDS-07 (WCAG 1.4.11 non-text contrast): same adjacency problem as the
  // main pie's fill wedges — a separator stroke between slices.
  // Reliability follow-up (post-PR4): reverted from the `stroke-card` token
  // class back to a theme-immune literal. THIS component is the sharpest
  // reason that revert has to stand: its pie renders inside a cell that is
  // `bg-card` normally but `bg-ingreso` when the month is selected
  // (`ResumenAnual`), so no single surface token could ever describe the
  // stroke's backdrop.
  //
  // Tecno-Analítico (2026-09-02, history): the literal's VALUE changed,
  // white → #0d0f15, dropping a bright halo on the dark ground (1.03:1 on
  // card, 1.24:1 on the ingreso tint) — that part of the stroke's job never
  // depends on the bucket fills. Its separation FROM the fills does, and the
  // fills themselves are not permanent — they were re-tinted for Brote
  // (2026-09-12); current separation numbers per fill live in
  // `lib/pie-colors.ts`, not here.
  it('renders a theme-immune dark stroke separator on each slice for WCAG 1.4.11 adjacency contrast, never a theme-flipping token', () => {
    render(<MiniDistribucionPie tajadas={tajadas} />);
    for (const slice of screen.getAllByTestId('mini-pie-slice')) {
      expect(slice).toHaveAttribute('stroke', '#0d0f15');
      expect(slice).not.toHaveClass('stroke-card');
    }
  });

  it('renders no percent labels, legend, or IDEAL inset — only the wedges', () => {
    render(<MiniDistribucionPie tajadas={tajadas} />);
    expect(screen.queryByText('50%')).not.toBeInTheDocument();
    expect(screen.queryByText('IDEAL')).not.toBeInTheDocument();
    expect(
      screen.queryByRole('img', { name: 'Distribución ideal 50/30/20' }),
    ).not.toBeInTheDocument();
  });

  it('is decorative — hidden from the accessibility tree', () => {
    const { container } = render(<MiniDistribucionPie tajadas={tajadas} />);
    expect(container.querySelector('svg')).toHaveAttribute(
      'aria-hidden',
      'true',
    );
  });

  it('is non-interactive — no button roles on slices', () => {
    render(<MiniDistribucionPie tajadas={tajadas} />);
    expect(screen.queryAllByRole('button')).toHaveLength(0);
  });

  it('renders a muted placeholder ring instead of dividing by zero when there is no spending', () => {
    render(<MiniDistribucionPie tajadas={[]} />);
    expect(screen.queryAllByTestId('mini-pie-slice')).toHaveLength(0);
    expect(screen.getByTestId('mini-pie-placeholder')).toBeInTheDocument();
  });

  it('renders without NaN when one slice has fraccion 0 mixed with non-zero slices', () => {
    const conCero: ReadonlyArray<TajadaGasto> = [
      { bucket: 'Necesidades', porcentaje: 60, fraccion: 0.6 },
      { bucket: 'Deseos', porcentaje: 40, fraccion: 0.4 },
      { bucket: 'Ahorro', porcentaje: 0, fraccion: 0 },
    ];
    render(<MiniDistribucionPie tajadas={conCero} />);
    const paths = screen.getAllByTestId('mini-pie-slice');
    expect(paths).toHaveLength(3);
    for (const path of paths) {
      expect(path.getAttribute('d')).not.toMatch(/NaN/);
    }
  });
});
