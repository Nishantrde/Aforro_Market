import { defineConfig } from 'vite';
import path from 'path';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/static/', 
  server: {
    cors: true, 
    port: 5174,
    strictPort: true,
  },
  build: {
    outDir: path.resolve(__dirname, './static'),
    emptyOutDir: false,
    manifest: "manifest.json",
    rollupOptions: {
      input: {
        'main': path.resolve(__dirname, './src/main.jsx'), 
        // 'style': path.resolve(__dirname, './src/style.css'),
      },
      output: {
        entryFileNames: `js/[name]-bundle.js`,
        assetFileNames: `css/[name].css`,
      },
    },
  },
});