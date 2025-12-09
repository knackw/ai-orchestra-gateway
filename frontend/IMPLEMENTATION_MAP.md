# I18N & Accessibility Implementation Map

## Visual File Structure

```
frontend/
│
├── 📄 ACCESSIBILITY.md                    # Complete A11y guide & WCAG checklist
├── 📄 I18N_USAGE.md                       # i18n usage examples & best practices
├── 📄 I18N_A11Y_IMPLEMENTATION.md         # Complete implementation summary
├── 📄 IMPLEMENTATION_CHECKLIST.md         # Task checklist & testing guide
├── 📄 IMPLEMENTATION_MAP.md               # This file (visual guide)
│
├── 📁 messages/                           # Translation files
│   ├── 📄 de.json                         # German translations (default/primary)
│   └── 📄 en.json                         # English translations
│
├── 📄 next.config.ts                      # ✏️ MODIFIED: Added next-intl plugin
│
└── 📁 src/
    │
    ├── 📁 app/
    │   ├── 📄 layout.tsx                  # ✏️ MODIFIED: Added i18n + a11y providers
    │   └── 📄 globals.css                 # ✏️ MODIFIED: Added a11y styles
    │
    ├── 📁 components/
    │   │
    │   ├── 📁 shared/                     # NEW: Shared components
    │   │   ├── 📄 AccessibilityPanel.tsx  # ✨ A11y settings panel (floating)
    │   │   ├── 📄 LanguageSwitcher.tsx    # ✨ Language dropdown with flags
    │   │   └── 📄 SkipLink.tsx            # ✨ Skip to main content link
    │   │
    │   └── 📁 ui/                         # NEW: UI components for A11y
    │       ├── 📄 slider.tsx              # ✨ Range slider (font size)
    │       ├── 📄 switch.tsx              # ✨ Toggle switch (settings)
    │       ├── 📄 popover.tsx             # ✨ Popover (A11y panel)
    │       ├── 📄 dropdown-menu.tsx       # ✨ Dropdown (language switcher)
    │       └── 📄 separator.tsx           # ✨ Separator component
    │
    ├── 📁 hooks/                          # NEW: Custom hooks
    │   └── 📄 use-accessibility.tsx       # ✨ A11y context + hook
    │
    └── 📁 i18n/                           # NEW: i18n configuration
        └── 📄 request.ts                  # ✨ i18n config & locale detection
```

## Legend

- 📄 = File
- 📁 = Directory
- ✨ = NEW file created
- ✏️ = MODIFIED existing file

---

## Implementation Flow

### 1. I18N Setup Flow

```
User Request → Browser Language Detection → Cookie Check
                                               ↓
                                         Locale Selected
                                               ↓
                                      /src/i18n/request.ts
                                               ↓
                                    Load messages/{locale}.json
                                               ↓
                                      NextIntlClientProvider
                                               ↓
                                    All components have access
                                               ↓
                                    useTranslations('namespace')
```

### 2. Language Switching Flow

```
User clicks LanguageSwitcher → Selects language (de/en)
                                      ↓
                              Set cookie: locale={lang}
                                      ↓
                              Reload page
                                      ↓
                       New locale detected from cookie
                                      ↓
                       Messages loaded for new locale
```

### 3. Accessibility Settings Flow

```
User opens AccessibilityPanel → Adjusts settings
                                      ↓
                            useAccessibility hook
                                      ↓
                    State updated in AccessibilityProvider
                                      ↓
                    Saved to localStorage: accessibility-settings
                                      ↓
                    Applied to document (html classes & styles)
                                      ↓
            - Font size → html.style.fontSize
            - High contrast → html.classList.add('high-contrast')
            - Reduced motion → html.classList.add('reduced-motion')
            - Focus indicators → html.classList.add('focus-indicators')
```

---

## Component Integration

### Adding to Existing Components

#### 1. Add Language Switcher to Navbar

```tsx
// In your Navbar component
import { LanguageSwitcher } from '@/components/shared/LanguageSwitcher'

export function Navbar() {
  return (
    <nav className="flex items-center justify-between">
      {/* Your existing nav items */}
      <div className="flex items-center gap-4">
        <ThemeSwitcher />
        <LanguageSwitcher />  {/* Add this */}
      </div>
    </nav>
  )
}
```

#### 2. Use Translations in Components

```tsx
// Any component
import { useTranslations } from 'next-intl'

export function MyComponent() {
  const t = useTranslations('common')

  return (
    <button>{t('save')}</button>
  )
}
```

#### 3. Use Accessibility Settings

