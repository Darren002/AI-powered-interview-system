/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Minimalist Black & White
        black: {
          DEFAULT: '#000000',
          50: '#0A0A0A',
          100: '#111111',
          200: '#1A1A1A',
          300: '#2A2A2A',
          400: '#3A3A3A',
          500: '#4A4A4A',
          600: '#5A5A5A',
          700: '#6A6A6A',
          800: '#7A7A7A',
          900: '#8A8A8A',
        },
        white: {
          DEFAULT: '#FFFFFF',
          50: '#F5F5F5',
          100: '#EBEBEB',
          200: '#DADADA',
          300: '#C0C0C0',
          400: '#A0A0A0',
        },
        // Accent colors (minimal use)
        accent: {
          DEFAULT: '#FFFFFF',
          muted: '#888888',
        },
        success: '#FFFFFF',
        warning: '#AAAAAA',
        error: '#666666',
        info: '#FFFFFF',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
        'score-up': 'scoreUp 0.8s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        scoreUp: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.3)',
        'glass-hover': '0 12px 40px rgba(0, 0, 0, 0.4)',
        'card': '0 2px 8px rgba(0, 0, 0, 0.3)',
      },
    },
  },
  plugins: [],
}
