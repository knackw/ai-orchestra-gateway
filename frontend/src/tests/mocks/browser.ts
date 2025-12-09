import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

/**
 * MSW Browser Worker Setup
 * This worker intercepts HTTP requests in the browser (for Storybook/dev mode)
 *
 * To use in development:
 * 1. Run: npx msw init public/ --save
 * 2. Import and start the worker in your app
 */
export const worker = setupWorker(...handlers)
