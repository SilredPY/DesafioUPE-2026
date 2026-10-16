import { useQuery } from '@tanstack/react-query';
import { CircleMarker, Popup } from 'react-leaflet';
import { getJson } from '../../shared/api/client';
import { Badge, COLOR_SEVERIDAD, type Severidad } from '../../shared/ui/Badge';
import { ErrorState } from '../../shared/ui/ErrorState';
import { Mapa } from '../../shared/ui/Mapa';
import { Skeleton } from '../../shared/ui/Skeleton';
import { CATEGORIAS, type ReporteResiduo } from './categorias';

export function MapaRiesgoPage() {
  const q = useQuery({
    queryKey: ['mapa-residuos'],
    queryFn: () => getJson<ReporteResiduo[]>('/residuos/mapa'),
    refetchInterval: 5 * 60_000,
  });

  return (
    <>
      <h1>Mapa de Riesgo Urbano</h1>
      <p className="subtitulo">Reportes de los últimos 30 días. Más grande y más rojo = más urgente.</p>
      {q.isPending ? (
        <Skeleton alto={320} />
      ) : q.isError ? (
        <ErrorState error={q.error} reintentar={() => q.refetch()} />
      ) : (
        <>
          <Mapa etiqueta="Mapa de reportes de residuos">
            {q.data.map((r) => (
              <CircleMarker key={r.id} center={[r.lat, r.lon]} radius={6 + r.peso * 12}
                pathOptions={{ color: COLOR_SEVERIDAD[r.severidad], fillOpacity: 0.35 + r.peso * 0.4 }}>
                <Popup>
                  <strong>{CATEGORIAS[r.categoria]}</strong> <Badge severidad={r.severidad} />
                  <br />
                  {r.descripcion}
                  <br />
                  <small>{new Date(r.creado).toLocaleString('es-PY')}</small>
                </Popup>
              </CircleMarker>
            ))}
          </Mapa>
          <div className="leyenda">
            {(Object.keys(COLOR_SEVERIDAD) as Severidad[]).map((s) => <Badge key={s} severidad={s} />)}
          </div>
          <p className="subtitulo">{q.data.length} reporte(s) en el mapa.</p>
        </>
      )}
    </>
  );
}
