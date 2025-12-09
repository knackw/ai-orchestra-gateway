import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/utils'
import userEvent from '@testing-library/user-event'
import { LoginForm } from '../LoginForm'
import * as auth from '@/lib/auth'

// Mock the auth module
vi.mock('@/lib/auth', () => ({
  signIn: vi.fn(),
  signInWithOAuth: vi.fn(),
}))

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}))

describe('LoginForm Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all form elements', () => {
    render(<LoginForm />)

    // OAuth buttons
    expect(screen.getByRole('button', { name: /mit google anmelden/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /mit github anmelden/i })).toBeInTheDocument()

    // Email/Password form
    expect(screen.getByLabelText(/e-mail/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/passwort/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^anmelden$/i })).toBeInTheDocument()

    // Links
    expect(screen.getByRole('link', { name: /passwort vergessen/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /jetzt registrieren/i })).toBeInTheDocument()
  })

  it('has correct link destinations', () => {
    render(<LoginForm />)

    const forgotPasswordLink = screen.getByRole('link', { name: /passwort vergessen/i })
    expect(forgotPasswordLink).toHaveAttribute('href', '/reset-password')

    const signupLink = screen.getByRole('link', { name: /jetzt registrieren/i })
    expect(signupLink).toHaveAttribute('href', '/signup')
  })

  it('toggles password visibility', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    const passwordInput = screen.getByLabelText(/passwort/i) as HTMLInputElement
    expect(passwordInput.type).toBe('password')

    // Find and click the eye icon button
    const toggleButton = passwordInput.parentElement?.querySelector('button')
    expect(toggleButton).toBeInTheDocument()

    if (toggleButton) {
      await user.click(toggleButton)
      expect(passwordInput.type).toBe('text')

      await user.click(toggleButton)
      expect(passwordInput.type).toBe('password')
    }
  })

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    const submitButton = screen.getByRole('button', { name: /^anmelden$/i })
    await user.click(submitButton)

    await waitFor(() => {
      const errors = screen.getAllByText(/erforderlich|required/i)
      expect(errors.length).toBeGreaterThan(0)
    })
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/e-mail/i)
    await user.type(emailInput, 'invalid-email')

    const submitButton = screen.getByRole('button', { name: /^anmelden$/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/gültige e-mail|valid email/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid credentials', async () => {
    const user = userEvent.setup()
    const mockSignIn = vi.mocked(auth.signIn)
    mockSignIn.mockResolvedValueOnce(undefined)

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/passwort/i)
    const submitButton = screen.getByRole('button', { name: /^anmelden$/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith('test@example.com', 'password123')
    })
  })

  it('handles OAuth sign in for Google', async () => {
    const user = userEvent.setup()
    const mockSignInWithOAuth = vi.mocked(auth.signInWithOAuth)
    mockSignInWithOAuth.mockResolvedValueOnce(undefined)

    render(<LoginForm />)

    const googleButton = screen.getByRole('button', { name: /mit google anmelden/i })
    await user.click(googleButton)

    await waitFor(() => {
      expect(mockSignInWithOAuth).toHaveBeenCalledWith('google')
    })
  })

  it('handles OAuth sign in for GitHub', async () => {
    const user = userEvent.setup()
    const mockSignInWithOAuth = vi.mocked(auth.signInWithOAuth)
    mockSignInWithOAuth.mockResolvedValueOnce(undefined)

    render(<LoginForm />)

    const githubButton = screen.getByRole('button', { name: /mit github anmelden/i })
    await user.click(githubButton)

    await waitFor(() => {
      expect(mockSignInWithOAuth).toHaveBeenCalledWith('github')
    })
  })

  it('disables all buttons during submission', async () => {
    const user = userEvent.setup()
    const mockSignIn = vi.mocked(auth.signIn)
    // Create a promise that we can control
    let resolveSignIn: () => void
    mockSignIn.mockImplementation(() => new Promise(resolve => {
      resolveSignIn = resolve as () => void
    }))

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/passwort/i)
    const submitButton = screen.getByRole('button', { name: /^anmelden$/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    // Check that all buttons are disabled during loading
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /wird angemeldet/i })).toBeDisabled()
      expect(screen.getByRole('button', { name: /mit google anmelden/i })).toBeDisabled()
      expect(screen.getByRole('button', { name: /mit github anmelden/i })).toBeDisabled()
    })

    // Resolve the promise
    resolveSignIn!()
  })

  it('shows loading spinner during submission', async () => {
    const user = userEvent.setup()
    const mockSignIn = vi.mocked(auth.signIn)
    mockSignIn.mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/passwort/i)
    const submitButton = screen.getByRole('button', { name: /^anmelden$/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/wird angemeldet/i)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper labels for form inputs', () => {
      render(<LoginForm />)

      const emailInput = screen.getByLabelText(/e-mail/i)
      const passwordInput = screen.getByLabelText(/passwort/i)

      expect(emailInput).toHaveAttribute('id', 'email')
      expect(passwordInput).toHaveAttribute('id', 'password')
    })

    it('has autocomplete attributes', () => {
      render(<LoginForm />)

      const emailInput = screen.getByLabelText(/e-mail/i)
      const passwordInput = screen.getByLabelText(/passwort/i)

      expect(emailInput).toHaveAttribute('autocomplete', 'email')
      expect(passwordInput).toHaveAttribute('autocomplete', 'current-password')
    })

    it('password toggle button is accessible', () => {
      render(<LoginForm />)

      const passwordInput = screen.getByLabelText(/passwort/i)
      const toggleButton = passwordInput.parentElement?.querySelector('button')

      expect(toggleButton).toHaveAttribute('type', 'button')
    })
  })
})
