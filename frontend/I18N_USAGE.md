# Internationalization (i18n) Usage Guide

## Overview

This application uses `next-intl` for internationalization, supporting German (de) and English (en).

## Quick Start

### 1. Using translations in Server Components

```tsx
import { useTranslations } from 'next-intl'

export default function ServerComponent() {
  const t = useTranslations('landing.hero')

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('subtitle')}</p>
    </div>
  )
}
```

### 2. Using translations in Client Components

```tsx
'use client'

import { useTranslations } from 'next-intl'

export default function ClientComponent() {
  const t = useTranslations('common')

  return (
    <button>{t('save')}</button>
  )
}
```

### 3. Multiple translation namespaces

```tsx
import { useTranslations } from 'next-intl'

export default function MyPage() {
  const tCommon = useTranslations('common')
  const tAuth = useTranslations('auth.login')

  return (
    <div>
      <h1>{tAuth('title')}</h1>
      <button>{tCommon('cancel')}</button>
    </div>
  )
}
```

## Available Translation Keys

### Common
- `common.loading` - "Laden..." / "Loading..."
- `common.save` - "Speichern" / "Save"
- `common.cancel` - "Abbrechen" / "Cancel"
- `common.delete` - "Löschen" / "Delete"
- `common.edit` - "Bearbeiten" / "Edit"
- `common.create` - "Erstellen" / "Create"
- `common.search` - "Suchen" / "Search"
- And more... (see `/messages/de.json` and `/messages/en.json`)

### Navigation
- `nav.home` - "Startseite" / "Home"
- `nav.features` - "Funktionen" / "Features"
- `nav.pricing` - "Preise" / "Pricing"
- `nav.login` - "Anmelden" / "Login"
- And more...

### Landing Page
- `landing.hero.title`
- `landing.hero.subtitle`
- `landing.hero.cta_primary`
- `landing.features.title`
- `landing.pricing.title`
- And more...

### Authentication
- `auth.login.title`
- `auth.login.email`
- `auth.login.password`
- `auth.signup.title`
- And more...

### Dashboard
- `dashboard.title`
- `dashboard.overview`
- `dashboard.credits.title`
- And more...

### Accessibility
- `accessibility.panel_title`
- `accessibility.font_size`
- `accessibility.high_contrast`
- And more...

## Adding New Translations

1. **Add to German file** (`/messages/de.json`):
```json
{
  "myFeature": {
    "title": "Mein Feature",
    "description": "Das ist mein tolles neues Feature"
  }
}
```

2. **Add to English file** (`/messages/en.json`):
```json
{
  "myFeature": {
    "title": "My Feature",
    "description": "This is my awesome new feature"
  }
}
```

3. **Use in component**:
```tsx
import { useTranslations } from 'next-intl'

export default function MyFeature() {
  const t = useTranslations('myFeature')

  return (
    <div>
      <h2>{t('title')}</h2>
      <p>{t('description')}</p>
    </div>
  )
}
```

## Language Switching

### Adding the Language Switcher

Add the `LanguageSwitcher` component to your navbar or header:

```tsx
import { LanguageSwitcher } from '@/components/shared/LanguageSwitcher'

export default function Navbar() {
  return (
    <nav>
      {/* Other nav items */}
      <LanguageSwitcher />
    </nav>
  )
}
```

### How it works

1. User clicks the language switcher dropdown
2. Selects a new language (de/en)
3. Cookie is set with the new locale
4. Page reloads with new language

### Programmatic Language Switch

```tsx
'use client'

export function CustomLanguageSwitch() {
  const switchToGerman = () => {
    document.cookie = 'locale=de; path=/; max-age=31536000; SameSite=Lax'
    window.location.reload()
  }

  const switchToEnglish = () => {
    document.cookie = 'locale=en; path=/; max-age=31536000; SameSite=Lax'
    window.location.reload()
  }

  return (
    <div>
      <button onClick={switchToGerman}>Deutsch</button>
      <button onClick={switchToEnglish}>English</button>
    </div>
  )
}
```

## Translation with Variables

Currently, the translations are static strings. If you need variables:

```json
{
  "welcome": "Welcome, {name}!"
}
```

```tsx
const t = useTranslations('messages')
t('welcome', { name: 'John' }) // "Welcome, John!"
```

## Translation with Rich Text

For rich text with formatting:

```json
{
  "terms": "I accept the <terms>Terms & Conditions</terms> and <privacy>Privacy Policy</privacy>"
}
```

```tsx
const t = useTranslations('auth.signup')

t.rich('accept_terms', {
  terms: (chunks) => <a href="/terms">{chunks}</a>,
  privacy: (chunks) => <a href="/privacy">{chunks}</a>
})
```

## Pluralization

For handling singular/plural forms:

```json
{
  "items": "{count, plural, =0 {No items} =1 {One item} other {# items}}"
}
```

```tsx
t('items', { count: 0 }) // "No items"
t('items', { count: 1 }) // "One item"
t('items', { count: 5 }) // "5 items"
```

## Date and Time Formatting

```tsx
import { useFormatter } from 'next-intl'

function MyComponent() {
  const format = useFormatter()

  const now = new Date()

  return (
    <div>
      <p>{format.dateTime(now, { dateStyle: 'long' })}</p>
      <p>{format.dateTime(now, { timeStyle: 'short' })}</p>
    </div>
  )
}
```

## Number Formatting

```tsx
import { useFormatter } from 'next-intl'

function MyComponent() {
  const format = useFormatter()

  return (
    <div>
      <p>{format.number(1234.56, { style: 'currency', currency: 'EUR' })}</p>
      <p>{format.number(0.42, { style: 'percent' })}</p>
    </div>
  )
}
```

## Best Practices

1. **Use namespaces:** Organize translations into logical namespaces (e.g., `auth.login`, `dashboard.credits`)

2. **Keep keys descriptive:** Use clear, descriptive keys that indicate what the text is for

3. **Consistent naming:** Use consistent naming conventions across all translation files

4. **Avoid hardcoded strings:** Always use translation keys instead of hardcoded text

5. **Default to German:** German is the primary language, so ensure German translations are complete

6. **Test both languages:** Always test your components in both German and English

7. **Use TypeScript:** next-intl provides type safety for translation keys

## Configuration Files

### `/src/i18n/request.ts`
Main i18n configuration file that:
- Detects locale from cookie or browser headers
- Loads appropriate translation file
- Sets default locale to German

### `/messages/de.json` & `/messages/en.json`
Translation files containing all text strings in German and English respectively.

## Troubleshooting

### Translation key not found

If you see `[missing: namespace.key]`:
1. Check that the key exists in both translation files
2. Verify the namespace is correct
3. Check for typos in the key name

### Language not switching

If language doesn't switch:
1. Check that cookie is being set correctly
2. Verify page is reloading after language change
3. Check browser console for errors

### Hydration errors

If you get hydration mismatches:
1. Make sure `NextIntlClientProvider` wraps client components
2. Use `'use client'` directive in client components
3. Check that messages are loaded correctly in layout

## Additional Resources

- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [ICU Message Format](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- Project translation files: `/messages/de.json`, `/messages/en.json`
