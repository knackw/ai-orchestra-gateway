import { AuthLayout } from '@/components/auth/AuthLayout'
import { SignupForm } from '@/components/auth/SignupForm'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Registrieren | AI Legal Ops',
  description: 'Erstellen Sie ein AI Legal Ops Konto.',
}

export default function SignupPage() {
  return (
    <AuthLayout
      title="Konto erstellen"
      subtitle="Starten Sie mit AI Legal Ops"
    >
      <SignupForm />
    </AuthLayout>
  )
}
