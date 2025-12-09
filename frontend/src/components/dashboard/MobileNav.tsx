'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Key,
  BarChart3,
  CreditCard,
  Settings,
  HelpCircle,
  LogOut,
} from 'lucide-react'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'

interface MobileNavProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  external?: boolean
}

const mainNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'API Keys', href: '/api-keys', icon: Key },
  { label: 'Usage & Analytics', href: '/analytics', icon: BarChart3 },
  { label: 'Billing', href: '/billing', icon: CreditCard },
  { label: 'Settings', href: '/settings', icon: Settings },
]

const helpNavItems: NavItem[] = [
  { label: 'Help', href: '/help', icon: HelpCircle, external: true },
]

export function MobileNav({ open, onOpenChange }: MobileNavProps) {
  const pathname = usePathname()

  const NavLink = ({ item }: { item: NavItem }) => {
    const Icon = item.icon
    const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)

    return (
      <Link
        href={item.href}
        target={item.external ? '_blank' : undefined}
        rel={item.external ? 'noopener noreferrer' : undefined}
        onClick={() => onOpenChange(false)}
        className={cn(
          'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
          'hover:bg-accent hover:text-accent-foreground',
          isActive
            ? 'bg-accent text-accent-foreground'
            : 'text-muted-foreground'
        )}
      >
        <Icon className="h-5 w-5 flex-shrink-0" />
        <span>{item.label}</span>
      </Link>
    )
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-64 p-0">
        <div className="flex h-full flex-col">
          {/* Header */}
          <SheetHeader className="h-16 flex-row items-center border-b px-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded bg-primary text-primary-foreground font-bold text-sm">
                AO
              </div>
              <SheetTitle className="font-semibold text-lg">
                AI Orchestra
              </SheetTitle>
            </div>
          </SheetHeader>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 overflow-y-auto p-3">
            {mainNavItems.map((item) => (
              <NavLink key={item.href} item={item} />
            ))}

            <div className="my-3">
              <Separator />
            </div>

            {helpNavItems.map((item) => (
              <NavLink key={item.href} item={item} />
            ))}
          </nav>

          {/* User Info */}
          <div className="border-t p-3">
            <div className="flex items-center gap-3 rounded-lg px-2 py-2">
              <Avatar className="h-10 w-10">
                <AvatarImage src="/avatars/user.png" alt="User" />
                <AvatarFallback>U</AvatarFallback>
              </Avatar>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">John Doe</p>
                <p className="text-xs text-muted-foreground truncate">
                  john@example.com
                </p>
              </div>

              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 flex-shrink-0"
                onClick={() => {
                  // TODO: Implement logout
                }}
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
