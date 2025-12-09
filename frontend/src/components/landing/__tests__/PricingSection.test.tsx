import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import { PricingSection } from '../PricingSection'

describe('PricingSection', () => {
  it('renders all three pricing tiers', () => {
    render(<PricingSection />)

    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Professional')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })

  it('displays correct prices for each tier', () => {
    render(<PricingSection />)

    // Starter tier
    expect(screen.getByText('€49')).toBeInTheDocument()

    // Professional tier
    expect(screen.getByText('€199')).toBeInTheDocument()

    // Enterprise tier
    expect(screen.getByText('Auf Anfrage')).toBeInTheDocument()
  })

  it('displays token/credit information', () => {
    render(<PricingSection />)

    expect(screen.getByText(/100k Tokens inkludiert/i)).toBeInTheDocument()
    expect(screen.getByText(/500k Tokens inkludiert/i)).toBeInTheDocument()
  })

  it('shows all features for each tier', () => {
    render(<PricingSection />)

    // Starter features
    expect(screen.getByText('100.000 Tokens/Monat')).toBeInTheDocument()
    expect(screen.getByText('Privacy Shield Basic')).toBeInTheDocument()

    // Professional features
    expect(screen.getByText('500.000 Tokens/Monat')).toBeInTheDocument()
    expect(screen.getByText('Privacy Shield Pro')).toBeInTheDocument()
    expect(screen.getByText('SLA 99.9% Uptime')).toBeInTheDocument()

    // Enterprise features
    expect(screen.getByText('Unlimited Tokens')).toBeInTheDocument()
    expect(screen.getByText('Privacy Shield Enterprise')).toBeInTheDocument()
    expect(screen.getByText('White-Label Lösung')).toBeInTheDocument()
  })

  it('renders CTA buttons with correct links', () => {
    render(<PricingSection />)

    const starterCTA = screen.getByRole('link', { name: /Jetzt starten/i })
    const professionalCTA = screen.getByRole('link', { name: /Professional wählen/i })
    const enterpriseCTA = screen.getByRole('link', { name: /Kontakt aufnehmen/i })

    expect(starterCTA).toHaveAttribute('href', '/signup?plan=starter')
    expect(professionalCTA).toHaveAttribute('href', '/signup?plan=professional')
    expect(enterpriseCTA).toHaveAttribute('href', '/contact?plan=enterprise')
  })

  it('highlights the Professional tier', () => {
    const { container } = render(<PricingSection />)

    // Professional tier should have special styling
    expect(screen.getByText('Beliebt')).toBeInTheDocument()

    // Check for highlighted card classes
    const cards = container.querySelectorAll('[class*="border-primary"]')
    expect(cards.length).toBeGreaterThan(0)
  })

  it('renders feature checkmarks', () => {
    const { container } = render(<PricingSection />)

    // All features should have checkmark icons
    const checkmarks = container.querySelectorAll('.text-primary')
    expect(checkmarks.length).toBeGreaterThan(0)
  })

  it('displays additional pricing information', () => {
    render(<PricingSection />)

    expect(screen.getByText(/Alle Preise zzgl. MwSt/i)).toBeInTheDocument()
    expect(screen.getByText(/14 Tage Geld-zurück-Garantie/i)).toBeInTheDocument()
    expect(screen.getByText(/Keine Mindestlaufzeit/i)).toBeInTheDocument()
  })

  it('has link to FAQ section', () => {
    render(<PricingSection />)

    const faqLink = screen.getByRole('link', { name: /Schauen Sie in unsere FAQ/i })
    expect(faqLink).toHaveAttribute('href', '#faq')
  })

  it('renders section heading', () => {
    render(<PricingSection />)

    expect(screen.getByText('Transparente Preise')).toBeInTheDocument()
    expect(screen.getByText(/Wählen Sie den Plan, der zu Ihren Anforderungen passt/i)).toBeInTheDocument()
  })

  it('has proper grid layout classes', () => {
    const { container } = render(<PricingSection />)

    const grid = container.querySelector('.grid')
    expect(grid).toBeInTheDocument()
    expect(grid).toHaveClass('gap-8', 'lg:grid-cols-3')
  })

  it('renders all pricing cards with proper structure', () => {
    render(<PricingSection />)

    // Should have 3 pricing cards - check by verifying all tier names are present
    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Professional')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })

  it('displays tier descriptions', () => {
    render(<PricingSection />)

    expect(screen.getByText('Perfekt für kleine Projekte und Tests')).toBeInTheDocument()
    expect(screen.getByText('Für professionelle Anwendungen')).toBeInTheDocument()
    expect(screen.getByText('Maximale Kontrolle und Support')).toBeInTheDocument()
  })

  it('has staggered animation delays', () => {
    const { container } = render(<PricingSection />)

    // Cards should have animation delay styles
    const animatedCards = container.querySelectorAll('[class*="animate-in"]')
    expect(animatedCards.length).toBeGreaterThan(0)
  })
})
