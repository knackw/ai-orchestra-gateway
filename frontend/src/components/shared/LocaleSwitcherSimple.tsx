'use client'

import { useLocale } from 'next-intl'
import { useRouter } from 'next/navigation'

export function LocaleSwitcherSimple() {
  const locale = useLocale()
  const router = useRouter()

  const switchLocale = (newLocale: string) => {
    // Set cookie to persist locale preference
    document.cookie = `locale=${newLocale};path=/;max-age=31536000`

    // Refresh the page to apply new locale
    router.refresh()
  }

  return (
    <select
      value={locale}
      onChange={(e) => switchLocale(e.target.value)}
      className="px-3 py-1.5 rounded-md border border-input bg-background text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    >
      <option value="de">Deutsch</option>
      <option value="en">English</option>
    </select>
  )
}
