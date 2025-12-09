import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';
import path from 'path';

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

/**
 * Security Headers Configuration (SEC-003, SEC-022)
 * Implements comprehensive security headers to protect against common web vulnerabilities
 *
 * SEC-022: HSTS Preload Preparation
 * - HSTS configured with max-age=63072000 (2 years)
 * - includeSubDomains directive enabled
 * - preload directive enabled for HSTS preload list submission
 *
 * To submit to HSTS preload list:
 * 1. Ensure HTTPS is working correctly on all subdomains
 * 2. Verify security.txt is accessible at /.well-known/security.txt
 * 3. Visit https://hstspreload.org/ and submit your domain
 * 4. Requirements: valid certificate, redirect HTTP to HTTPS, serve HSTS header on base domain
 */
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com https://js.stripe.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https: blob:",
      "font-src 'self' data:",
      "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://challenges.cloudflare.com https://api.stripe.com",
      "frame-src https://challenges.cloudflare.com https://js.stripe.com",
      "form-action 'self'",
      "base-uri 'self'",
      "upgrade-insecure-requests"
    ].join('; ')
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()'
  },
  {
    key: 'Strict-Transport-Security',
    // SEC-022: HSTS with preload support (2 years = 63072000 seconds)
    value: 'max-age=63072000; includeSubDomains; preload'
  }
];

const nextConfig: NextConfig = {
  /* config options here */
  outputFileTracingRoot: path.join(__dirname, './'),
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: false,
  },
  typescript: {
    // Only use in development - enforce type checking
    ignoreBuildErrors: false,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
  // SEC-003: Apply security headers to all routes
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};

export default withNextIntl(nextConfig);
