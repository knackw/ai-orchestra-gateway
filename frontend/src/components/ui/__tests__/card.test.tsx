import { describe, it, expect } from 'vitest'
import { render, screen } from '@/tests/utils'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '../card'

describe('Card Components', () => {
  describe('Card', () => {
    it('renders card with correct styles', () => {
      render(<Card data-testid="card">Card content</Card>)
      const card = screen.getByTestId('card')
      expect(card).toBeInTheDocument()
      expect(card).toHaveClass('rounded-lg', 'border', 'bg-card')
    })

    it('accepts custom className', () => {
      render(
        <Card className="custom-card" data-testid="card">
          Content
        </Card>
      )
      const card = screen.getByTestId('card')
      expect(card).toHaveClass('custom-card')
    })

    it('forwards ref correctly', () => {
      const ref = { current: null }
      render(
        <Card ref={ref as React.RefObject<HTMLDivElement>}>
          Content
        </Card>
      )
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })
  })

  describe('CardHeader', () => {
    it('renders with correct layout styles', () => {
      render(<CardHeader data-testid="header">Header content</CardHeader>)
      const header = screen.getByTestId('header')
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6')
    })
  })

  describe('CardTitle', () => {
    it('renders title with correct typography', () => {
      render(<CardTitle data-testid="title">Card Title</CardTitle>)
      const title = screen.getByTestId('title')
      expect(title).toHaveTextContent('Card Title')
      expect(title).toHaveClass('text-2xl', 'font-semibold')
    })
  })

  describe('CardDescription', () => {
    it('renders description with muted styling', () => {
      render(
        <CardDescription data-testid="description">
          Card description text
        </CardDescription>
      )
      const description = screen.getByTestId('description')
      expect(description).toHaveTextContent('Card description text')
      expect(description).toHaveClass('text-sm', 'text-muted-foreground')
    })
  })

  describe('CardContent', () => {
    it('renders content area with padding', () => {
      render(<CardContent data-testid="content">Main content</CardContent>)
      const content = screen.getByTestId('content')
      expect(content).toHaveClass('p-6', 'pt-0')
    })
  })

  describe('CardFooter', () => {
    it('renders footer with flex layout', () => {
      render(<CardFooter data-testid="footer">Footer buttons</CardFooter>)
      const footer = screen.getByTestId('footer')
      expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'pt-0')
    })
  })

  describe('Full Card Composition', () => {
    it('renders complete card with all sections', () => {
      render(
        <Card data-testid="full-card">
          <CardHeader>
            <CardTitle>Feature Card</CardTitle>
            <CardDescription>This is a feature description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Main content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Action</button>
          </CardFooter>
        </Card>
      )

      const card = screen.getByTestId('full-card')
      expect(card).toBeInTheDocument()

      expect(screen.getByText('Feature Card')).toBeInTheDocument()
      expect(screen.getByText('This is a feature description')).toBeInTheDocument()
      expect(screen.getByText('Main content goes here')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument()
    })

    it('maintains proper semantic structure', () => {
      const { container } = render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
          </CardHeader>
          <CardContent>Content</CardContent>
        </Card>
      )

      const divs = container.querySelectorAll('div')
      expect(divs.length).toBeGreaterThan(0)
    })
  })

  describe('Accessibility', () => {
    it('supports ARIA attributes', () => {
      render(
        <Card
          role="article"
          aria-label="Feature card"
          data-testid="card"
        >
          <CardHeader>
            <CardTitle>Accessible Card</CardTitle>
          </CardHeader>
        </Card>
      )

      const card = screen.getByTestId('card')
      expect(card).toHaveAttribute('role', 'article')
      expect(card).toHaveAttribute('aria-label', 'Feature card')
    })
  })
})
