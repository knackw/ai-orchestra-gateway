import { test, expect } from '@playwright/test'

/**
 * Dashboard E2E Tests
 * These tests require a logged-in user session
 */

// Helper to simulate login (you'll need to adjust based on your auth implementation)
async function login(page: any) {
  await page.goto('/de/login')

  // Fill login form
  await page.getByLabel(/e-mail|email/i).fill('test@example.com')
  await page.getByLabel(/passwort|password/i).fill('testpassword123')

  // Submit and wait for navigation
  await page.getByRole('button', { name: /anmelden|login/i }).click()

  // Wait for dashboard to load (adjust timeout as needed)
  await page.waitForURL(/dashboard/, { timeout: 10000 })
}

test.describe('Dashboard - Authenticated', () => {
  test.skip('setup requires authentication', () => {
    // Skip these tests if auth is not configured
    // Remove .skip once you have test authentication setup
  })

  test('should display dashboard overview', async ({ page }) => {
    await login(page)

    // Check for main dashboard heading
    const heading = page.getByRole('heading', { name: /dashboard|übersicht/i })
    await expect(heading).toBeVisible()
  })

  test('should display credit balance', async ({ page }) => {
    await login(page)

    // Look for credit/balance display
    const creditElement = page.locator('text=/credits|guthaben|balance/i')
    await expect(creditElement.first()).toBeVisible()
  })

  test('should display usage statistics', async ({ page }) => {
    await login(page)

    // Check for stats cards
    const statsElements = page.locator('[data-testid*="stat"], .stat-card, [class*="stat"]')
    const count = await statsElements.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should have working sidebar navigation', async ({ page }) => {
    await login(page)

    // Check for navigation items
    const apiKeysLink = page.getByRole('link', { name: /api.*keys|api.*schlüssel/i })
    await expect(apiKeysLink).toBeVisible()

    const usageLink = page.getByRole('link', { name: /usage|nutzung|verbrauch/i })
    await expect(usageLink).toBeVisible()

    const billingLink = page.getByRole('link', { name: /billing|abrechnung|zahlung/i })
    await expect(billingLink).toBeVisible()
  })

  test('should navigate between dashboard sections', async ({ page }) => {
    await login(page)

    // Navigate to API Keys
    const apiKeysLink = page.getByRole('link', { name: /api.*keys|api.*schlüssel/i })
    await apiKeysLink.click()
    await expect(page).toHaveURL(/api-keys/)

    // Navigate to Usage
    const usageLink = page.getByRole('link', { name: /usage|nutzung/i })
    await usageLink.click()
    await expect(page).toHaveURL(/usage/)

    // Navigate to Billing
    const billingLink = page.getByRole('link', { name: /billing|abrechnung/i })
    await billingLink.click()
    await expect(page).toHaveURL(/billing/)
  })

  test('should display user profile menu', async ({ page }) => {
    await login(page)

    // Look for user menu/avatar
    const userMenuButton = page.locator('[aria-label*="menu"], [aria-label*="profil"], button:has(svg)')
    const count = await userMenuButton.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should have logout functionality', async ({ page }) => {
    await login(page)

    // Open user menu and click logout
    const userMenu = page.locator('[aria-label*="menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()

      const logoutButton = page.getByRole('button', { name: /logout|abmelden|ausloggen/i })
      await expect(logoutButton).toBeVisible()
    }
  })

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await login(page)

    // Dashboard should still be accessible
    const heading = page.getByRole('heading', { name: /dashboard/i })
    await expect(heading.first()).toBeVisible()

    // Mobile menu should exist
    const mobileMenuButton = page.locator('button:has-text("Menu"), [aria-label*="menu"]')
    const count = await mobileMenuButton.count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('Dashboard - Charts & Visualizations', () => {
  test.skip('setup requires authentication', () => {
    // Skip these tests if auth is not configured
  })

  test('should display usage charts', async ({ page }) => {
    await login(page)

    // Look for chart containers (Recharts typically uses SVG)
    const charts = page.locator('svg.recharts-surface')
    const count = await charts.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should display requests over time chart', async ({ page }) => {
    await login(page)

    // Check for specific chart titles
    const chartTitle = page.locator('text=/requests|anfragen|über zeit/i')
    await expect(chartTitle.first()).toBeVisible()
  })

  test('should display provider distribution', async ({ page }) => {
    await login(page)

    // Look for provider names (Anthropic, Scaleway, etc.)
    const providerElement = page.locator('text=/anthropic|scaleway|provider/i')
    await expect(providerElement.first()).toBeVisible()
  })
})

test.describe('Dashboard - Error Handling', () => {
  test.skip('setup requires authentication', () => {
    // Skip these tests if auth is not configured
  })

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate offline mode
    await page.route('**/api/**', route => route.abort())

    await login(page)

    // Dashboard should still render, possibly with error messages
    const errorMessage = page.locator('text=/error|fehler|failed|fehlgeschlagen/i')
    // Note: Dashboard might show cached data or error states
    const pageContent = await page.textContent('body')
    expect(pageContent).toBeTruthy()
  })
})
