import { usePreferencia } from '../../shared/hooks/usePreferencia';
import { ErrorState } from '../../shared/ui/ErrorState';
import { Skeleton } from '../../shared/ui/Skeleton';
import { AlertaCard } from './AlertaCard';
import { useAlertas, useCiudades } from './useAlertas';

const TEMPORADA = { EL_NINO: 'El Niño (lluvias)', LA_NINA: 'La Niña (calor y sequía)', NEUTRAL: 'Neutral' };

export function AlertasPage() {
  const [ciudad, setCiudad] = usePreferencia('ciudad', 'ciudad-del-este');
  const ciudades = useCiudades();
  const q = useAlertas(ciudad);

  return (
    <>
      <h1>Aratiri & Oky</h1>
      <p className="subtitulo">Alertas del clima para tu ciudad, explicadas claro.</p>

      <label className="sr-only" htmlFor="ciudad">Ciudad</label>
      <select id="ciudad" value={ciudad} onChange={(e) => setCiudad(e.target.value)}>
        {(ciudades.data ?? [{ slug: ciudad, nombre: 'Cargando ciudades…' }]).map((c) => (
          <option key={c.slug} value={c.slug}>{c.nombre}</option>
        ))}
      </select>

      <div className="pila" style={{ marginTop: 16 }} aria-live="polite">
        {q.isPending ? (
          <Skeleton alto={120} cantidad={2} />
        ) : q.isError ? (
          <ErrorState error={q.error} reintentar={() => q.refetch()} />
        ) : (
          <>
            <div className="aviso">
              Temporada: <strong>{TEMPORADA[q.data.temporada]}</strong>
              {q.data.lluvia_activa && ' · 🌧️ Lluvia en las próximas horas'}
            </div>
            {q.data.alertas.length === 0 ? (
              <div className="tarjeta">✅ Sin alertas para {q.data.ciudad} en las próximas 6 horas. ¡Buen día!</div>
            ) : (
              q.data.alertas.map((a) => <AlertaCard key={a.tipo} alerta={a} />)
            )}
          </>
        )}
      </div>
    </>
  );
}
