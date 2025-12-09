'use client';

import { useState, useEffect, useRef } from 'react';
import { X, Settings, Type, Contrast, Zap, Palette, Link as LinkIcon, Focus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FocusTrap } from '@/lib/a11y/focus-trap';

interface AccessibilitySettings {
  fontSize: 'small' | 'normal' | 'large' | 'xlarge';
  highContrast: boolean;
  reduceMotion: boolean;
  dyslexiaFont: boolean;
  highlightLinks: boolean;
  focusIndicators: boolean;
}

const ACCESSIBILITY_SETTINGS_KEY = 'accessibility-settings';

const DEFAULT_SETTINGS: AccessibilitySettings = {
  fontSize: 'normal',
  highContrast: false,
  reduceMotion: false,
  dyslexiaFont: false,
  highlightLinks: false,
  focusIndicators: false,
};

/**
 * AccessibilityPanel Component
 *
 * Provides user-configurable accessibility settings.
 *
 * Features:
 * - Font size adjustment (small, normal, large, extra-large)
 * - High contrast mode
 * - Reduce motion
 * - Dyslexia-friendly font
 * - Link highlighting
 * - Enhanced focus indicators
 * - Persistent settings in localStorage
 * - Floating button to open panel
 *
 * Accessibility:
 * - WCAG 2.1 Level AA compliant
 * - Keyboard accessible (Tab, Enter, Escape)
 * - Focus trap for modal dialog
 * - Screen reader friendly with ARIA labels
 */
