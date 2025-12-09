# Testing Documentation - AI Legal Ops Frontend

Comprehensive testing setup for the AI Legal Ops Gateway Frontend.

## Table of Contents

1. [Overview](#overview)
2. [Test Stack](#test-stack)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Component Tests](#component-tests)
6. [E2E Tests](#e2e-tests)
7. [Writing Tests](#writing-tests)
8. [Best Practices](#best-practices)
9. [CI/CD Integration](#cicd-integration)

---

## Overview

This project uses a modern testing stack with:

- **Vitest** for unit and component tests
- **React Testing Library** for component testing
- **Playwright** for E2E tests
- **MSW (Mock Service Worker)** for API mocking

### Test Coverage Goals

- **Unit Tests**: 80%+ coverage on utilities and services
- **Component Tests**: All UI components and features
- **E2E Tests**: Critical user flows
- **Accessibility Tests**: WCAG 2.1 AA compliance

---

## Test Stack

### Vitest

Fast unit test framework with native ESM support and TypeScript.

```typescript
// vitest.config.ts
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],
  },
})
```

### React Testing Library

Testing library focused on user behavior rather than implementation details.

```typescript
import { render, screen } from '@/tests/utils'
import userEvent from '@testing-library/user-event'
```

### Playwright

E2E testing across multiple browsers with excellent debugging tools.

```typescript
import { test, expect } from '@playwright/test'
```

### MSW (Mock Service Worker)

API mocking for both development and testing.

```typescript
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
```

---

## Running Tests

### Unit & Component Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

### E2E Tests

```bash
# Run E2E tests (headless)
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run E2E tests in headed mode
npm run test:e2e:headed

# Run specific test file
npx playwright test e2e/landing-page.spec.ts

# Debug E2E tests
npx playwright test --debug
```

### Test Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui",
    "e2e": "playwright test",
    "e2e:ui": "playwright test --ui",
    "e2e:headed": "playwright test --headed"
  }
}
```

---

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── __tests__/
│   │   │   │   ├── button.test.tsx
│   │   │   │   ├── card.test.tsx
│   │   │   │   └── ...
│   │   │   └── button.tsx
│   │   ├── landing/
│   │   │   ├── __tests__/
│   │   │   │   └── Hero.test.tsx
│   │   │   └── Hero.tsx
│   │   └── auth/
│   │       ├── __tests__/
│   │       │   └── LoginForm.test.tsx
│   │       └── LoginForm.tsx
│   └── tests/
│       ├── setup.ts              # Test setup & global mocks
│       ├── utils.tsx              # Custom render utilities
│       └── mocks/
│           ├── handlers.ts        # MSW request handlers
│           ├── server.ts          # MSW server setup
│           └── browser.ts         # MSW browser setup
├── e2e/
│   ├── landing-page.spec.ts
│   ├── auth.spec.ts
│   ├── dashboard.spec.ts
│   ├── api-keys.spec.ts
│   └── accessibility.spec.ts
├── vitest.config.ts
└── playwright.config.ts
```

---

## Component Tests

### UI Component Tests

Located in `src/components/ui/__tests__/`

**Example: Button Component**

```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/utils'
import userEvent from '@testing-library/user-event'
import { Button } from '../button'

describe('Button Component', () => {
  it('renders with default variant', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### Feature Component Tests

**Example: LoginForm**

```typescript
import { render, screen, waitFor } from '@/tests/utils'
import { LoginForm } from '../LoginForm'

describe('LoginForm', () => {
  it('submits form with valid credentials', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    await user.type(screen.getByLabelText(/e-mail/i), 'test@example.com')
    await user.type(screen.getByLabelText(/passwort/i), 'password123')
    await user.click(screen.getByRole('button', { name: /anmelden/i }))

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalled()
    })
  })
})
```

---

## E2E Tests

### Landing Page Tests

**File**: `e2e/landing-page.spec.ts`

```typescript
test.describe('Landing Page', () => {
  test('should display hero section', async ({ page }) => {
    await page.goto('/')
    const headline = page.getByRole('heading', { level: 1 })
    await expect(headline).toBeVisible()
  })
})
```

### Authentication Flow

**File**: `e2e/auth.spec.ts`

```typescript
test('should login successfully', async ({ page }) => {
  await page.goto('/de/login')
  await page.getByLabel(/e-mail/i).fill('test@example.com')
  await page.getByLabel(/passwort/i).fill('password123')
  await page.getByRole('button', { name: /anmelden/i }).click()

  await expect(page).toHaveURL(/dashboard/)
})
```

### Dashboard Tests

**File**: `e2e/dashboard.spec.ts`

Tests require authenticated session:

```typescript
async function login(page: any) {
  await page.goto('/de/login')
  // ... login logic
  await page.waitForURL(/dashboard/)
}

test('should display dashboard', async ({ page }) => {
  await login(page)
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible()
})
```

### Accessibility Tests

**File**: `e2e/accessibility.spec.ts`

```typescript
test('should have proper heading hierarchy', async ({ page }) => {
  await page.goto('/')
  const h1Elements = page.locator('h1')
  const h1Count = await h1Elements.count()
  expect(h1Count).toBe(1)
})

test('should support keyboard navigation', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('Tab')
  const focusedTag = await page.evaluate(() => document.activeElement?.tagName)
  expect(['A', 'BUTTON', 'INPUT']).toContain(focusedTag)
})
```

---

## Writing Tests

### Component Testing Guidelines

#### 1. Use Testing Library Queries

```typescript
// ✅ Good - Query by role/label (user-centric)
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText(/email/i)
screen.getByText(/welcome/i)

