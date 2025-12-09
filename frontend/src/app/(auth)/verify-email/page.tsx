import { VerifyEmailCard } from '@/components/auth/VerifyEmailCard'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'E-Mail bestätigen | AI Legal Ops',
  description: 'Bestätigen Sie Ihre E-Mail-Adresse.',
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <VerifyEmailCard />
    </div>
  )
}