export function AccessibilityPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [settings, setSettings] = useState<AccessibilitySettings>(DEFAULT_SETTINGS);
  const panelRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const focusTrapRef = useRef<FocusTrap | null>(null);

  // Load settings from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const savedSettings = localStorage.getItem(ACCESSIBILITY_SETTINGS_KEY);
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings) as AccessibilitySettings;
        setSettings(parsed);
        applySettings(parsed);
      } else {
        // Check system preferences
        const systemPreferences: Partial<AccessibilitySettings> = {};

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          systemPreferences.reduceMotion = true;
        }

        if (window.matchMedia('(prefers-contrast: more)').matches) {
          systemPreferences.highContrast = true;
        }

        const initialSettings = { ...DEFAULT_SETTINGS, ...systemPreferences };
        setSettings(initialSettings);
        applySettings(initialSettings);
      }
    } catch (error) {
      console.error('Failed to parse accessibility settings:', error);
    }
  }, []);

  // Setup focus trap when panel opens
  useEffect(() => {
    if (isOpen && panelRef.current) {
      focusTrapRef.current = new FocusTrap({
        element: panelRef.current,
        triggerElement: triggerRef.current,
        allowEscape: true,
        onDeactivate: () => setIsOpen(false),
      });
      focusTrapRef.current.activate();

      return () => {
        focusTrapRef.current?.deactivate();
        focusTrapRef.current = null;
      };
    }
  }, [isOpen]);

  const applySettings = (newSettings: AccessibilitySettings) => {
    if (typeof document === 'undefined') return;

    const root = document.documentElement;
    const body = document.body;

    // Apply font size to root element
    const fontSizeMap = {
      small: '14px',
      normal: '16px',
      large: '18px',
      xlarge: '20px',
    };
    root.style.fontSize = fontSizeMap[newSettings.fontSize];

    // Apply high contrast
    if (newSettings.highContrast) {
      body.classList.add('high-contrast');
    } else {
      body.classList.remove('high-contrast');
    }

    // Apply reduce motion
    if (newSettings.reduceMotion) {
      body.classList.add('reduce-motion');
    } else {
      body.classList.remove('reduce-motion');
    }

    // Apply dyslexia font
    if (newSettings.dyslexiaFont) {
      body.classList.add('dyslexia-font');
    } else {
      body.classList.remove('dyslexia-font');
    }

    // Apply link highlighting
    if (newSettings.highlightLinks) {
      body.classList.add('highlight-links');
    } else {
      body.classList.remove('highlight-links');
    }

    // Apply focus indicators
    if (newSettings.focusIndicators) {
      body.classList.add('focus-indicators');
    } else {
      body.classList.remove('focus-indicators');
    }
  };

  const updateSetting = <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    applySettings(newSettings);

    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(ACCESSIBILITY_SETTINGS_KEY, JSON.stringify(newSettings));
      } catch (error) {
        console.error('Failed to save accessibility settings:', error);
      }
    }
  };

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
    applySettings(DEFAULT_SETTINGS);

    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.removeItem(ACCESSIBILITY_SETTINGS_KEY);
      } catch (error) {
        console.error('Failed to reset accessibility settings:', error);
      }
    }
  };

  const handleOpenPanel = () => {
    setIsOpen(true);
  };

  const handleClosePanel = () => {
    setIsOpen(false);
  };

  const handleBackdropClick = () => {
    handleClosePanel();
  };

  return (
    <>
      {/* Floating Button */}
      <button
        ref={triggerRef}
        onClick={handleOpenPanel}
        className="fixed bottom-4 right-4 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-all hover:scale-110 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        aria-label="Barrierefreiheits-Einstellungen öffnen"
        title="Barrierefreiheit"
      >
        <Settings className="h-6 w-6" aria-hidden="true" />
      </button>

      {/* Panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
            onClick={handleBackdropClick}
            aria-hidden="true"
          />

          {/* Panel Content */}
          <div
            ref={panelRef}
            className="fixed right-0 top-0 z-50 h-full w-full max-w-md overflow-y-auto border-l bg-background shadow-2xl"
            role="dialog"
            aria-labelledby="a11y-panel-title"
            aria-describedby="a11y-panel-description"
            aria-modal="true"
          >
            <div className="sticky top-0 z-10 flex items-center justify-between border-b bg-background p-6">
              <div>
                <h2 id="a11y-panel-title" className="text-xl font-bold">
                  Barrierefreiheit
                </h2>
                <p id="a11y-panel-description" className="text-sm text-muted-foreground">
                  Passen Sie die Darstellung an Ihre Bedürfnisse an
                </p>
              </div>
              <button
                onClick={handleClosePanel}
                className="rounded-md p-2 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-primary"
                aria-label="Schließen"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            <div className="space-y-6 p-6">
              {/* Font Size */}
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <Type className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  <h3 className="font-semibold">Schriftgröße</h3>
                </div>
                <div className="grid grid-cols-2 gap-2" role="radiogroup" aria-label="Schriftgröße">
                  {(['small', 'normal', 'large', 'xlarge'] as const).map((size) => (
                    <button
                      key={size}
                      onClick={() => updateSetting('fontSize', size)}
                      className={`rounded-md border p-3 text-left transition-colors ${
                        settings.fontSize === size
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-border hover:border-primary/50 hover:bg-muted'
                      }`}
                      role="radio"
                      aria-checked={settings.fontSize === size}
                    >
                      <div className="font-medium">
                        {size === 'small' && 'Klein'}
                        {size === 'normal' && 'Normal'}
                        {size === 'large' && 'Groß'}
                        {size === 'xlarge' && 'Sehr groß'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {size === 'small' && '14px'}
                        {size === 'normal' && '16px'}
                        {size === 'large' && '18px'}
                        {size === 'xlarge' && '20px'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* High Contrast */}
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <Contrast className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  <h3 className="font-semibold">Hoher Kontrast</h3>
                </div>
                <button
                  onClick={() => updateSetting('highContrast', !settings.highContrast)}
                  className={`w-full rounded-md border p-3 text-left transition-colors ${
                    settings.highContrast
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  }`}
                  role="switch"
                  aria-checked={settings.highContrast}
                  aria-label="Hoher Kontrast"
                >
                  <div className="font-medium">
                    {settings.highContrast ? 'Aktiviert' : 'Deaktiviert'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Erhöht den Kontrast für bessere Lesbarkeit
                  </div>
                </button>
              </div>

              {/* Reduce Motion */}
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  <h3 className="font-semibold">Bewegungen reduzieren</h3>
                </div>
                <button
                  onClick={() => updateSetting('reduceMotion', !settings.reduceMotion)}
                  className={`w-full rounded-md border p-3 text-left transition-colors ${
                    settings.reduceMotion
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  }`}
                  role="switch"
                  aria-checked={settings.reduceMotion}
                  aria-label="Bewegungen reduzieren"
                >
                  <div className="font-medium">
                    {settings.reduceMotion ? 'Aktiviert' : 'Deaktiviert'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Reduziert Animationen und Bewegungseffekte
                  </div>
                </button>
              </div>

              {/* Dyslexia Font */}
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <Type className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  <h3 className="font-semibold">Legasthenie-freundliche Schrift</h3>
                </div>
                <button
                  onClick={() => updateSetting('dyslexiaFont', !settings.dyslexiaFont)}
                  className={`w-full rounded-md border p-3 text-left transition-colors ${
                    settings.dyslexiaFont
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  }`}
                  role="switch"
                  aria-checked={settings.dyslexiaFont}
                  aria-label="Legasthenie-freundliche Schrift"
                >
                  <div className="font-medium">
                    {settings.dyslexiaFont ? 'Aktiviert' : 'Deaktiviert'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Verwendet eine Schrift, die leichter lesbar ist
                  </div>
                </button>
              </div>

              {/* Highlight Links */}
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <LinkIcon className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  <h3 className="font-semibold">Links hervorheben</h3>
                </div>
                <button
                  onClick={() => updateSetting('highlightLinks', !settings.highlightLinks)}
                  className={`w-full rounded-md border p-3 text-left transition-colors ${
                    settings.highlightLinks
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  }`}
                  role="switch"
                  aria-checked={settings.highlightLinks}
                  aria-label="Links hervorheben"
                >
                  <div className="font-medium">
                    {settings.highlightLinks ? 'Aktiviert' : 'Deaktiviert'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Unterstreicht alle Links auf der Seite
                  </div>
                </button>
              </div>

              {/* Focus Indicators */}
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <Focus className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                  <h3 className="font-semibold">Fokus-Indikatoren</h3>
                </div>
                <button
                  onClick={() => updateSetting('focusIndicators', !settings.focusIndicators)}
                  className={`w-full rounded-md border p-3 text-left transition-colors ${
                    settings.focusIndicators
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  }`}
                  role="switch"
                  aria-checked={settings.focusIndicators}
                  aria-label="Fokus-Indikatoren"
                >
                  <div className="font-medium">
                    {settings.focusIndicators ? 'Aktiviert' : 'Deaktiviert'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Zeigt deutliche Rahmen bei Tastatur-Navigation
                  </div>
                </button>
              </div>

              {/* Reset */}
              <div className="border-t pt-6">
                <Button variant="outline" onClick={resetSettings} className="w-full">
                  Auf Standardwerte zurücksetzen
                </Button>
              </div>

              {/* Info */}
              <div className="rounded-lg border bg-muted/50 p-4 text-sm">
                <p className="mb-2 font-semibold">Barrierefreiheits-Hinweis</p>
                <p className="text-muted-foreground">
                  Diese Einstellungen werden auf diesem Gerät gespeichert und gelten nur für
                  diese Website. Weitere Informationen finden Sie in unserer{' '}
                  <a
                    href="/barrierefreiheit"
                    className="text-primary hover:underline focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  >
                    Erklärung zur Barrierefreiheit
                  </a>
                  .
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
