'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import {
  CreditCard,
  TrendingUp,
  Activity,
  Zap,
  AlertCircle,
  Plus,
  Key,
  BookOpen,
  ArrowRight,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'
import api from '@/lib/api'

// Mock data - will be replaced with API calls
const usageData = [
  { date: '12/01', requests: 120 },
  { date: '12/02', requests: 150 },
  { date: '12/03', requests: 180 },
  { date: '12/04', requests: 140 },
  { date: '12/05', requests: 200 },
  { date: '12/06', requests: 170 },
  { date: '12/07', requests: 190 },
]

const recentActivity = [
  {
    id: '1',
    endpoint: '/v1/generate',
    model: 'claude-opus-4-5',
    tokens: 1250,
    status: 'success' as const,
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
  {
    id: '2',
    endpoint: '/v1/generate',
    model: 'claude-sonnet-4-5',
    tokens: 850,
    status: 'success' as const,
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
  },
  {
    id: '3',
    endpoint: '/v1/generate',
    model: 'claude-opus-4-5',
    tokens: 2100,
    status: 'success' as const,
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: '4',
    endpoint: '/v1/generate',
    model: 'claude-sonnet-4-5',
    tokens: 450,
    status: 'error' as const,
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
  },
  {
    id: '5',
    endpoint: '/v1/generate',
    model: 'claude-opus-4-5',
    tokens: 1800,
    status: 'success' as const,
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  },
]

interface StatCardProps {
  title: string
  value: string | number
  description: string
  icon: React.ReactNode
  trend?: {
    value: string
    positive: boolean
  }
}

function StatCard({ title, value, description, icon, trend }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
        {trend && (
          <div className="flex items-center pt-1">
            <TrendingUp
              className={`mr-1 h-4 w-4 ${
                trend.positive ? 'text-green-600' : 'text-red-600'
              }`}
            />
            <span
              className={`text-xs font-medium ${
                trend.positive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend.value}
            </span>
            <span className="text-xs text-muted-foreground ml-1">
              from last month
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // In production, uncomment this to use real API:
        // const data = await api.getDashboardStats()
        // setDashboardData(data)

        // Simulate loading
        setTimeout(() => setLoading(false), 500)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here&apos;s your overview.
          </p>
        </div>

        <Skeleton className="h-48" />

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>

        <Skeleton className="h-96" />
        <Skeleton className="h-80" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here&apos;s your overview.
          </p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here&apos;s your overview.
          </p>
        </div>
        <Button asChild>
          <Link href="/billing">
            <Plus className="mr-2 h-4 w-4" />
            Add Credits
          </Link>
        </Button>
      </div>

      {/* Credit Balance Card */}
      <Card className="border-primary">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Credit Balance</CardTitle>
              <CardDescription>Your available credits</CardDescription>
            </div>
            <CreditCard className="h-8 w-8 text-primary" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">12,450</div>
          <p className="text-sm text-muted-foreground mt-1">
            Estimated to last ~15 days at current usage
          </p>
          <div className="mt-4">
            <Button>Top Up Credits</Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Requests"
          value="1,234"
          description="This month"
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          trend={{ value: '+12.5%', positive: true }}
        />
        <StatCard
          title="Avg Tokens/Request"
          value="1,250"
          description="Across all models"
          icon={<Zap className="h-4 w-4 text-muted-foreground" />}
          trend={{ value: '+5.2%', positive: true }}
        />
        <StatCard
          title="Error Rate"
          value="0.5%"
          description="Last 30 days"
          icon={<AlertCircle className="h-4 w-4 text-muted-foreground" />}
          trend={{ value: '-0.2%', positive: true }}
        />
        <StatCard
          title="Credits Used"
          value="8,567"
          description="This month"
          icon={<CreditCard className="h-4 w-4 text-muted-foreground" />}
          trend={{ value: '+18.3%', positive: false }}
        />
      </div>

      {/* Usage Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Usage Overview</CardTitle>
          <CardDescription>Requests over the last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={usageData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="requests"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Quick Actions & Recent Activity */}
      <div className="grid gap-6 md:grid-cols-7">
        {/* Quick Actions */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild variant="outline" className="w-full justify-start">
              <Link href="/api-keys">
                <Key className="mr-2 h-4 w-4" />
                Create API Key
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start">
              <Link href="/analytics">
                <Activity className="mr-2 h-4 w-4" />
                View Analytics
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start">
              <Link href="/docs" target="_blank" rel="noopener noreferrer">
                <BookOpen className="mr-2 h-4 w-4" />
                API Documentation
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start">
              <Link href="/billing">
                <CreditCard className="mr-2 h-4 w-4" />
                Manage Billing
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="md:col-span-5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Your last 5 API calls</CardDescription>
              </div>
              <Button asChild variant="ghost" size="sm">
                <Link href="/analytics">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Endpoint</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Tokens</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentActivity.map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell className="font-mono text-sm">
                      {activity.endpoint}
                    </TableCell>
                    <TableCell>{activity.model}</TableCell>
                    <TableCell>{activity.tokens.toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          activity.status === 'success' ? 'default' : 'destructive'
                        }
                      >
                        {activity.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDistanceToNow(new Date(activity.timestamp), {
                        addSuffix: true,
                      })}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
