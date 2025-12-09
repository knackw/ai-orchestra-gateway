# Admin Dashboard Testing Checklist

## Pre-Testing Setup

- [ ] Install missing UI components: `bash INSTALL_UI_COMPONENTS.sh`
- [ ] Verify database schema includes all required tables
- [ ] Ensure Supabase environment variables are configured
- [ ] Create test admin user with role 'admin' or 'superadmin'

## Authentication & Access Control

- [ ] Unauthenticated users are redirected to /login
- [ ] Users with role 'user' are redirected to /dashboard
- [ ] Users with role 'admin' can access /admin
- [ ] Users with role 'superadmin' can access /admin

## Navigation

- [ ] Admin sidebar displays all menu items
- [ ] Active page is highlighted in sidebar
- [ ] All navigation links work correctly
- [ ] "Back to User Dashboard" link redirects to /dashboard

## Dashboard Overview (/admin)

- [ ] All KPI cards display correctly
- [ ] KPI values load from server actions
- [ ] Recent activity feed displays
- [ ] Page is responsive on mobile/tablet/desktop

## Tenants Management (/admin/tenants)

### List View
- [ ] Tenant table loads with all columns
- [ ] Search by name works
- [ ] Sorting works on sortable columns
- [ ] Pagination works correctly
- [ ] Status badges display correctly (Aktiv/Inaktiv)
- [ ] Plan badges display with correct colors
- [ ] Credits progress bar displays

### Create Tenant
- [ ] "Mandant erstellen" button opens dialog
- [ ] Form validation works (required fields)
- [ ] Creating tenant succeeds
- [ ] Success toast appears
- [ ] Table refreshes with new tenant
- [ ] Dialog closes after success

### Edit Tenant
- [ ] "Bearbeiten" action opens edit dialog
- [ ] Form pre-fills with existing data
- [ ] Updating tenant succeeds
- [ ] Changes reflect in table

### Tenant Details
- [ ] "Details anzeigen" opens slide-over sheet
- [ ] All tenant information displays
- [ ] Statistics show (licenses, users, API calls, revenue)

### Actions
- [ ] Deactivate/Activate tenant works
- [ ] Delete tenant shows confirmation
- [ ] Delete tenant removes from list

## Licenses Management (/admin/licenses)

- [ ] License table loads with all columns
- [ ] Tenant name displays (joined data)
- [ ] License key is masked properly
- [ ] Credits remaining displays correctly
- [ ] Status badges work
- [ ] Search by license key works
- [ ] "Lizenz erstellen" button present
- [ ] Sorting works

## Users Management (/admin/users)

- [ ] User table loads with all columns
- [ ] Email and name display
- [ ] Role badges display with correct colors
- [ ] Tenant name displays (joined data)
- [ ] Last login displays or "Noch nie"
- [ ] Status badges work
- [ ] Search by email works
- [ ] "Benutzer einladen" button present

## Audit Logs (/admin/audit-logs)

- [ ] Audit log table loads
- [ ] Timestamps display in German format
- [ ] Tenant names display
- [ ] License keys are masked
- [ ] Action badges display
- [ ] Details are truncated with ellipsis
- [ ] IP addresses display
- [ ] Search by action works
- [ ] "CSV exportieren" button works
- [ ] CSV download includes all data
- [ ] CSV has proper headers

## Settings (/admin/settings)

### General Tab
- [ ] Tab displays
- [ ] App name field loads current value
- [ ] Support email field loads current value
- [ ] Saving changes works
- [ ] Success toast appears

### Billing Tab
- [ ] Default plan field displays
- [ ] Credit pricing field displays
- [ ] Number input accepts decimals
- [ ] Saving changes works

### AI Providers Tab
- [ ] Anthropic toggle displays current state
- [ ] Scaleway toggle displays current state
- [ ] OpenAI toggle displays current state
- [ ] Toggling saves immediately
- [ ] Success toast appears

