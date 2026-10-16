import { Badge } from '../../shared/ui/Badge';
import type { Alerta } from './useAlertas';

const TITULO: Record<string, string> = {
  TORMENTA: '⛈️ Tormenta',
  LLUVIA_INTENSA: '🌧️ Lluvia intensa',
  INCENDIO: '🔥 Riesgo de incendio',
  CALOR: '🌡️ Calor extremo',
  UV: '☀️ Radiación UV',
};

export function AlertaCard({ alerta }: { alerta: Alerta }) {
  return (
    <article className={`tarjeta alerta sev-${alerta.severidad}`}>
      <div className="alerta-cabecera">
        <strong>{TITULO[alerta.tipo] ?? alerta.tipo}</strong>
        <Badge severidad={alerta.severidad} />
      </div>
      <p className="mensaje">{alerta.mensaje_ciudadano}</p>
      <ul>
        {alerta.consejos.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>
      <details>
        <summary>Dato técnico</summary>
        {alerta.mensaje_tecnico}
      </details>
    </article>
  );
}
