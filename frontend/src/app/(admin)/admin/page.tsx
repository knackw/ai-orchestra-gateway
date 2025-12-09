import { getAnalyticsStats } from '@/lib/actions/admin/analytics'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Building2, Key, DollarSign, Activity, Users, AlertCircle } from 'lucide-react'

export default async function AdminDashboardPage() {
  const stats = await getAnalyticsStats()

  const kpis = [
    {
      title: 'Mandanten gesamt',
      value: `${stats.active_tenants} / ${stats.total_tenants}`,
      description: 'Aktiv / Gesamt',
      icon: Building2,
      trend: stats.active_tenants > 0 ? '+12%' : null,
    },
    {
      title: 'Lizenzen gesamt',
      value: stats.total_licenses.toString(),
      description: 'Aktive Lizenzen',
      icon: Key,
      trend: null,
    },
    {
      title: 'Umsatz diesen Monat',
      value: `€${stats.total_revenue.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`,
      description: `MRR: €${stats.mrr.toLocaleString('de-DE')}`,
      icon: DollarSign,
      trend: stats.mrr > 0 ? '+8%' : null,
    },
    {
      title: 'API Aufrufe heute',
      value: stats.api_calls_today.toLocaleString('de-DE'),
      description: 'Anfragen',
      icon: Activity,
      trend: null,
    },
    {
      title: 'Aktive Benutzer',
      value: stats.active_users.toString(),
      description: 'Letzten 30 Tage',
      icon: Users,
      trend: stats.active_users > 0 ? '+5%' : null,
    },
    {
      title: 'Fehlerrate',
      value: `${stats.error_rate.toFixed(2)}%`,
      description: 'Heute',
      icon: AlertCircle,
      trend: stats.error_rate < 5 ? 'Gut' : 'Achtung',
    },
  ]

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Übersicht über alle System-Metriken und Aktivitäten
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {kpis.map((kpi) => {
          const Icon = kpi.icon
          return (
            <Card key={kpi.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{kpi.value}</div>
                <p className="text-xs text-muted-foreground">{kpi.description}</p>
                {kpi.trend && (
                  <p className="text-xs text-green-600 mt-1">{kpi.trend}</p>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Letzte Aktivitäten</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b pb-2">
              <div>
                <p className="font-medium">Neuer Mandant registriert</p>
                <p className="text-sm text-muted-foreground">Acme Corp - Starter Plan</p>
              </div>
              <span className="text-sm text-muted-foreground">vor 2 Stunden</span>
            </div>
            <div className="flex items-center justify-between border-b pb-2">
              <div>
                <p className="font-medium">Credits hinzugefügt</p>
                <p className="text-sm text-muted-foreground">TechStart GmbH - 10.000 Credits</p>
              </div>
              <span className="text-sm text-muted-foreground">vor 5 Stunden</span>
            </div>
            <div className="flex items-center justify-between border-b pb-2">
              <div>
                <p className="font-medium">Neue Lizenz erstellt</p>
                <p className="text-sm text-muted-foreground">Enterprise Plan</p>
              </div>
              <span className="text-sm text-muted-foreground">vor 1 Tag</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Benutzer eingeladen</p>
                <p className="text-sm text-muted-foreground">admin@example.com</p>
              </div>
              <span className="text-sm text-muted-foreground">vor 2 Tagen</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
