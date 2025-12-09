# Internationalization (i18n) Setup - Complete

## Overview

The AI Legal Ops Gateway frontend now has a complete internationalization setup using `next-intl` with support for German (de) and English (en).

## Files Created/Updated

### Translation Files
- **`/root/Projekte/ai-orchestra-gateway/frontend/messages/de.json`** - German translations (comprehensive)
- **`/root/Projekte/ai-orchestra-gateway/frontend/messages/en.json`** - English translations (comprehensive)

### Configuration Files
- **`/root/Projekte/ai-orchestra-gateway/frontend/src/i18n.ts`** - Main i18n configuration
- **`/root/Projekte/ai-orchestra-gateway/frontend/src/i18n/request.ts`** - Request-level i18n configuration (already existed, working correctly)
- **`/root/Projekte/ai-orchestra-gateway/frontend/src/middleware.ts`** - Updated to integrate i18n with Supabase auth
- **`/root/Projekte/ai-orchestra-gateway/frontend/next.config.ts`** - Already configured with next-intl plugin

### Components
- **`/root/Projekte/ai-orchestra-gateway/frontend/src/components/shared/LocaleSwitcher.tsx`** - Advanced locale switcher with dropdown menu
- **`/root/Projekte/ai-orchestra-gateway/frontend/src/components/shared/LocaleSwitcherSimple.tsx`** - Simple select-based locale switcher

## Translation Categories

The translation files include comprehensive translations for:

### 1. Common Translations
- Buttons: save, cancel, delete, edit, create, search, etc.
- States: loading, error, success, warning, info
- Actions: confirm, close, yes, no, submit, apply, reset

### 2. Navigation
- Main navigation items: home, dashboard, apiKeys, usage, billing, settings, admin
- Additional pages: features, pricing, docs, blog, apps, analytics, auditLogs, tenants, licenses, users

### 3. Landing Page
- **Hero Section**: title, subtitle, description, CTA buttons
- **Features Section**: 6 key features with titles and descriptions
  - Privacy Shield
  - Multi-Provider support
  - EU Hosting
  - Multi-Tenant architecture
  - Pay-per-Use billing
  - Provider Failover
  - Usage Analytics
  - GDPR Compliance
- **Pricing Section**: Starter, Professional, Enterprise plans
- **FAQ Section**
- **CTA Section**

### 4. Authentication
- **Login**: title, email, password, forgot password, signup link
- **Signup**: title, name, email, password, confirm password, terms acceptance
- **Reset Password**: title, description, submit, success messages
- **Verify Email**: title, message, resend options

### 5. Dashboard
- Overview stats: credits, requests, tokens, API keys
- Welcome messages
- Navigation items

### 6. Admin Panel
- Tenants management
- Licenses management
- Users management
- Audit logs
- Analytics
- Billing
- Settings

### 7. Error Messages
- Form validation: required, invalidEmail, passwordMin, passwordMatch
- HTTP errors: not_found, unauthorized, forbidden, validation
- Network errors: networkError, serverError, timeout

### 8. Accessibility
- Accessibility panel controls
- Font size adjustments
- High contrast mode
- Reduced motion
- Focus indicators
- Skip to content link

### 9. Language Switcher
- Language selection labels
- Language names (Deutsch, English)

### 10. Additional Sections
- **API Keys**: management, creation, status
- **Usage**: statistics, timeline, costs
- **Billing**: credits, invoices, payment methods
- **Settings**: profile, security, notifications
- **Form**: placeholders, validation
- **Notifications**: success/error messages
- **Footer**: company info, legal, resources

## How to Use

### Basic Usage in Components

```typescript
// In a Server Component
import { useTranslations } from 'next-intl'

export default function MyComponent() {
  const t = useTranslations('common')

  return (
    <div>
      <button>{t('save')}</button>
      <button>{t('cancel')}</button>
    </div>
  )
}
```

### Using Nested Translations

```typescript
import { useTranslations } from 'next-intl'

export default function Hero() {
  const t = useTranslations('landing.hero')

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('subtitle')}</p>
      <p>{t('description')}</p>
      <button>{t('cta')}</button>
    </div>
  )
}
```

### Using the LocaleSwitcher

```typescript
// Import in your layout or header component
import { LocaleSwitcher } from '@/components/shared/LocaleSwitcher'

export default function Header() {
  return (
    <header>
      <nav>
        {/* Your navigation */}
      </nav>
      <LocaleSwitcher />
    </header>
  )
}
```

### Simple Select-based Switcher

```typescript
import { LocaleSwitcherSimple } from '@/components/shared/LocaleSwitcherSimple'

export default function Footer() {
  return (
    <footer>
      <LocaleSwitcherSimple />
    </footer>
  )
}
```

### Dynamic Values in Translations

