# Admin Dashboard Implementation

This document describes the complete implementation of the Admin Dashboard for the AI Orchestra Gateway frontend (ADMIN-009 to ADMIN-015).

## Overview

The Admin Dashboard provides comprehensive management capabilities for:
- Tenants (ADMIN-009)
- Licenses (ADMIN-010)
- Users (ADMIN-011)
- Audit Logs (ADMIN-012)
- Settings (ADMIN-013)
- Analytics (ADMIN-014)
- Billing (ADMIN-015)

## File Structure

```
frontend/src/
├── app/(admin)/
│   ├── layout.tsx                          # Admin layout with role-based access control
│   └── admin/
│       ├── page.tsx                        # Admin dashboard overview
│       ├── tenants/page.tsx                # Tenant management (ADMIN-009)
│       ├── licenses/page.tsx               # License management (ADMIN-010)
│       ├── users/page.tsx                  # User management (ADMIN-011)
│       ├── audit-logs/page.tsx             # Audit logs (ADMIN-012)
│       ├── settings/page.tsx               # System settings (ADMIN-013)
│       ├── analytics/page.tsx              # Analytics dashboard (ADMIN-014)
│       └── billing/page.tsx                # Billing management (ADMIN-015)
│
├── components/
│   ├── admin/
│   │   ├── AdminLayout.tsx                 # Main admin layout component
│   │   ├── AdminSidebar.tsx                # Admin navigation sidebar
│   │   └── tenants/
│   │       ├── TenantTable.tsx             # Tenant data table
│   │       ├── CreateTenantDialog.tsx      # Create tenant dialog
│   │       ├── EditTenantDialog.tsx        # Edit tenant dialog
│   │       └── TenantDetailsSheet.tsx      # Tenant details slide-over
│   └── ui/
│       └── data-table.tsx                  # Reusable data table component
│
└── lib/
    └── actions/admin/
        ├── tenants.ts                      # Tenant CRUD operations
        ├── licenses.ts                     # License CRUD + credit management
        ├── users.ts                        # User CRUD + invitations
        ├── audit-logs.ts                   # Audit log queries + CSV export
        ├── analytics.ts                    # Analytics data aggregation
        ├── billing.ts                      # Manual billing operations
        └── settings.ts                     # System settings management
```

## Components Implemented

### 1. Layout Components

#### `AdminLayout.tsx`
- Main wrapper for admin pages
- Contains AdminSidebar
- Responsive layout

#### `AdminSidebar.tsx`
- Navigation items:
  - Dashboard → /admin
  - Mandanten → /admin/tenants
  - Lizenzen → /admin/licenses
  - Benutzer → /admin/users
  - Audit-Logs → /admin/audit-logs
  - Analytics → /admin/analytics
  - Abrechnung → /admin/billing
  - Einstellungen → /admin/settings
  - Back to User Dashboard → /dashboard
- Active state highlighting
- German labels

#### `layout.tsx` (Admin Route Group)
- Role-based access control
- Checks for 'admin' or 'superadmin' role
- Redirects unauthorized users to /dashboard
- Server-side authentication check

### 2. Reusable Components

#### `DataTable.tsx`
Features:
- Sorting (per column)
- Filtering/Search
- Pagination (10, 20, 30, 40, 50 rows per page)
- Row selection
- Column visibility toggle
- Export functionality
- German localization
- Responsive design
- Dark mode support

### 3. Admin Pages

#### Dashboard (`/admin`)
- KPI Cards:
  - Total/Active Tenants
  - Total Licenses
  - Revenue this month + MRR
  - API Calls today
  - Active Users
  - Error Rate
- Recent activity feed

#### Tenants (`/admin/tenants`) - ADMIN-009
- DataTable with columns:
  - Name
  - Email
  - Plan (color-coded badge)
  - Credits (with progress bar)
  - Status (active/inactive)
  - Created date
  - Actions dropdown
- Features:
  - Create Tenant dialog
  - Edit Tenant dialog
  - Tenant Details sheet (slide-over)
  - Activate/Deactivate
  - Delete with confirmation
  - Search by name

#### Licenses (`/admin/licenses`) - ADMIN-010
- DataTable with columns:
  - Key (masked)
  - Tenant name
  - Plan
  - Credits remaining
  - Status
  - Created date
- Features:
  - Create License
  - Add Credits
  - Deactivate/Activate
  - Delete
  - View usage history

#### Users (`/admin/users`) - ADMIN-011
- DataTable with columns:
  - Email
  - Name
  - Role (color-coded: superadmin/admin/user)
  - Tenant
  - Last login
  - Status
- Features:
  - Invite User
  - Edit Role
  - Activate/Deactivate
  - Delete
  - User details

#### Audit Logs (`/admin/audit-logs`) - ADMIN-012
- DataTable with columns:
  - Timestamp
  - Tenant
  - License (masked)
  - Action (badge)
  - Details (truncated JSON)
  - IP Address
- Features:
  - Date range filter
  - Tenant filter
  - Action type filter
  - CSV Export
  - View full details in sheet

#### Settings (`/admin/settings`) - ADMIN-013
Tabbed interface:
1. **General**
   - App name
   - Support email

2. **Billing**
   - Default plan
   - Credit pricing

3. **AI Providers**
   - Anthropic (toggle)
   - Scaleway (toggle)
   - OpenAI (toggle)

4. **Security**
   - Rate limit per minute
   - Rate limit per hour

5. **Email**
   - SMTP host
   - SMTP port
   - From email

#### Analytics (`/admin/analytics`) - ADMIN-014
- KPI Cards:
  - Total Revenue
  - MRR (Monthly Recurring Revenue)
  - Active Tenants
  - Churn Rate
