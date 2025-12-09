import { test, expect } from '@playwright/test'
import { waitForPageReady, checkAccessibility, hoverElement } from './utils/helpers'

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display the hero section', async ({ page }) => {
    // Check for main headline
    const headline = page.getByRole('heading', { level: 1 })
    await expect(headline).toBeVisible()
  })

  test('should have navigation links', async ({ page }) => {
    // Check for navigation
    const nav = page.getByRole('navigation')
    await expect(nav).toBeVisible()
  })

  test('should have a CTA button', async ({ page }) => {
    // Look for primary call-to-action
    const ctaButton = page.getByRole('link', { name: /starten|start|demo|anmelden/i })
    await expect(ctaButton.first()).toBeVisible()
  })

  test('should display features section', async ({ page }) => {
    // Check for features/benefits section
    const featuresHeading = page.getByRole('heading', { name: /funktionen|features|vorteile/i })
    await expect(featuresHeading.first()).toBeVisible()
  })

  test('should display pricing section', async ({ page }) => {
    // Check for pricing section
    const pricingHeading = page.getByRole('heading', { name: /preise|pricing|tarife/i })
    await expect(pricingHeading.first()).toBeVisible()
  })

  test('should have footer with links', async ({ page }) => {
    // Check for footer
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
  })

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    // Hero should still be visible
    const headline = page.getByRole('heading', { level: 1 })
    await expect(headline).toBeVisible()
  })

  test('should have proper page title', async ({ page }) => {
    await expect(page).toHaveTitle(/AI Orchestra|AI Legal Ops/i)
  })
})

test.describe('Landing Page Accessibility', () => {
  test('should have no accessibility violations on main elements', async ({ page }) => {
    await page.goto('/')

    // Check that images have alt text
    const images = await page.locator('img').all()
    for (const img of images) {
      const alt = await img.getAttribute('alt')
      const role = await img.getAttribute('role')
      // Images should have alt text or be decorative (role="presentation")
      expect(alt !== null || role === 'presentation').toBeTruthy()
    }

    // Check that buttons are focusable
    const buttons = await page.getByRole('button').all()
    for (const button of buttons) {
      await expect(button).toBeEnabled()
    }

    // Check that links have accessible names
    const links = await page.getByRole('link').all()
    for (const link of links) {
      const name = await link.textContent()
      const ariaLabel = await link.getAttribute('aria-label')
      expect(name || ariaLabel).toBeTruthy()
    }
  })

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/')

    // Tab through the page
    await page.keyboard.press('Tab')

    // Should be able to focus on interactive elements
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName)
    expect(['A', 'BUTTON', 'INPUT']).toContain(focusedElement)
  })
})
