import { Page, expect } from '@playwright/test'

/**
 * E2E Test Helper Functions
 */

/**
 * Login helper - performs user login
 */
export async function login(
  page: Page,
  email: string = process.env.TEST_USER_EMAIL || 'test@example.com',
  password: string = process.env.TEST_USER_PASSWORD || 'Test123!@#$%'
) {
  await page.goto('/login')
  await page.fill('input[name="email"]', email)
  await page.fill('input[name="password"]', password)
  await page.click('button[type="submit"]')
  await page.waitForURL(/\/(dashboard|admin)/, { timeout: 10000 })
}

/**
 * Logout helper - performs user logout
 */
export async function logout(page: Page) {
  // Look for logout button (might be in a dropdown menu)
  const logoutButton = page.locator('button:has-text("Abmelden"), button:has-text("Logout"), a:has-text("Abmelden")')
  await logoutButton.click()
  await page.waitForURL('/login', { timeout: 10000 })
}

/**
 * Wait for element to be visible and return it
 */
export async function waitForElement(page: Page, selector: string, timeout: number = 5000) {
  const element = page.locator(selector)
  await element.waitFor({ state: 'visible', timeout })
  return element
}

/**
 * Fill form field and wait for validation
 */
export async function fillFormField(
  page: Page,
  fieldName: string,
  value: string,
  waitForValidation: boolean = true
) {
  const field = page.locator(`input[name="${fieldName}"], textarea[name="${fieldName}"]`)
  await field.fill(value)

  if (waitForValidation) {
    // Wait a bit for validation to trigger
    await page.waitForTimeout(300)
  }
}

/**
 * Check if element has error state
 */
export async function hasError(page: Page, fieldName: string): Promise<boolean> {
  const errorMessage = page.locator(`text=/fehler|error|ungültig|invalid/i`).first()
  return errorMessage.isVisible()
}

/**
 * Take screenshot with timestamp
 */
export async function takeTimestampedScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  await page.screenshot({ path: `screenshots/${name}-${timestamp}.png`, fullPage: true })
}

/**
 * Mock API response
 */
export async function mockApiResponse(
  page: Page,
  url: string | RegExp,
  response: any,
  status: number = 200
) {
  await page.route(url, async (route) => {
    await route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(response),
    })
  })
}

/**
 * Wait for API call to complete
 */
export async function waitForApiCall(page: Page, urlPattern: string | RegExp) {
  return page.waitForResponse((response) => {
    const url = response.url()
    if (typeof urlPattern === 'string') {
      return url.includes(urlPattern)
    }
    return urlPattern.test(url)
  })
}

/**
 * Check accessibility violations using basic checks
 */
export async function checkAccessibility(page: Page) {
  // Check for basic accessibility issues
  const checks = [
    // Check for images without alt text
    async () => {
      const images = await page.locator('img:not([alt])').count()
      expect(images).toBe(0)
    },
    // Check for inputs without labels
    async () => {
      const inputsWithoutLabels = await page.evaluate(() => {
        const inputs = document.querySelectorAll('input:not([type="hidden"])')
        let count = 0
        inputs.forEach((input) => {
          const id = input.getAttribute('id')
          const ariaLabel = input.getAttribute('aria-label')
          const ariaLabelledBy = input.getAttribute('aria-labelledby')
          if (!id && !ariaLabel && !ariaLabelledBy) {
            const label = input.closest('label')
            if (!label) count++
          }
        })
        return count
      })
      expect(inputsWithoutLabels).toBe(0)
    },
    // Check for proper heading hierarchy
    async () => {
      const headingStructure = await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
        return headings.map((h) => parseInt(h.tagName[1]))
      })

      // Should have at least one h1
      expect(headingStructure.filter((level) => level === 1).length).toBeGreaterThan(0)
    },
  ]

  for (const check of checks) {
    await check()
  }
}

/**
 * Test keyboard navigation
 */
export async function testKeyboardNavigation(page: Page, elements: string[]) {
  for (const selector of elements) {
    await page.keyboard.press('Tab')
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  }
}

/**
 * Wait for loading to complete
 */
export async function waitForLoadingComplete(page: Page, timeout: number = 10000) {
  // Wait for common loading indicators to disappear
  const loadingSelectors = [
    '[data-testid="loading"]',
    '.loading',
    '.spinner',
    '[aria-busy="true"]',
  ]

  for (const selector of loadingSelectors) {
    const loader = page.locator(selector)
    if (await loader.isVisible()) {
      await loader.waitFor({ state: 'hidden', timeout })
    }
  }
}

/**
 * Get table row count
 */
export async function getTableRowCount(page: Page, tableSelector: string = 'table'): Promise<number> {
  return page.locator(`${tableSelector} tbody tr`).count()
}

/**
 * Click on table row by index
 */
export async function clickTableRow(page: Page, index: number, tableSelector: string = 'table') {
  const row = page.locator(`${tableSelector} tbody tr`).nth(index)
  await row.click()
}

/**
 * Verify toast/notification message
 */
export async function verifyToast(page: Page, message: string | RegExp, timeout: number = 5000) {
  const toast = page.locator('[role="alert"], [role="status"], .toast, [data-testid="toast"]')
  await toast.waitFor({ state: 'visible', timeout })

  if (typeof message === 'string') {
    await expect(toast).toContainText(message)
  } else {
    const text = await toast.textContent()
    expect(text).toMatch(message)
  }
}

/**
 * Dismiss toast/notification
 */
export async function dismissToast(page: Page) {
  const dismissButton = page.locator('[role="alert"] button, .toast button, [data-testid="toast"] button').first()
  if (await dismissButton.isVisible()) {
    await dismissButton.click()
  }
}

/**
 * Wait for page to be ready (no pending requests)
 */
export async function waitForPageReady(page: Page) {
  await page.waitForLoadState('networkidle')
  await page.waitForLoadState('domcontentloaded')
}

/**
 * Get element text content
 */
export async function getTextContent(page: Page, selector: string): Promise<string> {
  const element = page.locator(selector)
  return (await element.textContent()) || ''
}

/**
 * Check if element is disabled
 */
export async function isDisabled(page: Page, selector: string): Promise<boolean> {
  const element = page.locator(selector)
  return element.isDisabled()
}

/**
 * Select dropdown option
 */
export async function selectOption(page: Page, selector: string, value: string) {
  await page.selectOption(selector, value)
  await page.waitForTimeout(200) // Wait for any change handlers
}

/**
 * Upload file
 */
export async function uploadFile(page: Page, selector: string, filePath: string) {
  const fileInput = page.locator(selector)
  await fileInput.setInputFiles(filePath)
  await page.waitForTimeout(500) // Wait for upload to process
}

/**
 * Clear input field
 */
export async function clearInput(page: Page, selector: string) {
  const input = page.locator(selector)
  await input.fill('')
}

/**
 * Hover over element
 */
export async function hoverElement(page: Page, selector: string) {
  const element = page.locator(selector)
  await element.hover()
  await page.waitForTimeout(300) // Wait for hover effects
}
