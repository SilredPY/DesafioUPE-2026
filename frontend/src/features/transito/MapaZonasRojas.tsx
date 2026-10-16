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
      <div className="stats">
        <div className="stat critico"><strong>{q.data.length}</strong><small>Zonas rojas</small></div>
        <div className="stat"><strong>{q.data.reduce((n, z) => n + z.dispositivos, 0)}</strong><small>Vecinos confirmando</small></div>
        <div className="stat"><strong>3 h</strong><small>Ventana</small></div>
      </div>
      <Mapa etiqueta="Mapa de zonas rojas de tránsito">
        {q.data.map((z) => (
          <Circle key={`${z.tipo}-${z.lat}-${z.lon}`} center={[z.lat, z.lon]} radius={60}
            pathOptions={{ color: '#e53e3e', weight: 3, fillOpacity: 0.4 }}>
            <Popup>
              <strong>{TIPOS[z.tipo].emoji} {TIPOS[z.tipo].texto}</strong>
              <br />
              Confirmado por {z.dispositivos} vecinos · último aviso{' '}
              {new Date(z.ultimo).toLocaleTimeString('es-PY', { hour: '2-digit', minute: '2-digit' })}
            </Popup>
          </Circle>
        ))}
      </Mapa>
      <p className="leyenda">
        {q.data.length === 0
          ? '🟢 Sin zonas rojas confirmadas. Las calles se ven bien por ahora.'
          : '🔴 Zona Roja = al menos 3 vecinos distintos reportaron lo mismo a menos de 50 m.'}
      </p>
    </>
  );
}
