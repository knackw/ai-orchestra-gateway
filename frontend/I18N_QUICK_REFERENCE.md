# i18n Quick Reference Guide

## Common Use Cases

### 1. Simple Translation

```typescript
import { useTranslations } from 'next-intl'

export default function MyComponent() {
  const t = useTranslations('common')

  return <button>{t('save')}</button>
}
```

### 2. Nested Translation Keys

```typescript
const t = useTranslations('landing.hero')
// Accesses: landing.hero.title
return <h1>{t('title')}</h1>
```

### 3. Multiple Namespaces

```typescript
const tCommon = useTranslations('common')
const tAuth = useTranslations('auth.login')

return (
  <div>
    <button>{tCommon('cancel')}</button>
    <input placeholder={tAuth('email')} />
  </div>
)
```

### 4. Dynamic Values

```typescript
const t = useTranslations('errors')

// Translation: "At least {min} characters"
<p>{t('passwordMin', { min: 8 })}</p>
```

### 5. Client Components

```typescript
'use client'

import { useTranslations } from 'next-intl'

export default function ClientComponent() {
  const t = useTranslations('dashboard')
  return <h1>{t('welcome')}</h1>
}
```

### 6. Server Components

```typescript
import { useTranslations } from 'next-intl'

export default function ServerComponent() {
  const t = useTranslations('navigation')
  return <nav>{t('home')}</nav>
}
```

## Translation Keys by Section

### Common Actions
```typescript
const t = useTranslations('common')
t('login')      // "Anmelden" / "Login"
t('signup')     // "Registrieren" / "Sign Up"
t('logout')     // "Abmelden" / "Logout"
t('save')       // "Speichern" / "Save"
t('cancel')     // "Abbrechen" / "Cancel"
t('delete')     // "Löschen" / "Delete"
t('edit')       // "Bearbeiten" / "Edit"
t('create')     // "Erstellen" / "Create"
t('search')     // "Suchen" / "Search"
t('loading')    // "Wird geladen..." / "Loading..."
```

### Navigation
```typescript
const t = useTranslations('navigation')
t('home')       // "Startseite" / "Home"
t('dashboard')  // "Dashboard" / "Dashboard"
t('apiKeys')    // "API-Schlüssel" / "API Keys"
t('usage')      // "Nutzung" / "Usage"
t('billing')    // "Abrechnung" / "Billing"
t('settings')   // "Einstellungen" / "Settings"
t('admin')      // "Administration" / "Administration"
```

### Landing Page
```typescript
const tHero = useTranslations('landing.hero')
tHero('title')        // "KI-Power für Ihr Business"
tHero('subtitle')     // "DSGVO-konform"
tHero('description')  // "Multi-Provider AI Gateway..."
tHero('cta')          // "Kostenlos starten"

const tFeatures = useTranslations('landing.features')
tFeatures('title')                      // "Funktionen"
tFeatures('privacyShield.title')        // "Privacy Shield"
tFeatures('privacyShield.description')  // "Automatische PII-Erkennung..."
```

### Authentication
```typescript
const tLogin = useTranslations('auth.login')
tLogin('title')          // "Anmelden" / "Login"
tLogin('email')          // "E-Mail-Adresse" / "Email address"
tLogin('password')       // "Passwort" / "Password"
tLogin('submit')         // "Anmelden" / "Sign In"
tLogin('forgotPassword') // "Passwort vergessen?" / "Forgot password?"

const tSignup = useTranslations('auth.signup')
tSignup('title')           // "Registrieren" / "Sign Up"
tSignup('confirmPassword') // "Passwort bestätigen" / "Confirm Password"
tSignup('acceptTerms')     // "Ich akzeptiere die AGB"
```

### Dashboard
```typescript
const t = useTranslations('dashboard')
t('welcome')                    // "Willkommen zurück" / "Welcome back"
t('stats.requestsToday')        // "Anfragen heute" / "Requests today"
t('stats.tokensThisMonth')      // "Tokens diesen Monat" / "Tokens this month"
t('credits.title')              // "Guthaben" / "Credits"
t('credits.remaining')          // "Verbleibend" / "Remaining"
```

### Error Messages
```typescript
const t = useTranslations('errors')
t('required')       // "Dieses Feld ist erforderlich"
t('invalidEmail')   // "Ungültige E-Mail-Adresse"
t('passwordMin', { min: 8 })  // "Mindestens 8 Zeichen"
t('passwordMatch')  // "Passwörter stimmen nicht überein"
t('generic')        // "Ein Fehler ist aufgetreten"
```

## Locale Switcher Usage

### Option 1: Dropdown Menu (Advanced)

```typescript
import { LocaleSwitcher } from '@/components/shared/LocaleSwitcher'

export default function Header() {
  return (
    <header className="flex justify-between items-center p-4">
      <Logo />
      <LocaleSwitcher />
    </header>
  )
}
```

### Option 2: Simple Select

