# AI Orchestra Gateway - Frontend

Modern Next.js 15 frontend for the AI Orchestra Gateway platform.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI)
- **Authentication**: Supabase Auth
- **Payments**: Stripe
- **Charts**: Recharts
- **Internationalization**: next-intl
- **Theme**: next-themes (Dark mode support)

## Prerequisites

- Node.js 18+ and npm
- Supabase account and project
- Stripe account (for payments)

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```

   Then edit `.env.local` with your credentials:
   - Supabase URL and keys
   - Stripe API keys
   - App URLs

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (landing)/          # Public pages (home, pricing, docs)
│   │   ├── (auth)/             # Authentication pages
│   │   ├── (dashboard)/        # User dashboard (protected)
│   │   ├── (admin)/            # Admin panel (protected)
│   │   ├── api/                # API routes
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── landing/            # Landing page components
│   │   ├── dashboard/          # Dashboard components
│   │   ├── admin/              # Admin components
│   │   ├── auth/               # Auth components
│   │   ├── shared/             # Shared components
│   │   ├── providers/          # Context providers
│   │   └── ui/                 # shadcn/ui components
│   ├── lib/
│   │   ├── supabase/           # Supabase client setup
│   │   ├── stripe.ts           # Stripe configuration
│   │   └── utils.ts            # Utility functions
│   ├── hooks/                  # Custom React hooks
│   ├── types/                  # TypeScript type definitions
│   │   └── database.ts         # Supabase database types
│   └── middleware.ts           # Next.js middleware (auth)
├── messages/                   # i18n translations
│   ├── en.json                 # English
│   └── de.json                 # German
├── public/                     # Static assets
├── .env.local.example          # Environment variables template
├── next.config.ts              # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── components.json             # shadcn/ui configuration
└── package.json                # Dependencies
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Features

### Public Pages
- Landing page with hero, features, pricing
- Documentation
- Blog
- Contact form
- Changelog
- Help center
- **Datenschutz** (Privacy Policy - DSGVO compliant)
- **Impressum** (Imprint - German legal requirement)
- **AGB** (Terms of Service - German)

### Authentication
- Sign up / Sign in
- Password reset
- Email verification
- OAuth providers (optional)

### User Dashboard
- Overview with usage statistics
- API key management
- Usage analytics and charts
- Billing and subscriptions
- Account settings
- Dark mode toggle

### Admin Panel
- System overview and KPIs
- Tenant management
- License management
- User management
- Audit logs
- Analytics dashboard
- Billing management
- System settings

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import the project in Vercel
3. Set environment variables
4. Deploy

### Docker

```bash
docker build -t ai-orchestra-frontend .
docker run -p 3000:3000 ai-orchestra-frontend
```

## Environment Variables

See `.env.local.example` for all required environment variables.

### Required Variables

- `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key (server-side only)
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` - Stripe publishable key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `NEXT_PUBLIC_APP_URL` - Frontend URL
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Customization

### Adding New Components

Use shadcn/ui CLI to add components:

```bash
npx shadcn@latest add [component-name]
```

### Theming

Modify theme colors in `tailwind.config.ts` and `src/app/globals.css`.

### Internationalization

Add new languages by creating new JSON files in the `messages/` directory.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run linting and type checking
4. Submit a pull request

## License

See main project LICENSE file.
