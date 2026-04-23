
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) {
            return
          }
          if (id.includes('echarts')) {
            return 'chart-vendor'
          }
          if (id.includes('element-plus') || id.includes('@element-plus')) {
            return 'ui-vendor'
          }
          if (id.includes('vue-router') || id.includes('/vue/') || id.includes('pinia')) {
            return 'vue-vendor'
          }
          if (id.includes('axios')) {
            return 'http-vendor'
          }
          return 'vendor'
        }
      }
    }
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
