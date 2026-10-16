import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { enviar } from '../../shared/api/client';
import { ubicacionActual } from '../../shared/ubicacion';
import { Badge } from '../../shared/ui/Badge';
import { CalendarioBarrio } from './CalendarioBarrio';
import { CATEGORIAS, type ReporteResiduo } from './categorias';
import { comprimirImagen } from './comprimirImagen';

type Resultado = { tipo: 'ok'; reporte: ReporteResiduo } | { tipo: 'encolado' } | { tipo: 'error'; texto: string };

export function ReportarFotoPage() {
  const qc = useQueryClient();
  const [foto, setFoto] = useState<Blob | null>(null);
  const [vista, setVista] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<Resultado | null>(null);

  useEffect(() => () => { if (vista) URL.revokeObjectURL(vista); }, [vista]);

  async function elegirFoto(archivo: File | undefined) {
    setResultado(null);
    if (!archivo) return;
    try {
      const blob = await comprimirImagen(archivo);
      setFoto(blob);
      setVista(URL.createObjectURL(blob));
    } catch (e) {
      setResultado({ tipo: 'error', texto: e instanceof Error ? e.message : 'Foto inválida.' });
    }
  }

  async function enviarReporte() {
    if (!foto) return;
    setEnviando(true);
    try {
      const { lat, lon } = await ubicacionActual();
      const r = await enviar<ReporteResiduo>('/residuos/reportes', {
        tipo: 'form',
        campos: { foto, lat: String(lat), lon: String(lon) },
      });
      setResultado(r.estado === 'enviado' ? { tipo: 'ok', reporte: r.data } : { tipo: 'encolado' });
      setFoto(null);
      setVista(null);
      qc.invalidateQueries({ queryKey: ['mapa-residuos'] });
    } catch (e) {
      setResultado({ tipo: 'error', texto: e instanceof Error ? e.message : 'No se pudo enviar.' });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <h1>Yty & Sumideros</h1>
      <p className="subtitulo">Cazabasurales: la IA clasifica tu foto, calcula el riesgo según el clima y la marca en el mapa.</p>

      <div className="pila">
        <label className="zona-foto">
          {vista ? (
            <img className="preview" src={vista} alt="Vista previa de la foto a reportar (tocá para cambiarla)" />
          ) : (
            <>
              <span className="emoji" aria-hidden="true">📷</span>
              <strong>Sacá o elegí una foto</strong>
              <span>Basural, desagüe tapado o escombros en la calle</span>
            </>
          )}
          <input className="sr-only" type="file" accept="image/*" capture="environment"
            onChange={(e) => elegirFoto(e.target.files?.[0])} />
        </label>
        <button className="boton" disabled={!foto || enviando} onClick={enviarReporte}>
          {enviando ? '🤖 Analizando con IA…' : '📍 Enviar reporte con mi ubicación'}
        </button>

        <div aria-live="polite">
          {resultado?.tipo === 'ok' && (
            <div className={`tarjeta alerta sev-${resultado.reporte.severidad}`}>
              <div className="alerta-cabecera">
                <strong>{CATEGORIAS[resultado.reporte.categoria]}</strong>
                <Badge severidad={resultado.reporte.severidad} />
              </div>
              <p>{resultado.reporte.descripcion}</p>
              {resultado.reporte.severidad === 'CRITICO' && (
                <p><strong>🌧️ Viene lluvia: este sumidero tapado puede inundar la cuadra.</strong></p>
              )}
              <p><Link to="/yty/mapa">Ver en el mapa de riesgo →</Link></p>
            </div>
          )}
          {resultado?.tipo === 'encolado' && (
            <div className="aviso atencion">📶 Sin señal: guardamos tu foto y la enviamos apenas vuelva la conexión.</div>
          )}
          {resultado?.tipo === 'error' && <div className="aviso error">{resultado.texto}</div>}
        </div>
      </div>

      <h2>🚛 Calendario del camión recolector</h2>
      <CalendarioBarrio />
    </>
  );
}
