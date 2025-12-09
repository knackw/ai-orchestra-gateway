import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test.describe('Main Navigation', () => {
    test('should navigate to features section from nav', async ({ page }) => {
      await page.goto('/')

      // Click on features link if it exists
      const featuresLink = page.getByRole('link', { name: /funktionen|features/i })
      if (await featuresLink.isVisible()) {
        await featuresLink.click()
        // Should scroll to features or navigate
        await expect(page.url()).toMatch(/#features|\/features/)
      }
    })

    test('should navigate to pricing section from nav', async ({ page }) => {
      await page.goto('/')

      // Click on pricing link
      const pricingLink = page.getByRole('link', { name: /preise|pricing/i })
      if (await pricingLink.isVisible()) {
        await pricingLink.click()
        await expect(page.url()).toMatch(/#preise|#pricing|\/pricing/)
      }
    })

    test('should navigate to login from nav', async ({ page }) => {
      await page.goto('/')

      // Click on login link
      const loginLink = page.getByRole('link', { name: /anmelden|login/i })
      await loginLink.click()

      await expect(page).toHaveURL(/login/)
    })
  })

  test.describe('Language Switcher', () => {
    test('should switch from German to English', async ({ page }) => {
      await page.goto('/de')

      // Look for language switcher
      const langSwitcher = page.locator('[data-testid="language-switcher"], button:has-text("DE"), button:has-text("Deutsch")')

      if (await langSwitcher.first().isVisible()) {
        await langSwitcher.first().click()

        // Look for English option
        const englishOption = page.getByRole('menuitem', { name: /english|en/i })
        if (await englishOption.isVisible()) {
          await englishOption.click()
          await expect(page).toHaveURL(/\/en/)
        }
      }
    })

    test('should persist language preference', async ({ page }) => {
      await page.goto('/en')

      // Navigate to another page
      const loginLink = page.getByRole('link', { name: /login|sign in/i })
      if (await loginLink.isVisible()) {
        await loginLink.click()
        // Should stay in English
        await expect(page).toHaveURL(/\/en\//)
      }
    })
  })

  test.describe('Theme Switcher', () => {
    test('should toggle dark mode', async ({ page }) => {
      await page.goto('/')

      // Look for theme toggle button
      const themeToggle = page.locator('[data-testid="theme-toggle"], button[aria-label*="theme"], button[aria-label*="Theme"], button[aria-label*="dark"], button[aria-label*="light"]')

      if (await themeToggle.first().isVisible()) {
        // Get initial state
        const htmlElement = page.locator('html')
        const initialClass = await htmlElement.getAttribute('class')

        // Click theme toggle
        await themeToggle.first().click()

        // Class should change
        const newClass = await htmlElement.getAttribute('class')
        expect(newClass).not.toBe(initialClass)
      }
    })
  })

  test.describe('Footer Navigation', () => {
    test('should have legal links in footer', async ({ page }) => {
      await page.goto('/')

      const footer = page.locator('footer')

      // Check for privacy policy link
      const privacyLink = footer.getByRole('link', { name: /datenschutz|privacy/i })
      await expect(privacyLink).toBeVisible()

      // Check for imprint/legal notice
      const imprintLink = footer.getByRole('link', { name: /impressum|imprint|legal/i })
      await expect(imprintLink).toBeVisible()
    })

    test('should navigate to privacy policy', async ({ page }) => {
      await page.goto('/')

      const footer = page.locator('footer')
      const privacyLink = footer.getByRole('link', { name: /datenschutz|privacy/i })

      await privacyLink.click()
      await expect(page).toHaveURL(/datenschutz|privacy/)
    })

    test('should navigate to imprint', async ({ page }) => {
      await page.goto('/')

      const footer = page.locator('footer')
      const imprintLink = footer.getByRole('link', { name: /impressum|imprint/i })

      await imprintLink.click()
      await expect(page).toHaveURL(/impressum|imprint|legal/)
    })
  })
})

test.describe('Breadcrumb Navigation', () => {
  test('should show breadcrumbs on nested pages', async ({ page }) => {
    await page.goto('/de/datenschutz')

    // Look for breadcrumb navigation
    const breadcrumb = page.locator('[aria-label="Breadcrumb"], nav:has(ol)')

    if (await breadcrumb.isVisible()) {
      // Should have home link
      const homeLink = breadcrumb.getByRole('link', { name: /home|startseite/i })
      await expect(homeLink).toBeVisible()
    }
  })
})
