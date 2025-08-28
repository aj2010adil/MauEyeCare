import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    port: 5175, // Ensure Vite uses the correct port
  },
  build: {
    sourcemap: true, // Enable sourcemaps for debugging
  },
})
