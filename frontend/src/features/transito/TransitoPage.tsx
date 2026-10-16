import { BotonesReporteRapido } from './BotonesReporteRapido';
import { MapaZonasRojas } from './MapaZonasRojas';

export function TransitoPage() {
  return (
    <>
      <h1>Tape Ysyry</h1>
      <p className="subtitulo">El Waze de los raudales: avisá en un toque qué pasa en la calle donde estás.</p>
      <BotonesReporteRapido />
      <h2>🔴 Zonas rojas ahora</h2>
      <MapaZonasRojas />
    </>
  );
}
