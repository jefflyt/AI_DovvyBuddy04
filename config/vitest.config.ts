import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()] as any,
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: [path.resolve(__dirname, './vitest.setup.ts')],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
      // Exclude old component tests that need @testing-library/react
      'src/components/chat/__tests__/TripLeadForm.test.tsx',
      'src/components/chat/__tests__/TrainingLeadForm.test.tsx',
      'src/components/chat/__tests__/LeadCaptureModal.test.tsx',
      // Exclude Playwright E2E tests (run separately with pnpm test:e2e)
      'tests/e2e/**',
      // Exclude archived tests (preserved for reference only)
      'tests/archived/**',
    ],
    environmentOptions: {
      jsdom: {
        resources: 'usable',
        url: 'http://localhost:3000',
      },
    },
    env: {
      NODE_ENV: 'development', // Enable console logging in analytics/monitoring tests
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
    },
  },
})
