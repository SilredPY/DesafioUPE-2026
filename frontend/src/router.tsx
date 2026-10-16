import { createBrowserRouter } from 'react-router-dom';
import { App } from './App';
import { AlertasPage } from './features/clima/AlertasPage';

// Solo la portada va en el bundle inicial; el resto (mapas con Leaflet, campus, ajustes) se descarga al abrirse.
export const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      { path: '/', element: <AlertasPage /> },
      { path: '/tape-ysyry', lazy: () => import('./features/transito/TransitoPage').then((m) => ({ Component: m.TransitoPage })) },
      { path: '/yty', lazy: () => import('./features/residuos/ReportarFotoPage').then((m) => ({ Component: m.ReportarFotoPage })) },
      { path: '/yty/mapa', lazy: () => import('./features/residuos/MapaRiesgoPage').then((m) => ({ Component: m.MapaRiesgoPage })) },
      { path: '/campus', lazy: () => import('./features/campus/CampusPage').then((m) => ({ Component: m.CampusPage })) },
      { path: '/ajustes', lazy: () => import('./features/ajustes/AjustesPage').then((m) => ({ Component: m.AjustesPage })) },
      { path: '*', element: <AlertasPage /> },
    ],
  },
]);
