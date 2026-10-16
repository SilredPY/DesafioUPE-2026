import { useQuery } from '@tanstack/react-query';
import { getJson } from '../../shared/api/client';
import type { Severidad } from '../../shared/ui/Badge';

export type Ciudad = { slug: string; nombre: string };

export type Alerta = {
  tipo: string;
  severidad: Severidad;
  mensaje_ciudadano: string;
  mensaje_tecnico: string;
  consejos: string[];
};

export type ResumenClima = {
  ciudad: string;
  temporada: 'EL_NINO' | 'LA_NINA' | 'NEUTRAL';
  lluvia_activa: boolean;
  alertas: Alerta[];
};

export const useCiudades = () =>
  useQuery({ queryKey: ['ciudades'], queryFn: () => getJson<Ciudad[]>('/clima/ciudades'), staleTime: Infinity });

export const useAlertas = (ciudad: string) =>
  useQuery({
    queryKey: ['alertas', ciudad],
    queryFn: () => getJson<ResumenClima>(`/clima/alertas?ciudad=${encodeURIComponent(ciudad)}`),
    refetchInterval: 10 * 60_000,
  });
