import { getAnalyticsStats, getTopTenants } from '@/lib/actions/admin/analytics'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DollarSign, TrendingUp, Users, Activity } from 'lucide-react'

export default async function AnalyticsPage() {
  const stats = await getAnalyticsStats()
  const topTenants = await getTopTenants(10)

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">Systemweite Analysen und Einblicke</p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gesamtumsatz</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">€{stats.total_revenue.toLocaleString('de-DE')}</div>
            <p className="text-xs text-muted-foreground">Lifetime</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">MRR</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">€{stats.mrr.toLocaleString('de-DE')}</div>
            <p className="text-xs text-muted-foreground">Monatlich wiederkehrende Einnahmen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aktive Mandanten</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active_tenants}</div>
            <p className="text-xs text-muted-foreground">von {stats.total_tenants} gesamt</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Abwanderungsrate</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.churn_rate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Letzten 30 Tage</p>
          </CardContent>
        </Card>
      </div>

      {/* Top Tenants */}
      <Card>
        <CardHeader>
          <CardTitle>Top 10 Mandanten nach Nutzung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topTenants.map((tenant, index) => (
              <div key={tenant.tenant_id} className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-muted-foreground w-6">#{index + 1}</span>
                  <span className="font-medium">{tenant.tenant_name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-muted-foreground">
                    {tenant.usage_count.toLocaleString('de-DE')} Anfragen
                  </span>
                  <span className="font-medium">
                    {tenant.credits_used.toLocaleString('de-DE')} Credits
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Placeholder for charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Umsatz über Zeit</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Chart-Komponente würde hier angezeigt werden</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>API-Aufrufe über Zeit</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Chart-Komponente würde hier angezeigt werden</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