```typescript
import { LocaleSwitcherSimple } from '@/components/shared/LocaleSwitcherSimple'

export default function Footer() {
  return (
    <footer className="p-4">
      <LocaleSwitcherSimple />
    </footer>
  )
}
```

## Adding New Translations

### 1. Add to German file (`messages/de.json`):
```json
{
  "mySection": {
    "myKey": "Mein deutscher Text"
  }
}
```

### 2. Add to English file (`messages/en.json`):
```json
{
  "mySection": {
    "myKey": "My English text"
  }
}
```

### 3. Use in component:
```typescript
const t = useTranslations('mySection')
return <p>{t('myKey')}</p>
```

## Locale Detection

1. **Cookie** (highest priority) - User's explicit choice via LocaleSwitcher
2. **Accept-Language Header** - Browser's language preference
3. **Default** (fallback) - German (`de`)

## Cookie Management

The locale is stored in a cookie named `locale` with:
- **Path**: `/` (site-wide)
- **Max-Age**: 1 year (31536000 seconds)
- **Set by**: LocaleSwitcher components
- **Read by**: Middleware and i18n config

## Common Patterns

### Form with Translations

```typescript
'use client'

import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function LoginForm() {
  const t = useTranslations('auth.login')
  const tCommon = useTranslations('common')
  const tErrors = useTranslations('errors')

  return (
    <form>
      <h2>{t('title')}</h2>
      <Input
        type="email"
        placeholder={t('email')}
        required
        aria-label={t('email')}
      />
      <Input
        type="password"
        placeholder={t('password')}
        required
        aria-label={t('password')}
      />
      <Button type="submit">{t('submit')}</Button>
      <Button type="button" variant="ghost">
        {tCommon('cancel')}
      </Button>
    </form>
  )
}
```

### Navigation with Translations

```typescript
import { useTranslations } from 'next-intl'
import Link from 'next/link'

export default function Navigation() {
  const t = useTranslations('navigation')

  const links = [
    { href: '/', label: t('home') },
    { href: '/dashboard', label: t('dashboard') },
    { href: '/usage', label: t('usage') },
    { href: '/billing', label: t('billing') },
    { href: '/settings', label: t('settings') },
  ]

  return (
    <nav>
      {links.map(link => (
        <Link key={link.href} href={link.href}>
          {link.label}
        </Link>
      ))}
    </nav>
  )
}
```

### Stats Card with Translations

```typescript
import { useTranslations } from 'next-intl'

export default function StatsCard({ value }: { value: number }) {
  const t = useTranslations('dashboard.stats')

  return (
    <div className="card">
      <h3>{t('requestsToday')}</h3>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  )
}
```

## TypeScript Support

For better type safety, you can create a type definition for your translations:

```typescript
// types/i18n.ts
import de from '@/messages/de.json'

type Messages = typeof de

declare global {
  interface IntlMessages extends Messages {}
}
```

Then use it in your components for autocomplete and type checking:

```typescript
const t = useTranslations('common')
t('save') // ✅ TypeScript knows this key exists
t('invalid') // ❌ TypeScript error - key doesn't exist
```

## Performance Tips

1. **Use Specific Namespaces**: Instead of loading all translations, use specific namespaces
   ```typescript
   // ✅ Good - only loads 'common' namespace
   const t = useTranslations('common')

   // ❌ Avoid - loads all translations
   const t = useTranslations()
   ```

2. **Server Components**: Prefer server components for static content
   ```typescript
   // ✅ Server component - no client JS needed
   export default function StaticContent() {
     const t = useTranslations('landing.hero')
     return <h1>{t('title')}</h1>
   }
   ```

3. **Memoization**: For complex client components, memoize translations
   ```typescript
   'use client'
   import { useMemo } from 'react'
   import { useTranslations } from 'next-intl'

   export default function ComplexComponent() {
     const t = useTranslations('navigation')
     const links = useMemo(() => [
       { href: '/', label: t('home') },
       // ...
     ], [t])
   }
   ```

## Debugging

### Check Current Locale

```typescript
'use client'
import { useLocale } from 'next-intl'

export default function DebugLocale() {
  const locale = useLocale()
  return <p>Current locale: {locale}</p>
}
```

### Check If Translation Exists

```typescript
const t = useTranslations('common')

try {
  const text = t('someKey')
  console.log(text)
} catch (error) {
  console.error('Translation missing:', error)
}
```

### View All Cookies

Browser DevTools → Application → Cookies → Select your domain → Look for `locale` cookie

## Summary

- **Import**: `import { useTranslations } from 'next-intl'`
- **Usage**: `const t = useTranslations('namespace')`
- **Access**: `t('key')` or `t('nested.key')`
- **Dynamic**: `t('key', { variable: value })`
- **Switcher**: `<LocaleSwitcher />` or `<LocaleSwitcherSimple />`
- **Supported**: German (de), English (en)
- **Default**: German (de)
