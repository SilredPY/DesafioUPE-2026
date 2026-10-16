import { NavLink } from 'react-router-dom';
import { useInstalar } from '../hooks/useInstalar';

export function Header() {
  const instalar = useInstalar();
  return (
    <header className="header">
      <div className="header-marca">
        <img src="/icon.svg" alt="" width={34} height={34} />
        <div style={{ flex: 1 }}>
          <strong>Ñangarekó IA</strong>
          <small>Cuidamos juntos Alto Paraná</small>
        </div>
        {instalar && (
          <button className="boton chico" onClick={instalar}>
            ⬇ Instalar
          </button>
        )}
        <NavLink to="/ajustes" className="icono-boton" aria-label="Ajustes: tema y colores" viewTransition>
          ⚙️
        </NavLink>
      </div>
    </header>
  );
}
