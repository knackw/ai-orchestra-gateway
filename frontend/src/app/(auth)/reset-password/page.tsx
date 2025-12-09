import { AuthLayout } from '@/components/auth/AuthLayout'
import { ResetPasswordForm } from '@/components/auth/ResetPasswordForm'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Passwort zurücksetzen | AI Legal Ops',
  description: 'Setzen Sie Ihr neues Passwort.',
}

export default function ResetPasswordPage() {
  return (
    <AuthLayout
      title="Neues Passwort setzen"
      subtitle="Geben Sie Ihr neues Passwort ein"
    >
      <ResetPasswordForm />
    </AuthLayout>
  )
}
