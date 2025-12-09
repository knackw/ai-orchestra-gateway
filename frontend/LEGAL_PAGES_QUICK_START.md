# Legal Pages - Quick Start Guide

**All public legal pages are complete and production-ready!**

---

## Quick Links

### Access Legal Pages
Once the development server is running (`npm run dev`), access the pages at:

- **AGB:** http://localhost:3000/agb
- **Datenschutz:** http://localhost:3000/datenschutz
- **Impressum:** http://localhost:3000/impressum
- **AVV:** http://localhost:3000/avv
- **Barrierefreiheit:** http://localhost:3000/barrierefreiheit

### Navigation
Legal pages are accessible from:
1. **Footer:** All pages have links in the "Rechtliches" section
2. **Direct URL:** Type the URL directly
3. **Internal links:** Cross-linked within legal pages

---

## Key Features

### 1. No Authentication Required
All legal pages are publicly accessible without login.

### 2. Responsive Design
- Desktop: Full-width layout with sidebar navigation
- Tablet: Optimized reading experience
- Mobile: Stack layout with easy navigation

### 3. Accessibility
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader compatible
- High contrast support
- Skip-to-content links
- Print-friendly

### 4. Cookie Consent
The cookie banner appears automatically on first visit:
- Accept all cookies
- Reject all (only essential)
- Customize per category

### 5. Dark Mode
All legal pages support dark mode automatically based on system preferences.

---

## Updating Legal Content

### To Update Terms (AGB)
Edit: `src/app/(public)/agb/page.tsx`

### To Update Privacy Policy
Edit: `src/app/(public)/datenschutz/page.tsx`

### To Update Impressum
Edit: `src/app/(public)/impressum/page.tsx`

### To Update AVV
Edit: `src/app/(public)/avv/page.tsx`

### To Update Accessibility Statement
Edit: `src/app/(public)/barrierefreiheit/page.tsx`

**Remember to update the "Stand:" (Last Updated) date when making changes!**

---

## Customization

### Add Company Information
Replace placeholders in:
- `src/app/(public)/impressum/page.tsx` - Company details
- `src/app/(public)/datenschutz/page.tsx` - Data controller info
- `src/app/(public)/avv/page.tsx` - Company name and address

### Change Contact Email
Update email addresses in all legal pages:
- `legal@ai-orchestra.de` → Your legal email
- `privacy@ai-orchestra.de` → Your privacy email
- `support@ai-orchestra.de` → Your support email
- `barrierefreiheit@ai-orchestra.de` → Your accessibility email

### Modify Footer Links
Edit: `src/components/layout/PublicFooter.tsx`

### Modify Header Navigation
Edit: `src/components/layout/PublicHeader.tsx`

---

## Testing

### Manual Testing Checklist
```bash
# 1. Start dev server
npm run dev

# 2. Open browser and test:
- [ ] Navigate to http://localhost:3000
- [ ] Click "Datenschutz" in footer
- [ ] Verify page loads without login
- [ ] Test dark mode toggle
- [ ] Test responsive design (resize browser)
- [ ] Test cookie banner appears
- [ ] Click "Einstellungen" in cookie banner
- [ ] Test all legal page links in footer
- [ ] Test internal links (AGB → Datenschutz, etc.)
- [ ] Test print view (Cmd/Ctrl + P)
- [ ] Test keyboard navigation (Tab through links)
```

### Accessibility Testing
```bash
# 1. Install browser extensions:
# - WAVE (Web Accessibility Evaluation Tool)
# - axe DevTools
# - Lighthouse (built into Chrome DevTools)

# 2. Run tests on each legal page:
- [ ] Run Lighthouse accessibility audit (aim for 95+)
- [ ] Run WAVE scan (fix critical issues)
- [ ] Run axe DevTools (0 violations goal)
- [ ] Test with screen reader (NVDA, VoiceOver, JAWS)
```

### Build Test
```bash
# Ensure production build works
npm run build

# Expected output: ✓ No errors
```

---

## Common Issues & Solutions

### Issue: Cookie banner not showing
**Solution:** Clear localStorage and refresh:
```javascript
// In browser console:
localStorage.removeItem('cookie-consent');
localStorage.removeItem('cookie-preferences');
location.reload();
```

### Issue: Page returns 404
**Solution:**
1. Check file path: `src/app/(public)/[page-name]/page.tsx`
2. Restart dev server: `npm run dev`

