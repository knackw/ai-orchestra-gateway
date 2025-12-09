'use client';

import { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAccessibility } from '@/hooks/useAccessibility';
import type { AccessibilitySettings } from '@/hooks/useAccessibility';

/**
 * Accessibility Context
 *
 * Provides accessibility settings throughout the application.
 */
interface AccessibilityContextValue {
  settings: AccessibilitySettings;
  isLoaded: boolean;
  updateSetting: <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => void;
  updateSettings: (updates: Partial<AccessibilitySettings>) => void;
  resetSettings: () => void;
}

const AccessibilityContext = createContext<AccessibilityContextValue | undefined>(
  undefined
);

/**
 * AccessibilityProvider Component
 *
 * Wraps the application to provide accessibility settings.
 *
 * Usage:
 * ```tsx
 * <AccessibilityProvider>
 *   <App />
 * </AccessibilityProvider>
 * ```
 */
export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const accessibility = useAccessibility();

  // Apply settings on initial load
  useEffect(() => {
    if (accessibility.isLoaded && typeof document !== 'undefined') {
      // Settings are automatically applied by useAccessibility hook
      // This is just a notification for analytics or logging
      console.debug('[A11Y] Accessibility settings loaded', accessibility.settings);
    }
  }, [accessibility.isLoaded, accessibility.settings]);

  return (
    <AccessibilityContext.Provider value={accessibility}>
      {children}
    </AccessibilityContext.Provider>
  );
}

/**
 * Hook to access accessibility context
 *
 * Must be used within AccessibilityProvider.
 *
 * Usage:
 * ```tsx
 * const { settings, updateSetting } = useAccessibilityContext();
 * ```
 */
export function useAccessibilityContext() {
  const context = useContext(AccessibilityContext);

  if (!context) {
    throw new Error(
      'useAccessibilityContext must be used within AccessibilityProvider'
    );
  }

  return context;
}

/**
 * Hook to check if a specific accessibility feature is enabled
 *
 * Usage:
 * ```tsx
 * const isHighContrast = useAccessibilityFeature('highContrast');
 * ```
 */
export function useAccessibilityFeature<K extends keyof AccessibilitySettings>(
  feature: K
): AccessibilitySettings[K] {
  const { settings } = useAccessibilityContext();
  return settings[feature];
}

/**
 * Higher-order component to inject accessibility settings
 *
 * Usage:
 * ```tsx
 * export default withAccessibility(MyComponent);
 * ```
 */
export function withAccessibility<P extends object>(
  Component: React.ComponentType<P & { accessibility: AccessibilityContextValue }>
) {
  return function WithAccessibilityComponent(props: P) {
    const accessibility = useAccessibilityContext();

    return <Component {...props} accessibility={accessibility} />;
  };
}
