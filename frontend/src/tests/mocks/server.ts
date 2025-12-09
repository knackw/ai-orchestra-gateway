import { setupServer } from 'msw/node'
import { handlers } from './handlers'

/**
 * MSW Server Setup for Node.js (Vitest) tests
 * This server intercepts HTTP requests during testing
 */
export const server = setupServer(...handlers)

// Enable API mocking before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))

// Reset handlers after each test
afterEach(() => server.resetHandlers())

// Clean up after all tests
afterAll(() => server.close())
