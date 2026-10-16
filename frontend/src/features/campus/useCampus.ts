import { useQuery } from '@tanstack/react-query';
import { getJson } from '../../shared/api/client';
import type { Alerta } from '../clima/useAlertas';
import type { TipoIncidente } from '../transito/BotonesReporteRapido';

export type Institucion = { slug: string; nombre: string; ciudad: string; lat: number; lon: number; radio_m: number };

export type TipoAviso = 'CLASES_SUSPENDIDAS' | 'CLASES_VIRTUALES' | 'CLIMA' | 'TRANSITO' | 'GENERAL';

export type Aviso = { id: string; tipo: TipoAviso; titulo: string; mensaje: string; vigente_hasta: string; creado: string };

export type EstadoCampus = {
  institucion: Institucion;
  recomendacion: { nivel: 'NORMAL' | 'PRECAUCION' | 'NO_SALIR' | 'SIN_CLASES'; titulo: string; texto: string };
  lluvia_activa: boolean;
  alertas: Alerta[];
  zonas_rojas: { tipo: TipoIncidente; lat: number; lon: number; dispositivos: number; ultimo: string }[];
  residuos_criticos: number;
  avisos: Aviso[];
};

export const useInstituciones = () =>
  useQuery({ queryKey: ['instituciones'], queryFn: () => getJson<Institucion[]>('/campus/instituciones'), staleTime: 10 * 60_000 });

export const useEstadoCampus = (slug: string) =>
  useQuery({
    queryKey: ['campus', slug],
    queryFn: () => getJson<EstadoCampus>(`/campus/${encodeURIComponent(slug)}/estado`),
    enabled: !!slug,
    refetchInterval: 5 * 60_000,
  });
