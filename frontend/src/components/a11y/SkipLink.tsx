'use client';

/**
 * SkipLink Component
 *
 * Provides a "Skip to main content" link for keyboard and screen reader users.
 * The link is visually hidden by default and becomes visible when focused.
 *
 * Accessibility features:
 * - Allows keyboard users to skip repetitive navigation
 * - WCAG 2.1 Level A requirement (2.4.1 Bypass Blocks)
 * - Visible on focus for keyboard navigation
 */
export function SkipLink() {
  const handleSkipToMain = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <a
      href="#main-content"
      onClick={handleSkipToMain}
      className="skip-link sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
    >
      Zum Hauptinhalt springen
    </a>
  );
}
