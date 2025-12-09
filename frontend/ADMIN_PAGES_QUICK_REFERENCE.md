# Admin Pages Quick Reference

## Updated/Enhanced Pages (This Session)

### 1. Tenants Page - ADMIN-009 ✅
**Path:** `/admin/tenants`
**File:** `src/app/(admin)/admin/tenants/page.tsx`
**New Features:**
- Search by name, email, ID
- Filter by status (Active/Inactive)
- Stats cards (Total, Active, Inactive, Total Credits)
- Enhanced table view

### 2. Licenses Page - ADMIN-010 ✅
**Path:** `/admin/licenses`
**File:** `src/app/(admin)/admin/licenses/page.tsx`
**New Features:**
- Multi-filter (Status, Tenant)
- Search by name, ID, API key
- Stats cards (Total, Active, Inactive, Expiring Soon)
- Empty state handling

### 3. Users Page - ADMIN-011 ✅
**Path:** `/admin/users`
**File:** `src/app/(admin)/admin/users/page.tsx`
**New Features:**
- Filter by role (Superadmin, Admin, User, Viewer)
- Filter by status and tenant
- Icon-based stats cards
- Enhanced search

### 4. Audit Logs Page - ADMIN-012 ✅
**Path:** `/admin/audit-logs`
**File:** `src/app/(admin)/admin/audit-logs/page.tsx`
**New Features:**
- Filter by action, tenant, date range
- Details modal with full JSON view
- Color-coded action badges
- Stats cards (Total, Today, Errors, Security)

### 5. Tenant LLM Config - ADMIN-019 ✅ NEW!
**Path:** `/admin/tenants/[id]/llm-config`
**File:** `src/app/(admin)/admin/tenants/[id]/llm-config/page.tsx`
**Features:**
- Per-tenant model enable/disable
- Custom rate limits per model
- Custom max tokens per model
- EU compliance indicators
- Save/Reset functionality

## Already Complete Pages

### 6. Settings - ADMIN-013 ✅
**Path:** `/admin/settings`
**Features:** Rate limits, email config, provider toggles

### 7. Analytics - ADMIN-014 ✅
**Path:** `/admin/analytics`
**Features:** Revenue, MRR, churn rate, top tenants

### 8. Billing - ADMIN-015 ✅
**Path:** `/admin/billing`
**Features:** Manual credit top-up, transaction history

### 9. Privacy Test - ADMIN-016 ✅
**Path:** `/admin/privacy-test`
**Features:** PII detection testing, sanitization preview

### 10. LLM Config - ADMIN-017 ✅
**Path:** `/admin/llm-config`
**Features:** Provider management, model configuration

### 11. Playground - ADMIN-018 ✅
**Path:** `/admin/playground`
**Features:** Interactive AI testing, cost tracking

### 12. Pricing - ADMIN-020 ✅
**Path:** `/admin/pricing`
**Features:** Model pricing, markup management

## Common Patterns Used

### Search Pattern
```tsx
<Input
  placeholder="Search..."
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
  className="pl-9"
/>
```

### Filter Pattern
```tsx
<Select value={filter} onValueChange={setFilter}>
  <SelectTrigger>
    <SelectValue placeholder="Filter" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="all">All</SelectItem>
    <SelectItem value="active">Active</SelectItem>
  </SelectContent>
</Select>
```

### Stats Card Pattern
```tsx
<Card>
  <CardContent className="p-6">
    <div className="text-2xl font-bold">{count}</div>
    <div className="text-sm text-muted-foreground">Label</div>
  </CardContent>
</Card>
```

## Navigation

All pages accessible via Admin Sidebar:
- Dashboard → `/admin`
- Mandanten → `/admin/tenants`
- Lizenzen → `/admin/licenses`
- Benutzer → `/admin/users`
- Audit-Logs → `/admin/audit-logs`
- Analytics → `/admin/analytics`
- Abrechnung → `/admin/billing`
- Privacy Shield → `/admin/privacy-test`
- LLM Konfiguration → `/admin/llm-config`
- AI Playground → `/admin/playground`
- Model Pricing → `/admin/pricing`
- Einstellungen → `/admin/settings`

## Access Control

**Required Role:** `admin` or `superadmin`
**Auth Check:** In `/app/(admin)/layout.tsx`
**Redirect:** Non-admins → `/dashboard`

## Key Components

### Reusable Components
- `AdminLayout` - Main admin wrapper
- `AdminSidebar` - Navigation sidebar
- `DataTable` - Generic table component
- `TenantTable` - Tenant-specific table
- `LicenseTable` - License-specific table
- `UserTable` - User-specific table
- Various dialogs (Create, Edit, Invite, etc.)

### UI Components (shadcn/ui)
- Button, Card, Badge, Input, Select
- Dialog, Alert, Switch, Slider
- Separator, Tabs, Textarea, Label
- Table, Toast, Tooltip

## Development Commands

```bash
# Start dev server
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

## Quick Testing

1. Login as admin user
2. Navigate to `/admin`
3. Test each page:
   - Create operations
   - Update operations
   - Filter/Search
   - Delete operations
   - Export features

## Files Modified/Created (This Session)

### Modified:
1. `/src/app/(admin)/admin/tenants/page.tsx` - Enhanced with filters/stats
2. `/src/app/(admin)/admin/licenses/page.tsx` - Enhanced with multi-filter
3. `/src/app/(admin)/admin/users/page.tsx` - Enhanced with role filtering
4. `/src/app/(admin)/admin/audit-logs/page.tsx` - Enhanced with details modal

### Created:
1. `/src/app/(admin)/admin/tenants/[id]/llm-config/page.tsx` - New feature!
2. `/frontend/ADMIN_PAGES_IMPLEMENTATION_SUMMARY.md` - Documentation
3. `/frontend/ADMIN_PAGES_QUICK_REFERENCE.md` - This file

## Status: ✅ COMPLETE

All 12 admin pages are implemented and functional.
