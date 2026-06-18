import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Base path matches the GitHub Pages project subpath: https://<user>.github.io/NCS-DASH/
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === 'build' ? '/NCS-DASH/' : '/',
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
}))
