import { Outlet, useLocation } from 'react-router-dom';
import { BottomNav } from './shared/ui/BottomNav';
import { Header } from './shared/ui/Header';
import { OfflineBanner } from './shared/ui/OfflineBanner';

export function App() {
  const { pathname } = useLocation();
  return (
    <>
      <OfflineBanner />
      <Header />
      <main className="app">
        {/* key: reinicia la animación de entrada en cada sección */}
        <div className="pagina" key={pathname}>
          <Outlet />
        </div>
      </main>
      <BottomNav />
    </>
  );
}
