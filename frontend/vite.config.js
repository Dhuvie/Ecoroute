import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        host: true,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: false,
        chunkSizeWarningLimit: 2000,
        rollupOptions: {
            output: {
                manualChunks: {
                    'react-vendor': ['react', 'react-dom', 'react-router-dom'],
                    'plotly': ['react-plotly.js', 'plotly.js-dist-min'],
                    'leaflet': ['leaflet', 'react-leaflet'],
                },
            },
        },
        // Reduce memory usage during build
        minify: 'esbuild',
        target: 'es2020',
    },
    esbuild: {
        logLevel: 'info',
    },
});
