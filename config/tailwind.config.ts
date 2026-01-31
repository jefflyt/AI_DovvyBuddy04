import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    '../src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    '../src/components/**/*.{js,ts,jsx,tsx,mdx}',
    '../src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Ocean-inspired brand colors
        primary: {
          50: '#e6f4ff',
          100: '#b3deff',
          200: '#80c9ff',
          300: '#4db3ff',
          400: '#1a9dff',
          500: '#0077BE', // Primary ocean blue
          600: '#005f9a',
          700: '#004876',
          800: '#003052',
          900: '#00182e',
        },
        accent: {
          50: '#e6f9f5',
          100: '#b3ede0',
          200: '#80e1cb',
          300: '#4dd5b6',
          400: '#1ac9a1',
          500: '#00B894', // Tropical teal
          600: '#009376',
          700: '#006e58',
          800: '#00493a',
          900: '#00241c',
        },
        neutral: {
          50: '#f8f9fa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Oxygen',
          'Ubuntu',
          'Cantarell',
          'Fira Sans',
          'Droid Sans',
          'Helvetica Neue',
          'sans-serif',
        ],
      },
      spacing: {
        '18': '4.5rem',
        '112': '28rem',
        '128': '32rem',
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 12px rgba(0, 0, 0, 0.12)',
        'hard': '0 8px 24px rgba(0, 0, 0, 0.16)',
      },
    },
  },
  plugins: [],
}

export default config
