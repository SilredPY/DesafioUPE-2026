import 'leaflet/dist/leaflet.css';
import type { ReactNode } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';

// Centro entre Ciudad del Este, Pdte. Franco, Hernandarias y Minga Guazú.
const CENTRO_METRO: [number, number] = [-25.49, -54.66];

export function Mapa({ children, etiqueta, clase = 'mapa' }: { children: ReactNode; etiqueta: string; clase?: string }) {
  return (
    <div role="region" aria-label={etiqueta}>
      <MapContainer center={CENTRO_METRO} zoom={12} className={clase} scrollWheelZoom={false}>
        {/* shortcut: tiles públicos de OSM (uso moderado); usar un proveedor propio si crece el tráfico. */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {children}
      </MapContainer>
    </div>
  );
}
