import { usePreferencia } from '../../shared/hooks/usePreferencia';
import { peorSeveridad } from '../../shared/ui/Badge';
import { ErrorState } from '../../shared/ui/ErrorState';
import { Skeleton } from '../../shared/ui/Skeleton';
import { AlertaCard } from './AlertaCard';
import { useAlertas, useCiudades, type ResumenClima } from './useAlertas';

const TEMPORADA = { EL_NINO: '🌊 El Niño · lluvias', LA_NINA: '🔥 La Niña · calor y sequía', NEUTRAL: '🌤️ Temporada neutral' };

function estado(r: ResumenClima | undefined) {
  const peor = r && peorSeveridad(r.alertas.map((a) => a.severidad));
  if (peor === 'CRITICO') return { clase: 'CRITICO', icono: '🚨', titulo: 'Oĩ la peligro', texto: 'Hay alertas críticas: seguí los consejos de abajo.' };
  if (peor) return { clase: 'ALTO', icono: '⚠️', titulo: 'Atención', texto: 'Hay alertas para tu ciudad en las próximas horas.' };
  return { clase: '', icono: '🌿', titulo: 'Todo tranquilo', texto: 'Sin alertas en las próximas 6 horas.' };
}

export function AlertasPage() {
  const [ciudad, setCiudad] = usePreferencia('ciudad', 'ciudad-del-este');
  const ciudades = useCiudades();
  const q = useAlertas(ciudad);
  const e = estado(q.data);

  return (
    <>
      <section className={`hero ${e.clase}`} aria-live="polite">
        <div className="hero-icono" aria-hidden="true">{q.isPending ? '⏳' : e.icono}</div>
        <h1>{q.isPending ? 'Consultando el cielo…' : e.titulo}</h1>
        <p>{q.isPending ? 'Aratiri & Oky revisa el pronóstico de tu zona.' : e.texto}</p>
        {q.data && (
          <div className="chips">
            <span className="chip">{TEMPORADA[q.data.temporada]}</span>
            {q.data.lluvia_activa && <span className="chip">🌧️ Lluvia en camino</span>}
            <span className="chip">{q.data.alertas.length} alerta(s)</span>
          </div>
        )}
        <label className="sr-only" htmlFor="ciudad">Ciudad</label>
        <select id="ciudad" value={ciudad} onChange={(ev) => setCiudad(ev.target.value)}>
          {(ciudades.data ?? [{ slug: ciudad, nombre: 'Cargando ciudades…' }]).map((c) => (
            <option key={c.slug} value={c.slug}>📍 {c.nombre}</option>
          ))}
        </select>
      </section>

      <h2>Aratiri & Oky · Alertas</h2>
      <div className="pila">
        {q.isPending ? (
          <Skeleton alto={140} cantidad={2} />
        ) : q.isError ? (
          <ErrorState error={q.error} reintentar={() => q.refetch()} />
        ) : q.data.alertas.length === 0 ? (
          <div className="tarjeta vacio">
            <span className="emoji" aria-hidden="true">☀️</span>
            Buen día para {q.data.ciudad}. Igual podés ayudar reportando basura o calles en mal estado.
          </div>
        ) : (
          q.data.alertas.map((a) => <AlertaCard key={a.tipo} alerta={a} />)
        )}
      </div>
    </>
  );
}
