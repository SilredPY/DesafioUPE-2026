import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { reenviarCola } from './shared/api/client';
import './shared/ui/estilos.css';
import { router } from './router';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 2, staleTime: 60_000, refetchOnWindowFocus: true } },
});

window.addEventListener('online', () => void reenviarCola());
void reenviarCola();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
