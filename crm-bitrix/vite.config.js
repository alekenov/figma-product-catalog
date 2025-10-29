import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    root: '.',
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      rollupOptions: {
        input: './index.html'
      }
    },
    server: {
      port: parseInt(env.VITE_CRM_PORT || '5177'),
      host: true,
      proxy: {
        '/api/v1': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8014',
          changeOrigin: true,
          rewrite: (path) => path,
          secure: false,
          ws: false
        },
        '/api/v2': {
          target: 'https://cvety.kz',
          changeOrigin: true,
          rewrite: (path) => path,
          secure: false,
          ws: false,
          configure: (proxy, _options) => {
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              // Forward Authorization header from frontend
              if (req.headers.authorization) {
                proxyReq.setHeader('Authorization', req.headers.authorization);
              }
              proxyReq.setHeader('X-City', env.VITE_BITRIX_CITY || 'astana');
            });
          }
        }
      }
    },
    preview: {
      host: true,
      port: parseInt(env.PORT || '3000'),
      allowedHosts: [
        'crm-bitrix.workers.dev',
        '.railway.app',
        'localhost'
      ]
    }
  }
})
