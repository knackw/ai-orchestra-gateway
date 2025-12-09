import { AuthLayout } from '@/components/auth/AuthLayout'
import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Passwort vergessen | AI Legal Ops',
  description: 'Setzen Sie Ihr Passwort zurück.',
}

export default function ForgotPasswordPage() {
  return (
    <AuthLayout
      title="Passwort vergessen?"
      subtitle="Geben Sie Ihre E-Mail-Adresse ein, um einen Link zum Zurücksetzen zu erhalten"
    >
      <ForgotPasswordForm />
    </AuthLayout>
  )
}
