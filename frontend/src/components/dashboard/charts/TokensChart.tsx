'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface TokensChartProps {
  data: Array<{
    date: string
    tokens: number
    inputTokens?: number
    outputTokens?: number
  }>
}

export function TokensChart({ data }: TokensChartProps) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data}>
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
        {data.some((d) => d.inputTokens !== undefined && d.outputTokens !== undefined) ? (
          <>
            <Bar
              dataKey="inputTokens"
              stackId="a"
              fill="hsl(var(--chart-1))"
              name="Input Tokens"
            />
            <Bar
              dataKey="outputTokens"
              stackId="a"
              fill="hsl(var(--chart-2))"
              name="Output Tokens"
            />
          </>
        ) : (
          <Bar
            dataKey="tokens"
            fill="hsl(var(--primary))"
            name="Total Tokens"
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  )
}
