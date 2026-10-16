import { useQuery } from '@tanstack/react-query';
import { CircleMarker, Popup } from 'react-leaflet';
import { getJson } from '../../shared/api/client';
import { Badge, COLOR_SEVERIDAD, SEVERIDADES } from '../../shared/ui/Badge';
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
        <Skeleton alto={360} />
      ) : q.isError ? (
        <ErrorState error={q.error} reintentar={() => q.refetch()} />
      ) : (
        <>
          <div className="stats">
            <div className="stat"><strong>{q.data.length}</strong><small>Reportes</small></div>
            <div className="stat critico">
              <strong>{q.data.filter((r) => r.severidad === 'CRITICO').length}</strong><small>Críticos</small>
            </div>
            <div className="stat">
              <strong>{q.data.filter((r) => r.categoria === 'SUMIDERO_BLOQUEADO').length}</strong><small>Sumideros tapados</small>
            </div>
          </div>
          <Mapa etiqueta="Mapa de reportes de residuos">
            {/* Los críticos al final para que queden dibujados encima. */}
            {[...q.data].sort((a, b) => a.peso - b.peso).map((r) => (
              <CircleMarker key={r.id} center={[r.lat, r.lon]} radius={7 + r.peso * 14}
                pathOptions={{ color: COLOR_SEVERIDAD[r.severidad], weight: 2, fillOpacity: 0.3 + r.peso * 0.45 }}>
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
            Riesgo: {SEVERIDADES.map((s) => <Badge key={s} severidad={s} />)}
          </div>
        </>
      )}
    </>
  );
}