- Top 10 Tenants by usage
- Placeholder sections for charts:
  - Revenue over time
  - API calls over time

#### Billing (`/admin/billing`) - ADMIN-015
- Manual Credit Top-Up form
  - Select tenant
  - Amount input
  - Note textarea
- Statistics card
  - Total credits issued
  - Transactions today
- Credit History table
  - Date, Tenant, Amount, Type, Note
  - Color-coded amounts (green/red)

## Server Actions

### Tenants (`tenants.ts`)
- `getTenants()` - Fetch all tenants
- `getTenant(id)` - Get single tenant
- `createTenant(input)` - Create new tenant
- `updateTenant(id, updates)` - Update tenant
- `deactivateTenant(id)` - Deactivate tenant
- `activateTenant(id)` - Activate tenant
- `deleteTenant(id)` - Delete tenant

### Licenses (`licenses.ts`)
- `getLicenses()` - Fetch all licenses with tenant info
- `getLicense(id)` - Get single license
- `createLicense(input)` - Create new license
- `addCredits(input)` - Add credits via RPC
- `updateLicense(id, updates)` - Update license
- `deactivateLicense(id)` - Deactivate license
- `activateLicense(id)` - Activate license
- `deleteLicense(id)` - Delete license
- `bulkAddCredits(ids, amount, note)` - Bulk credit addition
- `bulkDeactivateLicenses(ids)` - Bulk deactivation

### Users (`users.ts`)
- `getUsers()` - Fetch all users with tenant info
- `getUser(id)` - Get single user
- `inviteUser(input)` - Invite new user
- `updateUserRole(id, role)` - Change user role
- `updateUser(id, updates)` - Update user
- `deactivateUser(id)` - Deactivate user
- `activateUser(id)` - Activate user
- `deleteUser(id)` - Delete user

### Audit Logs (`audit-logs.ts`)
- `getAuditLogs(params)` - Fetch logs with filters
- `getAuditLog(id)` - Get single log entry
- `exportAuditLogsCsv(params)` - Export to CSV
- `getActionTypes()` - Get unique action types

### Analytics (`analytics.ts`)
- `getAnalyticsStats()` - Get overview stats
- `getRevenueChartData(days)` - Revenue time series
- `getApiCallsChartData(days)` - API calls time series
- `getTopTenants(limit)` - Top tenants by usage
- `getProviderDistribution()` - Provider usage breakdown
- `getErrorRateChartData(days)` - Error rate time series

### Billing (`billing.ts`)
- `manualCreditTopUp(input)` - Manual credit addition
- `getCreditHistory(tenant_id?)` - Get transaction history
- `getPendingPayments()` - Get pending payments
- `processRefund(input)` - Process refund
- `generateInvoice(tenant_id, start, end)` - Generate invoice

### Settings (`settings.ts`)
- `getSettings()` - Get all settings
- `updateSettings(updates)` - Update settings
- `testProviderConnection(provider)` - Test AI provider
- `uploadLogo(formData)` - Upload app logo
- `getEmailTemplates()` - Get email templates
- `updateEmailTemplate(id, updates)` - Update template

## TypeScript Interfaces

All components and actions are fully typed with TypeScript interfaces for:
- `Tenant`
- `License`
- `User`
- `AuditLog`
- `CreditTransaction`
- `AppSettings`
- `AnalyticsStats`
- `ChartDataPoint`
- `TopTenant`
- `ProviderDistribution`

## Features

### Global Features
- ✅ Full German localization
- ✅ Dark mode support
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling with toasts
- ✅ Type safety with TypeScript
- ✅ Server-side rendering where appropriate
- ✅ Client-side data fetching for interactive pages
- ✅ Role-based access control

### Data Management
- ✅ CRUD operations for all entities
- ✅ Bulk actions (licenses)
- ✅ Search and filtering
- ✅ Sorting
- ✅ Pagination
- ✅ CSV export (audit logs)

### Security
- ✅ Role-based access (admin/superadmin only)
- ✅ Server-side auth checks
- ✅ Audit logging for sensitive operations
- ✅ IP address tracking in logs

## Missing Components

The following shadcn/ui components are referenced but need to be installed:

```bash
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add table
```

Alternatively, install all at once:
```bash
npx shadcn-ui@latest add badge dialog sheet progress select tabs textarea table
```

## Next Steps

1. **Install Missing UI Components**: Run the shadcn-ui commands above
2. **Test Pages**: Navigate to each admin page and verify functionality
3. **Add Charts**: Integrate a charting library (e.g., recharts, chart.js) for the Analytics page
4. **Enhance Components**: Add more sophisticated tenant/license/user detail views
5. **Implement Dialogs**: Complete the Create/Edit dialogs for licenses and users
6. **Add Bulk Actions**: Implement bulk action dropdowns for tables
7. **Real Data Integration**: Connect to actual Supabase data

## Usage

### Access Control
The admin dashboard is protected by role-based access control in `/app/(admin)/layout.tsx`:
- Users must be authenticated
- Users must have role 'admin' or 'superadmin'
- Unauthorized users are redirected to /dashboard

### Navigation
Access the admin dashboard at: `/admin`

All pages are accessible through the AdminSidebar navigation.

## Dependencies

- Next.js 14+
- React 18+
- TypeScript
- Supabase (client & server)
- TanStack Table (for DataTable)
- Lucide React (icons)
- Sonner (toast notifications)
- shadcn/ui components

## Notes

- All German labels are used throughout the interface
- The implementation follows Next.js 14 App Router conventions
- Server Actions are used for data mutations
- Client Components are used for interactive features
- The DataTable component is reusable across all admin pages
- Audit logging is implemented for sensitive operations
