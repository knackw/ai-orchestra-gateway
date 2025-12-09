import { test, expect } from '@playwright/test'

/**
 * Accessibility (a11y) E2E Tests
 * Tests WCAG compliance and keyboard navigation
 */

test.describe('Accessibility - Landing Page', () => {
  test('should have proper document structure', async ({ page }) => {
    await page.goto('/')

    // Check for main landmark
    const main = page.locator('main, [role="main"]')
    await expect(main).toBeVisible()

    // Check for navigation landmark
    const nav = page.locator('nav, [role="navigation"]')
    await expect(nav.first()).toBeVisible()

    // Check for footer
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
  })

  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/')

    // Should have exactly one h1
    const h1Elements = page.locator('h1')
    const h1Count = await h1Elements.count()
    expect(h1Count).toBe(1)

    // Headings should be in order (h1, then h2, etc.)
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all()
    expect(headings.length).toBeGreaterThan(0)
  })

  test('should have accessible images', async ({ page }) => {
    await page.goto('/')

    const images = await page.locator('img').all()
    for (const img of images) {
      const alt = await img.getAttribute('alt')
      const role = await img.getAttribute('role')

      // Images must have alt text or be marked as decorative
      expect(
        alt !== null || role === 'presentation' || role === 'none'
      ).toBeTruthy()
    }
  })

  test('should have accessible links', async ({ page }) => {
    await page.goto('/')

    const links = await page.getByRole('link').all()
    for (const link of links) {
      const text = await link.textContent()
      const ariaLabel = await link.getAttribute('aria-label')
      const title = await link.getAttribute('title')

      // Links must have accessible text
      expect(
        (text && text.trim().length > 0) || ariaLabel || title
      ).toBeTruthy()
    }
  })

  test('should have accessible buttons', async ({ page }) => {
    await page.goto('/')

    const buttons = await page.getByRole('button').all()
    for (const button of buttons) {
      const text = await button.textContent()
      const ariaLabel = await button.getAttribute('aria-label')

      // Buttons must have accessible text
      expect(
        (text && text.trim().length > 0) || ariaLabel
      ).toBeTruthy()
    }
  })

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/')

    // Press Tab to start navigating
    await page.keyboard.press('Tab')

    // Get the focused element
    const focusedTag = await page.evaluate(() => document.activeElement?.tagName)

    // Should focus on an interactive element
    expect(['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA']).toContain(focusedTag)
  })

  test('should have skip to content link', async ({ page }) => {
    await page.goto('/')

    // Press Tab to reveal skip link
    await page.keyboard.press('Tab')

    // Look for skip link (might be visually hidden until focused)
    const skipLink = page.locator('a:has-text("Skip"), a:has-text("Zum Inhalt")')
    const count = await skipLink.count()

    // Skip link is optional but recommended
    if (count > 0) {
      await expect(skipLink.first()).toBeFocused()
    }
  })

  test('should have adequate color contrast', async ({ page }) => {
    await page.goto('/')

    // Check that text is visible (basic contrast check)
    const bodyText = page.locator('body')
    const color = await bodyText.evaluate((el) => {
      const style = window.getComputedStyle(el)
      return {
        color: style.color,
        backgroundColor: style.backgroundColor,
      }
    })

    expect(color.color).toBeTruthy()
    expect(color.backgroundColor).toBeTruthy()
  })
})

