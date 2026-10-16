import { Outlet } from 'react-router-dom';
import { BottomNav } from './shared/ui/BottomNav';
import { OfflineBanner } from './shared/ui/OfflineBanner';

export function App() {
  return (
    <>
      <OfflineBanner />
      <main className="app">
        <Outlet />
      </main>
      <BottomNav />
    </>
  );
}