```typescript
const t = useTranslations('errors')

// For translations with placeholders like "At least {min} characters"
<p>{t('passwordMin', { min: 8 })}</p>
```

### Client Components

```typescript
'use client'

import { useTranslations } from 'next-intl'

export default function MyClientComponent() {
  const t = useTranslations('dashboard')

  return <h1>{t('welcome')}</h1>
}
```

## Locale Detection Flow

1. **Cookie**: First checks for `locale` cookie (set by LocaleSwitcher)
2. **Accept-Language Header**: Falls back to browser language preference
3. **Default**: Uses German (`de`) as the default locale

## Middleware Integration

The middleware combines:
- **i18n locale detection**: Sets and persists locale preference
- **Supabase session management**: Handles authentication
- **Route protection**: Redirects unauthenticated users to login

## Configuration

### Supported Locales

```typescript
// src/i18n.ts
export const locales = ['de', 'en'] as const
export const defaultLocale = 'de'
```

### Adding a New Language

1. Create a new message file: `messages/fr.json`
2. Add the locale to `src/i18n.ts`:
   ```typescript
   export const locales = ['de', 'en', 'fr'] as const
   ```
3. Update `LocaleSwitcher.tsx` to include the new language:
   ```typescript
   const locales = [
     { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
     { code: 'en', name: 'English', flag: '🇬🇧' },
     { code: 'fr', name: 'Français', flag: '🇫🇷' },
   ]
   ```

## Testing

### Test Locale Switching

1. Open the application in your browser
2. Use the LocaleSwitcher component to switch between languages
3. Verify that all text updates correctly
4. Refresh the page - the locale should persist (stored in cookie)

### Test Browser Language Detection

1. Clear your browser cookies
2. Change your browser's language preference to German
3. Visit the site - it should default to German
4. Change browser language to English
5. Clear cookies and visit again - it should default to English

## Package Dependencies

The following package is already installed:

```json
{
  "dependencies": {
    "next-intl": "^3.26.2"
  }
}
```

## Next.js Configuration

The `next.config.ts` is already configured with the next-intl plugin:

```typescript
import createNextIntlPlugin from 'next-intl/plugin'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

export default withNextIntl(nextConfig)
```

## Best Practices

1. **Namespace Organization**: Group related translations under namespaces (e.g., `common`, `auth`, `dashboard`)
2. **Consistent Keys**: Use camelCase for translation keys (e.g., `confirmPassword`, not `confirm_password`)
3. **Avoid Hardcoded Text**: Always use translations, never hardcode text in components
4. **Keep Translations Synchronized**: When adding a key to one language file, add it to all language files
5. **Use Descriptive Keys**: Make keys self-explanatory (e.g., `hero.cta_primary` instead of `button1`)

## Accessibility

The LocaleSwitcher components include:
- Proper ARIA labels
- Keyboard navigation support
- Visual indicators for current locale
- Screen reader friendly

## Performance

- **Tree Shaking**: Only the required locale messages are loaded
- **Code Splitting**: Translation files are loaded on-demand
- **Cookie Caching**: Locale preference is cached in a cookie (1 year expiry)
- **Server Components**: Translations work in both server and client components

## Troubleshooting

### Translations Not Showing

1. Check that the translation key exists in both `de.json` and `en.json`
2. Verify the namespace is correct (first parameter to `useTranslations`)
3. Check the browser console for any error messages

### Locale Not Persisting

1. Verify cookies are enabled in your browser
2. Check that the `locale` cookie is being set (Developer Tools → Application → Cookies)
3. Ensure middleware is running correctly

### Build Errors

1. Ensure all JSON files are valid (no trailing commas, proper quotes)
2. Run `npm run type-check` to verify TypeScript errors
3. Check that all translation files have the same structure

## Files Structure

```
frontend/
├── messages/
│   ├── de.json          # German translations
│   └── en.json          # English translations
├── src/
│   ├── i18n.ts          # Main i18n config
│   ├── i18n/
│   │   └── request.ts   # Request-level config
│   ├── middleware.ts    # Combined middleware (i18n + auth)
│   └── components/
│       └── shared/
│           ├── LocaleSwitcher.tsx        # Advanced switcher
│           └── LocaleSwitcherSimple.tsx  # Simple switcher
└── next.config.ts       # Next.js config with i18n plugin
```

## Summary

The i18n setup is now complete and production-ready with:
- ✅ Complete German and English translations
- ✅ Two locale switcher components (advanced and simple)
- ✅ Middleware integration with Supabase authentication
- ✅ Cookie-based locale persistence
- ✅ Browser language detection fallback
- ✅ Comprehensive translation coverage for all application sections
- ✅ Type-safe configuration
- ✅ Accessibility support
- ✅ Performance optimizations

You can now use translations throughout your application and easily add more languages in the future!
