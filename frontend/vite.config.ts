import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'tailwindcss',
      config: {
        postcss: {
          plugins: [tailwindcss, autoprefixer],
        },
      },
    },
  ],
  server: {
    port: 5175,
    hmr: true,  // Enable hot module replacement
  },
  build: {
    sourcemap: true,
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
});
