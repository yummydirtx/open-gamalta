import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      // Proxy WebSocket connections to backend
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
})
