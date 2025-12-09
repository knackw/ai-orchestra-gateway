'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Download, Calendar, TrendingUp, TrendingDown } from 'lucide-react'
import { RequestsChart } from '@/components/dashboard/charts/RequestsChart'
import { TokensChart } from '@/components/dashboard/charts/TokensChart'
import { CreditsChart } from '@/components/dashboard/charts/CreditsChart'
import { ProviderPieChart } from '@/components/dashboard/charts/ProviderPieChart'
import { RequestLogsTable, type RequestLog } from '@/components/dashboard/RequestLogsTable'
import { Badge } from '@/components/ui/badge'

// Mock data - TODO: Replace with actual API calls
const mockRequestsData = [
  { date: '12/01', requests: 120, successful: 118, failed: 2 },
  { date: '12/02', requests: 150, successful: 148, failed: 2 },
  { date: '12/03', requests: 180, successful: 175, failed: 5 },
  { date: '12/04', requests: 140, successful: 138, failed: 2 },
  { date: '12/05', requests: 200, successful: 196, failed: 4 },
  { date: '12/06', requests: 170, successful: 168, failed: 2 },
  { date: '12/07', requests: 190, successful: 187, failed: 3 },
]

const mockTokensData = [
  { date: '12/01', tokens: 125000, inputTokens: 50000, outputTokens: 75000 },
  { date: '12/02', tokens: 160000, inputTokens: 65000, outputTokens: 95000 },
  { date: '12/03', tokens: 185000, inputTokens: 75000, outputTokens: 110000 },
  { date: '12/04', tokens: 145000, inputTokens: 58000, outputTokens: 87000 },
  { date: '12/05', tokens: 210000, inputTokens: 85000, outputTokens: 125000 },
  { date: '12/06', tokens: 175000, inputTokens: 70000, outputTokens: 105000 },
  { date: '12/07', tokens: 195000, inputTokens: 78000, outputTokens: 117000 },
]

const mockCreditsData = [
  { date: '12/01', credits: 1250 },
  { date: '12/02', credits: 1600 },
  { date: '12/03', credits: 1850 },
  { date: '12/04', credits: 1450 },
  { date: '12/05', credits: 2100 },
  { date: '12/06', credits: 1750 },
  { date: '12/07', credits: 1950 },
]

const mockProviderData = [
  { name: 'Claude Opus 4.5', value: 450, color: 'hsl(var(--chart-1))' },
  { name: 'Claude Sonnet 4.5', value: 320, color: 'hsl(var(--chart-2))' },
  { name: 'Claude Haiku 3.5', value: 180, color: 'hsl(var(--chart-3))' },
  { name: 'Scaleway AI', value: 120, color: 'hsl(var(--chart-4))' },
]

const mockRequestLogs: RequestLog[] = [
  {
    id: '1',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    endpoint: '/v1/generate',
    method: 'POST',
    model: 'claude-opus-4-5',
    tokens: 1250,
    credits: 125,
    status: 'success',
    responseTime: 1.24,
    statusCode: 200,
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    endpoint: '/v1/generate',
    method: 'POST',
    model: 'claude-sonnet-4-5',
    tokens: 850,
    credits: 65,
    status: 'success',
    responseTime: 0.89,
    statusCode: 200,
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    endpoint: '/v1/generate',
    method: 'POST',
    model: 'claude-opus-4-5',
    tokens: 2100,
    credits: 210,
    status: 'success',
    responseTime: 2.15,
    statusCode: 200,
  },
  {
    id: '4',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    endpoint: '/v1/generate',
    method: 'POST',
    model: 'claude-sonnet-4-5',
    tokens: 450,
    credits: 0,
    status: 'error',
    responseTime: 0.32,
    statusCode: 429,
  },
  {
    id: '5',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    endpoint: '/v1/generate',
    method: 'POST',
    model: 'claude-opus-4-5',
    tokens: 1800,
    credits: 180,
    status: 'success',
    responseTime: 1.67,
    statusCode: 200,
  },
]

const topModels = [
  { name: 'claude-opus-4-5', requests: 450, percentage: 42 },
  { name: 'claude-sonnet-4-5', requests: 320, percentage: 30 },
  { name: 'claude-haiku-3-5', requests: 180, percentage: 17 },
  { name: 'scaleway-llama-3', requests: 120, percentage: 11 },
]

interface SummaryCardProps {
  title: string
  value: string | number
  description: string
  trend?: {
    value: string
    positive: boolean
  }
}

