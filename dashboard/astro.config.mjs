import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import AstroPWA from '@vite-pwa/astro';

// https://astro.build/config
export default defineConfig({
  integrations: [
    react(),
    AstroPWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'AlphaBot-50 Control Center',
        short_name: 'AlphaBot',
        description: 'Elite Algorithmic Trading Dashboard',
        theme_color: '#020617',
        icons: [
          {
            src: 'pwa-192x192.png', // Nota: Deberás generar estos archivos o usar placeholders
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,jpg,jpeg,gif,webp,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.origin === 'http://localhost:8000',
            handler: 'NetworkOnly', # Los datos de trading siempre deben ser frescos
          }
        ]
      }
    })
  ],
});