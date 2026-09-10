import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      // Forward requests to the existing 3D View Vite dev server
      '/3d-view-app': {
        target: 'http://localhost:4173',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/3d-view-app/, ''),
        ws: true,
      },
    },
  },
})
