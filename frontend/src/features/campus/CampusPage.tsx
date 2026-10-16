import { useEffect } from 'react';
import { usePreferencia } from '../../shared/hooks/usePreferencia';
import { ErrorState } from '../../shared/ui/ErrorState';
import { Skeleton } from '../../shared/ui/Skeleton';
import { AlertaCard } from '../clima/AlertaCard';
import { TIPOS } from '../transito/BotonesReporteRapido';
import { AdminCampus } from './AdminCampus';
import { useEstadoCampus, useInstituciones, type EstadoCampus, type TipoAviso } from './useCampus';

const HERO: Record<EstadoCampus['recomendacion']['nivel'], { clase: string; icono: string }> = {
  NORMAL: { clase: '', icono: '🎓' },
  PRECAUCION: { clase: 'ALTO', icono: '⚠️' },
  NO_SALIR: { clase: 'CRITICO', icono: '🏠' },
  SIN_CLASES: { clase: 'INFO', icono: '📢' },
};

const AVISO: Record<TipoAviso, string> = {
  CLASES_SUSPENDIDAS: '⛔ Clases suspendidas',
  CLASES_VIRTUALES: '💻 Clases virtuales',
  CLIMA: '⛈️ Clima',
  TRANSITO: '🚦 Tránsito',
  GENERAL: '📌 General',
};

const hora = (iso: string) =>
  new Date(iso).toLocaleString('es-PY', { weekday: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'America/Asuncion' });

export function CampusPage() {
  const [slug, setSlug] = usePreferencia('institucion', 'upe-presidente-franco');
  const insts = useInstituciones();
  const q = useEstadoCampus(slug);

  // Si la institución guardada ya no existe, volver a la primera disponible.
  useEffect(() => {
    if (insts.data?.length && !insts.data.some((i) => i.slug === slug)) setSlug(insts.data[0].slug);
  }, [insts.data, slug, setSlug]);

  const e = q.data;
  const hero = e ? HERO[e.recomendacion.nivel] : null;

  return (
    <>
      <section className={`hero ${hero?.clase ?? ''}`} aria-live="polite">
        <div className="hero-icono" aria-hidden="true">{hero?.icono ?? '⏳'}</div>
        <h1>{e?.recomendacion.titulo ?? 'Revisando tu campus…'}</h1>
        <p>{e?.recomendacion.texto ?? 'Clima, tránsito y avisos de tu institución en un solo lugar.'}</p>
        {e && (
          <div className="chips">
            {e.lluvia_activa && <span className="chip">🌧️ Lluvia en camino</span>}
            <span className="chip">🚦 {e.zonas_rojas.length} zona(s) roja(s) cerca</span>
            <span className="chip">📢 {e.avisos.length} aviso(s)</span>
          </div>
        )}
        <label className="sr-only" htmlFor="institucion">Institución</label>
        <select id="institucion" value={slug} onChange={(ev) => setSlug(ev.target.value)}>
          {(insts.data ?? [{ slug, nombre: 'Cargando instituciones…' }]).map((i) => (
            <option key={i.slug} value={i.slug}>🎓 {i.nombre}</option>
          ))}
        </select>
      </section>

      {q.isPending ? (
        <div style={{ marginTop: 16 }}><Skeleton alto={110} cantidad={3} /></div>
      ) : q.isError ? (
        <div style={{ marginTop: 16 }}><ErrorState error={q.error} reintentar={() => q.refetch()} /></div>
      ) : (
        <>
          <h2>📢 Avisos de la institución</h2>
          <div className="pila">
            {q.data.avisos.length === 0 ? (
              <div className="tarjeta meta">Sin avisos vigentes.</div>
            ) : (
              q.data.avisos.map((a) => (
                <article key={a.id} className={`tarjeta alerta ${a.tipo.startsWith('CLASES') ? 'sev-CRITICO' : 'sev-MEDIO'}`}>
                  <div className="alerta-cabecera">
                    <strong>{a.titulo}</strong>
                    <span className="badge INFO">{AVISO[a.tipo]}</span>
                  </div>
                  <p>{a.mensaje}</p>
                  <p className="meta">Publicado {hora(a.creado)} · vigente hasta {hora(a.vigente_hasta)}</p>
                </article>
              ))
            )}
          </div>

          <h2>⛈️ Clima en el campus</h2>
          <div className="pila">
            {q.data.alertas.length === 0 ? (
              <div className="tarjeta meta">☀️ Sin alertas climáticas en las próximas 6 horas.</div>
            ) : (
              q.data.alertas.map((a) => <AlertaCard key={a.tipo} alerta={a} />)
            )}
          </div>

          <h2>🚦 Alrededores (radio de {(q.data.institucion.radio_m / 1000).toLocaleString('es-PY')} km)</h2>
          <div className="stats">
            <div className="stat critico"><strong>{q.data.zonas_rojas.length}</strong><small>Zonas rojas</small></div>
            <div className="stat critico"><strong>{q.data.residuos_criticos}</strong><small>Sumideros/basura críticos</small></div>
            <div className="stat"><strong>{q.data.lluvia_activa ? 'Sí' : 'No'}</strong><small>Lluvia en camino</small></div>
          </div>
          {q.data.zonas_rojas.length > 0 && (
            <div className="pila">
              {q.data.zonas_rojas.map((z) => (
                <div key={`${z.tipo}-${z.lat}-${z.lon}`} className="aviso error">
                  {TIPOS[z.tipo].emoji} <strong>{TIPOS[z.tipo].texto}</strong>
                  <span className="meta"> · {z.dispositivos} vecinos · {hora(z.ultimo)}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      <AdminCampus slug={slug} />
    </>
  );
}