function SummaryCard({ title, value, description, trend }: SummaryCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
        {trend && (
          <div className="flex items-center pt-2">
            {trend.positive ? (
              <TrendingUp className="mr-1 h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="mr-1 h-4 w-4 text-red-600" />
            )}
            <span
              className={`text-xs font-medium ${
                trend.positive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend.value}
            </span>
            <span className="text-xs text-muted-foreground ml-1">
              vs last period
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState('7d')
  const [selectedApiKey, setSelectedApiKey] = useState('all')

  useEffect(() => {
    // TODO: Fetch from API based on dateRange and selectedApiKey
    setTimeout(() => setLoading(false), 500)
  }, [dateRange, selectedApiKey])

  const handleExportCsv = () => {
    // TODO: Implement CSV export
    const csvContent = `Timestamp,Endpoint,Model,Tokens,Credits,Status,Response Time\n${mockRequestLogs
      .map(
        (log) =>
          `${log.timestamp},${log.endpoint},${log.model},${log.tokens},${log.credits},${log.status},${log.responseTime}`
      )
      .join('\n')}`

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `usage-analytics-${dateRange}-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-48" />
          <div className="flex gap-2">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-96" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Usage & Analytics</h1>
          <p className="text-muted-foreground">
            Detailed insights into your API usage and performance metrics
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-[140px]">
              <Calendar className="mr-2 h-4 w-4" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="custom">Custom range</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedApiKey} onValueChange={setSelectedApiKey}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All API Keys" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All API Keys</SelectItem>
              <SelectItem value="prod">Production Key</SelectItem>
              <SelectItem value="dev">Development Key</SelectItem>
              <SelectItem value="test">Testing Key</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" onClick={handleExportCsv}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          title="Total API Calls"
          value="1,150"
          description="In selected period"
          trend={{ value: '+12.5%', positive: true }}
        />
        <SummaryCard
          title="Total Tokens"
          value="1.24M"
          description="Input + Output tokens"
          trend={{ value: '+8.3%', positive: true }}
        />
        <SummaryCard
          title="Credits Consumed"
          value="12,450"
          description="Total credits spent"
          trend={{ value: '+15.2%', positive: false }}
        />
        <SummaryCard
          title="Avg Response Time"
          value="1.2s"
          description="Across all requests"
          trend={{ value: '-5.1%', positive: true }}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Requests Chart */}
        <Card>
          <CardHeader>
            <CardTitle>API Calls Over Time</CardTitle>
            <CardDescription>
              Total, successful, and failed requests over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RequestsChart data={mockRequestsData} />
          </CardContent>
        </Card>

        {/* Tokens Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Tokens Used</CardTitle>
            <CardDescription>
              Input and output tokens consumed daily
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TokensChart data={mockTokensData} />
          </CardContent>
        </Card>

        {/* Credits Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Credits Consumed</CardTitle>
            <CardDescription>
              Daily credit consumption over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CreditsChart data={mockCreditsData} />
          </CardContent>
        </Card>

        {/* Provider Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Provider Breakdown</CardTitle>
            <CardDescription>
              Requests by AI provider and model (pie chart)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ProviderPieChart data={mockProviderData} />
          </CardContent>
        </Card>
      </div>

      {/* Top Models Used */}
      <Card>
        <CardHeader>
          <CardTitle>Top Models Used</CardTitle>
          <CardDescription>
            Most frequently requested AI models in the selected period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topModels.map((model, index) => (
              <div key={model.name} className="flex items-center gap-4">
                <div className="flex-shrink-0 w-8 text-center font-semibold text-muted-foreground">
                  #{index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{model.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">
                        {model.requests.toLocaleString()} requests
                      </span>
                      <Badge variant="secondary">{model.percentage}%</Badge>
                    </div>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${model.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Response Time Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Response Time Metrics</CardTitle>
          <CardDescription>
            Performance statistics for your API requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Average</p>
              <p className="text-2xl font-bold">1.24s</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Median</p>
              <p className="text-2xl font-bold">1.15s</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">P95</p>
              <p className="text-2xl font-bold">2.48s</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">P99</p>
              <p className="text-2xl font-bold">3.12s</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Request Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Request Logs</CardTitle>
          <CardDescription>
            Detailed log of all API requests in the selected period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RequestLogsTable logs={mockRequestLogs} />
        </CardContent>
      </Card>
    </div>
  )
}