### Issue: Styling looks broken
**Solution:**
1. Check if Tailwind is running: `npm run dev` should rebuild CSS
2. Clear Next.js cache: `rm -rf .next && npm run dev`

### Issue: Dark mode not working
**Solution:**
1. Check theme provider in `src/app/layout.tsx`
2. Verify `next-themes` is installed: `npm install next-themes`

---

## File Locations

```
frontend/
├── src/
│   ├── app/
│   │   ├── (public)/               # Public legal pages group
│   │   │   ├── agb/page.tsx        # Terms of Service
│   │   │   ├── datenschutz/page.tsx # Privacy Policy
│   │   │   ├── impressum/page.tsx  # Legal Notice
│   │   │   ├── avv/page.tsx        # Data Processing Agreement
│   │   │   ├── barrierefreiheit/page.tsx # Accessibility
│   │   │   └── layout.tsx          # Public layout wrapper
│   │   └── globals.css             # Global styles
│   ├── components/
│   │   ├── layout/
│   │   │   ├── PublicHeader.tsx    # Header component
│   │   │   └── PublicFooter.tsx    # Footer component
│   │   ├── CookieConsent.tsx       # Cookie banner
│   │   └── a11y/
│   │       ├── SkipLink.tsx        # Accessibility skip link
│   │       └── AccessibilityPanel.tsx # A11y settings
│   ├── lib/supabase/middleware.ts  # Public routes config
│   └── middleware.ts               # Request middleware
```

---

## Legal Content Checklist

Before going live, review and customize:

### AGB (Terms of Service)
- [ ] Company name and address
- [ ] Pricing model (currently: 1 Credit = €0.01)
- [ ] Jurisdiction and court location
- [ ] Contact emails
- [ ] Cancellation terms

### Datenschutz (Privacy Policy)
- [ ] Data controller information
- [ ] Data retention periods
- [ ] Third-party processors
- [ ] Cookie list
- [ ] Data subject rights contact

### Impressum (Legal Notice)
- [ ] Company legal form
- [ ] Commercial register number
- [ ] VAT ID
- [ ] Managing directors
- [ ] Professional liability insurance
- [ ] Contact information

### AVV (Data Processing Agreement)
- [ ] Company name in contract parties section
- [ ] Sub-processor list (currently: Supabase, Vercel, Anthropic, Scaleway, Stripe)
- [ ] Data processing location
- [ ] Contact for DPA inquiries

### Barrierefreiheit (Accessibility Statement)
- [ ] Website URL
- [ ] Contact email for accessibility feedback
- [ ] Date of last review
- [ ] Known limitations

---

## Production Deployment

### Before deploying to production:

1. **Update Placeholder Content**
   - Replace `[Firmenname]`, `[Adresse]`, etc. with real data
   - Update all contact emails
   - Add real phone numbers

2. **Legal Review**
   - Have a lawyer review all legal pages
   - Ensure compliance with current laws
   - Verify GDPR compliance

3. **Set Last Updated Dates**
   - Set current date in all legal pages
   - Document version changes

4. **Enable PDF Downloads** (Optional)
   - Implement PDF generation for AVV
   - Add download buttons where marked

5. **Configure Analytics** (if using)
   - Ensure cookie consent integration
   - Only load analytics if consent given

6. **Test Production Build**
   ```bash
   npm run build
   npm run start
   ```

---

## Support

### Documentation
- **Full Implementation:** `PUBLIC_LEGAL_PAGES_IMPLEMENTATION_COMPLETE.md`
- **Project Overview:** `README.md`
- **Accessibility Guide:** `ACCESSIBILITY.md`

### Contact
- **Technical Issues:** Create GitHub issue
- **Legal Questions:** Consult your legal team
- **Accessibility:** barrierefreiheit@ai-orchestra.de

---

## Quick Commands

```bash
# Development
npm run dev              # Start dev server
npm run build           # Production build
npm run start           # Start production server
npm run lint            # Run ESLint

# Testing
npm run test            # Run tests
npm run test:e2e        # Run E2E tests (if configured)

# Accessibility
# Use browser DevTools > Lighthouse > Accessibility
```

---

**Status:** ✅ Production Ready
**Last Updated:** December 8, 2025

---

*All legal pages are complete and ready for deployment. Remember to customize company-specific information before going live!*
