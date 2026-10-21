import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5174,
    strictPort: true,
  },
  build: {
    manifest: true,
    outDir: resolve(__dirname, 'static'),
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.jsx'),
      },
      output: {
        entryFileNames: 'js/main-bundle.js',
        assetFileNames: 'css/main.[ext]',
      },
    },
  },
})