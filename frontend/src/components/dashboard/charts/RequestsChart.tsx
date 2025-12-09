'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface RequestsChartProps {
  data: Array<{
    date: string
    requests: number
    successful?: number
    failed?: number
  }>
}

export function RequestsChart({ data }: RequestsChartProps) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="date"
          className="text-xs"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <YAxis
          className="text-xs"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="requests"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          name="Total Requests"
          dot={{ fill: 'hsl(var(--primary))' }}
        />
        {data.some((d) => d.successful !== undefined) && (
          <Line
            type="monotone"
            dataKey="successful"
            stroke="hsl(var(--success))"
            strokeWidth={2}
            name="Successful"
            dot={{ fill: 'hsl(var(--success))' }}
          />
        )}
        {data.some((d) => d.failed !== undefined) && (
          <Line
            type="monotone"
            dataKey="failed"
            stroke="hsl(var(--destructive))"
            strokeWidth={2}
            name="Failed"
            dot={{ fill: 'hsl(var(--destructive))' }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  )
}
