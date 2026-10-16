import type { Severidad } from '../../shared/ui/Badge';

export const CATEGORIAS: Record<string, string> = {
  VERTEDERO_CLANDESTINO: '🗑️ Vertedero clandestino',
  SUMIDERO_BLOQUEADO: '🕳️ Sumidero bloqueado',
  OBSTRUCCION_VIAL: '🚧 Obstrucción vial',
  PENDIENTE: '⏳ Pendiente de revisión',
};

export type ReporteResiduo = {
  id: string | null;
  lat: number;
  lon: number;
  categoria: string;
  confianza: number;
  descripcion: string;
  severidad: Severidad;
  peso: number;
  creado: string;
};
