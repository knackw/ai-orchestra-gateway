'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

interface AccessibilitySettings {
  fontSize: number // 80-150
  highContrast: boolean
  reducedMotion: boolean
  focusIndicators: boolean
}

interface AccessibilityContextType extends AccessibilitySettings {
  setFontSize: (size: number) => void
  setHighContrast: (enabled: boolean) => void
  setReducedMotion: (enabled: boolean) => void
  setFocusIndicators: (enabled: boolean) => void
  resetToDefaults: () => void
}

const defaultSettings: AccessibilitySettings = {
  fontSize: 100,
  highContrast: false,
  reducedMotion: false,
  focusIndicators: true,
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined)

export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AccessibilitySettings>(defaultSettings)
  const [isClient, setIsClient] = useState(false)

  // Load settings from localStorage on mount
  useEffect(() => {
    setIsClient(true)
    const stored = localStorage.getItem('accessibility-settings')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setSettings({ ...defaultSettings, ...parsed })
      } catch (error) {
        console.error('Failed to parse accessibility settings:', error)
      }
    }
  }, [])

  // Save settings to localStorage whenever they change
  useEffect(() => {
    if (isClient) {
      localStorage.setItem('accessibility-settings', JSON.stringify(settings))
    }
  }, [settings, isClient])

  // Apply settings to document
  useEffect(() => {
    if (!isClient) return

    const html = document.documentElement

    // Apply font size
    html.style.fontSize = `${settings.fontSize}%`

    // Apply high contrast
    if (settings.highContrast) {
      html.classList.add('high-contrast')
    } else {
      html.classList.remove('high-contrast')
    }

    // Apply reduced motion
    if (settings.reducedMotion) {
      html.classList.add('reduced-motion')
    } else {
      html.classList.remove('reduced-motion')
    }

    // Apply focus indicators
    if (settings.focusIndicators) {
      html.classList.add('focus-indicators')
    } else {
      html.classList.remove('focus-indicators')
    }
  }, [settings, isClient])

  const setFontSize = (fontSize: number) => {
    setSettings((prev) => ({ ...prev, fontSize: Math.min(150, Math.max(80, fontSize)) }))
  }

  const setHighContrast = (highContrast: boolean) => {
    setSettings((prev) => ({ ...prev, highContrast }))
  }

  const setReducedMotion = (reducedMotion: boolean) => {
    setSettings((prev) => ({ ...prev, reducedMotion }))
  }

  const setFocusIndicators = (focusIndicators: boolean) => {
    setSettings((prev) => ({ ...prev, focusIndicators }))
  }

  const resetToDefaults = () => {
    setSettings(defaultSettings)
  }

  const value: AccessibilityContextType = {
    ...settings,
    setFontSize,
    setHighContrast,
    setReducedMotion,
    setFocusIndicators,
    resetToDefaults,
  }

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  )
}

export function useAccessibility() {
  const context = useContext(AccessibilityContext)
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider')
  }
  return context
}
