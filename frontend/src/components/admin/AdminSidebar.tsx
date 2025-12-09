'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Building2,
  Key,
  Users,
  FileText,
  BarChart3,
  CreditCard,
  Settings,
  ArrowLeft,
  Shield,
  Sparkles,
  Server,
  DollarSign,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/admin',
    icon: LayoutDashboard,
  },
  {
    title: 'Mandanten',
    href: '/admin/tenants',
    icon: Building2,
  },
  {
    title: 'Lizenzen',
    href: '/admin/licenses',
    icon: Key,
  },
  {
    title: 'Benutzer',
    href: '/admin/users',
    icon: Users,
  },
  {
    title: 'Audit-Logs',
    href: '/admin/audit-logs',
    icon: FileText,
  },
  {
    title: 'Analytics',
    href: '/admin/analytics',
    icon: BarChart3,
  },
  {
    title: 'Abrechnung',
    href: '/admin/billing',
    icon: CreditCard,
  },
  {
    title: 'Privacy Shield',
    href: '/admin/privacy-test',
    icon: Shield,
  },
  {
    title: 'LLM Konfiguration',
    href: '/admin/llm-config',
    icon: Server,
  },
  {
    title: 'AI Playground',
    href: '/admin/playground',
    icon: Sparkles,
  },
  {
    title: 'Model Pricing',
    href: '/admin/pricing',
    icon: DollarSign,
  },
  {
    title: 'Einstellungen',
    href: '/admin/settings',
    icon: Settings,
  },
]

export function AdminSidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card">
      <div className="flex h-16 items-center border-b px-6">
        <h2 className="text-lg font-semibold">Admin Dashboard</h2>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link key={item.href} href={item.href}>
              <Button
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn(
                  'w-full justify-start',
                  isActive && 'bg-secondary'
                )}
              >
                <Icon className="mr-3 h-4 w-4" />
                {item.title}
              </Button>
            </Link>
          )
        })}
      </nav>

      <Separator />

      <div className="p-4">
        <Link href="/dashboard">
          <Button variant="outline" className="w-full justify-start">
            <ArrowLeft className="mr-3 h-4 w-4" />
            Zurück zu Benutzer-Dashboard
          </Button>
        </Link>
      </div>
    </div>
  )
}
