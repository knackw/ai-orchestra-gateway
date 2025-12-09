import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/utils'
import userEvent from '@testing-library/user-event'
import { Button } from '../button'

describe('Button Component', () => {
  it('renders with default variant and size', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass('bg-primary')
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Button variant="destructive">Delete</Button>)
    let button = screen.getByRole('button', { name: /delete/i })
    expect(button).toHaveClass('bg-destructive')

    rerender(<Button variant="outline">Outline</Button>)
    button = screen.getByRole('button', { name: /outline/i })
    expect(button).toHaveClass('border')

    rerender(<Button variant="secondary">Secondary</Button>)
    button = screen.getByRole('button', { name: /secondary/i })
    expect(button).toHaveClass('bg-secondary')

    rerender(<Button variant="ghost">Ghost</Button>)
    button = screen.getByRole('button', { name: /ghost/i })
    expect(button).toHaveClass('hover:bg-accent')

    rerender(<Button variant="link">Link</Button>)
    button = screen.getByRole('button', { name: /link/i })
    expect(button).toHaveClass('underline-offset-4')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    let button = screen.getByRole('button', { name: /small/i })
    expect(button).toHaveClass('h-9')

    rerender(<Button size="lg">Large</Button>)
    button = screen.getByRole('button', { name: /large/i })
    expect(button).toHaveClass('h-11')

    rerender(<Button size="icon">Icon</Button>)
    button = screen.getByRole('button', { name: /icon/i })
    expect(button).toHaveClass('h-10', 'w-10')
  })

  it('handles click events', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button onClick={handleClick}>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })

    await user.click(button)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is passed', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button disabled onClick={handleClick}>Disabled</Button>)
    const button = screen.getByRole('button', { name: /disabled/i })

    expect(button).toBeDisabled()
    expect(button).toHaveClass('disabled:opacity-50')

    await user.click(button)
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('accepts custom className', () => {
    render(<Button className="custom-class">Custom</Button>)
    const button = screen.getByRole('button', { name: /custom/i })
    expect(button).toHaveClass('custom-class')
  })

  it('renders as child component when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    )
    const link = screen.getByRole('link', { name: /link button/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/test')
  })

  it('supports different HTML button types', () => {
    render(<Button type="submit">Submit</Button>)
    const button = screen.getByRole('button', { name: /submit/i })
    expect(button).toHaveAttribute('type', 'submit')
  })

  it('has proper accessibility attributes', () => {
    render(
      <Button aria-label="Close dialog" aria-pressed="false">
        X
      </Button>
    )
    const button = screen.getByRole('button', { name: /close dialog/i })
    expect(button).toHaveAttribute('aria-label', 'Close dialog')
    expect(button).toHaveAttribute('aria-pressed', 'false')
  })

  it('supports keyboard navigation', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button onClick={handleClick}>Press me</Button>)
    const button = screen.getByRole('button', { name: /press me/i })

    button.focus()
    expect(button).toHaveFocus()

    await user.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalledTimes(1)

    await user.keyboard(' ')
    expect(handleClick).toHaveBeenCalledTimes(2)
  })
})
