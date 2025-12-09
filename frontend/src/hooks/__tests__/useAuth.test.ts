import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import * as auth from '@/lib/auth'

// Mock the auth module
vi.mock('@/lib/auth', () => ({
  signIn: vi.fn(),
  signUp: vi.fn(),
  signOut: vi.fn(),
  getSession: vi.fn(),
  getUser: vi.fn(),
  signInWithOAuth: vi.fn(),
}))

// Mock Supabase client
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(() => ({
    auth: {
      getSession: vi.fn(() => Promise.resolve({ data: { session: null }, error: null })),
      getUser: vi.fn(() => Promise.resolve({ data: { user: null }, error: null })),
      onAuthStateChange: vi.fn(() => ({
        data: { subscription: { unsubscribe: vi.fn() } },
      })),
    },
  })),
}))

// Custom hook for testing auth functionality
import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

function useAuth() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [session, setSession] = useState<any>(null)

  useEffect(() => {
    const supabase = createClient()

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const login = async (email: string, password: string) => {
    return auth.signIn(email, password)
  }

  const signup = async (email: string, password: string, metadata?: any) => {
    return auth.signUp(email, password, metadata)
  }

  const logout = async () => {
    return auth.signOut()
  }

  const loginWithOAuth = async (provider: 'google' | 'github') => {
    return auth.signInWithOAuth(provider)
  }

  return {
    user,
    session,
    loading,
    login,
    signup,
    logout,
    loginWithOAuth,
  }
}

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with loading state', () => {
    const { result } = renderHook(() => useAuth())

    expect(result.current.loading).toBe(true)
    expect(result.current.user).toBe(null)
    expect(result.current.session).toBe(null)
  })

  it('sets loading to false after initialization', async () => {
    const { result } = renderHook(() => useAuth())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
  })

  it('provides login function', async () => {
    const { result } = renderHook(() => useAuth())
    const mockSignIn = vi.mocked(auth.signIn)
    mockSignIn.mockResolvedValue({
      user: { id: '123', email: 'test@example.com' },
      session: { access_token: 'token' },
    } as any)

    await act(async () => {
      await result.current.login('test@example.com', 'password123')
    })

    expect(mockSignIn).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('provides signup function', async () => {
    const { result } = renderHook(() => useAuth())
    const mockSignUp = vi.mocked(auth.signUp)
    mockSignUp.mockResolvedValue({
      user: { id: '123', email: 'new@example.com' },
      session: null,
    } as any)

    await act(async () => {
      await result.current.signup('new@example.com', 'password123', { company: 'Test Co' })
    })

    expect(mockSignUp).toHaveBeenCalledWith('new@example.com', 'password123', { company: 'Test Co' })
  })

  it('provides logout function', async () => {
    const { result } = renderHook(() => useAuth())
    const mockSignOut = vi.mocked(auth.signOut)
    mockSignOut.mockResolvedValue(undefined)

    await act(async () => {
      await result.current.logout()
    })

    expect(mockSignOut).toHaveBeenCalled()
  })

  it('provides OAuth login function', async () => {
    const { result } = renderHook(() => useAuth())
    const mockSignInWithOAuth = vi.mocked(auth.signInWithOAuth)
    mockSignInWithOAuth.mockResolvedValue(undefined)

    await act(async () => {
      await result.current.loginWithOAuth('google')
    })

    expect(mockSignInWithOAuth).toHaveBeenCalledWith('google')
  })

  it('handles login errors', async () => {
    const { result } = renderHook(() => useAuth())
    const mockSignIn = vi.mocked(auth.signIn)
    mockSignIn.mockRejectedValue(new Error('Invalid credentials'))

    await expect(async () => {
      await act(async () => {
        await result.current.login('wrong@example.com', 'wrongpassword')
      })
    }).rejects.toThrow('Invalid credentials')
  })

  it('handles signup errors', async () => {
    const { result } = renderHook(() => useAuth())
    const mockSignUp = vi.mocked(auth.signUp)
    mockSignUp.mockRejectedValue(new Error('Email already exists'))

    await expect(async () => {
      await act(async () => {
        await result.current.signup('existing@example.com', 'password123')
      })
    }).rejects.toThrow('Email already exists')
  })

  it('returns user data when authenticated', async () => {
    const mockUser = { id: '123', email: 'test@example.com' }
    const mockSession = { access_token: 'token', user: mockUser }

    const { createClient } = await import('@/lib/supabase/client')
    const mockCreateClient = vi.mocked(createClient)
    mockCreateClient.mockReturnValue({
      auth: {
        getSession: vi.fn(() =>
          Promise.resolve({ data: { session: mockSession }, error: null })
        ),
        onAuthStateChange: vi.fn(() => ({
          data: { subscription: { unsubscribe: vi.fn() } },
        })),
      },
    } as any)

    const { result } = renderHook(() => useAuth())

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.session).toEqual(mockSession)
      expect(result.current.loading).toBe(false)
    })
  })

  it('cleans up subscription on unmount', () => {
    const unsubscribeMock = vi.fn()
    const { createClient } = require('@/lib/supabase/client')
    const mockCreateClient = vi.mocked(createClient)

    mockCreateClient.mockReturnValue({
      auth: {
        getSession: vi.fn(() =>
          Promise.resolve({ data: { session: null }, error: null })
        ),
        onAuthStateChange: vi.fn(() => ({
          data: { subscription: { unsubscribe: unsubscribeMock } },
        })),
      },
    } as any)

    const { unmount } = renderHook(() => useAuth())

    unmount()

    expect(unsubscribeMock).toHaveBeenCalled()
  })
})
