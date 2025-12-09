# AI Orchestra Gateway - Frontend Features Documentation

**Version:** 2.0
**Last Updated:** December 2025

This document provides a comprehensive overview of all features implemented in the AI Orchestra Gateway frontend.

---

## Table of Contents

1. [Design System](#design-system)
2. [Architecture](#architecture)
3. [Authentication & Authorization](#authentication--authorization)
4. [Public Pages](#public-pages)
5. [User Dashboard](#user-dashboard)
6. [Admin Panel](#admin-panel)
7. [Components Library](#components-library)
8. [Internationalization](#internationalization)
9. [Accessibility](#accessibility)
10. [API Integration](#api-integration)

---

## Design System

### Color Palette

The application uses a carefully designed color system optimized for both light and dark modes:

#### Light Mode
- **Primary Blue:** `#3B82F6` (hsl(217, 91%, 60%)) - Main brand color for buttons, links, and emphasis
- **Success Green:** `#10B981` (hsl(160, 84%, 39%)) - Positive actions, success states
- **Warning Orange:** `#F59E0B` (hsl(38, 92%, 50%)) - Caution messages, warnings
- **Error Red:** `#EF4444` (hsl(0, 84%, 60%)) - Errors, destructive actions
- **Background:** White `#FFFFFF`
- **Foreground:** Dark gray for text
- **Muted:** Light gray for secondary text and backgrounds

#### Dark Mode
All colors are automatically adjusted for optimal contrast and readability in dark mode.

### Typography
- **Font Family:** System fonts (SF Pro, Segoe UI, Roboto)
- **Headings:** Bold weights (600-700)
- **Body:** Regular weight (400)
- **Code:** Monospace font family

### Spacing
- Consistent 4px/8px base grid
- Responsive breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)

### Border Radius
- Small: 4px
- Medium: 6px
- Large: 8px
- Default (--radius): 8px

---

## Architecture

### Next.js 15 App Router

The application uses Next.js 15 with the App Router architecture:

```
app/
├── (landing)/          # Public pages (no auth required)
├── (auth)/             # Authentication pages
├── (dashboard)/        # User dashboard (protected)
├── (admin)/            # Admin panel (admin role required)
├── api/                # API routes
└── layout.tsx          # Root layout
```

### Route Groups
- **(landing)**: Public marketing pages, legal pages
- **(auth)**: Login, signup, password reset
- **(dashboard)**: User dashboard with usage stats, API keys, billing
- **(admin)**: Admin-only pages for tenant management, analytics

### Middleware
- **Authentication:** Automatic session refresh using Supabase
- **Route Protection:** Redirects unauthenticated users to login
- **Role-Based Access:** Admin routes protected by role check

---

## Authentication & Authorization

### Supabase Auth Integration

#### Client-Side Auth
- **Location:** `src/lib/supabase/client.ts`
- Browser-based authentication with automatic cookie management

#### Server-Side Auth
- **Location:** `src/lib/supabase/server.ts`
- Server Components and API routes authentication

#### Middleware
- **Location:** `src/lib/supabase/middleware.ts`
- Automatic session refresh on every request
- Route protection for authenticated pages

### Pages

#### Login (`/login`)
- Email + Password authentication
- OAuth providers (optional)
- "Remember me" functionality
- Password reset link
- Redirect to dashboard after login

#### Signup (`/signup`)
- Email + Password registration
- Email verification required
- Automatic tenant creation
- Terms & Privacy acceptance checkbox
- Redirect to email verification page

#### Password Reset (`/reset-password`)
- Request reset email
- Secure token validation
- New password confirmation

#### Email Verification (`/verify-email`)
- Automatic verification on link click
- Manual resend verification email
- Clear instructions

---

## Public Pages

### Landing Page (`/`)

**Components:**
- `Hero` - Eye-catching headline with CTA
- `Features` - Key platform features (Privacy Shield, Multi-Provider, Credit System)
- `Pricing` - Pricing tiers with comparison
- `Testimonials` - Customer reviews
- `FAQ` - Common questions
- `CTA` - Final call-to-action
- `Footer` - Links, social media, legal

**Features:**
- Responsive design
- Dark mode support
- Smooth scroll animations
- Mobile-optimized

### Pricing Page (`/pricing`)
- Detailed pricing tiers
- Feature comparison table
- Credit packages
- Enterprise options
- FAQ section

### Documentation (`/docs`)
- Getting started guide
- API reference
- Code examples
- Integration tutorials

### Blog (`/blog`)
- News and updates
- Technical articles
- Use cases
- Industry insights

### Legal Pages

#### Datenschutz (`/datenschutz`) - Privacy Policy
**Content:**
- DSGVO-compliant privacy policy
- Data collection and processing
- Third-party services (Anthropic, Scaleway, Stripe)
- User rights (GDPR Art. 15-21)
- Privacy Shield technology explanation
- Cookie policy
- Data retention periods
- AVV (Data Processing Agreement) information

#### Impressum (`/impressum`) - Legal Notice
**Content:**
- Company information (§5 TMG compliant)
- Contact details
- Registration information
- VAT ID
- Liability disclaimer
- Copyright notice
- Dispute resolution

#### AGB (`/agb`) - Terms of Service
**Content:**
- Scope of services
- Contract formation
- Credit-based pricing model
- User obligations
- Service availability (99.5% SLA)
- Data protection (DSGVO)
- Liability limitations
- Termination rights
- Intellectual property
- Governing law (German law)

---

## User Dashboard

### Overview (`/dashboard`)

**Widgets:**
- **Credit Balance:** Current credits with trend
- **Usage Stats:** Requests today/month, tokens, error rate
- **Active API Keys:** Quick count
- **Recent Activity:** Last API calls with status
- **Usage Chart:** 7/30/90 day request trends

**Data Sources:**
- Real-time credit balance from Supabase
- Usage statistics from backend API
- Recharts for visualizations

### API Keys (`/dashboard/api-keys`)

**Features:**
- List all API keys with metadata
- Create new API key with name
- Copy key to clipboard (shown once)
- View last used timestamp
- Revoke/delete keys
- Key prefix display (security)

**Implementation:**
- Secure key generation on backend
- Client-side clipboard API
- Toast notifications

### Usage Analytics (`/dashboard/usage`)

**Features:**
- Date range selector (7d/30d/90d/custom)
- Total requests and tokens
- Breakdown by model (Claude, Scaleway)
- Credit usage per model
- Export to CSV/JSON
- Interactive charts (Recharts)

**Metrics:**
- Request count
- Token usage (prompt + completion)
- Credits consumed
- Average response time
- Error rate

### Billing (`/dashboard/billing`)

**Features:**
- Current credit balance (large display)
- Credit purchase options (packages)
- Transaction history with pagination
- Stripe integration for payments
- Invoice download (PDF)
- Auto-refill settings (future)

**Payment Flow:**
1. Select credit package
2. Redirect to Stripe Checkout
3. Payment confirmation
4. Credits added automatically
5. Receipt email sent

### Settings (`/dashboard/settings`)

**Sections:**

#### Profile
- Name, email, company
- Avatar upload
- Password change
- 2FA setup (future)

#### Preferences
- Language selection (DE/EN)
- Dark mode toggle
- Email notifications
- Timezone

#### API Configuration
- Default model selection
- Rate limit preferences
- Webhook URL for usage alerts

#### Danger Zone
- Export all data (GDPR)
- Delete account

---

## Admin Panel

**Access:** Requires `admin` role in user profile

### Admin Overview (`/admin`)

**KPIs:**
- Total tenants (active/inactive)
- Total users
- Credits distributed
- Requests today/month
- Revenue (current month)
- System health status

**Charts:**
- Usage trends (7/30 days)
- Top tenants by usage
- Model distribution
- Revenue over time

### Tenant Management (`/admin/tenants`)

**Features:**
- List all tenants with search/filter
- Create new tenant
- Edit tenant details
- Activate/deactivate tenant
- View tenant usage
- Add/deduct credits
- IP whitelist management
- Delete tenant (with confirmation)

**Tenant Details:**
- Name, email, status
- Created date
- Credit balance
- Total requests
- Active licenses
- Usage history
- Allowed IPs

### License Management (`/admin/licenses`)

**Features:**
- List all licenses by tenant
- Create new license
- Set credits included
- Define validity period
- Revoke license
- View license usage

**License Types:**
- Time-based (valid_from → valid_until)
- Credit-based (credits_included)
- Combined (time + credits)

### User Management (`/admin/users`)

**Features:**
- List all users across tenants
- View user details
- Assign roles (user/admin)
- Suspend/unsuspend users
- View user activity
- Force password reset

### Analytics Dashboard (`/admin/analytics`)

**Views:**

#### Overview
- Total requests, credits, revenue
- Active vs inactive tenants
- Model usage distribution
- Error rates

#### Usage by Model
- Requests per model
- Credits consumed per model
- Average cost per request
- Trend over time

#### Usage by Tenant
- Top 10 tenants by usage
- Credit consumption
- Request patterns
- Anomaly detection

#### Time Series
- Hourly/daily/monthly trends
- Peak usage times
- Seasonal patterns

**Export Options:**
- CSV export for all data
- Date range selection
- Filter by tenant/model

### Audit Logs (`/admin/audit-logs`)

**Tracked Actions:**
- User login/logout
- Tenant creation/modification
- License creation/revocation
- Credit adjustments
- Settings changes
- API key generation

**Log Details:**
- Timestamp
- User/Admin who performed action
- Action type
- Resource type and ID
- IP address
- User agent
- Additional metadata (JSON)

**Features:**
- Real-time log streaming
- Search by action, user, tenant
- Date range filter
- Export logs
- Retention: 90 days

### Billing Management (`/admin/billing`)

**Features:**
- Stripe integration
- View all transactions
- Generate invoices
- Manage subscriptions (if applicable)
- Refund requests
- Revenue reports

### System Settings (`/admin/settings`)

**Configuration:**
- Global rate limits
- Default credit packages
- Email templates
- Webhook endpoints
- Feature flags
- Maintenance mode

---

## Components Library

### UI Components (shadcn/ui)

All components are based on Radix UI with custom styling:

- **Button** - Primary, secondary, outline, ghost variants
- **Card** - Content containers with header/footer
- **Dialog** - Modals and overlays
- **Dropdown Menu** - Context menus
- **Input** - Text inputs with validation
- **Select** - Dropdown selectors
- **Switch** - Toggle switches
- **Tabs** - Tabbed interfaces
- **Toast** - Notification system
- **Progress** - Progress bars
- **Badge** - Status indicators
- **Avatar** - User avatars
- **Checkbox** - Checkboxes
- **Radio Group** - Radio buttons
- **Slider** - Range sliders
- **Textarea** - Multi-line text input
- **Tooltip** - Hover tooltips
- **Accordion** - Collapsible sections
- **Alert Dialog** - Confirmation modals
- **Popover** - Floating panels
- **Separator** - Dividers

### Custom Components

#### Landing Components (`src/components/landing/`)
- `Hero` - Landing page hero section
- `Features` - Feature showcase grid
- `Pricing` - Pricing cards
- `Testimonials` - Customer testimonials carousel
- `FAQ` - Frequently asked questions accordion
- `CTA` - Call-to-action sections
- `Navbar` - Navigation header
- `Footer` - Site footer

#### Shared Components (`src/components/shared/`)
- `SkipLink` - Accessibility skip to main content
- `AccessibilityPanel` - A11y settings panel
- `LanguageSwitcher` - Language toggle (DE/EN)

### Providers

#### ThemeProvider (`src/components/providers/theme-provider.tsx`)
- Dark mode toggle
- System preference detection
- Persistent theme selection

---

## Internationalization

### next-intl Integration

**Supported Languages:**
- **German (de):** Primary language
- **English (en):** Secondary language

**Translation Files:**
- `messages/de.json` - German translations
- `messages/en.json` - English translations

**Usage:**
```tsx
import { useTranslations } from 'next-intl';

const t = useTranslations('Dashboard');
<h1>{t('title')}</h1>
```

**Features:**
- Automatic locale detection
- URL-based locale switching
- Server-side translations
- Type-safe translation keys

---

## Accessibility

### WCAG 2.1 Level AA Compliance

**Features:**

#### Keyboard Navigation
- Full keyboard support (Tab, Enter, Escape)
- Focus indicators on all interactive elements
- Skip links to main content

#### Screen Reader Support
- ARIA labels and roles
- Semantic HTML
- Alt text for images
- Descriptive link text

#### Visual Accessibility
- High contrast mode
- Adjustable font sizes
- Focus indicators (3px outline)
- Color contrast ratios (4.5:1 minimum)

#### Motion & Animations
- Reduced motion support
- Configurable animation preferences
- No auto-playing videos

**Accessibility Panel (`/dashboard/settings`):**
- Toggle high contrast
- Toggle reduced motion
- Adjust font size
- Enable focus indicators

---

## API Integration

### Backend Communication

**Location:** `src/lib/api.ts`

### API Client Features

- **Type-safe:** Full TypeScript definitions
- **Error handling:** Custom ApiError class
- **Authentication:** Automatic Bearer token injection
- **Query parameters:** Automatic URL encoding
- **JSON handling:** Automatic serialization/deserialization

### Available API Methods

#### Health Check
```typescript
api.healthCheck() // GET /health
```

#### Generation
```typescript
api.generate(request, token) // POST /api/v1/generate
```

#### Tenants (Admin)
```typescript
api.tenants.list(token, params)      // GET /api/admin/tenants
api.tenants.get(id, token)           // GET /api/admin/tenants/:id
api.tenants.create(data, token)      // POST /api/admin/tenants
api.tenants.update(id, data, token)  // PATCH /api/admin/tenants/:id
api.tenants.delete(id, token)        // DELETE /api/admin/tenants/:id
```

#### Licenses (Admin)
```typescript
api.licenses.list(token, params)    // GET /api/admin/licenses
api.licenses.create(data, token)    // POST /api/admin/licenses
api.licenses.revoke(id, token)      // POST /api/admin/licenses/:id/revoke
```

#### Analytics (Admin)
```typescript
api.analytics.overview(token)            // GET /api/admin/analytics/overview
api.analytics.byModel(token, params)     // GET /api/admin/analytics/usage-by-model
api.analytics.byTenant(token, params)    // GET /api/admin/analytics/usage-by-tenant
```

#### Audit Logs (Admin)
```typescript
api.auditLogs.list(token, params)   // GET /api/admin/audit-logs
```

#### Usage Stats (User)
```typescript
api.usage.stats(token, params)      // GET /api/v1/usage
```

#### Billing (User)
```typescript
api.billing.balance(token)              // GET /api/v1/billing/credits
api.billing.transactions(token, params) // GET /api/v1/billing/transactions
api.billing.purchase(amount, token)     // POST /api/v1/billing/purchase
```

#### API Keys (User)
```typescript
api.apiKeys.list(token)            // GET /api/v1/api-keys
api.apiKeys.create(data, token)    // POST /api/v1/api-keys
api.apiKeys.revoke(id, token)      // DELETE /api/v1/api-keys/:id
```

#### Profile (User)
```typescript
api.profile.get(token)             // GET /api/v1/profile
api.profile.update(data, token)    // PATCH /api/v1/profile
```

### Error Handling

```typescript
try {
  const data = await api.tenants.list(token);
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.status}: ${error.message}`);
    // Access error.data for additional details
  } else {
    console.error('Network error:', error);
  }
}
```

---

## Testing

### Unit Tests (Vitest)
- Component tests with React Testing Library
- Hook tests
- Utility function tests

**Run tests:**
```bash
npm run test        # Watch mode
npm run test:run    # Single run
npm run test:coverage # Coverage report
```

### E2E Tests (Playwright)
- User flows (signup, login, dashboard)
- Admin flows (tenant management)
- Payment flows (Stripe checkout)

**Run E2E tests:**
```bash
npm run e2e         # Headless
npm run e2e:headed  # With browser
npm run e2e:ui      # Interactive mode
```

---

## Performance Optimizations

### Next.js Optimizations
- **Image Optimization:** Automatic with next/image
- **Font Optimization:** next/font for web fonts
- **Code Splitting:** Automatic route-based splitting
- **Static Generation:** Pre-rendered pages where possible
- **ISR:** Incremental Static Regeneration for dynamic content

### Loading States
- Skeleton loaders for async content
- Suspense boundaries
- Progressive enhancement

### Caching
- SWR for client-side data fetching
- Supabase query caching
- Static asset caching (CDN)

---

## Security Features

### Authentication Security
- Secure session management (Supabase)
- HTTP-only cookies
- CSRF protection
- Rate limiting on login attempts

### Data Protection
- Environment variable separation
- No sensitive data in client-side code
- API keys hidden after creation
- Secure password hashing (Supabase)

### GDPR Compliance
- Privacy Policy (Datenschutz)
- Cookie consent (if needed)
- Data export functionality
- Account deletion
- Audit logs

---

## Deployment

### Vercel (Recommended)
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Docker
```bash
docker build -t ai-orchestra-frontend .
docker run -p 3000:3000 ai-orchestra-frontend
```

### Environment Variables
See `.env.local.example` for required variables.

---

## Future Roadmap

### Planned Features
- [ ] Webhook management UI
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] SSO integration (SAML, OAuth)
- [ ] Custom domain support for white-label
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSockets)
- [ ] AI model comparison tool
- [ ] Prompt library and templates
- [ ] Cost optimization recommendations

---

## Support & Contact

- **Documentation:** [/docs](/docs)
- **Support Email:** support@ai-orchestra.de
- **GitHub Issues:** [Issues](https://github.com/your-org/ai-orchestra-gateway/issues)

---

**Last Updated:** December 2025
**Version:** 2.0
