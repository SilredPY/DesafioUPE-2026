import L from 'leaflet';
import { useEffect, useState } from 'react';
import { Circle, Marker, useMap, useMapEvents } from 'react-leaflet';
import { ubicacionActual } from '../../shared/ubicacion';
import { Mapa } from '../../shared/ui/Mapa';
import { dentroDeZona, leerCoordenadas, type Coord } from './coordenadas';

// Ícono propio: el ícono por defecto de Leaflet no se resuelve bien con bundlers.
const PIN = L.divIcon({ className: 'pin-mapa', html: '📍', iconSize: [36, 36], iconAnchor: [18, 34] });

// Leaflet dibuja con atributos SVG, que no entienden var(--…): se lee el color del tema ya resuelto.
const colorTema = () => getComputedStyle(document.documentElement).getPropertyValue('--primario').trim() || '#0f766e';

type Resultado ={ lat: string; lon: string; display_name: string };
type Mensaje = { clase: string; texto: string } | null;

function AlTocar({ alElegir }: { alElegir: (c: Coord) => void }) {
  useMapEvents({ click: (e) => alElegir({ lat: e.latlng.lat, lon: e.latlng.lng }) });
  return null;
}

function Seguir({ a }: { a: Coord | null }) {
  const map = useMap();
  useEffect(() => {
    if (a) map.flyTo([a.lat, a.lon], Math.max(map.getZoom(), 16), { duration: 0.6 });
  }, [a, map]);
  return null;
}

/** Elegir la ubicación exacta de un campus: tocar el mapa, arrastrar el pin, buscar o pegar un link de Google Maps. */
export function SelectorUbicacion({ valor, alCambiar, radio }: { valor: Coord | null; alCambiar: (c: Coord) => void; radio: number }) {
  const [busqueda, setBusqueda] = useState('');
  const [resultados, setResultados] = useState<Resultado[]>([]);
  const [link, setLink] = useState('');
  const [buscando, setBuscando] = useState(false);
  const [mensaje, setMensaje] = useState<Mensaje>(null);

  function elegir(c: Coord) {
    if (!dentroDeZona(c)) {
      setMensaje({ clase: 'error', texto: 'Ese punto está fuera del área metropolitana de Alto Paraná.' });
      return;
    }
    setMensaje(null);
    alCambiar({ lat: Number(c.lat.toFixed(6)), lon: Number(c.lon.toFixed(6)) });
  }

  async function buscar() {
    if (busqueda.trim().length < 3) return;
    setBuscando(true);
    setMensaje(null);
    try {
      // Nominatim (OpenStreetMap): gratis, limitado a Alto Paraná. Búsqueda solo al confirmar, no mientras se escribe.
      const params = new URLSearchParams({
        q: busqueda, format: 'jsonv2', limit: '5', countrycodes: 'py', 'accept-language': 'es',
        viewbox: '-55.0,-25.2,-54.55,-25.8', bounded: '1',
      });
      const r = await fetch(`https://nominatim.openstreetmap.org/search?${params}`, { signal: AbortSignal.timeout(8000) });
      const datos: Resultado[] = await r.json();
      setResultados(datos);
      if (!datos.length) setMensaje({ clase: 'atencion', texto: 'Sin resultados. Probá con otro nombre o tocá el mapa.' });
    } catch {
      setMensaje({ clase: 'error', texto: 'No se pudo buscar (¿sin señal?). Tocá el mapa o pegá un link.' });
    } finally {
      setBuscando(false);
    }
  }

  function usarLink() {
    const r = leerCoordenadas(link);
    if (r.ok) {
      elegir(r.coord);
      setLink('');
    } else setMensaje({ clase: 'error', texto: r.error });
  }

  const alEnter = (accion: () => void) => (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // estamos dentro del formulario de alta: Enter no debe enviarlo
      accion();
    }
  };

  return (
    <div className="pila">
      <div className="fila">
        <input style={{ flex: 1 }} value={busqueda} onChange={(e) => setBusqueda(e.target.value)}
          onKeyDown={alEnter(buscar)} placeholder="Buscar: Universidad, colegio, calle…" aria-label="Buscar lugar" />
        <button type="button" className="boton secundario" onClick={buscar} disabled={buscando}>
          {buscando ? '…' : '🔎'}
        </button>
      </div>
      {resultados.length > 0 && (
        <div className="resultados">
          {resultados.map((r) => (
            <button type="button" key={`${r.lat},${r.lon}`}
              onClick={() => { elegir({ lat: Number(r.lat), lon: Number(r.lon) }); setResultados([]); }}>
              📍 {r.display_name}
            </button>
          ))}
        </div>
      )}

      <Mapa etiqueta="Mapa para elegir la ubicación del campus" clase="mapa compacto">
        <AlTocar alElegir={elegir} />
        <Seguir a={valor} />
        {valor && (
          <>
            <Circle center={[valor.lat, valor.lon]} radius={radio}
              pathOptions={{ color: colorTema(), weight: 2, fillOpacity: 0.12, dashArray: '6 6' }} />
            <Marker position={[valor.lat, valor.lon]} icon={PIN} draggable
              eventHandlers={{ dragend: (e) => { const p = e.target.getLatLng(); elegir({ lat: p.lat, lon: p.lng }); } }} />
          </>
        )}
      </Mapa>
      <p className="meta" style={{ margin: 0 }}>
        {valor
          ? `📍 ${valor.lat}, ${valor.lon} · el círculo muestra el radio de influencia. Arrastrá el pin para ajustar.`
          : 'Tocá el mapa sobre la entrada del campus para marcarlo.'}
      </p>

      <div className="fila">
        <input style={{ flex: 1 }} value={link} onChange={(e) => setLink(e.target.value)} onKeyDown={alEnter(usarLink)}
          placeholder="…o pegá un link de Google Maps" aria-label="Link de Google Maps" />
        <button type="button" className="boton secundario" onClick={usarLink} disabled={!link.trim()}>Usar</button>
      </div>
      <button type="button" className="boton secundario" onClick={async () => {
        try {
          elegir(await ubicacionActual());
        } catch (e) {
          setMensaje({ clase: 'error', texto: e instanceof Error ? e.message : 'Sin ubicación.' });
        }
      }}>📍 Estoy en el campus: usar mi ubicación</button>

      <div aria-live="polite">{mensaje && <div className={`aviso ${mensaje.clase}`}>{mensaje.texto}</div>}</div>
    </div>
  );
}
