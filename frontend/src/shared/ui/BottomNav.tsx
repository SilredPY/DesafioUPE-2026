import { NavLink } from 'react-router-dom';

const SECCIONES = [
  { a: '/', icono: '⛈️', texto: 'Clima' },
  { a: '/tape-ysyry', icono: '🚦', texto: 'Tránsito' },
  { a: '/yty', icono: '📷', texto: 'Reportar' },
  { a: '/yty/mapa', icono: '🗺️', texto: 'Mapa' },
];

export function BottomNav() {
  return (
    <nav className="nav" aria-label="Secciones">
      {SECCIONES.map((s) => (
        <NavLink key={s.a} to={s.a} end>
          <span aria-hidden="true">{s.icono}</span>
          {s.texto}
        </NavLink>
      ))}
    </nav>
  );
}
