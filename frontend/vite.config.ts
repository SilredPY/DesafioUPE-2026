import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Ñangarekó IA',
        short_name: 'Ñangarekó',
        description: 'Tu compañero diario para anticiparte al clima, ordenar tu ciudad y moverte seguro.',
        lang: 'es-PY',
        theme_color: '#0f766e',
        background_color: '#0f766e',
        display: 'standalone',
        start_url: '/',
        icons: [{ src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any maskable' }],
      },
      workbox: {
        navigateFallbackDenylist: [/^\/api\//],
        runtimeCaching: [
          {
            // Mapas disponibles sin señal en la zona ya visitada.
            urlPattern: /^https:\/\/tile\.openstreetmap\.org\//,
            handler: 'CacheFirst',
            options: { cacheName: 'mapas', expiration: { maxEntries: 600, maxAgeSeconds: 30 * 24 * 3600 } },
          },
          {
            // Última respuesta conocida si la red falla o tarda más de 5 s.
            urlPattern: ({ url, request }) => url.pathname.startsWith('/api/') && request.method === 'GET',
            handler: 'NetworkFirst',
            options: { cacheName: 'api', networkTimeoutSeconds: 5 },
          },
        ],
      },
    }),
  ],
  server: { proxy: { '/api': 'http://localhost:8000' } },
  preview: { proxy: { '/api': 'http://localhost:8000' } },
});
