export type Severidad = 'BAJO' | 'MEDIO' | 'ALTO' | 'CRITICO';

const ETIQUETA: Record<Severidad, string> = { BAJO: 'Bajo', MEDIO: 'Medio', ALTO: 'Alto', CRITICO: 'Crítico' };

export const COLOR_SEVERIDAD: Record<Severidad, string> = {
  BAJO: '#2f855a',
  MEDIO: '#b7791f',
  ALTO: '#c05621',
  CRITICO: '#c53030',
};

export function Badge({ severidad }: { severidad: Severidad }) {
  return <span className={`badge ${severidad}`}>{ETIQUETA[severidad]}</span>;
}
