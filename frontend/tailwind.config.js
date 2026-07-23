/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // LED Glowing Palette
        eco: {
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
        },
        // Skeuomorphic Panel / Metal colors
        panel: {
          400: '#475569',
          500: '#334155', // Base metal
          600: '#1e293b', // Dark metal
          700: '#171e2e', // Deep recessed panel
          800: '#0f172a', // Very deep base
          900: '#0b1120',
          950: '#020617', // Pitch black
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
        display: ['"Exo 2"', 'Inter', 'sans-serif'], // Mechanical look
      },
      boxShadow: {
        // Raised physical buttons
        'btn-raised': 'inset 0 1px 1px rgba(255, 255, 255, 0.15), inset 0 -1px 1px rgba(0, 0, 0, 0.4), 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
        'btn-active': 'inset 0 3px 6px rgba(0,0,0,0.6), inset 0 0 10px rgba(0,0,0,0.5)',
        
        // Panels and frames
        'bezel': 'inset 0 1px 1px rgba(255,255,255,0.1), inset 0 -1px 2px rgba(0,0,0,0.8), 0 1px 2px rgba(0,0,0,0.5)',
        'recessed': 'inset 0 2px 8px rgba(0, 0, 0, 0.8), inset 0 1px 3px rgba(0, 0, 0, 0.6), 0 1px 0 rgba(255, 255, 255, 0.05)',
        'lcd': 'inset 0 3px 12px rgba(0,0,0,0.8), 0 1px 1px rgba(255,255,255,0.05)',
        
        // LED Glows
        'glow-green': '0 0 10px rgba(34, 197, 94, 0.4), 0 0 20px rgba(34, 197, 94, 0.2)',
        'glow-red': '0 0 10px rgba(239, 68, 68, 0.4), 0 0 20px rgba(239, 68, 68, 0.2)',
        'glow-blue': '0 0 10px rgba(59, 130, 246, 0.4), 0 0 20px rgba(59, 130, 246, 0.2)',
        'glow-amber': '0 0 10px rgba(245, 158, 11, 0.4), 0 0 20px rgba(245, 158, 11, 0.2)',
      },
      backgroundImage: {
        'metal-gradient': 'linear-gradient(180deg, #334155 0%, #1e293b 100%)',
        'btn-gradient': 'linear-gradient(180deg, #475569 0%, #334155 100%)',
        'led-screen': 'linear-gradient(180deg, #0f172a 0%, #0b1120 100%)',
        'brushed-metal': 'repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 2px), linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.4s ease-in-out',
        'led-blink': 'ledBlink 1s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        ledBlink: {
          '0%, 100%': { opacity: '1', filter: 'brightness(1.2)' },
          '50%': { opacity: '0.4', filter: 'brightness(0.8)' },
        },
      },
    },
  },
  plugins: [],
}
