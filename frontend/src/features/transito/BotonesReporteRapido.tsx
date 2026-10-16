import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { enviar } from '../../shared/api/client';
import { ubicacionActual } from '../../shared/ubicacion';

export const TIPOS = {
  RAUDAL: '🌊 Raudal peligroso / calle intransitable',
  SEMAFORO_CABLE: '⚡ Semáforo apagado / cable caído',
  BACHE: '🕳️ Bache ciego u obstrucción por agua',
} as const;

export type TipoIncidente = keyof typeof TIPOS;

export function BotonesReporteRapido() {
  const qc = useQueryClient();
  const [enviando, setEnviando] = useState<TipoIncidente | null>(null);
  const [estado, setEstado] = useState<{ ok: boolean; texto: string } | null>(null);

  async function reportar(tipo: TipoIncidente) {
    setEnviando(tipo);
    setEstado(null);
    try {
      const { lat, lon } = await ubicacionActual();
      const r = await enviar('/transito/reportes', { tipo: 'json', datos: { tipo, lat, lon } });
      setEstado({
        ok: true,
        texto: r.estado === 'enviado'
          ? '¡Gracias! Tu reporte ya está en el mapa de la comunidad.'
          : 'Sin señal: guardamos tu reporte y lo enviamos apenas vuelva la conexión.',
      });
      qc.invalidateQueries({ queryKey: ['zonas-rojas'] });
    } catch (e) {
      setEstado({ ok: false, texto: e instanceof Error ? e.message : 'No se pudo enviar el reporte.' });
    } finally {
      setEnviando(null);
    }
  }

  return (
    <div className="pila">
      {(Object.keys(TIPOS) as TipoIncidente[]).map((t) => (
        <button key={t} className="boton grande" disabled={enviando !== null} onClick={() => reportar(t)}>
          {enviando === t ? 'Enviando…' : TIPOS[t]}
        </button>
      ))}
      <div aria-live="polite">
        {estado && <div className={`aviso ${estado.ok ? '' : 'error'}`}>{estado.texto}</div>}
      </div>
    </div>
  );
}
