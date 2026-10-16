import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { getJson, reenviarCola } from '../../shared/api/client';
import { pendientes } from '../../shared/api/colaOffline';
import { cambiarTema, colorGuardado, PALETA, temaGuardado, type Tema } from '../../shared/tema';
import { Badge } from '../../shared/ui/Badge';

const TEMAS: { valor: Tema; texto: string }[] = [
  { valor: 'claro', texto: '☀️ Claro' },
  { valor: 'oscuro', texto: '🌙 Oscuro' },
  { valor: 'sistema', texto: '📱 Sistema' },
];

type Salud = { ok: boolean; motor_agrupacion: string; modo_demo: string | null };

export function AjustesPage() {
  const [tema, setTema] = useState(temaGuardado);
  const [color, setColor] = useState(colorGuardado);
  const cola = useQuery({ queryKey: ['cola'], queryFn: async () => (await pendientes()).length });
  const salud = useQuery({ queryKey: ['salud'], queryFn: () => getJson<Salud>('/salud'), staleTime: Infinity });

  function elegir(t: Tema, c: string) {
    setTema(t);
    setColor(c);
    cambiarTema(t, c);
  }

  const personalizado = !PALETA.some((p) => p.color === color);

  return (
    <>
      <h1>Ajustes</h1>
      <p className="subtitulo">Personalizá Ñangarekó a tu gusto. Se guarda en este dispositivo.</p>

      <h2>Apariencia</h2>
      <div className="segmentado" role="group" aria-label="Tema">
        {TEMAS.map((t) => (
          <button key={t.valor} aria-pressed={tema === t.valor} onClick={() => elegir(t.valor, color)}>
            {t.texto}
          </button>
        ))}
      </div>

      <h2>Paleta de colores</h2>
      <div className="paleta" role="group" aria-label="Color principal">
        {PALETA.map((p) => (
          <button key={p.color} className="muestra" style={{ background: p.color }} title={p.nombre}
            aria-label={p.nombre} aria-pressed={color === p.color} onClick={() => elegir(tema, p.color)} />
        ))}
        <label className="muestra personal" title="Color personalizado" aria-pressed={personalizado}>
          <span className="sr-only">Color personalizado</span>
          <input type="color" value={color} onChange={(e) => elegir(tema, e.target.value)} />
        </label>
      </div>

      <h2>Vista previa</h2>
      <div className="pila">
        <section className="hero">
          <div className="hero-icono" aria-hidden="true">🌿</div>
          <h1>Todo tranquilo</h1>
          <p>Así se ven los avisos con tu color.</p>
        </section>
        <div className="fila">
          <button className="boton">Botón principal</button>
          <button className="boton secundario">Secundario</button>
          <Badge severidad="CRITICO" />
        </div>
      </div>

      <h2>Reportes sin enviar</h2>
      <div className="tarjeta fila" style={{ justifyContent: 'space-between' }}>
        <span>
          {cola.data === undefined ? '…' : cola.data === 0 ? '✅ No hay reportes pendientes.' : `📦 ${cola.data} reporte(s) esperando señal.`}
        </span>
        {!!cola.data && (
          <button className="boton chico" onClick={async () => { await reenviarCola(); void cola.refetch(); }}>
            Reintentar ahora
          </button>
        )}
      </div>

      <h2>Acerca de</h2>
      <div className="tarjeta">
        <strong>Ñangarekó IA</strong> v{__APP_VERSION__}
        <p className="meta">
          Motor de agrupación: {salud.data?.motor_agrupacion === 'c++' ? '⚡ C++ nativo' : salud.data ? '🐍 Python' : '…'}
          {salud.data?.modo_demo && ` · Modo demo: ${salud.data.modo_demo}`}
        </p>
        <p className="meta">Hecho en Alto Paraná para el Desafío UPE 2026.</p>
      </div>
    </>
  );
}
