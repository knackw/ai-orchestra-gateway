import { http, HttpResponse } from 'msw'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

/**
 * MSW Request Handlers for API Mocking
 * These handlers intercept network requests during tests
 */
export const handlers = [
  // Auth endpoints
  http.post(`${API_URL}/api/v1/auth/login`, () => {
    return HttpResponse.json({
      access_token: 'mock-access-token',
      token_type: 'bearer',
      user: {
        id: 'user-123',
        email: 'test@example.com',
        tenant_id: 'tenant-123',
      },
    })
  }),

  http.post(`${API_URL}/api/v1/auth/signup`, () => {
    return HttpResponse.json({
      user: {
        id: 'user-123',
        email: 'test@example.com',
        tenant_id: 'tenant-123',
      },
      message: 'User created successfully',
    })
  }),

  http.post(`${API_URL}/api/v1/auth/logout`, () => {
    return HttpResponse.json({ message: 'Logged out successfully' })
  }),

  // API Keys endpoints
  http.get(`${API_URL}/api/v1/api-keys`, () => {
    return HttpResponse.json([
      {
        id: 'key-1',
        name: 'Production Key',
        key: 'sk_test_***',
        created_at: '2024-01-01T00:00:00Z',
        last_used_at: '2024-01-15T10:30:00Z',
        is_active: true,
      },
      {
        id: 'key-2',
        name: 'Development Key',
        key: 'sk_test_***',
        created_at: '2024-01-05T00:00:00Z',
        last_used_at: null,
        is_active: true,
      },
    ])
  }),

  http.post(`${API_URL}/api/v1/api-keys`, async ({ request }) => {
    const body = await request.json() as { name: string }
    return HttpResponse.json({
      id: 'key-new',
      name: body.name,
      key: 'sk_test_abc123xyz789',
      created_at: new Date().toISOString(),
      last_used_at: null,
      is_active: true,
    })
  }),

  http.delete(`${API_URL}/api/v1/api-keys/:keyId`, ({ params }) => {
    return HttpResponse.json({
      message: `API key ${params.keyId} deleted successfully`,
    })
  }),

  // Usage/Analytics endpoints
  http.get(`${API_URL}/api/v1/usage`, () => {
    return HttpResponse.json({
      current_period: {
        requests: 1234,
        tokens: 45678,
        credits_used: 123.45,
        period_start: '2024-01-01T00:00:00Z',
        period_end: '2024-01-31T23:59:59Z',
      },
      by_provider: [
        { provider: 'anthropic', requests: 800, tokens: 30000, credits_used: 80 },
        { provider: 'scaleway', requests: 434, tokens: 15678, credits_used: 43.45 },
      ],
      daily_stats: Array.from({ length: 30 }, (_, i) => ({
        date: `2024-01-${String(i + 1).padStart(2, '0')}`,
        requests: Math.floor(Math.random() * 100),
        tokens: Math.floor(Math.random() * 5000),
        credits_used: Math.random() * 10,
      })),
    })
  }),

  // Billing endpoints
  http.get(`${API_URL}/api/v1/billing/balance`, () => {
    return HttpResponse.json({
      credits: 500.75,
      currency: 'EUR',
      last_updated: new Date().toISOString(),
    })
  }),

  http.get(`${API_URL}/api/v1/billing/invoices`, () => {
    return HttpResponse.json([
      {
        id: 'inv-1',
        amount: 50.0,
        currency: 'EUR',
        status: 'paid',
        created_at: '2024-01-01T00:00:00Z',
        invoice_pdf: 'https://example.com/invoice-1.pdf',
      },
      {
        id: 'inv-2',
        amount: 100.0,
        currency: 'EUR',
        status: 'paid',
        created_at: '2024-02-01T00:00:00Z',
        invoice_pdf: 'https://example.com/invoice-2.pdf',
      },
    ])
  }),

  http.post(`${API_URL}/api/v1/billing/checkout`, () => {
    return HttpResponse.json({
      session_id: 'cs_test_123',
      url: 'https://checkout.stripe.com/test',
    })
  }),

  // Admin endpoints
  http.get(`${API_URL}/api/admin/tenants`, () => {
    return HttpResponse.json([
      {
        id: 'tenant-1',
        name: 'Acme Corp',
        email: 'admin@acme.com',
        is_active: true,
        credits: 1000,
        created_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'tenant-2',
        name: 'Test Inc',
        email: 'admin@test.com',
        is_active: true,
        credits: 500,
        created_at: '2024-01-15T00:00:00Z',
      },
    ])
  }),

  http.post(`${API_URL}/api/admin/tenants`, async ({ request }) => {
    const body = await request.json() as { name: string; email: string }
    return HttpResponse.json({
      id: 'tenant-new',
      name: body.name,
      email: body.email,
      is_active: true,
      credits: 0,
      created_at: new Date().toISOString(),
    })
  }),

  http.get(`${API_URL}/api/admin/analytics`, () => {
    return HttpResponse.json({
      total_tenants: 25,
      active_tenants: 20,
      total_requests_today: 5432,
      total_revenue_month: 12500,
      growth_rate: 15.5,
    })
  }),

  // AI Generate endpoint (for E2E testing)
  http.post(`${API_URL}/api/v1/generate`, async ({ request }) => {
    const body = await request.json() as { prompt: string; provider?: string }
    return HttpResponse.json({
      id: 'msg-123',
      content: `Response to: ${body.prompt}`,
      provider: body.provider || 'anthropic',
      model: 'claude-3-sonnet-20240229',
      usage: {
        input_tokens: 10,
        output_tokens: 50,
      },
      credits_used: 0.15,
    })
  }),

  // Audit logging endpoint (SEC-020)
  http.post('/api/v1/audit/log', async ({ request }) => {
    const body = await request.json() as any
    return HttpResponse.json({
      id: 'audit-event-' + Math.random().toString(36).substring(7),
      created_at: new Date().toISOString(),
      event_type: body.event_type,
      success: body.success ?? true,
    })
  }),
]

/**
 * Error handlers for testing error scenarios
 */
export const errorHandlers = [
  http.get(`${API_URL}/api/v1/api-keys`, () => {
    return HttpResponse.json(
      { error: 'Unauthorized', message: 'Invalid or expired token' },
      { status: 401 }
    )
  }),

  http.post(`${API_URL}/api/v1/api-keys`, () => {
    return HttpResponse.json(
      { error: 'Bad Request', message: 'API key name is required' },
      { status: 400 }
    )
  }),

  http.get(`${API_URL}/api/v1/billing/balance`, () => {
    return HttpResponse.json(
      { error: 'Service Unavailable', message: 'Billing service temporarily unavailable' },
      { status: 503 }
    )
  }),
]
