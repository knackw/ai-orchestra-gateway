# Public Pages Implementation Guide

## Quick Start

All public/legal pages have been created in `/root/Projekte/ai-orchestra-gateway/frontend/`.

### File Locations

```
frontend/src/
├── app/(public)/
│   ├── layout.tsx                      ✅ Public layout
│   ├── agb/page.tsx                    ✅ Terms of Service
│   ├── datenschutz/page.tsx            ✅ Privacy Policy
│   ├── impressum/page.tsx              ✅ Legal Notice
│   ├── avv/page.tsx                    ✅ Data Processing Agreement
│   └── barrierefreiheit/page.tsx       ✅ Accessibility Statement
│
├── components/
│   ├── layout/
│   │   ├── PublicHeader.tsx            ✅ Header component
│   │   └── PublicFooter.tsx            ✅ Footer component
│   ├── a11y/
│   │   ├── SkipLink.tsx                ✅ Skip link
│   │   └── AccessibilityPanel.tsx      ✅ Enhanced A11y panel
│   └── CookieConsent.tsx               ✅ Cookie banner
```

---

## Testing the Pages

### 1. Start the Development Server

```bash
cd /root/Projekte/ai-orchestra-gateway/frontend
npm run dev
```

### 2. Access the Pages

Open your browser and navigate to:

- http://localhost:3000/agb
- http://localhost:3000/datenschutz
- http://localhost:3000/impressum
- http://localhost:3000/avv
- http://localhost:3000/barrierefreiheit

### 3. Test Functionality

**Cookie Consent:**
- Should appear on first visit
- Test "Accept All", "Reject", and "Settings"
- Check that preferences persist (localStorage)

**Accessibility Panel:**
- Click the floating button (bottom-right)
- Test all settings (font size, contrast, animations, theme)
- Verify settings persist after page reload

**Skip Link:**
- Press Tab key immediately after page load
- "Zum Hauptinhalt springen" link should appear
- Press Enter to jump to main content

**Navigation:**
- Test header navigation
- Test footer links
- Test table of contents on legal pages
- Test mobile menu (resize browser)

**Keyboard Navigation:**
- Tab through all interactive elements
- Ensure all elements are reachable
- Check focus indicators are visible

---

## Customization Guide

### Update Company Information

Replace placeholder data in these files:

1. **Impressum** (`src/app/(public)/impressum/page.tsx`)
   - Company name
   - Address
   - Geschäftsführer
   - Handelsregister
   - USt-IdNr

2. **Datenschutz** (`src/app/(public)/datenschutz/page.tsx`)
   - Verantwortlicher section
   - Contact information
   - Data Protection Officer

3. **AVV** (`src/app/(public)/avv/page.tsx`)
   - Company name in contract parties
   - Sub-processor list (if different)

4. **Footer** (`src/components/layout/PublicFooter.tsx`)
   - Company name
   - Copyright year (auto-updates)

### Update Legal Texts

**Important:** Have all legal texts reviewed by a lawyer before going live!

Areas marked with "(Platzhalter)" need to be updated:
- Company registration details
- Specific liability clauses
- Service-specific terms
- Pricing details

### Styling

All pages use Tailwind CSS classes. To customize:

1. **Colors:** Update `tailwind.config.ts`
2. **Fonts:** Change in `src/app/layout.tsx` (Inter font)
3. **Spacing:** Adjust container padding in individual components

### Add New Legal Pages

1. Create new directory: `src/app/(public)/[page-name]/`
2. Add `page.tsx` with similar structure to existing pages
3. Add link to footer in `PublicFooter.tsx`
4. Add metadata for SEO

---

## Integration Notes

### Cookie Tracking

The `CookieConsent.tsx` component includes placeholders for actual tracking:

```typescript
const applyCookieSettings = (prefs: CookiePreferences) => {
  // TODO: Implement actual tracking
  if (prefs.analytics) {
    // Enable Google Analytics
  }
  if (prefs.marketing) {
    // Enable marketing cookies
  }
};
```

**Recommended services:**
- Analytics: Matomo (self-hosted, GDPR-friendly)
- Error tracking: Sentry (with consent)
- Marketing: Only with explicit consent

### AVV PDF Generation

The AVV page has a "Download as PDF" button prepared. To implement:

```typescript
// Option 1: Use react-pdf
import { PDFDownloadLink } from '@react-pdf/renderer';

// Option 2: Server-side with Puppeteer
// Create API route: /api/avv/pdf
```

### Multi-Language Support

To add English versions:

1. Create `/en/agb`, `/en/datenschutz`, etc.
2. Translate all German texts
3. Update `PublicHeader.tsx` to include language switcher
4. Add hreflang tags for SEO

**Legal Note:** Specify which language version is legally binding!

---

## Accessibility Features

### Current Implementation (WCAG 2.1 Level AA)