// ❌ Avoid - Query by implementation details
screen.getByClassName('btn-primary')
screen.getByTestId('submit-button')
```

#### 2. Test User Behavior, Not Implementation

```typescript
// ✅ Good - Test what user does
it('should submit form when button is clicked', async () => {
  render(<Form />)
  await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com')
  await userEvent.click(screen.getByRole('button', { name: /submit/i }))
  expect(mockSubmit).toHaveBeenCalled()
})

// ❌ Avoid - Test internal state
it('should update email state', () => {
  const { result } = renderHook(() => useFormState())
  act(() => result.current.setEmail('test@example.com'))
  expect(result.current.email).toBe('test@example.com')
})
```

#### 3. Use MSW for API Mocking

```typescript
import { server } from '@/tests/mocks/server'
import { http, HttpResponse } from 'msw'

test('handles API error', async () => {
  // Override default handler for this test
  server.use(
    http.get('/api/user', () => {
      return HttpResponse.json({ error: 'Not found' }, { status: 404 })
    })
  )

  render(<UserProfile />)
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument()
  })
})
```

#### 4. Test Accessibility

```typescript
it('has proper labels', () => {
  render(<LoginForm />)
  const emailInput = screen.getByLabelText(/e-mail/i)
  expect(emailInput).toHaveAttribute('id')
})

it('supports keyboard navigation', async () => {
  render(<Modal />)
  await userEvent.keyboard('{Escape}')
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
})
```

### E2E Testing Guidelines

#### 1. Use Page Object Model (POM) for Complex Flows

```typescript
// e2e/helpers/auth.ts
export async function login(page: Page, email: string, password: string) {
  await page.goto('/de/login')
  await page.getByLabel(/e-mail/i).fill(email)
  await page.getByLabel(/passwort/i).fill(password)
  await page.getByRole('button', { name: /anmelden/i }).click()
  await page.waitForURL(/dashboard/)
}
```

#### 2. Use Descriptive Test Names

```typescript
// ✅ Good
test('should create new API key and display it in table', async ({ page }) => {})

// ❌ Avoid
test('API key creation', async ({ page }) => {})
```

#### 3. Wait for Elements Properly

```typescript
// ✅ Good - Wait for specific condition
await expect(page.getByText('Success')).toBeVisible()
await page.waitForURL(/dashboard/)

// ❌ Avoid - Arbitrary timeouts
await page.waitForTimeout(5000)
```

---

## Best Practices

### 1. Test Organization

- **Co-locate tests** with components (`__tests__` folders)
- **Use descriptive `describe` blocks** for grouping related tests
- **One assertion per test** when possible (but don't be dogmatic)

### 2. Test Isolation

```typescript
beforeEach(() => {
  vi.clearAllMocks()
  // Reset any global state
})

afterEach(() => {
  // Clean up after each test
})
```

### 3. Async Testing

```typescript
// ✅ Good - Use waitFor for async updates
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument()
})

// ✅ Good - Use findBy queries (built-in waitFor)
expect(await screen.findByText('Loaded')).toBeInTheDocument()

// ❌ Avoid - Direct assertions without waiting
expect(screen.getByText('Loaded')).toBeInTheDocument()
```

### 4. Coverage Goals

- **Critical paths**: 100% coverage (auth, payments, data mutations)
- **UI components**: 80%+ coverage
- **Utility functions**: 90%+ coverage
- **Config/types**: Not required

### 5. Test Performance

- **Run unit tests in parallel**: Vitest does this by default
- **Skip heavy E2E tests locally**: Use `test.skip()` or run specific files
- **Use MSW instead of real API calls**: Faster and more reliable

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:run
      - run: npm run test:coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### Pre-commit Hooks

```bash
# .husky/pre-commit
npm run test:run
npm run lint
```

---

## Troubleshooting

### Common Issues

#### MSW Not Intercepting Requests

```typescript
// Ensure setup.ts imports server
import './mocks/server'

// Check handler URL matches exactly
http.get('http://localhost:9001/api/v1/users', ...)
```

#### React 19 Warnings

```typescript
// Already handled in setup.ts
console.error = (...args) => {
  if (args[0]?.includes?.('ReactDOMTestUtils.act')) return
  originalConsoleError(...args)
}
```

#### E2E Tests Timing Out

```typescript
// Increase timeout in playwright.config.ts
use: {
  baseURL: 'http://localhost:3000',
  timeout: 30000, // 30s
}

// Or use test.setTimeout
test.setTimeout(60000)
```

---

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [MSW Documentation](https://mswjs.io/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

## Conclusion

This testing setup provides:

- **Fast feedback** with Vitest's instant HMR
- **Reliable E2E tests** with Playwright
- **Realistic API mocking** with MSW
- **Accessibility testing** built-in
- **Type-safe tests** with TypeScript

Happy testing! 🧪
