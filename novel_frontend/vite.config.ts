import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 部署平台自适应 base 路径
// - EdgeOne Pages / Vercel / 自定义域名: '/'
// - GitHub Pages: '/novel-web/'
const getBase = () => {
  if (process.env.GITHUB_PAGES === 'true') return '/novel-web/'
  if (process.env.EDGEONE_PAGES === 'true') return '/'
  return '/'
}

export default defineConfig({
  plugins: [vue()],
  base: getBase(),
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
