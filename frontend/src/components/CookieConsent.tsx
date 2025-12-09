'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { X, Settings, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CookiePreferences {
  necessary: boolean;
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
}

const COOKIE_CONSENT_KEY = 'cookie-consent';
const COOKIE_PREFERENCES_KEY = 'cookie-preferences';

/**
 * CookieConsent Component
 *
 * GDPR-compliant cookie consent banner with granular controls.
 *
 * Features:
 * - Required cookies always enabled
 * - Granular consent for functional, analytics, and marketing cookies
 * - Persistent storage in localStorage
 * - Link to privacy policy
 * - Accessible dialog with keyboard navigation
 */
export function CookieConsent() {
  const [showBanner, setShowBanner] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    functional: false,
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    // Check if user has already made a choice
    const consent = localStorage.getItem(COOKIE_CONSENT_KEY);
    const savedPreferences = localStorage.getItem(COOKIE_PREFERENCES_KEY);

    if (!consent) {
      // Show banner after a short delay for better UX
      const timer = setTimeout(() => setShowBanner(true), 1000);
      return () => clearTimeout(timer);
    } else if (savedPreferences) {
      try {
        setPreferences(JSON.parse(savedPreferences));
      } catch (error) {
        console.error('Failed to parse cookie preferences:', error);
      }
    }
  }, []);

  const savePreferences = (prefs: CookiePreferences) => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'true');
    localStorage.setItem(COOKIE_PREFERENCES_KEY, JSON.stringify(prefs));
    setPreferences(prefs);
    setShowBanner(false);
    setShowSettings(false);

    // Apply cookie settings
    applyCookieSettings(prefs);
  };

  const applyCookieSettings = (prefs: CookiePreferences) => {
    // Here you would actually enable/disable different tracking scripts
    // For example:
    // if (prefs.analytics) {
    //   // Enable Google Analytics
    // }
    // if (prefs.marketing) {
    //   // Enable marketing cookies
    // }
    void prefs // SEC-016: Prevent unused variable warning
  };

  const acceptAll = () => {
    savePreferences({
      necessary: true,
      functional: true,
      analytics: true,
      marketing: true,
    });
  };

  const rejectAll = () => {
    savePreferences({
      necessary: true,
      functional: false,
      analytics: false,
      marketing: false,
    });
  };

  const saveCustomSettings = () => {
    savePreferences(preferences);
  };

  if (!showBanner) {
    return null;
  }

  return (
    <div
      className="fixed inset-x-0 bottom-0 z-50 border-t bg-background shadow-lg"
      role="dialog"
      aria-labelledby="cookie-consent-title"
      aria-describedby="cookie-consent-description"
    >
      <div className="container mx-auto px-4 py-6">
        {!showSettings ? (
          // Simple Banner
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex-1">
              <h2 id="cookie-consent-title" className="mb-2 text-lg font-semibold">
                Cookie-Einstellungen
              </h2>
              <p id="cookie-consent-description" className="text-sm text-muted-foreground">
                Wir verwenden Cookies, um Ihnen die beste Erfahrung auf unserer Website zu
                bieten. Einige sind notwendig, andere helfen uns, die Website zu verbessern
                und Ihnen personalisierte Inhalte anzubieten.{' '}
                <Link href="/datenschutz" className="text-primary hover:underline">
                  Mehr erfahren
                </Link>
              </p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Button variant="outline" onClick={() => setShowSettings(true)} size="sm">
                <Settings className="mr-2 h-4 w-4" />
                Einstellungen
              </Button>
              <Button variant="outline" onClick={rejectAll} size="sm">
                Ablehnen
              </Button>
              <Button onClick={acceptAll} size="sm">
                Alle akzeptieren
              </Button>
            </div>
          </div>
        ) : (
          // Detailed Settings
          <div className="relative">
            <button
              onClick={() => setShowSettings(false)}
              className="absolute right-0 top-0 rounded-md p-2 hover:bg-muted"
              aria-label="Einstellungen schließen"
            >
              <X className="h-4 w-4" />
            </button>

            <h2 id="cookie-consent-title" className="mb-4 text-lg font-semibold">
              Cookie-Einstellungen anpassen
            </h2>

            <div className="mb-6 space-y-4">
              {/* Necessary Cookies */}
              <div className="flex items-start justify-between rounded-lg border p-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">Notwendige Cookies</h3>
                    <span className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">
                      Immer aktiv
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Diese Cookies sind für die Grundfunktionen der Website erforderlich und
                    können nicht deaktiviert werden.
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Beispiele: Session-Cookies, Sicherheits-Cookies, Cookie-Einstellungen
                  </p>
                </div>
                <div className="ml-4 flex items-center">
                  <Check className="h-5 w-5 text-primary" />
                </div>
              </div>

              {/* Functional Cookies */}
              <div className="flex items-start justify-between rounded-lg border p-4">
                <div className="flex-1">
                  <h3 className="font-semibold">Funktionale Cookies</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Diese Cookies ermöglichen erweiterte Funktionen wie Spracheinstellungen
                    und personalisierte Inhalte.
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Beispiele: Sprachauswahl, Theme-Präferenzen, Barrierefreiheits-Einstellungen
                  </p>
                </div>
                <div className="ml-4 flex items-center">
                  <label className="relative inline-flex cursor-pointer items-center">
                    <input
                      type="checkbox"
                      className="peer sr-only"
                      checked={preferences.functional}
                      onChange={(e) =>
                        setPreferences({ ...preferences, functional: e.target.checked })
                      }
                    />
                    <div className="peer h-6 w-11 rounded-full bg-muted after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary peer-focus:ring-offset-2"></div>
                  </label>
                </div>
              </div>

              {/* Analytics Cookies */}
              <div className="flex items-start justify-between rounded-lg border p-4">
                <div className="flex-1">
                  <h3 className="font-semibold">Analyse-Cookies</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Diese Cookies helfen uns zu verstehen, wie Sie unsere Website nutzen,
                    damit wir sie verbessern können.
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Beispiele: Seitenaufrufe, Verweildauer, Klickpfade (anonymisiert)
                  </p>
                </div>
                <div className="ml-4 flex items-center">
                  <label className="relative inline-flex cursor-pointer items-center">
                    <input
                      type="checkbox"
                      className="peer sr-only"
                      checked={preferences.analytics}
                      onChange={(e) =>
                        setPreferences({ ...preferences, analytics: e.target.checked })
                      }
                    />
                    <div className="peer h-6 w-11 rounded-full bg-muted after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary peer-focus:ring-offset-2"></div>
                  </label>
                </div>
              </div>

              {/* Marketing Cookies */}
              <div className="flex items-start justify-between rounded-lg border p-4">
                <div className="flex-1">
                  <h3 className="font-semibold">Marketing-Cookies</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Diese Cookies werden verwendet, um Ihnen relevante Werbung und Marketing-
                    Inhalte anzuzeigen.
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Beispiele: Remarketing, personalisierte Werbung, Social Media Integration
                  </p>
                </div>
                <div className="ml-4 flex items-center">
                  <label className="relative inline-flex cursor-pointer items-center">
                    <input
                      type="checkbox"
                      className="peer sr-only"
                      checked={preferences.marketing}
                      onChange={(e) =>
                        setPreferences({ ...preferences, marketing: e.target.checked })
                      }
                    />
                    <div className="peer h-6 w-11 rounded-full bg-muted after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary peer-focus:ring-offset-2"></div>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
              <Button variant="outline" onClick={rejectAll} size="sm">
                Nur notwendige
              </Button>
              <Button onClick={saveCustomSettings} size="sm">
                Auswahl speichern
              </Button>
            </div>

            <div className="mt-4 text-center text-xs text-muted-foreground">
              Weitere Informationen finden Sie in unserer{' '}
              <Link href="/datenschutz" className="text-primary hover:underline">
                Datenschutzerklärung
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
