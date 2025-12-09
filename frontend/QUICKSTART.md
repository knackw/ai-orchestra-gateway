# AI Orchestra Gateway - Frontend Quick Start Guide

**Version:** 2.0
**Time to Setup:** ~10 minutes

---

## Prerequisites

Before you begin, ensure you have:

- ✓ Node.js 18+ installed ([Download](https://nodejs.org/))
- ✓ npm or yarn package manager
- ✓ A Supabase account ([Sign up free](https://supabase.com))
- ✓ A Stripe account ([Sign up](https://stripe.com))
- ✓ Backend API running (see backend README)

---

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd /root/Projekte/ai-orchestra-gateway/frontend
npm install
```

**Expected time:** 2-3 minutes

---

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your credentials:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...

# App URLs
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Metadata
NEXT_PUBLIC_APP_NAME="AI Orchestra Gateway"
NEXT_PUBLIC_APP_DESCRIPTION="High-security AI orchestration middleware"
```

**Where to find these values:**

#### Supabase
1. Go to [app.supabase.com](https://app.supabase.com)
2. Select your project
3. Go to Settings → API
4. Copy:
   - Project URL → `NEXT_PUBLIC_SUPABASE_URL`
   - `anon` `public` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role` `secret` key → `SUPABASE_SERVICE_ROLE_KEY`

#### Stripe
1. Go to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Developers → API keys
3. Copy:
   - Publishable key → `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
   - Secret key → `STRIPE_SECRET_KEY`
4. Developers → Webhooks → Add endpoint
5. Add endpoint URL: `http://localhost:3000/api/webhooks/stripe`
6. Copy webhook secret → `STRIPE_WEBHOOK_SECRET`

---

### 3. Start Development Server

```bash
npm run dev
```

**Output:**
```
▲ Next.js 15.5.7
- Local:        http://localhost:3000
- Environments: .env.local

✓ Ready in 2.3s
```

---

### 4. Open Your Browser

Navigate to: [http://localhost:3000](http://localhost:3000)

You should see the **AI Orchestra Gateway** landing page.

---

## Quick Navigation

### Public Pages
- **Landing:** [http://localhost:3000/](http://localhost:3000/)
- **Pricing:** [http://localhost:3000/pricing](http://localhost:3000/pricing)
- **Docs:** [http://localhost:3000/docs](http://localhost:3000/docs)
- **Legal:**
  - [Privacy Policy (Datenschutz)](http://localhost:3000/datenschutz)
  - [Legal Notice (Impressum)](http://localhost:3000/impressum)
  - [Terms of Service (AGB)](http://localhost:3000/agb)

### Authentication
- **Login:** [http://localhost:3000/login](http://localhost:3000/login)
- **Signup:** [http://localhost:3000/signup](http://localhost:3000/signup)

### User Dashboard (requires login)
- **Overview:** [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- **API Keys:** [http://localhost:3000/dashboard/api-keys](http://localhost:3000/dashboard/api-keys)
- **Usage:** [http://localhost:3000/dashboard/usage](http://localhost:3000/dashboard/usage)
- **Billing:** [http://localhost:3000/dashboard/billing](http://localhost:3000/dashboard/billing)
- **Settings:** [http://localhost:3000/dashboard/settings](http://localhost:3000/dashboard/settings)

### Admin Panel (requires admin role)
- **Admin Overview:** [http://localhost:3000/admin](http://localhost:3000/admin)
- **Tenants:** [http://localhost:3000/admin/tenants](http://localhost:3000/admin/tenants)
- **Licenses:** [http://localhost:3000/admin/licenses](http://localhost:3000/admin/licenses)
- **Analytics:** [http://localhost:3000/admin/analytics](http://localhost:3000/admin/analytics)
- **Audit Logs:** [http://localhost:3000/admin/audit-logs](http://localhost:3000/admin/audit-logs)

---

## Testing the Application

### 1. Create Test User

**Option A: Via Signup Page**
1. Go to [http://localhost:3000/signup](http://localhost:3000/signup)
2. Enter email and password
3. Click "Sign Up"
4. Check email for verification link
5. Click verification link
6. Login at [http://localhost:3000/login](http://localhost:3000/login)

**Option B: Via Supabase Dashboard**
1. Go to Supabase Dashboard → Authentication → Users
2. Click "Add User"
3. Enter email and password
4. Confirm email manually
5. Login at [http://localhost:3000/login](http://localhost:3000/login)

### 2. Create Admin User

**Via Supabase SQL Editor:**
```sql
-- 1. Create user (or use existing user ID)
-- Find user ID from Authentication → Users

-- 2. Set role to admin in user_metadata
UPDATE auth.users
SET raw_user_meta_data =
  raw_user_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'your-admin@email.com';

-- 3. Verify
SELECT email, raw_user_meta_data->>'role' as role
FROM auth.users
WHERE email = 'your-admin@email.com';
```

### 3. Test Flows

#### User Flow
1. ✓ Signup → Email verification → Login
2. ✓ View dashboard with stats
3. ✓ Create API key
4. ✓ Check usage stats
5. ✓ Purchase credits (test mode)
6. ✓ Update profile settings

#### Admin Flow
1. ✓ Login as admin
2. ✓ View admin dashboard
3. ✓ Create tenant
4. ✓ Assign credits to tenant
5. ✓ Create license
6. ✓ View analytics
7. ✓ Check audit logs

---

## Common Issues & Solutions

### Issue: "Cannot connect to Supabase"

**Solution:**
1. Check `.env.local` has correct Supabase URL and keys
2. Verify Supabase project is active
3. Check network connection
4. Restart dev server: `Ctrl+C` then `npm run dev`

### Issue: "Stripe not working"

**Solution:**
1. Verify Stripe keys are in test mode (pk_test_, sk_test_)
2. Check webhook endpoint is created
3. Use Stripe CLI for local testing:
   ```bash
   stripe listen --forward-to localhost:3000/api/webhooks/stripe
   ```

### Issue: "Pages not loading / 404 errors"

**Solution:**
1. Clear `.next` cache: `rm -rf .next`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Restart dev server

### Issue: "TypeScript errors"

**Solution:**
1. Run type check: `npm run type-check`
2. Check for missing types: `npm install --save-dev @types/node @types/react @types/react-dom`
3. Restart TypeScript server in IDE

### Issue: "Backend API not responding"

**Solution:**
1. Ensure backend is running: `cd ../app && python -m uvicorn app.main:app --reload`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled in backend
4. Test backend health: `curl http://localhost:8000/health`

---

## Development Scripts

### Essential Commands

```bash
# Development
npm run dev              # Start dev server (hot reload)

# Building
npm run build            # Build production bundle
npm run start            # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking

# Testing
npm run test             # Run unit tests (watch mode)
npm run test:run         # Run tests once
npm run test:coverage    # Generate coverage report
npm run e2e              # Run E2E tests
npm run e2e:ui           # E2E with UI
npm run e2e:headed       # E2E with browser visible
```

### Recommended Workflow

1. **Start dev server:** `npm run dev`
2. **Make changes** in your code editor
3. **Test manually** in browser
4. **Run type check:** `npm run type-check`
5. **Run tests:** `npm run test:run`
6. **Run linting:** `npm run lint`
7. **Commit changes**

---

## IDE Setup

### VS Code (Recommended)

**Recommended Extensions:**
- ESLint (`dbaeumer.vscode-eslint`)
- Tailwind CSS IntelliSense (`bradlc.vscode-tailwindcss`)
- TypeScript Importer (`pmneo.tsimporter`)
- Prettier (`esbenp.prettier-vscode`)
- GitLens (`eamodio.gitlens`)

**Settings (`.vscode/settings.json`):**
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Other IDEs

- **WebStorm:** TypeScript support built-in
- **Vim/Neovim:** Use coc-tsserver
- **Emacs:** Use tide

---

## Next Steps

### For Developers
1. ✓ Read [FEATURES.md](./FEATURES.md) for detailed feature documentation
2. ✓ Read [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) for project overview
3. ✓ Explore component library in `src/components/ui/`
4. ✓ Check API client in `src/lib/api.ts`
5. ✓ Review page templates in `src/app/`

### For Designers
1. ✓ Review design system in `src/app/globals.css`
2. ✓ Check Tailwind config in `tailwind.config.ts`
3. ✓ Explore UI components in Storybook (if available)
4. ✓ Test dark mode toggle
5. ✓ Verify responsive breakpoints

### For QA/Testing
1. ✓ Review test files in `src/**/*.test.tsx`
2. ✓ Run E2E tests in `e2e/`
3. ✓ Test accessibility features
4. ✓ Verify i18n translations (DE/EN)
5. ✓ Check browser compatibility

---

## Additional Resources

### Documentation
- **Main README:** [README.md](./README.md)
- **Features:** [FEATURES.md](./FEATURES.md)
- **Project Summary:** [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)

### External Links
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Stripe Documentation](https://stripe.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)

### Support
- **Email:** support@ai-orchestra.de
- **GitHub Issues:** [Report a bug](https://github.com/your-org/ai-orchestra-gateway/issues)

---

## Production Deployment

### Prerequisites for Production
- ✓ Supabase production project
- ✓ Stripe production keys
- ✓ Domain name configured
- ✓ SSL certificate (automatic with Vercel)

### Deploy to Vercel (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "feat: complete frontend setup"
   git push origin master
   ```

2. **Import to Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import GitHub repository
   - Select `frontend` directory as root

3. **Configure Environment Variables:**
   - Add all variables from `.env.local`
   - Use production Supabase and Stripe keys

4. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your site is live!

### Deploy with Docker

```bash
# Build
docker build -t ai-orchestra-frontend .

# Run
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_SUPABASE_URL=your-url \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key \
  ai-orchestra-frontend
```

---

## Success Checklist

✓ Dependencies installed
✓ Environment variables configured
✓ Dev server running
✓ Landing page loads
✓ Can signup/login
✓ Dashboard accessible
✓ Admin panel works (with admin user)
✓ Legal pages visible
✓ Dark mode toggle works
✓ Language switcher works (DE/EN)

---

**Congratulations! Your AI Orchestra Gateway frontend is ready to use.**

For questions or issues, please contact: support@ai-orchestra.de

---

**Last Updated:** December 2025
**Version:** 2.0
