import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/utils'
import { Hero } from '../Hero'

describe('Hero Component', () => {
  beforeEach(() => {
    // Reset any timers or state between tests
    vi.clearAllTimers()
  })

  it('renders main headline', () => {
    render(<Hero />)
    const headline = screen.getByRole('heading', { level: 1 })
    expect(headline).toBeInTheDocument()
    expect(headline).toHaveTextContent(/AI Gateway mit/i)
    expect(headline).toHaveTextContent(/Datenschutz-Garantie/i)
  })

  it('renders subheadline with value proposition', () => {
    render(<Hero />)
    expect(screen.getByText(/Multi-Tenant AI-Proxy mit automatischer PII-Erkennung/i)).toBeInTheDocument()

    // Use getAllByText since 'DSGVO-konform' appears multiple times (subheadline + trust badge)
    const dsgvoElements = screen.getAllByText(/DSGVO-konform/i)
    expect(dsgvoElements.length).toBeGreaterThan(0)
  })

  it('displays version badge', () => {
    render(<Hero />)
    expect(screen.getByText(/v2\.0 jetzt verfügbar/i)).toBeInTheDocument()
  })

  it('renders CTA buttons with correct links', () => {
    render(<Hero />)

    const signupButton = screen.getByRole('link', { name: /kostenlos starten/i })
    expect(signupButton).toBeInTheDocument()
    expect(signupButton).toHaveAttribute('href', '/signup')

    const demoButton = screen.getByRole('link', { name: /live demo/i })
    expect(demoButton).toBeInTheDocument()
    expect(demoButton).toHaveAttribute('href', '#features')
  })

  it('displays trust badges with icons', () => {
    render(<Hero />)

    // Use getAllByText since 'DSGVO-konform' appears multiple times (subheadline + trust badge)
    const dsgvoElements = screen.getAllByText('DSGVO-konform')
    expect(dsgvoElements.length).toBeGreaterThan(0)

    expect(screen.getByText('EU Hosting')).toBeInTheDocument()
    expect(screen.getByText('99.9% Uptime')).toBeInTheDocument()
  })

  it('has proper section structure', () => {
    const { container } = render(<Hero />)
    const section = container.querySelector('section')
    expect(section).toBeInTheDocument()
    expect(section).toHaveClass('relative', 'overflow-hidden')
  })

  it('includes background gradient elements', () => {
    const { container } = render(<Hero />)
    const gradients = container.querySelectorAll('.bg-gradient-to-br')
    expect(gradients.length).toBeGreaterThan(0)
  })

  it('applies fade-in animation on mount', async () => {
    render(<Hero />)

    // Check that animation classes are applied
    await waitFor(() => {
      const container = screen.getByRole('heading', { level: 1 }).closest('div')
      expect(container).toHaveClass('opacity-100')
    })
  })

  it('has accessible button text', () => {
    render(<Hero />)

    const signupButton = screen.getByRole('link', { name: /kostenlos starten/i })
    const demoButton = screen.getByRole('link', { name: /live demo/i })

    expect(signupButton).toBeVisible()
    expect(demoButton).toBeVisible()
  })

  it('renders all trust badge icons', () => {
    const { container } = render(<Hero />)
    const icons = container.querySelectorAll('svg')
    // Should have icons for: ArrowRight, Play, Shield, Server, Zap
    expect(icons.length).toBeGreaterThanOrEqual(5)
  })

  it('has proper responsive container', () => {
    const { container } = render(<Hero />)
    const containerDiv = container.querySelector('.container')
    expect(containerDiv).toBeInTheDocument()
  })

  it('displays pulsing status indicator', () => {
    const { container } = render(<Hero />)
    const pulsingDot = container.querySelector('.animate-ping')
    expect(pulsingDot).toBeInTheDocument()
    expect(pulsingDot).toHaveClass('bg-green-400')
  })

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      render(<Hero />)
      const h1 = screen.getByRole('heading', { level: 1 })
      expect(h1).toBeInTheDocument()
    })

    it('has semantic HTML structure', () => {
      const { container } = render(<Hero />)
      const section = container.querySelector('section')
      expect(section).toBeInTheDocument()
    })

    it('buttons are keyboard accessible', () => {
      render(<Hero />)
      const links = screen.getAllByRole('link')
      links.forEach(link => {
        expect(link).toBeVisible()
      })
    })
  })
})