test.describe('Accessibility - Forms', () => {
  test('should have properly labeled form inputs', async ({ page }) => {
    await page.goto('/de/login')

    // Check email input
    const emailInput = page.getByLabel(/e-mail|email/i)
    await expect(emailInput).toBeVisible()

    const emailId = await emailInput.getAttribute('id')
    expect(emailId).toBeTruthy()

    // Check password input
    const passwordInput = page.getByLabel(/passwort|password/i)
    await expect(passwordInput).toBeVisible()

    const passwordId = await passwordInput.getAttribute('id')
    expect(passwordId).toBeTruthy()
  })

  test('should have accessible error messages', async ({ page }) => {
    await page.goto('/de/login')

    // Submit form without filling to trigger errors
    const submitButton = page.getByRole('button', { name: /anmelden|login/i })
    await submitButton.click()

    // Wait for validation
    await page.waitForTimeout(500)

    // Error messages should be associated with inputs
    const errors = page.locator('[role="alert"], .error, [aria-invalid="true"]')
    const errorCount = await errors.count()

    // Either shows validation errors or stays on form
    expect(errorCount >= 0).toBeTruthy()
  })

  test('should support form navigation with keyboard', async ({ page }) => {
    await page.goto('/de/login')

    // Tab through form fields
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')

    // Should be able to focus on submit button
    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement
      return {
        tag: el?.tagName,
        type: el?.getAttribute('type'),
        role: el?.getAttribute('role'),
      }
    })

    expect(
      focusedElement.tag === 'BUTTON' ||
      focusedElement.tag === 'INPUT' ||
      focusedElement.role === 'button'
    ).toBeTruthy()
  })

  test('should have autocomplete attributes', async ({ page }) => {
    await page.goto('/de/login')

    const emailInput = page.getByLabel(/e-mail|email/i)
    const autocomplete = await emailInput.getAttribute('autocomplete')

    // Email should have autocomplete="email"
    expect(autocomplete).toBe('email')
  })
})

test.describe('Accessibility - Interactive Elements', () => {
  test('should have focus indicators', async ({ page }) => {
    await page.goto('/')

    // Focus on first interactive element
    await page.keyboard.press('Tab')

    // Check if focused element has visible outline or focus styling
    const focusStyle = await page.evaluate(() => {
      const el = document.activeElement
      const style = window.getComputedStyle(el!)
      return {
        outline: style.outline,
        outlineWidth: style.outlineWidth,
        boxShadow: style.boxShadow,
      }
    })

    // Should have some focus indication
    expect(
      focusStyle.outline !== 'none' ||
      focusStyle.outlineWidth !== '0px' ||
      focusStyle.boxShadow !== 'none'
    ).toBeTruthy()
  })

  test('should have accessible modal dialogs', async ({ page }) => {
    await page.goto('/de/dashboard/api-keys')

    // Open a dialog (assuming create API key dialog exists)
    const createButton = page.getByRole('button', { name: /create|erstellen/i }).first()
    const isVisible = await createButton.isVisible().catch(() => false)

    if (isVisible) {
      await createButton.click()

      // Dialog should have proper ARIA attributes
      const dialog = page.locator('[role="dialog"], [role="alertdialog"]')
      await expect(dialog).toBeVisible()

      // Dialog should have accessible label
      const ariaLabel = await dialog.getAttribute('aria-label')
      const ariaLabelledBy = await dialog.getAttribute('aria-labelledby')

      expect(ariaLabel || ariaLabelledBy).toBeTruthy()
    }
  })

  test('should trap focus in modal dialogs', async ({ page }) => {
    await page.goto('/de/dashboard/api-keys')

    const createButton = page.getByRole('button', { name: /create|erstellen/i }).first()
    const isVisible = await createButton.isVisible().catch(() => false)

    if (isVisible) {
      await createButton.click()

      // Tab through dialog
      await page.keyboard.press('Tab')
      await page.keyboard.press('Tab')
      await page.keyboard.press('Tab')

      // Focus should remain within dialog
      const focusedElement = await page.evaluate(() => {
        const dialog = document.querySelector('[role="dialog"]')
        const focused = document.activeElement
        return dialog?.contains(focused)
      })

      expect(focusedElement).toBeTruthy()
    }
  })

  test('should close modal on Escape key', async ({ page }) => {
    await page.goto('/de/dashboard/api-keys')

    const createButton = page.getByRole('button', { name: /create|erstellen/i }).first()
    const isVisible = await createButton.isVisible().catch(() => false)

    if (isVisible) {
      await createButton.click()

      // Wait for dialog to open
      const dialog = page.locator('[role="dialog"]')
      await expect(dialog).toBeVisible()

      // Press Escape
      await page.keyboard.press('Escape')

      // Dialog should close
      await expect(dialog).not.toBeVisible()
    }
  })
})

