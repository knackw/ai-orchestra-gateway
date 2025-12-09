# Authentication Flow Diagram

## User Journey Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         Landing Page                             │
│                      https://domain.com/                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
        ▼                  ▼
┌──────────────┐    ┌──────────────┐
│  Login Link  │    │ Signup Link  │
└──────┬───────┘    └──────┬───────┘
       │                   │
       ▼                   ▼
```

---

## 1. Login Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      /login Page                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  LoginForm Component                                  │     │
│  │  • Email input                                        │     │
│  │  • Password input (with visibility toggle)           │     │
│  │  • Remember me checkbox ✨NEW                        │     │
│  │  • Forgot password link                              │     │
│  │  • Math CAPTCHA (SEC-004)                           │     │
│  │  • Login button (with loading state)                 │     │
│  │  • OR separator                                       │     │
│  │  • Google OAuth button                               │     │
│  │  • GitHub OAuth button                               │     │
│  │  • Link to signup                                     │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
        Email/Password          OAuth (Google/GitHub)
                │                     │
                ▼                     ▼
        ┌──────────────┐      ┌──────────────┐
        │   Supabase   │      │   Supabase   │
        │  Auth API    │      │   OAuth      │
        └──────┬───────┘      └──────┬───────┘
               │                     │
               └──────────┬──────────┘
                          ▼
                 ┌─────────────────┐
                 │ Auth Callback   │
                 │ /api/auth/      │
                 │  callback       │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │   Dashboard     │
                 │  /dashboard     │
                 └─────────────────┘
```

---

## 2. Signup Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      /signup Page                               │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  SignupForm Component                                 │     │
│  │  • Email input                                        │     │
│  │  • Password input (with visibility toggle)           │     │
│  │  • Password strength indicator ✨NEW                 │     │
│  │  • Confirm password input (with visibility toggle)   │     │
│  │  • Company name input (optional)                     │     │
│  │  • Terms of Service checkbox + link                  │     │
│  │  • Privacy Policy checkbox + link                    │     │
│  │  • AVV checkbox + link ✨NEW                         │     │
│  │  • Math CAPTCHA (SEC-004)                           │     │
│  │  • Signup button (with loading state)                │     │
│  │  • Link to login                                      │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │   Supabase      │
                 │  Auth Signup    │
                 └────────┬────────┘
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                  /verify-email Page                             │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  VerifyEmailCard Component                            │     │
│  │  • Confirmation message                               │     │
│  │  • Email display                                      │     │
│  │  • Resend email button                                │     │
│  │  • Tips (check spam)                                  │     │
│  │  • Back to login link                                 │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                           │
                    User checks email
                           │
                           ▼
                 ┌─────────────────┐
                 │  Click verify   │
                 │   link in       │
                 │     email       │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ Auth Callback   │
                 │ /api/auth/      │
                 │  callback       │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │   Dashboard     │
                 │  /dashboard     │
                 └─────────────────┘
```

---

## 3. Password Reset Flow

```
┌────────────────────────────────────────────────────────────────┐
│              /forgot-password Page                              │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  ForgotPasswordForm Component                         │     │
│  │  • Email input                                        │     │
│  │  • Math CAPTCHA (SEC-004)                           │     │
│  │  • Send reset link button                            │     │
│  │  • Back to login link                                │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │   Supabase      │
                 │ Password Reset  │
                 │   API           │
                 └────────┬────────┘
                          ▼
┌────────────────────────────────────────────────────────────────┐
│            Success Confirmation Screen                          │
│  • "Email sent" message                                        │
│  • Instructions                                                 │
│  • Back to login link                                          │
└────────────────────────────────────────────────────────────────┘
                           │
                    User checks email
                           │
                           ▼
                 ┌─────────────────┐
                 │  Click reset    │
                 │   link in       │
                 │     email       │
                 └────────┬────────┘
                          ▼
┌────────────────────────────────────────────────────────────────┐
│           /reset-password/confirm Page                          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  ResetPasswordForm Component                          │     │
│  │  • New password input (with visibility toggle)       │     │
│  │  • Confirm password input (with visibility toggle)   │     │
│  │  • Password requirements (SEC-012)                   │     │
│  │  • Submit button (with loading state)                │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │   Supabase      │
                 │  Update         │
                 │  Password       │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │   Login Page    │
                 │    /login       │
                 └─────────────────┘
```

---

## 4. OAuth Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      /login Page                                │
│                                                                 │
│               Click Google or GitHub button                     │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │   Supabase      │
                 │  OAuth Start    │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │     Google      │
                 │       or        │
                 │     GitHub      │
                 │  Login Screen   │
                 └────────┬────────┘
                          │
                User authorizes
                          │
                          ▼
                 ┌─────────────────┐
                 │ Auth Callback   │
                 │ /api/auth/      │
                 │  callback       │
                 │                 │
                 │ • Exchange code │
                 │ • Create session│
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │   Dashboard     │
                 │  /dashboard     │
                 └─────────────────┘
```

---

## Component Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     Page Components                          │
├─────────────────────────────────────────────────────────────┤
│  /app/(auth)/login/page.tsx                                 │
│  /app/(auth)/signup/page.tsx                                │
│  /app/(auth)/forgot-password/page.tsx                       │
│  /app/(auth)/reset-password/confirm/page.tsx                │
│  /app/(auth)/verify-email/page.tsx                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Form Components                            │
├─────────────────────────────────────────────────────────────┤
│  LoginForm.tsx                                              │
│  SignupForm.tsx                                             │
│  ForgotPasswordForm.tsx                                     │
│  ResetPasswordForm.tsx                                      │
│  VerifyEmailCard.tsx                                        │
└────────────────────┬───────────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Security │  │   UI     │  │  Password    │
│ Components│  │Components│  │  Strength    │
│          │  │          │  │  Indicator   │
│• Honeypot│  │• Input   │  │   ✨NEW      │
│• CAPTCHA │  │• Button  │  └──────────────┘
│          │  │• Label   │
│          │  │• Checkbox│
└──────────┘  └──────────┘
       │             │
       └──────┬──────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Supporting Libraries                       │