```tsx
'use client'
import { useAccessibility } from '@/hooks/use-accessibility'

export function MyComponent() {
  const { fontSize, highContrast } = useAccessibility()

  // Settings are automatically applied to html element
  // Just use them for conditional rendering if needed
  return (
    <div className={highContrast ? 'font-bold' : ''}>
      Content
    </div>
  )
}
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Root Layout                              │
│  /src/app/layout.tsx                                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ NextIntlClientProvider (messages from i18n/request.ts)  │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ AccessibilityProvider (from use-accessibility)  │   │   │
│  │  │  ┌───────────────────────────────────────────┐  │   │   │
│  │  │  │ ThemeProvider                             │  │   │   │
│  │  │  │  ┌─────────────────────────────────────┐  │  │   │   │
│  │  │  │  │ SkipLink (keyboard nav)             │  │  │   │   │
│  │  │  │  │ <main id="main-content">            │  │  │   │   │
│  │  │  │  │   {children} ← Your pages/routes    │  │  │   │   │
│  │  │  │  │ </main>                             │  │  │   │   │
│  │  │  │  │ Toaster                             │  │  │   │   │
│  │  │  │  │ AccessibilityPanel (floating)       │  │  │   │   │
│  │  │  │  └─────────────────────────────────────┘  │  │   │   │
│  │  │  └───────────────────────────────────────────┘  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Translation Namespace Structure

```json
{
  "common": {                    // Shared UI elements
    "loading": "...",
    "save": "...",
    "cancel": "..."
  },
  "nav": {                       // Navigation
    "home": "...",
    "features": "..."
  },
  "landing": {                   // Landing page
    "hero": {
      "title": "...",
      "subtitle": "..."
    },
    "features": {
      "title": "...",
      "pii_shield": { ... }
    },
    "pricing": { ... }
  },
  "auth": {                      // Authentication
    "login": { ... },
    "signup": { ... }
  },
  "dashboard": {                 // Dashboard
    "title": "...",
    "credits": { ... }
  },
  "admin": {                     // Admin panel
    "tenants": "..."
  },
  "accessibility": {             // A11y panel
    "font_size": "...",
    "high_contrast": "..."
  },
  "language": {                  // Language switcher
    "select": "...",
    "de": "Deutsch",
    "en": "English"
  }
}
```

---

## Accessibility Features Map

### Font Size Control
- **Range:** 80% - 150%
- **Default:** 100%
- **Applied to:** `html.style.fontSize`
- **Component:** Slider in AccessibilityPanel

### High Contrast Mode
- **States:** On/Off
- **Default:** Off
- **Applied to:** `html.classList` → `.high-contrast`
- **Component:** Switch in AccessibilityPanel
- **Styles:** Custom CSS variables in globals.css

### Reduced Motion
- **States:** On/Off
- **Default:** Off
- **Applied to:** `html.classList` → `.reduced-motion`
- **Component:** Switch in AccessibilityPanel
- **Effect:** Disables animations/transitions

### Focus Indicators
- **States:** On/Off
- **Default:** On
- **Applied to:** `html.classList` → `.focus-indicators`
- **Component:** Switch in AccessibilityPanel
- **Effect:** Shows/hides focus rings

### Skip Link
- **Visibility:** Hidden until focused (Tab key)
- **Target:** `#main-content`
- **Purpose:** Bypass navigation for keyboard users

---

## CSS Classes Added

### Accessibility Classes

```css
/* High contrast mode */
.high-contrast { /* Custom color variables */ }
.dark.high-contrast { /* Dark mode variant */ }

/* Focus indicators */
.focus-indicators *:focus-visible { /* Enhanced focus styles */ }

/* Reduced motion */
.reduced-motion * { /* Disable animations */ }

/* Screen reader only */
.sr-only { /* Visually hidden */ }
.sr-only:focus { /* Visible on focus */ }
```

---

## Browser Storage

### Cookies
- **Key:** `locale`
- **Values:** `de` | `en`
- **Max-Age:** 1 year (31536000 seconds)
- **Path:** `/`
- **SameSite:** `Lax`

### LocalStorage
- **Key:** `accessibility-settings`
- **Value:** JSON object
  ```json
  {
    "fontSize": 100,
    "highContrast": false,
    "reducedMotion": false,
    "focusIndicators": true
  }
  ```

---

## Testing Endpoints

### Visual Testing
1. Open `http://localhost:3000`
2. Look for floating accessibility button (bottom-right)
3. Look for language switcher in navbar (add to navbar first)

### Functional Testing
1. **Language Switch:** Click language dropdown → Select language → Page reloads
2. **Font Size:** Open A11y panel → Move slider → Text size changes
3. **High Contrast:** Open A11y panel → Toggle switch → Colors change
4. **Skip Link:** Press Tab key → "Skip to main content" appears

---

## File Sizes

- **de.json:** ~5.8 KB (192 translation keys)
- **en.json:** ~5.5 KB (192 translation keys)
- **AccessibilityPanel.tsx:** ~4.3 KB
- **use-accessibility.tsx:** ~3.2 KB
- **LanguageSwitcher.tsx:** ~1.9 KB
- **dropdown-menu.tsx:** ~7.4 KB
- **SkipLink.tsx:** ~0.5 KB

**Total Implementation Size:** ~50 KB (source code + translations)

---

## Dependencies Used

All dependencies were already installed:

```json
{
  "next-intl": "^3.26.2",
  "@radix-ui/react-slider": "^1.2.1",
  "@radix-ui/react-switch": "^1.1.2",
  "@radix-ui/react-popover": "^1.1.4",
  "@radix-ui/react-dropdown-menu": "^2.1.4",
  "@radix-ui/react-separator": "^1.1.1"
}
```

**No additional npm packages needed!**

---

## Quick Reference

### Import Paths

```tsx
// i18n
import { useTranslations } from 'next-intl'
import { useLocale } from 'next-intl'

// Accessibility
import { useAccessibility } from '@/hooks/use-accessibility'
import { AccessibilityProvider } from '@/hooks/use-accessibility'

// Components
import { LanguageSwitcher } from '@/components/shared/LanguageSwitcher'
import { AccessibilityPanel } from '@/components/shared/AccessibilityPanel'
import { SkipLink } from '@/components/shared/SkipLink'
```

### Usage Examples

```tsx
// Get translations
const t = useTranslations('namespace')
const text = t('key')

// Get current locale
const locale = useLocale() // 'de' | 'en'

// Get accessibility settings
const { fontSize, highContrast, reducedMotion, focusIndicators } = useAccessibility()

// Update accessibility settings
const { setFontSize, setHighContrast, resetToDefaults } = useAccessibility()
```

---

## Implementation Complete!

All i18n and accessibility features are now fully implemented and ready to use. Refer to the documentation files for detailed usage instructions and testing guidelines.
