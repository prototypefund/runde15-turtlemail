import { URL, fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import svgLoader from 'vite-svg-loader'

export default defineConfig(({ mode }) => {
  return {
    base: mode === 'development' ? '/' : '/-/static/turtlemail/bundled/',
    clearScreen: false,
    publicDir: './src/public',
    plugins: [svgLoader(), vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    build: {
      manifest: true,
      rollupOptions: {
        input: ['./src/main.ts', './src/style.css'],
        output: {
          hashCharacters: 'hex',
          assetFileNames: 'assets/[name].hash-[hash][extname]',
          chunkFileNames: '[name].hash-[hash].js',
          entryFileNames: '[name].hash-[hash].js',
          dir: './turtlemail/static/turtlemail/bundled/',
        },
      },
    },
  }
})
