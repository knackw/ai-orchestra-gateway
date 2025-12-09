import { AuthLayout } from '@/components/auth/AuthLayout'
import { LoginForm } from '@/components/auth/LoginForm'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Anmelden | AI Legal Ops',
  description: 'Melden Sie sich bei Ihrem AI Legal Ops Konto an.',
}

export default function LoginPage() {
  return (
    <AuthLayout
      title="Willkommen zurück"
      subtitle="Melden Sie sich an, um fortzufahren"
    >
      <LoginForm />
    </AuthLayout>
  )
}
