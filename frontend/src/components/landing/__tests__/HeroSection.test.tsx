import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { HeroSection } from '../HeroSection'

describe('HeroSection', () => {
  it('renders the main headline', () => {
    render(<HeroSection />)

    expect(screen.getByText(/KI-Power für Ihr Business/i)).toBeInTheDocument()
    expect(screen.getByText(/DSGVO-konform/i)).toBeInTheDocument()
  })

  it('renders the subheadline', () => {
    render(<HeroSection />)

    expect(screen.getByText(/Multi-Provider AI Gateway mit Privacy Shield/i)).toBeInTheDocument()
    expect(screen.getByText(/Sichere AI-Integration für europäische Unternehmen/i)).toBeInTheDocument()
  })

  it('renders CTA buttons', () => {
    render(<HeroSection />)

    const startButton = screen.getByRole('link', { name: /Kostenlos starten/i })
    const demoButton = screen.getByRole('link', { name: /Demo anfragen/i })

    expect(startButton).toBeInTheDocument()
    expect(demoButton).toBeInTheDocument()

    expect(startButton).toHaveAttribute('href', '/signup')
    expect(demoButton).toHaveAttribute('href', '/contact')
  })

  it('renders trust badges', () => {
    render(<HeroSection />)

    expect(screen.getByText('DSGVO-konform')).toBeInTheDocument()
    expect(screen.getByText('EU Hosting')).toBeInTheDocument()
    expect(screen.getByText('99.9% Uptime')).toBeInTheDocument()
  })

  it('renders the version badge', () => {
    render(<HeroSection />)

    expect(screen.getByText(/v2.0 jetzt verfügbar - Enterprise Ready/i)).toBeInTheDocument()
  })

  it('applies fade-in animation on mount', () => {
    const { container } = render(<HeroSection />)

    // Check for animation classes
    const mainContent = container.querySelector('.transition-all.duration-1000')
    expect(mainContent).toBeInTheDocument()
  })

  it('renders all icons in trust badges', () => {
    const { container } = render(<HeroSection />)

    // Trust badges have icons with specific classes
    const trustBadgeIcons = container.querySelectorAll('.h-10.w-10')
    expect(trustBadgeIcons.length).toBe(3)
  })

  it('has responsive layout classes', () => {
    const { container } = render(<HeroSection />)

    // Check for responsive padding classes
    const section = container.querySelector('section')
    expect(section).toBeInTheDocument()

    // Check for responsive text sizing on headline
    const headline = screen.getByText(/KI-Power für Ihr Business/i)
    expect(headline).toHaveClass('text-4xl', 'sm:text-5xl', 'md:text-6xl', 'lg:text-7xl')
  })

  it('renders background gradient elements', () => {
    const { container } = render(<HeroSection />)

    // Check for gradient background
    const gradients = container.querySelectorAll('.bg-gradient-to-br, .bg-gradient-to-r')
    expect(gradients.length).toBeGreaterThan(0)
  })

  it('has proper semantic HTML structure', () => {
    const { container } = render(<HeroSection />)

    // Should have a section element
    expect(container.querySelector('section')).toBeInTheDocument()

    // Should have h1
    const h1 = container.querySelector('h1')
    expect(h1).toBeInTheDocument()

    // Should have paragraph
    const p = container.querySelector('p')
    expect(p).toBeInTheDocument()
  })
})