### Security Tab
- [ ] Rate limit fields display current values
- [ ] Number inputs accept integers
- [ ] Saving changes works

### Email Tab
- [ ] SMTP host field displays
- [ ] SMTP port field displays
- [ ] From email field displays
- [ ] Saving changes works

## Analytics (/admin/analytics)

- [ ] Page loads without errors
- [ ] All KPI cards display
- [ ] Total Revenue displays correctly
- [ ] MRR displays correctly
- [ ] Active Tenants count displays
- [ ] Churn Rate displays
- [ ] Top 10 Tenants list populates
- [ ] Tenant names display
- [ ] Usage counts display
- [ ] Credits used display
- [ ] Chart placeholders display

## Billing (/admin/billing)

### Credit Top-Up Form
- [ ] Form displays correctly
- [ ] Tenant dropdown populates
- [ ] Amount input works
- [ ] Note textarea works
- [ ] Submitting form succeeds
- [ ] Success toast appears
- [ ] Form resets after submit
- [ ] Credit history refreshes

### Statistics
- [ ] Total credits issued calculates correctly
- [ ] Transactions today counts correctly

### Credit History Table
- [ ] Table loads all transactions
- [ ] Date displays in German format
- [ ] Tenant names display
- [ ] Amounts color-coded (green for positive, red for negative)
- [ ] Amount formatting includes +/- sign
- [ ] Type badges display
- [ ] Notes display or show "-"
- [ ] Search by type works

## Responsive Design

### Mobile (< 768px)
- [ ] Sidebar is collapsible or hidden
- [ ] Tables scroll horizontally
- [ ] Forms are usable
- [ ] Buttons are tap-friendly
- [ ] Dialogs/sheets are full-screen

### Tablet (768px - 1024px)
- [ ] Sidebar displays
- [ ] Tables fit reasonably
- [ ] Cards layout adjusts
- [ ] Forms are well-spaced

### Desktop (> 1024px)
- [ ] Full layout displays
- [ ] All columns visible
- [ ] Optimal spacing
- [ ] No horizontal scroll

## Dark Mode

- [ ] All pages support dark mode
- [ ] Text is readable
- [ ] Badges have appropriate contrast
- [ ] Cards have proper background
- [ ] Tables are readable
- [ ] Forms are usable
- [ ] No white flashes on page load

## Error Handling

- [ ] Network errors show toast notifications
- [ ] Form validation errors display inline
- [ ] Empty states display properly
- [ ] Loading states show "Lädt..."
- [ ] Failed actions show error toasts

## Performance

- [ ] Pages load within 2 seconds
- [ ] Tables with 100+ rows perform well
- [ ] Search/filter is responsive
- [ ] No layout shifts during load
- [ ] Images/icons load quickly

## German Localization

- [ ] All labels are in German
- [ ] All buttons are in German
- [ ] All toasts are in German
- [ ] All error messages are in German
- [ ] Dates use German format (DD.MM.YYYY)
- [ ] Numbers use German format (1.000,00)

## Security

- [ ] Audit logs created for:
  - [ ] Tenant creation/update/deletion
  - [ ] License creation/credit additions
  - [ ] User invitations/role changes
  - [ ] Manual credit top-ups
  - [ ] Settings changes
- [ ] Sensitive operations require confirmation
- [ ] No PII exposed in logs
- [ ] API keys/secrets are masked

## Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Known Issues / TODOs

- [ ] Chart components not yet implemented (Analytics page)
- [ ] License Create/Edit dialogs not fully implemented
- [ ] User Invite/Edit dialogs not fully implemented
- [ ] Bulk actions not yet implemented
- [ ] Email template editing not implemented
- [ ] Logo upload not implemented
- [ ] Provider connection testing not fully implemented

## Notes

Add any additional testing notes here:

---

**Testing Date**: __________
**Tester**: __________
**Browser**: __________
**Environment**: __________
