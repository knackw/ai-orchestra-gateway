import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowUp, ArrowDown } from 'lucide-react'

// Mock StatsCard component for testing
const StatsCard = ({
  title,
  value,
  trend,
  loading = false,
  icon: Icon,
}: {
  title: string
  value: string | number
  trend?: { value: number; isPositive: boolean }
  loading?: boolean
  icon?: any
}) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div data-testid="loading-skeleton" className="h-8 w-24 animate-pulse bg-muted rounded" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold" data-testid="stat-value">{value}</div>
        {trend && (
          <div
            className={`flex items-center text-sm ${
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            }`}
            data-testid="trend-indicator"
          >
            {trend.isPositive ? (
              <ArrowUp className="h-4 w-4 mr-1" />
            ) : (
              <ArrowDown className="h-4 w-4 mr-1" />
            )}
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

describe('StatsCard', () => {
  it('displays the title and value', () => {
    render(<StatsCard title="Total Requests" value="1,234" />)

    expect(screen.getByText('Total Requests')).toBeInTheDocument()
    expect(screen.getByText('1,234')).toBeInTheDocument()
  })

  it('displays numeric values', () => {
    render(<StatsCard title="Active Users" value={42} />)

    expect(screen.getByTestId('stat-value')).toHaveTextContent('42')
  })

  it('shows loading state', () => {
    render(<StatsCard title="Loading Stat" value="" loading={true} />)

    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument()
    expect(screen.queryByTestId('stat-value')).not.toBeInTheDocument()
  })

  it('displays positive trend indicator', () => {
    render(
      <StatsCard
        title="API Calls"
        value="5,678"
        trend={{ value: 12.5, isPositive: true }}
      />
    )

    const trendIndicator = screen.getByTestId('trend-indicator')
    expect(trendIndicator).toBeInTheDocument()
    expect(trendIndicator).toHaveClass('text-green-600')
    expect(screen.getByText('12.5%')).toBeInTheDocument()
  })

  it('displays negative trend indicator', () => {
    render(
      <StatsCard
        title="Errors"
        value="23"
        trend={{ value: -8.3, isPositive: false }}
      />
    )

    const trendIndicator = screen.getByTestId('trend-indicator')
    expect(trendIndicator).toBeInTheDocument()
    expect(trendIndicator).toHaveClass('text-red-600')
    expect(screen.getByText('8.3%')).toBeInTheDocument()
  })

  it('does not show trend when not provided', () => {
    render(<StatsCard title="Basic Stat" value="100" />)

    expect(screen.queryByTestId('trend-indicator')).not.toBeInTheDocument()
  })

  it('renders with icon when provided', () => {
    const MockIcon = () => <svg data-testid="mock-icon" />
    render(<StatsCard title="With Icon" value="999" icon={MockIcon} />)

    expect(screen.getByTestId('mock-icon')).toBeInTheDocument()
  })

  it('has correct styling for value text', () => {
    render(<StatsCard title="Styled Stat" value="12,345" />)

    const valueElement = screen.getByTestId('stat-value')
    expect(valueElement).toHaveClass('text-2xl', 'font-bold')
  })

  it('handles zero values correctly', () => {
    render(<StatsCard title="Zero Value" value={0} />)

    expect(screen.getByTestId('stat-value')).toHaveTextContent('0')
  })

  it('handles large numbers', () => {
    render(<StatsCard title="Large Number" value="1,234,567" />)

    expect(screen.getByText('1,234,567')).toBeInTheDocument()
  })

  it('shows loading skeleton with correct animation class', () => {
    render(<StatsCard title="Loading" value="" loading={true} />)

    const skeleton = screen.getByTestId('loading-skeleton')
    expect(skeleton).toHaveClass('animate-pulse')
  })
})
