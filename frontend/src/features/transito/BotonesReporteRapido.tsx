import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { enviar } from '../../shared/api/client';
import { ubicacionActual } from '../../shared/ubicacion';

export const TIPOS = {
  RAUDAL: { emoji: '🌊', texto: 'Raudal / calle intransitable' },
  SEMAFORO_CABLE: { emoji: '⚡', texto: 'Semáforo apagado / cable caído' },
  BACHE: { emoji: '🕳️', texto: 'Bache ciego / agua' },
} as const;

export type TipoIncidente = keyof typeof TIPOS;

export function BotonesReporteRapido() {
  const qc = useQueryClient();
  const [enviando, setEnviando] = useState<TipoIncidente | null>(null);
  const [estado, setEstado] = useState<{ clase: string; texto: string } | null>(null);

  async function reportar(tipo: TipoIncidente) {
    setEnviando(tipo);
    setEstado(null);
    try {
      const { lat, lon } = await ubicacionActual();
      const r = await enviar('/transito/reportes', { tipo: 'json', datos: { tipo, lat, lon } });
      navigator.vibrate?.(60);
      setEstado(r.estado === 'enviado'
        ? { clase: '', texto: '✅ ¡Gracias! Si 3 vecinos confirman, se marca como Zona Roja.' }
        : { clase: 'atencion', texto: '📶 Sin señal: guardamos tu reporte y lo enviamos apenas vuelva la conexión.' });
      qc.invalidateQueries({ queryKey: ['zonas-rojas'] });
    } catch (e) {
      setEstado({ clase: 'error', texto: e instanceof Error ? e.message : 'No se pudo enviar el reporte.' });
    } finally {
      setEnviando(null);
    }
  }

  return (
    <div className="pila">
      <div className="tiles">
        {(Object.keys(TIPOS) as TipoIncidente[]).map((t) => (
          <button key={t} className={`tile ${t} ${enviando === t ? 'enviando' : ''}`} disabled={enviando !== null}
            onClick={() => reportar(t)}>
            <span className="emoji" aria-hidden="true">{TIPOS[t].emoji}</span>
            {enviando === t ? 'Enviando…' : TIPOS[t].texto}
          </button>
        ))}
      </div>
      <div aria-live="polite">{estado && <div className={`aviso ${estado.clase}`}>{estado.texto}</div>}</div>
    </div>
  );
}
