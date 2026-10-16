import { useQuery } from '@tanstack/react-query';
import { Circle, Popup } from 'react-leaflet';
import { getJson } from '../../shared/api/client';
import { ErrorState } from '../../shared/ui/ErrorState';
import { Mapa } from '../../shared/ui/Mapa';
import { Skeleton } from '../../shared/ui/Skeleton';
import { TIPOS, type TipoIncidente } from './BotonesReporteRapido';

type ZonaRoja = { tipo: TipoIncidente; lat: number; lon: number; reportes: number; dispositivos: number; ultimo: string };

export function MapaZonasRojas() {
  const q = useQuery({
    queryKey: ['zonas-rojas'],
    queryFn: () => getJson<ZonaRoja[]>('/transito/zonas-rojas'),
    refetchInterval: 60_000,
  });

  if (q.isPending) return <Skeleton alto={300} />;
  if (q.isError) return <ErrorState error={q.error} reintentar={() => q.refetch()} />;

  return (
    <>
      <Mapa etiqueta="Mapa de zonas rojas de tránsito">
        {q.data.map((z) => (
          <Circle key={`${z.tipo}-${z.lat}-${z.lon}`} center={[z.lat, z.lon]} radius={50}
            pathOptions={{ color: '#c53030', fillOpacity: 0.45 }}>
            <Popup>
              <strong>{TIPOS[z.tipo]}</strong>
              <br />
              Confirmado por {z.dispositivos} vecinos · último aviso{' '}
              {new Date(z.ultimo).toLocaleTimeString('es-PY', { hour: '2-digit', minute: '2-digit' })}
            </Popup>
          </Circle>
        ))}
      </Mapa>
      <p className="subtitulo" style={{ marginTop: 8 }}>
        {q.data.length === 0
          ? 'Sin zonas rojas confirmadas en las últimas 3 horas.'
          : `${q.data.length} zona(s) roja(s) confirmadas por al menos 3 vecinos en las últimas 3 horas.`}
      </p>
    </>
  );
}
