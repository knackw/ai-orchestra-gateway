# Dashboard Routes Reference

Quick reference for all dashboard routes in the AI Orchestra Gateway frontend.

## Main Dashboard Routes

| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | Dashboard Overview | Main dashboard with stats and quick actions |
| `/api-keys` | API Keys | Manage API keys for authentication |
| `/analytics` | Usage & Analytics | Detailed usage metrics and charts |
| `/billing` | Billing | Manage subscription, credits, and payments |
| `/settings` | Settings | Account settings and preferences |
| `/help` | Help | External help resources |

## File Locations

```
/root/Projekte/ai-orchestra-gateway/frontend/src/app/(dashboard)/
├── layout.tsx                 # Shared layout
├── dashboard/page.tsx        # Dashboard overview
├── api-keys/page.tsx         # API keys page
├── analytics/page.tsx        # Analytics page
├── billing/page.tsx          # Billing page
└── settings/page.tsx         # Settings page
```

## Navigation Components

- **Sidebar:** `/src/components/dashboard/Sidebar.tsx`
- **Mobile Nav:** `/src/components/dashboard/MobileNav.tsx`
- **Header:** `/src/components/dashboard/Header.tsx`

## Key Features per Page

### Dashboard (`/dashboard`)
- Credit balance card
- 4 stat cards with trends
- Usage chart (7 days)
- Recent activity table
- Quick action buttons

### API Keys (`/api-keys`)
- API keys table
- Create new key dialog
- Copy/rotate/delete actions
- Getting started code example

### Analytics (`/analytics`)
- Date range selector
- API key filter
- Export to CSV
- 4 summary cards
- 4 charts (line, area, bar, pie)
- Top models section
- Response time metrics
- Request logs table

### Billing (`/billing`)
- Current plan card
- Credit balance widget
- Buy credits section (4 packages)
- Payment methods manager
- Invoice history table

### Settings (`/settings`)
5 tabs:
- Profile (avatar, name, email, company)
- Security (password, 2FA, sessions)
- Notifications (7 email preferences)
- API Settings (provider, rate limit)
- Danger Zone (delete account)

## Quick Navigation

From any dashboard page, users can navigate via:

1. **Sidebar** (desktop) - Always visible on left
2. **Mobile Menu** (mobile) - Hamburger icon in header
3. **Quick Actions** - Buttons on dashboard overview
4. **User Menu** - Avatar dropdown in header

## Protected Routes

All routes under `(dashboard)` are meant to be protected. Authentication should be added to:
- Layout: `/src/app/(dashboard)/layout.tsx`
- Or Middleware: `/src/middleware.ts`

Example protection:
```tsx
// In layout.tsx or middleware
const session = await getSession()
if (!session) {
  redirect('/login')
}
```

## External Links

| Link | Purpose |
|------|---------|
| `/docs` | API Documentation |
| `/help` | Help Center |
| `/pricing` | Pricing page |

---

**Created:** December 8, 2025
**Status:** Complete
