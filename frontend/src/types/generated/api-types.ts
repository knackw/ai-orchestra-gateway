/**
 * SEC-013: Core API Types (Fallback)
 *
 * These are core types used when the OpenAPI schema is not available.
 * Run `npm run generate:api-types` with the backend running to get
 * the complete generated types.
 *
 * Generated at: 2025-12-09T00:00:00.000Z
 */


/**
 * RFC 7807 Problem Details for HTTP APIs
 *
 * Standardized error response format used by the backend.
 * See: https://datatracker.ietf.org/doc/html/rfc7807
 */
export interface ProblemDetail {
  /** URI reference identifying the problem type */
  type: string
  /** Short human-readable summary */
  title: string
  /** HTTP status code */
  status: number
  /** Human-readable explanation specific to this occurrence */
  detail?: string
  /** URI reference to the specific occurrence */
  instance?: string
  /** Correlation ID for distributed tracing */
  trace_id?: string
  /** ISO 8601 timestamp */
  timestamp?: string
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data?: T
  error?: ProblemDetail
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  limit?: number
  offset?: number
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

/**
 * Date range filter
 */
export interface DateRangeFilter {
  start_date?: string
  end_date?: string
}

/**
 * Common timestamp fields (ISO 8601 UTC)
 */
export interface TimestampFields {
  created_at: string
  updated_at: string
}

// ============================================================================
// Tenant Types
// ============================================================================

/**
 * Tenant entity
 */
export interface Tenant {
  id: string
  name: string
  email?: string
  plan_type: PlanType
  is_active: boolean
  created_at: string
  updated_at: string
}

export type PlanType = 'free' | 'starter' | 'professional' | 'enterprise'

/**
 * Tenant creation request
 */
export interface TenantCreate {
  name: string
  email: string
  plan_type?: PlanType
}

/**
 * Tenant update request
 */
export interface TenantUpdate {
  name?: string
  email?: string
  is_active?: boolean
  plan_type?: PlanType
}

// ============================================================================
// License/API Key Types
// ============================================================================

/**
 * License (API Key) entity
 */
export interface License {
  id: string
  tenant_id: string
  name: string
  key_prefix: string
  is_active: boolean
  rate_limit: number
  scopes: string[]
  last_used_at?: string
  expires_at?: string
  created_at: string
  updated_at: string
}

/**
 * License creation request
 */
export interface LicenseCreate {
  name: string
  tenant_id: string
  rate_limit?: number
  scopes?: string[]
}

/**
 * License creation response (includes the full key only once)
 */
export interface LicenseCreateResponse {
  id: string
  key: string
  name: string
  created_at: string
}

/**
 * License update request
 */
export interface LicenseUpdate {
  name?: string
  is_active?: boolean
  rate_limit?: number
}

// ============================================================================
// Usage Types
// ============================================================================

/**
 * Usage log entry
 */
export interface UsageLog {
  id: string
  tenant_id: string
  license_id?: string
  request_id: string
  endpoint: string
  model: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  credits_used: number
  pii_detected: boolean
  status: 'success' | 'error'
  error_message?: string
  latency_ms: number
  created_at: string
}

/**
 * Usage statistics aggregation
 */
export interface UsageStats {
  period_start: string
  period_end: string
  total_requests: number
  total_tokens: number
  total_credits: number
  error_count: number
  error_rate: number
  avg_latency_ms: number
  by_model: Record<string, {
    requests: number
    tokens: number
    credits: number
  }>
  by_day: Array<{
    date: string
    requests: number
    tokens: number
    credits: number
  }>
}

// ============================================================================
// Billing Types
// ============================================================================

/**
 * Credit balance
 */
export interface CreditBalance {
  tenant_id: string
  credits_remaining: number
  credits_total: number
  credits_used: number
  last_refill_at?: string
  next_refill_at?: string
}

/**
 * Invoice entity
 */
export interface Invoice {
  id: string
  tenant_id: string
  invoice_number: string
  period_start: string
  period_end: string
  total_amount: number
  total_tokens: number
  status: InvoiceStatus
  stripe_invoice_id?: string
  pdf_url?: string
  created_at: string
}

export type InvoiceStatus = 'draft' | 'pending' | 'paid' | 'failed' | 'cancelled'

// ============================================================================
// Audit Types
// ============================================================================

/**
 * Audit log entry
 */
export interface AuditLog {
  id: string
  tenant_id: string
  user_id?: string
  action: string
  resource_type: string
  resource_id?: string
  details?: Record<string, unknown>
  ip_address?: string
  user_agent?: string
  created_at: string
}

// ============================================================================
// Auth Types
// ============================================================================

/**
 * User profile
 */
export interface UserProfile {
  id: string
  email: string
  name?: string
  avatar_url?: string
  tenant_id: string
  role: UserRole
  created_at: string
  updated_at: string
}

export type UserRole = 'admin' | 'user' | 'viewer'

/**
 * Password change request
 */
export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

/**
 * Password validation result
 */
export interface PasswordValidationResult {
  is_valid: boolean
  errors: string[]
  strength: PasswordStrength
}

export type PasswordStrength = 'weak' | 'medium' | 'strong' | 'very_strong'

// ============================================================================
// AI Generation Types
// ============================================================================

/**
 * AI generation request
 */
export interface GenerateRequest {
  prompt: string
  model?: string
  max_tokens?: number
  temperature?: number
  system_prompt?: string
}

/**
 * AI generation response
 */
export interface GenerateResponse {
  id: string
  content: string
  model: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  credits_used: number
  pii_detected: boolean
  pii_redacted?: boolean
  created_at: string
}

// ============================================================================
// Dashboard Types
// ============================================================================

/**
 * Dashboard statistics
 */
export interface DashboardStats {
  credits: {
    current: number
    estimatedDaysRemaining?: number
  }
  usage: {
    requestsToday: number
    requestsTrend: number
    tokensThisMonth: number
    tokensTrend: number
    errorRate: number
    errorTrend: number
    creditsUsedThisMonth: number
    creditsTrend: number
  }
  activeApiKeys: number
  recentActivity: Array<{
    id: string
    endpoint: string
    model: string
    tokens: number
    status: 'success' | 'error'
    timestamp: string
  }>
  usageChart: Array<{
    date: string
    requests: number
  }>
}
