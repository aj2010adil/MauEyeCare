import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { checker } from 'vite-plugin-checker'
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
   checker({
      typescript: true,
    }),  ],
  server: {
    port: 5175,
    hmr: true,
  },
  base: '/',
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