✅ **Perceivable:**
- Text alternatives (alt texts)
- Color contrast (4.5:1 minimum)
- Resizable text (up to 200%)
- Multiple ways to access content

✅ **Operable:**
- Keyboard accessible
- No keyboard traps
- Skip links
- Visible focus indicators
- No time limits

✅ **Understandable:**
- Readable and understandable language
- Predictable navigation
- Input assistance (forms)
- Error identification

✅ **Robust:**
- Valid HTML
- Compatible with assistive technologies
- Semantic markup

### Testing Tools

**Automated:**
```bash
# Install dependencies
npm install -D @axe-core/playwright

# Run accessibility tests
npm run test:a11y
```

**Manual:**
- Screen readers: NVDA (Windows), VoiceOver (Mac)
- Keyboard navigation: Tab, Shift+Tab, Enter, Escape
- Browser extensions: axe DevTools, WAVE

---

## Performance Optimization

### Current Status
- Static pages (no SSR needed)
- Minimal JavaScript
- Code splitting by route

### Recommendations

1. **Images:** Use Next.js Image component for logos
2. **Fonts:** Optimize font loading (already using next/font)
3. **JavaScript:** Lazy load AccessibilityPanel
4. **CSS:** Purge unused Tailwind classes (automatic)

### Lighthouse Scores (Target)
- Performance: 95+
- Accessibility: 100
- Best Practices: 100
- SEO: 100

---

## Legal Compliance Checklist

### GDPR (DSGVO)
- [x] Privacy policy with all required information
- [x] Cookie consent (opt-in)
- [x] Data processing agreement (AVV)
- [x] Information about data subject rights
- [x] Contact for data protection officer
- [x] Sub-processor transparency
- [x] International data transfer information
- [ ] **TODO:** Implement actual cookie tracking
- [ ] **TODO:** Test GDPR request workflow

### German Law (TMG)
- [x] Impressum with all required fields
- [x] Disclaimer for external links
- [x] Copyright notice
- [ ] **TODO:** Add real company data
- [ ] **TODO:** Verify all legal requirements with lawyer

### Accessibility (BITV 2.0)
- [x] Accessibility statement
- [x] Contact for accessibility feedback
- [x] Dispute resolution information
- [x] Accessibility tools
- [ ] **TODO:** External WCAG 2.1 audit (Q1 2026)
- [ ] **TODO:** User testing with assistive technologies

---

## Deployment Checklist

Before going live:

### Content Review
- [ ] Replace all "(Platzhalter)" with real data
- [ ] Have lawyer review all legal texts
- [ ] Update all contact email addresses
- [ ] Verify company registration details
- [ ] Check USt-IdNr and other IDs
- [ ] Update "Last Updated" dates

### Technical Review
- [ ] Test all pages on different devices
- [ ] Test all interactive elements
- [ ] Verify cookie consent works
- [ ] Test accessibility panel
- [ ] Check all internal links
- [ ] Verify responsive design
- [ ] Test print layouts
- [ ] Check dark mode

### SEO
- [ ] Verify all meta tags
- [ ] Submit sitemap to Google
- [ ] Add structured data
- [ ] Check robots.txt
- [ ] Verify canonical URLs

### Analytics & Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure analytics (Matomo)
- [ ] Set up uptime monitoring
- [ ] Configure cookie consent integration

---

## Maintenance Schedule

### Monthly
- Check for broken links
- Review cookie consent acceptance rates
- Monitor accessibility panel usage

### Quarterly
- Review and update legal texts
- Check for regulatory changes
- Update sub-processor list
- Verify contact information

### Annually
- External legal audit
- WCAG compliance audit
- Update copyright year (automatic)
- Review and update roadmap

---

## Support & Resources

### Documentation
- GDPR: https://gdpr.eu/
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- BITV 2.0: https://www.bitvtest.de/
- TMG: https://www.gesetze-im-internet.de/tmg/

### Tools
- Accessibility: https://www.a11yproject.com/
- GDPR Compliance: https://gdpr.eu/checklist/
- German Law: https://www.it-recht-kanzlei.de/

### Contact
For questions about this implementation:
- Technical: dev@ailegalops.de
- Legal: legal@ailegalops.de
- Accessibility: barrierefreiheit@ailegalops.de

---

## Troubleshooting

### Pages Not Loading
- Check if Next.js dev server is running
- Verify file paths are correct
- Check browser console for errors

### Styling Issues
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run build`
- Check Tailwind config

### Cookie Consent Not Appearing
- Clear localStorage
- Check browser console
- Verify component is imported in layout

### Accessibility Panel Not Working
- Check if button is visible (bottom-right)
- Verify localStorage is available
- Check browser console for errors

---

**Version:** 1.0.0
**Created:** 2025-12-08
**Last Updated:** 2025-12-08