├─────────────────────────────────────────────────────────────┤
│  • lib/auth.ts (Client auth functions)                      │
│  • lib/actions/auth.ts (Server actions)                     │
│  • lib/validations/auth.ts (Zod schemas)                    │
│  • hooks/useAuth.ts (Custom hook) ✨NEW                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Supabase                                │
├─────────────────────────────────────────────────────────────┤
│  • lib/supabase/client.ts                                   │
│  • lib/supabase/server.ts                                   │
│  • @supabase/supabase-js                                    │
│  • @supabase/ssr                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Flow (SEC-004 & SEC-012)

```
┌─────────────────────────────────────────────────────────────┐
│                   User Fills Form                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Client-Side Validation                          │
├─────────────────────────────────────────────────────────────┤
│  ✓ Email format (Zod)                                       │
│  ✓ Password requirements (SEC-012)                          │
│    • 12+ characters                                          │
│    • Uppercase letter                                        │
│    • Lowercase letter                                        │
│    • Number                                                  │
│    • Special character                                       │
│    • Not common password                                     │
│  ✓ Field matching (password confirm)                        │
│  ✓ Required checkboxes                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Bot Protection (SEC-004)                        │
├─────────────────────────────────────────────────────────────┤
│  1. Honeypot Field Check                                    │
│     • Hidden field                                           │
│     • If filled → Silent rejection                          │
│     • Bot detected                                           │
│                                                              │
│  2. Math CAPTCHA                                            │
│     • Simple addition (e.g., 5 + 3 = ?)                    │
│     • Must be solved correctly                              │
│     • Human verification                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Supabase Auth API                               │
├─────────────────────────────────────────────────────────────┤
│  • Server-side validation                                    │
│  • Rate limiting                                             │
│  • CSRF protection                                           │
│  • Session creation                                          │
│  • HTTP-only cookies                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Authenticated Session                           │
└─────────────────────────────────────────────────────────────┘
```

---

## State Management with useAuth Hook

```
┌─────────────────────────────────────────────────────────────┐
│                 Component Mounts                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              const { user, isLoading,                        │
│                      isAuthenticated,                        │
│                      signOut } = useAuth()                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              useAuth Hook Lifecycle                          │
├─────────────────────────────────────────────────────────────┤
│  1. Initialize State                                         │
│     • user: null                                             │
│     • session: null                                          │
│     • isLoading: true                                        │
│                                                              │
│  2. Get Initial Session                                      │
│     • Call supabase.auth.getSession()                       │
│     • Set user and session                                   │
│     • Set isLoading: false                                   │
│                                                              │
│  3. Subscribe to Auth Changes                                │
│     • Listen for login events                                │
│     • Listen for logout events                               │
│     • Listen for session refresh                             │
│     • Auto-update state                                      │
│     • Router refresh                                         │
│                                                              │
│  4. Cleanup on Unmount                                       │
│     • Unsubscribe from events                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Password Strength Indicator Flow

```
┌─────────────────────────────────────────────────────────────┐
│              User Types Password                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│        PasswordStrengthIndicator Component                   │
├─────────────────────────────────────────────────────────────┤
│  1. Calculate Strength Score (0-8)                          │
│     • +1 for 8+ chars                                        │
│     • +1 for 12+ chars                                       │
│     • +1 for 16+ chars                                       │
│     • +1 for uppercase                                       │
│     • +1 for lowercase                                       │
│     • +1 for number                                          │
│     • +1 for special char                                    │
│     • +1 for not common                                      │
│                                                              │
│  2. Display Visual Bars                                      │
│     • 0-3: Weak (2 red bars)                                │
│     • 4-5: Medium (3 yellow bars)                           │
│     • 6-7: Strong (4 green bars)                            │
│     • 8: Very Strong (4 dark green bars)                    │
│                                                              │
│  3. Show Requirements Checklist                              │
│     ○ 12+ characters (○ or ✓)                              │
│     ○ Uppercase letter                                       │
│     ○ Lowercase letter                                       │
│     ○ Number                                                 │
│     ○ Special character                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  User Action Failed                          │
└────────────────────┬────────────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Validation│  │ Network  │  │ Server   │
│  Error   │  │  Error   │  │  Error   │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └──────┬──────┴──────┬──────┘
            │             │
            ▼             ▼
┌─────────────┐    ┌─────────────┐
│  Display    │    │   Toast     │
│  Field      │    │Notification │
│  Error      │    │             │
└─────────────┘    └─────────────┘
```

---

## Summary

This authentication system provides:

1. **Complete User Flows**
   - Login (email/password + OAuth)
   - Signup with email verification
   - Password reset
   - Email verification

2. **Security Features**
   - SEC-004: Bot protection
   - SEC-012: Strong passwords
   - CSRF protection
   - Rate limiting

3. **Enhanced UX**
   - Password strength indicator
   - Real-time validation
   - Clear error messages
   - Loading states

4. **State Management**
   - useAuth hook for global state
   - Real-time updates
   - Automatic cleanup

5. **Type Safety**
   - Full TypeScript coverage
   - Zod validation schemas
   - Type-safe forms
