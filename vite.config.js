import { defineConfig } from 'vite'
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    outDir: 'website/static',  // 👈 Adjust as needed
    rollupOptions: {
      input: {
        main: 'frontend/js/main.js', // 👈 Adjust as needed
      },
      output: {
        entryFileNames: 'js/main.min.js',
        assetFileNames: 'css/main.min.[ext]',
      },
    },
  },
})
