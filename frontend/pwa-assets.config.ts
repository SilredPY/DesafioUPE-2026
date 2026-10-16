import { defineConfig, minimal2023Preset as base } from '@vite-pwa/assets-generator/config';

// Íconos a sangre: iOS y Android recortan sus propias esquinas, así que el fondo debe ser el color de marca.
const aSangre = { padding: 0, resizeOptions: { background: '#0f766e' } };

export default defineConfig({
  preset: {
    ...base,
    transparent: { ...base.transparent, padding: 0 },
    maskable: { ...base.maskable, ...aSangre },
    apple: { ...base.apple, ...aSangre },
  },
  images: ['public/icon.svg'],
});
