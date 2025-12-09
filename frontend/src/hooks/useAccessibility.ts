'use client';

import { useEffect, useState } from 'react';

/**
 * Accessibility Settings
 */
export interface AccessibilitySettings {
  fontSize: 'small' | 'normal' | 'large' | 'xlarge';
  highContrast: boolean;
  reduceMotion: boolean;
  dyslexiaFont: boolean;
  highlightLinks: boolean;
  focusIndicators: boolean;
}

const STORAGE_KEY = 'accessibility-preferences';

const DEFAULT_SETTINGS: AccessibilitySettings = {
  fontSize: 'normal',
  highContrast: false,
  reduceMotion: false,
  dyslexiaFont: false,
  highlightLinks: false,
  focusIndicators: false,
};

/**
 * Hook to manage accessibility preferences
 *
 * Features:
 * - Persistent storage in localStorage
 * - Automatic application of CSS classes to document
 * - Respects system preferences (prefers-reduced-motion, prefers-contrast)
 *
 * Usage:
 * const { settings, updateSetting, resetSettings } = useAccessibility();
 */
export function useAccessibility() {
  const [settings, setSettings] = useState<AccessibilitySettings>(DEFAULT_SETTINGS);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as AccessibilitySettings;
        setSettings(parsed);
      } else {
        // Check system preferences on first load
        const systemPreferences: Partial<AccessibilitySettings> = {};

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          systemPreferences.reduceMotion = true;
        }

        if (window.matchMedia('(prefers-contrast: more)').matches) {
          systemPreferences.highContrast = true;
        }

        const initialSettings = { ...DEFAULT_SETTINGS, ...systemPreferences };
        setSettings(initialSettings);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(initialSettings));
      }
    } catch (error) {
      console.error('Failed to load accessibility settings:', error);
    }

    setIsLoaded(true);
  }, []);

  // Apply settings to document
  useEffect(() => {
    if (!isLoaded || typeof document === 'undefined') return;

    const root = document.documentElement;
    const body = document.body;

    // Apply font size
    const fontSizeMap = {
      small: '14px',
      normal: '16px',
      large: '18px',
      xlarge: '20px',
    };
    root.style.fontSize = fontSizeMap[settings.fontSize];

    // Apply high contrast
    if (settings.highContrast) {
      body.classList.add('high-contrast');
    } else {
      body.classList.remove('high-contrast');
    }

    // Apply reduce motion
    if (settings.reduceMotion) {
      body.classList.add('reduce-motion');
    } else {
      body.classList.remove('reduce-motion');
    }

    // Apply dyslexia font
    if (settings.dyslexiaFont) {
      body.classList.add('dyslexia-font');
    } else {
      body.classList.remove('dyslexia-font');
    }

    // Apply link highlighting
    if (settings.highlightLinks) {
      body.classList.add('highlight-links');
    } else {
      body.classList.remove('highlight-links');
    }

    // Apply focus indicators
    if (settings.focusIndicators) {
      body.classList.add('focus-indicators');
    } else {
      body.classList.remove('focus-indicators');
    }
  }, [settings, isLoaded]);

  /**
   * Update a single setting
   */
  const updateSetting = <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings));
      } catch (error) {
        console.error('Failed to save accessibility settings:', error);
      }
    }
  };

  /**
   * Update multiple settings at once
   */
  const updateSettings = (updates: Partial<AccessibilitySettings>) => {
    const newSettings = { ...settings, ...updates };
    setSettings(newSettings);

    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings));
      } catch (error) {
        console.error('Failed to save accessibility settings:', error);
      }
    }
  };

  /**
   * Reset all settings to defaults
   */
  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);

    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (error) {
        console.error('Failed to reset accessibility settings:', error);
      }
    }
  };

  return {
    settings,
    isLoaded,
    updateSetting,
    updateSettings,
    resetSettings,
  };
}

/**
 * Hook to check if user prefers reduced motion
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return prefersReducedMotion;
}

/**
 * Hook to check if user prefers high contrast
 */
export function usePrefersHighContrast(): boolean {
  const [prefersHighContrast, setPrefersHighContrast] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-contrast: more)');
    setPrefersHighContrast(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setPrefersHighContrast(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return prefersHighContrast;
}
