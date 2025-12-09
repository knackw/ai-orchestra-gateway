import { test as base, Page } from '@playwright/test'

/**
 * Authentication state for E2E tests
 */
export interface AuthState {
  accessToken: string
  refreshToken: string
  user: {
    id: string
    email: string
    role: 'user' | 'admin'
  }
}

/**
 * Test fixtures for authenticated users
 */
export const test = base.extend<{
  authenticatedPage: Page
  adminPage: Page
}>({
  /**
   * Regular authenticated user fixture
   * Logs in as a standard user before each test
   */
  authenticatedPage: async ({ page }, use) => {
    // Navigate to login page
    await page.goto('/login')

    // Fill in login form
    await page.fill('input[name="email"]', process.env.TEST_USER_EMAIL || 'test@example.com')
    await page.fill('input[name="password"]', process.env.TEST_USER_PASSWORD || 'Test123!@#$%')

    // Submit login form
    await page.click('button[type="submit"]')

    // Wait for navigation to dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 })

    // Use the authenticated page
    await use(page)
  },

  /**
   * Admin user fixture
   * Logs in as an admin user before each test
   */
  adminPage: async ({ page }, use) => {
    // Navigate to login page
    await page.goto('/login')

    // Fill in admin login form
    await page.fill('input[name="email"]', process.env.TEST_ADMIN_EMAIL || 'admin@example.com')
    await page.fill('input[name="password"]', process.env.TEST_ADMIN_PASSWORD || 'Admin123!@#$%')

    // Submit login form
    await page.click('button[type="submit"]')

    // Wait for navigation to admin dashboard
    await page.waitForURL(/\/(admin|dashboard)/, { timeout: 10000 })

    // Use the authenticated admin page
    await use(page)
  },
})

export { expect } from '@playwright/test'

/**
 * Mock authentication state for testing
 */
export const mockAuthState: AuthState = {
  accessToken: 'mock-access-token',
  refreshToken: 'mock-refresh-token',
  user: {
    id: 'test-user-123',
    email: 'test@example.com',
    role: 'user',
  },
}

/**
 * Mock admin authentication state for testing
 */
export const mockAdminAuthState: AuthState = {
  accessToken: 'mock-admin-access-token',
  refreshToken: 'mock-admin-refresh-token',
  user: {
    id: 'admin-user-123',
    email: 'admin@example.com',
    role: 'admin',
  },
}

/**
 * Helper to set authentication cookies
 */
export async function setAuthCookies(page: Page, authState: AuthState) {
  await page.context().addCookies([
    {
      name: 'sb-access-token',
      value: authState.accessToken,
      domain: 'localhost',
      path: '/',
      httpOnly: true,
      secure: false,
      sameSite: 'Lax',
    },
    {
      name: 'sb-refresh-token',
      value: authState.refreshToken,
      domain: 'localhost',
      path: '/',
      httpOnly: true,
      secure: false,
      sameSite: 'Lax',
    },
  ])
}

/**
 * Helper to clear authentication
 */
export async function clearAuth(page: Page) {
  await page.context().clearCookies()
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
}
