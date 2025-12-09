'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import type { User, Session } from '@supabase/supabase-js'

interface UseAuthReturn {
  user: User | null
  session: Session | null
  isLoading: boolean
  isAuthenticated: boolean
  signOut: () => Promise<void>
  refreshSession: () => Promise<void>
}

/**
 * Custom hook to manage authentication state
 *
 * @returns {UseAuthReturn} Authentication state and methods
 *
 * @example
 * ```tsx
 * function ProtectedPage() {
 *   const { user, isLoading, isAuthenticated, signOut } = useAuth()
 *
 *   if (isLoading) return <LoadingSpinner />
 *   if (!isAuthenticated) return <Navigate to="/login" />
 *
 *   return (
 *     <div>
 *       <h1>Welcome {user.email}</h1>
 *       <button onClick={signOut}>Sign Out</button>
 *     </div>
 *   )
 * }
 * ```
 */
export function useAuth(): UseAuthReturn {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const supabase = createClient()

    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session: initialSession }, error } = await supabase.auth.getSession()

        if (error) {
          console.error('Error fetching session:', error)
          return
        }

        setSession(initialSession)
        setUser(initialSession?.user ?? null)
      } catch (error) {
        console.error('Error in getInitialSession:', error)
      } finally {
        setIsLoading(false)
      }
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, newSession) => {
        setSession(newSession)
        setUser(newSession?.user ?? null)
        setIsLoading(false)

        // Refresh the page to update any server-side data
        router.refresh()
      }
    )

    // Cleanup subscription
    return () => {
      subscription.unsubscribe()
    }
  }, [router])

  const signOut = async () => {
    const supabase = createClient()

    try {
      await supabase.auth.signOut()
      setUser(null)
      setSession(null)
      router.push('/login')
      router.refresh()
    } catch (error) {
      console.error('Error signing out:', error)
      throw error
    }
  }

  const refreshSession = async () => {
    const supabase = createClient()

    try {
      const { data: { session: refreshedSession }, error } = await supabase.auth.refreshSession()

      if (error) {
        console.error('Error refreshing session:', error)
        return
      }

      setSession(refreshedSession)
      setUser(refreshedSession?.user ?? null)
    } catch (error) {
      console.error('Error in refreshSession:', error)
      throw error
    }
  }

  return {
    user,
    session,
    isLoading,
    isAuthenticated: !!user,
    signOut,
    refreshSession,
  }
}
