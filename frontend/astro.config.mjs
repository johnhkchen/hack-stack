import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({
    mode: 'standalone'
  }),
  integrations: [svelte()],
  server: {
    port: 4321,
    host: true,
    allowedHosts: ['pipe.b28.dev', 'localhost', '127.0.0.1', '.ngrok.io', '.ngrok-free.app']
  },
  vite: {
    server: {
      allowedHosts: ['pipe.b28.dev', 'localhost', '127.0.0.1', '.ngrok.io', '.ngrok-free.app'],
      proxy: {
        '/api': {
          target: 'http://backend:8000',
          changeOrigin: true
        }
      }
    }
  }
});