import { BotonesReporteRapido } from './BotonesReporteRapido';
import { MapaZonasRojas } from './MapaZonasRojas';

export function TransitoPage() {
  return (
    <>
      <h1>Tape Ysyry</h1>
      <p className="subtitulo">Avisá en un toque qué está pasando en la calle donde estás.</p>
      <BotonesReporteRapido />
      <h2>Zonas rojas</h2>
      <MapaZonasRojas />
    </>
  );
}
