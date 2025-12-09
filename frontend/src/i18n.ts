import { notFound } from 'next/navigation'
import { getRequestConfig } from 'next-intl/server'

// Supported locales
export const locales = ['de', 'en'] as const
export type Locale = (typeof locales)[number]

// Default locale
export const defaultLocale: Locale = 'de'

/**
 * next-intl configuration
 *
 * This configuration is used by next-intl to:
 * 1. Load the correct translation messages based on the locale
 * 2. Provide locale information to the application
 *
 * The locale is determined by:
 * 1. Cookie preference (set by LocaleSwitcher)
 * 2. Accept-Language header (browser preference)
 * 3. Default locale (de)
 */
export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as Locale)) {
    notFound()
  }

  return {
    messages: (await import(`../messages/${locale}.json`)).default,
  }
})
