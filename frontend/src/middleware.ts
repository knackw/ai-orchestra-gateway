import { type NextRequest, NextResponse } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

/**
 * Middleware that combines i18n locale detection with Supabase session management
 *
 * Flow:
 * 1. Detect and set locale from cookie or Accept-Language header
 * 2. Update Supabase session
 * 3. Handle authentication redirects
 */
export async function middleware(request: NextRequest) {
  // Step 1: Handle locale detection
  let locale = request.cookies.get('locale')?.value;

  if (!locale) {
    // Fallback to Accept-Language header
    const acceptLanguage = request.headers.get('accept-language');
    locale = acceptLanguage?.startsWith('de') ? 'de' : 'en';
  }

  // Validate locale
  if (!['de', 'en'].includes(locale)) {
    locale = 'de'; // Default to German
  }

  // Step 2: Update Supabase session and handle auth
  const response = await updateSession(request);

  // Step 3: Ensure locale cookie is set on the response
  if (!request.cookies.get('locale')) {
    response.cookies.set('locale', locale, {
      path: '/',
      maxAge: 60 * 60 * 24 * 365, // 1 year
    });
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - files with extensions (images, etc.)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
