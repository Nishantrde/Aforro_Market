import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
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