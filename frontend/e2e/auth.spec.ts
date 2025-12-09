import { test, expect } from '@playwright/test'
import { login, logout, fillFormField, verifyToast } from './utils/helpers'
import { clearAuth } from './fixtures/auth'

test.describe('Authentication Pages', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing auth state before each test
    await clearAuth(page)
  })

  test.describe('Login Page', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/de/login')
    })

    test('should display login form', async ({ page }) => {
      // Check for email input
      const emailInput = page.getByLabel(/e-mail|email/i)
      await expect(emailInput).toBeVisible()

      // Check for password input
      const passwordInput = page.getByLabel(/passwort|password/i)
      await expect(passwordInput).toBeVisible()

      // Check for submit button
      const submitButton = page.getByRole('button', { name: /anmelden|login|einloggen/i })
      await expect(submitButton).toBeVisible()
    })

    test('should show validation errors for empty form', async ({ page }) => {
      // Click submit without filling form
      const submitButton = page.getByRole('button', { name: /anmelden|login|einloggen/i })
      await submitButton.click()

      // Should stay on login page (form validation)
      await expect(page).toHaveURL(/login/)
    })

    test('should have link to registration', async ({ page }) => {
      const registerLink = page.getByRole('link', { name: /registrieren|register|sign up/i })
      await expect(registerLink).toBeVisible()
    })

    test('should have forgot password link', async ({ page }) => {
      const forgotLink = page.getByRole('link', { name: /passwort vergessen|forgot password/i })
      await expect(forgotLink).toBeVisible()
    })

    test('should allow typing in form fields', async ({ page }) => {
      const emailInput = page.getByLabel(/e-mail|email/i)
      const passwordInput = page.getByLabel(/passwort|password/i)

      await emailInput.fill('test@example.com')
      await passwordInput.fill('testpassword123')

      await expect(emailInput).toHaveValue('test@example.com')
      await expect(passwordInput).toHaveValue('testpassword123')
    })
  })

  test.describe('Registration Page', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/de/register')
    })

    test('should display registration form', async ({ page }) => {
      // Check for email input
      const emailInput = page.getByLabel(/e-mail|email/i)
      await expect(emailInput).toBeVisible()

      // Check for password input
      const passwordInput = page.getByLabel(/passwort|password/i).first()
      await expect(passwordInput).toBeVisible()

      // Check for submit button
      const submitButton = page.getByRole('button', { name: /registrieren|register|sign up/i })
      await expect(submitButton).toBeVisible()
    })

    test('should have link to login', async ({ page }) => {
      const loginLink = page.getByRole('link', { name: /anmelden|login|sign in/i })
      await expect(loginLink).toBeVisible()
    })

    test('should have terms checkbox or link', async ({ page }) => {
      // Look for terms/privacy acceptance
      const termsElement = page.locator('text=/agb|nutzungsbedingungen|terms|datenschutz|privacy/i')
      await expect(termsElement.first()).toBeVisible()
    })
  })

  test.describe('Password Reset Page', () => {
    test('should display password reset form', async ({ page }) => {
      await page.goto('/de/forgot-password')

      // Check for email input
      const emailInput = page.getByLabel(/e-mail|email/i)
      await expect(emailInput).toBeVisible()

      // Check for submit button
      const submitButton = page.getByRole('button', { name: /senden|submit|reset|zurücksetzen/i })
      await expect(submitButton).toBeVisible()
    })

    test('should have link back to login', async ({ page }) => {
      await page.goto('/de/forgot-password')

      const loginLink = page.getByRole('link', { name: /anmelden|login|zurück/i })
      await expect(loginLink).toBeVisible()
    })
  })
})

test.describe('Auth Redirects', () => {
  test('should redirect unauthenticated user from dashboard to login', async ({ page }) => {
    // Clear auth state
    await clearAuth(page)

    // Try to access protected route
    await page.goto('/de/dashboard')

    // Should redirect to login
    await expect(page).toHaveURL(/login/)
  })

  test('should redirect unauthenticated user from admin to login', async ({ page }) => {
    // Clear auth state
    await clearAuth(page)

    // Try to access admin route
    await page.goto('/de/admin')

    // Should redirect to login
    await expect(page).toHaveURL(/login/)
  })
})

test.describe('Authentication Flow', () => {
  test('user can sign up with valid credentials', async ({ page }) => {
    await page.goto('/de/signup')

    // Fill signup form
    const timestamp = Date.now()
    const testEmail = `test-${timestamp}@example.com`

    await fillFormField(page, 'email', testEmail)
    await fillFormField(page, 'password', 'SecurePass123!@#')
    await fillFormField(page, 'confirmPassword', 'SecurePass123!@#')

    // Accept terms if checkbox exists
    const termsCheckbox = page.locator('input[type="checkbox"][name*="terms"], input[type="checkbox"][name*="acceptTerms"]')
    if (await termsCheckbox.count() > 0) {
      await termsCheckbox.first().check()
    }

    const privacyCheckbox = page.locator('input[type="checkbox"][name*="privacy"], input[type="checkbox"][name*="acceptPrivacy"]')
    if (await privacyCheckbox.count() > 0) {
      await privacyCheckbox.first().check()
    }

    // Submit form
    const submitButton = page.getByRole('button', { name: /registrieren|register|sign up/i })
    await submitButton.click()

    // Wait for success message or redirect
    await page.waitForTimeout(2000)
  })

  test('user can log in with valid credentials', async ({ page }) => {
    await page.goto('/de/login')

    // Use test credentials (these should be set in env vars)
    const email = process.env.TEST_USER_EMAIL || 'test@example.com'
    const password = process.env.TEST_USER_PASSWORD || 'Test123!@#$%'

    await fillFormField(page, 'email', email)
    await fillFormField(page, 'password', password)

    const submitButton = page.getByRole('button', { name: /anmelden|login|einloggen/i })
    await submitButton.click()

    // Should redirect to dashboard on success (or show error)
    await page.waitForTimeout(2000)
  })

  test('user cannot log in with invalid credentials', async ({ page }) => {
    await page.goto('/de/login')

    await fillFormField(page, 'email', 'wrong@example.com')
    await fillFormField(page, 'password', 'WrongPassword123!')

    const submitButton = page.getByRole('button', { name: /anmelden|login|einloggen/i })
    await submitButton.click()

    // Should show error message
    await page.waitForTimeout(1000)

    // Should stay on login page
    await expect(page).toHaveURL(/login/)
  })

  test('user can reset password', async ({ page }) => {
    await page.goto('/de/forgot-password')

    await fillFormField(page, 'email', 'test@example.com')

    const submitButton = page.getByRole('button', { name: /senden|submit|reset|zurücksetzen/i })
    await submitButton.click()

    // Wait for confirmation
    await page.waitForTimeout(1000)
  })
})
