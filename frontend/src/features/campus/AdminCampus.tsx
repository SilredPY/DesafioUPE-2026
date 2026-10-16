import { useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { postJson } from '../../shared/api/client';
import { ubicacionActual } from '../../shared/ubicacion';
import type { Institucion, TipoAviso } from './useCampus';

const TIPOS_AVISO: { valor: TipoAviso; texto: string }[] = [
  { valor: 'GENERAL', texto: '📌 General' },
  { valor: 'CLIMA', texto: '⛈️ Clima' },
  { valor: 'TRANSITO', texto: '🚦 Tránsito' },
  { valor: 'CLASES_VIRTUALES', texto: '💻 Clases virtuales' },
  { valor: 'CLASES_SUSPENDIDAS', texto: '⛔ Clases suspendidas' },
];

type Estado = { clase: string; texto: string } | null;

/** Panel para personal de la institución: publicar avisos y sumar nuevas instituciones (requiere ADMIN_TOKEN). */
export function AdminCampus({ slug }: { slug: string }) {
  const qc = useQueryClient();
  const [token, setToken] = useState('');
  const [estado, setEstado] = useState<Estado>(null);
  const [coords, setCoords] = useState({ lat: '', lon: '' });

  async function ejecutar(accion: () => Promise<string>) {
    setEstado(null);
    try {
      setEstado({ clase: '', texto: await accion() });
    } catch (e) {
      setEstado({ clase: 'error', texto: e instanceof Error ? e.message : 'No se pudo completar.' });
    }
  }

  function publicarAviso(ev: FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    const f = new FormData(ev.currentTarget);
    const form = ev.currentTarget;
    void ejecutar(async () => {
      await postJson(`/campus/${slug}/avisos`, {
        tipo: f.get('tipo'), titulo: f.get('titulo'), mensaje: f.get('mensaje'), horas_vigencia: Number(f.get('horas')),
      }, { 'X-Admin-Token': token });
      form.reset();
      await qc.invalidateQueries({ queryKey: ['campus', slug] });
      return '✅ Aviso publicado. Ya lo ven todos los estudiantes.';
    });
  }

  function agregarInstitucion(ev: FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    const f = new FormData(ev.currentTarget);
    const form = ev.currentTarget;
    void ejecutar(async () => {
      const i = await postJson<Institucion>('/campus/instituciones', {
        nombre: f.get('nombre'), ciudad: f.get('ciudad'), lat: Number(coords.lat), lon: Number(coords.lon),
        radio_m: Number(f.get('radio')),
      }, { 'X-Admin-Token': token });
      form.reset();
      setCoords({ lat: '', lon: '' });
      await qc.invalidateQueries({ queryKey: ['instituciones'] });
      return `✅ ${i.nombre} agregada. Ya aparece en la lista.`;
    });
  }

  return (
    <details className="tarjeta" style={{ marginTop: 28 }}>
      <summary><strong>🔐 Administración de la institución</strong></summary>
      <div className="pila" style={{ marginTop: 12 }}>
        <label className="campo">
          Token de administración
          <input type="password" autoComplete="off" value={token} onChange={(e) => setToken(e.target.value)}
            placeholder="ADMIN_TOKEN del servidor" />
        </label>

        <form className="pila" onSubmit={publicarAviso}>
          <strong>Publicar aviso</strong>
          <label className="campo">Tipo
            <select name="tipo" defaultValue="GENERAL">
              {TIPOS_AVISO.map((t) => <option key={t.valor} value={t.valor}>{t.texto}</option>)}
            </select>
          </label>
          <label className="campo">Título<input name="titulo" required minLength={3} maxLength={120} /></label>
          <label className="campo">Mensaje<textarea name="mensaje" required minLength={3} maxLength={1000} /></label>
          <label className="campo">Vigencia (horas)<input name="horas" type="number" min={1} max={720} defaultValue={24} /></label>
          <button className="boton" disabled={!token}>Publicar aviso</button>
        </form>

        <form className="pila" onSubmit={agregarInstitucion}>
          <strong>Agregar institución educativa</strong>
          <label className="campo">Nombre<input name="nombre" required minLength={3} maxLength={120}
            placeholder="Ej.: Facultad Politécnica — UNE" /></label>
          <label className="campo">Ciudad<input name="ciudad" required minLength={2} maxLength={60} /></label>
          <div className="fila">
            <label className="campo" style={{ flex: 1 }}>Latitud
              <input required inputMode="decimal" value={coords.lat} onChange={(e) => setCoords({ ...coords, lat: e.target.value })} />
            </label>
            <label className="campo" style={{ flex: 1 }}>Longitud
              <input required inputMode="decimal" value={coords.lon} onChange={(e) => setCoords({ ...coords, lon: e.target.value })} />
            </label>
          </div>
          <button type="button" className="boton secundario" onClick={() => void ejecutar(async () => {
            const p = await ubicacionActual();
            setCoords({ lat: p.lat.toFixed(6), lon: p.lon.toFixed(6) });
            return '📍 Ubicación cargada: revisá que sea la del campus.';
          })}>📍 Usar mi ubicación actual</button>
          <label className="campo">Radio de influencia (metros)
            <input name="radio" type="number" min={200} max={10000} defaultValue={1500} />
          </label>
          <button className="boton" disabled={!token}>Agregar institución</button>
        </form>

        <div aria-live="polite">{estado && <div className={`aviso ${estado.clase}`}>{estado.texto}</div>}</div>
      </div>
    </details>
  );
}
