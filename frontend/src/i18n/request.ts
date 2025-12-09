import { getRequestConfig } from 'next-intl/server'
import { cookies, headers } from 'next/headers'

export default getRequestConfig(async () => {
  const cookieStore = await cookies()
  const headersList = await headers()

  // Check cookie first, then Accept-Language header
  let locale = cookieStore.get('locale')?.value

  if (!locale) {
    const acceptLanguage = headersList.get('accept-language')
    locale = acceptLanguage?.startsWith('de') ? 'de' : 'en'
  }

  // Fallback to German
  if (!['de', 'en'].includes(locale)) {
    locale = 'de'
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default
  }
})
