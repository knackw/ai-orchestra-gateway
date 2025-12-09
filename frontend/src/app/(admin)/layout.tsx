import { AdminLayout } from '@/components/admin/AdminLayout'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function Layout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  // Check admin role
  const { data: profile } = await supabase
    .from('users')
    .select('role')
    .eq('id', user.id)
    .single<{ role: string }>()

  if (!profile || !['admin', 'superadmin'].includes(profile.role)) {
    redirect('/dashboard')
  }

  return <AdminLayout>{children}</AdminLayout>
}
