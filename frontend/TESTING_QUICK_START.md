# Testing Quick Start Guide

**AI Legal Ops Frontend - Get Testing in 5 Minutes**

---

## 🚀 Quick Setup (3 Steps)

### 1. Install Dependencies

```bash
cd /root/Projekte/ai-orchestra-gateway/frontend

# Install MSW (Mock Service Worker)
npm install --save-dev msw@latest

# Install coverage tool
npm install --save-dev @vitest/coverage-v8
```

### 2. Verify Installation

```bash
# Check if all test dependencies are installed
npm list vitest @testing-library/react @playwright/test msw
```

### 3. Run Tests

```bash
# Run unit tests
npm test

# Run E2E tests
npm run e2e
```

---

## ✅ What's Already Done

- ✅ **120+ Tests** created and ready to run
- ✅ **MSW Handlers** for all API endpoints
- ✅ **Component Tests** for UI, Landing, Auth, Dashboard
- ✅ **E2E Tests** for critical user flows
- ✅ **Accessibility Tests** for WCAG 2.1 AA compliance
- ✅ **Documentation** complete

---

## 📋 Test Commands Cheat Sheet

### Unit & Component Tests

```bash
npm test                    # Run in watch mode
npm run test:run           # Run once (CI)
npm run test:coverage      # Generate coverage report
npm run test:ui            # Open Vitest UI
```

### E2E Tests

```bash
npm run e2e                # Run all E2E tests
npm run e2e:ui             # Open Playwright UI
npm run e2e:headed         # Run with browser visible
```

### Specific Tests

```bash
# Run specific unit test
npm test -- button.test

# Run specific E2E test
npx playwright test e2e/auth.spec.ts

# Debug E2E test
npx playwright test --debug
```

---

## 📊 Test Coverage

### Component Tests (56 tests)

- **UI Components**: Button, Card (19 tests)
- **Landing**: Hero (12 tests)
- **Auth**: LoginForm (11 tests)
- **Dashboard**: ApiKeyTable (14 tests)

### E2E Tests (65+ tests)

- **Landing Page**: 8 tests
- **Auth Flow**: 12 tests
- **Dashboard**: 12 tests
- **API Keys**: 15 tests
- **Accessibility**: 22 tests

### Total: **120+ comprehensive tests**

---

## 🗂️ Documentation

| File | Purpose |
|------|---------|
| **TESTING.md** | Complete testing guide (read this first!) |
| **TEST_SETUP_SUMMARY.md** | What was created and why |
| **TEST_INVENTORY.md** | Complete list of all tests |
| **TESTING_QUICK_START.md** | This file |

---

## 🔍 File Locations

### Component Tests

```
src/components/
├── ui/__tests__/
│   ├── button.test.tsx
│   └── card.test.tsx
├── landing/__tests__/
│   └── Hero.test.tsx
├── auth/__tests__/
│   └── LoginForm.test.tsx
└── dashboard/__tests__/
    └── ApiKeyTable.test.tsx
```

### E2E Tests

```
e2e/
├── landing-page.spec.ts
├── auth.spec.ts
├── dashboard.spec.ts
├── api-keys.spec.ts
└── accessibility.spec.ts
```

### Test Setup

```
src/tests/
├── setup.ts                # Global mocks
├── utils.tsx               # Custom render
└── mocks/
    ├── handlers.ts         # API mocks
    ├── server.ts           # Node setup
    └── browser.ts          # Browser setup
```

---

## 🐛 Troubleshooting

### MSW Not Working?

```bash
# Reinstall MSW
npm install --save-dev msw@latest

# Verify it's imported in setup.ts
# File: src/tests/setup.ts should have:
# import './mocks/server'
```

### E2E Tests Failing?

```bash
# Update Playwright browsers
npx playwright install --with-deps

# Check dev server is accessible
npm run dev
# Then in another terminal:
npm run e2e
```

### Coverage Not Generated?

```bash
# Install coverage tool
npm install --save-dev @vitest/coverage-v8

# Run coverage
npm run test:coverage
```

---

## 📖 Example Test

### Component Test Example

```typescript
// src/components/ui/__tests__/button.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/utils'
import userEvent from '@testing-library/user-event'
import { Button } from '../button'

describe('Button', () => {
  it('handles click events', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()

    render(<Button onClick={onClick}>Click me</Button>)

    await user.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
```

### E2E Test Example

```typescript
// e2e/landing-page.spec.ts
import { test, expect } from '@playwright/test'

test('should display hero section', async ({ page }) => {
  await page.goto('/')

  const headline = page.getByRole('heading', { level: 1 })
  await expect(headline).toBeVisible()
  await expect(headline).toContainText('AI Gateway')
})
```

---

## 🎯 Next Steps

1. **Install dependencies** (Step 1 above)
2. **Run tests** to verify setup
3. **Check coverage**: `npm run test:coverage`
4. **Add tests** for new features as you build
5. **Setup CI/CD** (see TESTING.md)

---

## 💡 Tips

- **Run tests while developing**: `npm test` runs in watch mode
- **Focus on one test**: Use `it.only()` or `test.only()`
- **Skip slow E2E tests**: Use `test.skip()` when developing
- **Check coverage**: Aim for 80%+ on new code
- **Write tests first**: Try TDD for new features

---

## 🆘 Need Help?

1. **Read TESTING.md** - Complete guide with examples
2. **Check TEST_INVENTORY.md** - See all test examples
3. **Look at existing tests** - Copy patterns from working tests
4. **MSW issues** - Check `src/tests/mocks/handlers.ts`

---

## ✨ You're Ready!

You now have a **production-ready testing suite** with:

- ✅ Fast unit tests (Vitest)
- ✅ Comprehensive E2E tests (Playwright)
- ✅ Realistic API mocking (MSW)
- ✅ Accessibility testing (WCAG 2.1 AA)
- ✅ Full documentation

**Just run**: `npm test` and `npm run e2e`

Happy testing! 🎉
