export type Coord = { lat: number; lon: number };

// Mismo rectángulo que backend/app/shared/geo.py (el servidor vuelve a validar).
const ZONA = { latMin: -25.8, latMax: -25.2, lonMin: -55.0, lonMax: -54.55 };

export const dentroDeZona = (c: Coord) =>
  c.lat >= ZONA.latMin && c.lat <= ZONA.latMax && c.lon >= ZONA.lonMin && c.lon <= ZONA.lonMax;

const NUM = String.raw`(-?\d{1,3}\.\d+)`;
// En orden de precisión: el pin del lugar (!3d!4d) es exacto; "@" es el centro de la vista.
const PATRONES = [
  new RegExp(String.raw`!3d${NUM}!4d${NUM}`),
  new RegExp(String.raw`[?&](?:q|query|ll|destination|center)=${NUM},\s*${NUM}`),
  new RegExp(String.raw`@${NUM},${NUM}`),
  new RegExp(String.raw`^\s*${NUM}\s*,\s*${NUM}\s*$`),
];

export type Lectura = { ok: true; coord: Coord } | { ok: false; error: string };

/** Extrae coordenadas de un link de Google Maps (o de un texto "lat, lon"). */
export function leerCoordenadas(texto: string): Lectura {
  let t = texto.trim();
  try {
    t = decodeURIComponent(t);
  } catch {
    /* texto con % sueltos: se usa tal cual */
  }
  if (/(maps\.app\.goo\.gl|goo\.gl\/maps)/i.test(t)) {
    return { ok: false, error: 'Es un link corto: abrilo en el navegador y copiá el link largo de la barra de direcciones.' };
  }
  for (const p of PATRONES) {
    const m = t.match(p);
    if (!m) continue;
    const coord = { lat: Number(m[1]), lon: Number(m[2]) };
    if (!dentroDeZona(coord)) return { ok: false, error: 'Esa ubicación está fuera del área metropolitana de Alto Paraná.' };
    return { ok: true, coord };
  }
  return { ok: false, error: 'No encontramos coordenadas en ese texto. Pegá el link completo de Google Maps.' };
}
