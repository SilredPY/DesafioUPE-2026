export const SEVERIDADES = ['BAJO', 'MEDIO', 'ALTO', 'CRITICO'] as const;
export type Severidad = (typeof SEVERIDADES)[number];

const ETIQUETA: Record<Severidad, string> = { BAJO: 'Bajo', MEDIO: 'Medio', ALTO: 'Alto', CRITICO: 'Crítico' };

export const COLOR_SEVERIDAD: Record<Severidad, string> = {
  BAJO: '#2f855a',
  MEDIO: '#b7791f',
  ALTO: '#dd6b20',
  CRITICO: '#e53e3e',
};

export const peorSeveridad = (lista: Severidad[]): Severidad | null =>
  lista.reduce<Severidad | null>((peor, s) => (!peor || SEVERIDADES.indexOf(s) > SEVERIDADES.indexOf(peor) ? s : peor), null);

export function Badge({ severidad }: { severidad: Severidad }) {
  return <span className={`badge ${severidad}`}>{ETIQUETA[severidad]}</span>;
}
