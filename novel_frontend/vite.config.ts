import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// GitHub Pages 部署时 base 为仓库名，本地开发为 '/'
const base = process.env.GITHUB_PAGES === 'true' ? '/novel-web/' : '/'

export default defineConfig({
  plugins: [vue()],
  base,
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
