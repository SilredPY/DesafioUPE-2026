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
    <article className="tarjeta">
      <strong>{TITULO[alerta.tipo] ?? alerta.tipo}</strong> <Badge severidad={alerta.severidad} />
      <p>{alerta.mensaje_ciudadano}</p>
      <ul>
        {alerta.consejos.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>
      <details>
        <summary>Dato técnico</summary>
        <small>{alerta.mensaje_tecnico}</small>
      </details>
    </article>
  );
}