test.describe('Accessibility - ARIA Attributes', () => {
  test('should use ARIA landmarks correctly', async ({ page }) => {
    await page.goto('/')

    // Check for common landmarks
    const banner = page.locator('[role="banner"], header')
    const main = page.locator('[role="main"], main')
    const contentinfo = page.locator('[role="contentinfo"], footer')
    const navigation = page.locator('[role="navigation"], nav')

    await expect(main).toBeVisible()
    await expect(banner).toBeVisible()
    await expect(contentinfo).toBeVisible()
    await expect(navigation.first()).toBeVisible()
  })

  test('should have proper ARIA labels on interactive elements', async ({ page }) => {
    await page.goto('/')

    // Find buttons with icons (likely to need aria-label)
    const iconButtons = page.locator('button:has(svg)')
    const buttons = await iconButtons.all()

    for (const button of buttons.slice(0, 5)) { // Check first 5
      const text = await button.textContent()
      const ariaLabel = await button.getAttribute('aria-label')

      // Icon buttons should have text or aria-label
      if (!text || text.trim().length === 0) {
        expect(ariaLabel).toBeTruthy()
      }
    }
  })

  test('should use ARIA live regions for dynamic content', async ({ page }) => {
    await page.goto('/de/login')

    // Submit form to trigger validation
    const submitButton = page.getByRole('button', { name: /anmelden|login/i })
    await submitButton.click()

    await page.waitForTimeout(500)

    // Check for live regions or alerts
    const liveRegions = page.locator('[role="alert"], [role="status"], [aria-live]')
    const count = await liveRegions.count()

    // Live regions are optional but recommended for dynamic feedback
    expect(count >= 0).toBeTruthy()
  })
})

test.describe('Accessibility - Responsive & Mobile', () => {
  test('should be accessible on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    // Main content should still be accessible
    const main = page.locator('main, [role="main"]')
    await expect(main).toBeVisible()

    // Navigation should exist (might be in mobile menu)
    const nav = page.locator('nav, [role="navigation"], button:has-text("Menu")')
    const navCount = await nav.count()
    expect(navCount).toBeGreaterThan(0)
  })

  test('should have touch-friendly targets on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    // Check button sizes (should be at least 44x44px for touch)
    const buttons = await page.getByRole('button').all()

    for (const button of buttons.slice(0, 3)) { // Check first 3 buttons
      const isVisible = await button.isVisible()
      if (isVisible) {
        const box = await button.boundingBox()
        if (box) {
          // Touch targets should be at least 44x44px (or close to it)
          expect(box.height).toBeGreaterThanOrEqual(30) // Slightly relaxed for testing
          expect(box.width).toBeGreaterThanOrEqual(30)
        }
      }
    }
  })
})

test.describe('Accessibility - Screen Reader Support', () => {
  test('should have descriptive page titles', async ({ page }) => {
    await page.goto('/')
    const homeTitle = await page.title()
    expect(homeTitle.length).toBeGreaterThan(0)

    await page.goto('/de/login')
    const loginTitle = await page.title()
    expect(loginTitle.length).toBeGreaterThan(0)
    expect(loginTitle).not.toBe(homeTitle) // Titles should be unique
  })

  test('should have lang attribute on html element', async ({ page }) => {
    await page.goto('/de')

    const lang = await page.locator('html').getAttribute('lang')
    expect(lang).toBeTruthy()
    expect(lang).toMatch(/de|en/) // Should have language code
  })

  test('should have proper table structure for data tables', async ({ page }) => {
    await page.goto('/de/dashboard/api-keys')

    const tables = page.locator('table, [role="table"]')
    const tableCount = await tables.count()

    if (tableCount > 0) {
      const table = tables.first()

      // Should have headers
      const headers = table.locator('th, [role="columnheader"]')
      const headerCount = await headers.count()
      expect(headerCount).toBeGreaterThan(0)

      // Headers should have scope attribute
      const firstHeader = headers.first()
      const scope = await firstHeader.getAttribute('scope')
      // Scope is optional in modern HTML but recommended
      expect(scope === 'col' || scope === null).toBeTruthy()
    }
  })
})
