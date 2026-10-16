import { createBrowserRouter } from 'react-router-dom';
import { App } from './App';
import { AlertasPage } from './features/clima/AlertasPage';

// Las pantallas con mapa (Leaflet) se descargan recién cuando se abren: primera carga más liviana.
export const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      { path: '/', element: <AlertasPage /> },
      { path: '/tape-ysyry', lazy: () => import('./features/transito/TransitoPage').then((m) => ({ Component: m.TransitoPage })) },
      { path: '/yty', lazy: () => import('./features/residuos/ReportarFotoPage').then((m) => ({ Component: m.ReportarFotoPage })) },
      { path: '/yty/mapa', lazy: () => import('./features/residuos/MapaRiesgoPage').then((m) => ({ Component: m.MapaRiesgoPage })) },
    ],
  },
]);
