# Authentication Quick Reference Guide

## Routes

| Page | URL | Component |
|------|-----|-----------|
| Login | `/login` | `LoginForm` |
| Signup | `/signup` | `SignupForm` |
| Forgot Password | `/forgot-password` | `ForgotPasswordForm` |
| Reset Password | `/reset-password/confirm` | `ResetPasswordForm` |
| Verify Email | `/verify-email` | `VerifyEmailCard` |
| Auth Callback | `/api/auth/callback` | OAuth handler |

## Components Location

```
/root/Projekte/ai-orchestra-gateway/frontend/src/components/auth/
├── AuthLayout.tsx                    # Reusable layout
├── LoginForm.tsx                     # ✅ Enhanced with remember me
├── SignupForm.tsx                    # ✅ Enhanced with AVV & password strength
├── ForgotPasswordForm.tsx            # Password reset request
├── ResetPasswordForm.tsx             # New password form
├── VerifyEmailCard.tsx               # Email verification
└── PasswordStrengthIndicator.tsx     # ✅ NEW - Password strength UI
```

## New Files Created

1. **PasswordStrengthIndicator.tsx** - Visual password strength indicator
2. **useAuth.ts** - Custom authentication hook
3. **AUTH_PAGES_IMPLEMENTATION.md** - Full documentation
4. **AUTH_QUICK_REFERENCE.md** - This file

## Updated Files

1. **LoginForm.tsx** - Added "Remember me" checkbox
2. **SignupForm.tsx** - Added password strength indicator and AVV checkbox
3. **auth.ts (validations)** - Updated schemas for rememberMe and acceptAvv

## Using the useAuth Hook

```tsx
import { useAuth } from '@/hooks/useAuth'

function ProtectedComponent() {
  const { user, isLoading, isAuthenticated, signOut } = useAuth()

  if (isLoading) return <div>Loading...</div>
  if (!isAuthenticated) return <div>Please login</div>

  return (
    <div>
      <p>Welcome {user?.email}</p>
      <button onClick={signOut}>Logout</button>
    </div>
  )
}
```

## Password Requirements (SEC-012)

- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not in common password list

## Security Features (SEC-004)

- Honeypot fields on all forms
- Math CAPTCHA challenges
- Bot detection with silent rejection

## Form Validation

All forms use:
- `react-hook-form` for form state
- `zod` for schema validation
- `@hookform/resolvers` for integration

## Supabase Integration

### Client-side (lib/auth.ts)
```ts
import { signIn, signUp, signOut, resetPassword } from '@/lib/auth'

// Login
await signIn('user@example.com', 'password')

// Signup
await signUp('user@example.com', 'password', { company: 'ACME' })

// Logout
await signOut()

// Reset password
await resetPassword('user@example.com')
```

### Server-side (lib/actions/auth.ts)
```ts
'use server'
import { login, signup, signOut } from '@/lib/actions/auth'

// Use in Server Components or Server Actions
```

## Testing

```bash
# Run all tests
npm run test

# Run specific test
npm run test LoginForm.test.tsx

# Run with coverage
npm run test:coverage
```

## Environment Variables

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Common Patterns

### Protected Route
```tsx
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

export default async function ProtectedPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return <div>Protected content</div>
}
```

### Form with Validation
```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema, type LoginInput } from '@/lib/validations/auth'

const { register, handleSubmit, formState: { errors } } = useForm<LoginInput>({
  resolver: zodResolver(loginSchema),
})
```

## Troubleshooting

**Q: OAuth not working?**
A: Check redirect URLs in Supabase dashboard

**Q: Email not received?**
A: Check Supabase email settings and spam folder

**Q: Password validation failing?**
A: Ensure it meets all requirements (12+ chars, mixed case, number, special char)

**Q: TypeScript errors?**
A: Run `npm run type-check`

## Links

- Full documentation: `AUTH_PAGES_IMPLEMENTATION.md`
- Supabase docs: https://supabase.com/docs/guides/auth
- Next.js docs: https://nextjs.org/docs
