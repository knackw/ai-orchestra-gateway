export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      tenants: {
        Row: {
          id: string;
          name: string;
          api_key_hash: string;
          created_at: string;
          updated_at: string;
          is_active: boolean;
          allowed_ips: string[] | null;
          avv_signed: boolean;
          avv_signed_at: string | null;
          avv_signed_by: string | null;
        };
        Insert: {
          id?: string;
          name: string;
          api_key_hash: string;
          created_at?: string;
          updated_at?: string;
          is_active?: boolean;
          allowed_ips?: string[] | null;
          avv_signed?: boolean;
          avv_signed_at?: string | null;
          avv_signed_by?: string | null;
        };
        Update: {
          id?: string;
          name?: string;
          api_key_hash?: string;
          created_at?: string;
          updated_at?: string;
          is_active?: boolean;
          allowed_ips?: string[] | null;
          avv_signed?: boolean;
          avv_signed_at?: string | null;
          avv_signed_by?: string | null;
        };
      };
      licenses: {
        Row: {
          id: string;
          tenant_id: string;
          plan_type: string;
          credits_total: number;
          credits_used: number;
          credits_remaining: number;
          valid_from: string;
          valid_until: string;
          is_active: boolean;
          stripe_subscription_id: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          tenant_id: string;
          plan_type: string;
          credits_total: number;
          credits_used?: number;
          credits_remaining?: number;
          valid_from?: string;
          valid_until: string;
          is_active?: boolean;
          stripe_subscription_id?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          tenant_id?: string;
          plan_type?: string;
          credits_total?: number;
          credits_used?: number;
          credits_remaining?: number;
          valid_from?: string;
          valid_until?: string;
          is_active?: boolean;
          stripe_subscription_id?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      usage_logs: {
        Row: {
          id: string;
          tenant_id: string;
          request_id: string;
          model: string;
          input_tokens: number;
          output_tokens: number;
          total_tokens: number;
          credits_used: number;
          pii_detected: boolean;
          created_at: string;
        };
        Insert: {
          id?: string;
          tenant_id: string;
          request_id: string;
          model: string;
          input_tokens: number;
          output_tokens: number;
          total_tokens: number;
          credits_used: number;
          pii_detected?: boolean;
          created_at?: string;
        };
        Update: {
          id?: string;
          tenant_id?: string;
          request_id?: string;
          model?: string;
          input_tokens?: number;
          output_tokens?: number;
          total_tokens?: number;
          credits_used?: number;
          pii_detected?: boolean;
          created_at?: string;
        };
      };
      audit_logs: {
        Row: {
          id: string;
          tenant_id: string;
          user_id: string | null;
          action: string;
          resource_type: string;
          resource_id: string | null;
          details: Json | null;
          ip_address: string | null;
          user_agent: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          tenant_id: string;
          user_id?: string | null;
          action: string;
          resource_type: string;
          resource_id?: string | null;
          details?: Json | null;
          ip_address?: string | null;
          user_agent?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          tenant_id?: string;
          user_id?: string | null;
          action?: string;
          resource_type?: string;
          resource_id?: string | null;
          details?: Json | null;
          ip_address?: string | null;
          user_agent?: string | null;
          created_at?: string;
        };
      };
      invoices: {
        Row: {
          id: string;
          tenant_id: string;
          invoice_number: string;
          period_start: string;
          period_end: string;
          total_amount: number;
          total_tokens: number;
          status: string;
          stripe_invoice_id: string | null;
          pdf_url: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          tenant_id: string;
          invoice_number: string;
          period_start: string;
          period_end: string;
          total_amount: number;
          total_tokens: number;
          status?: string;
          stripe_invoice_id?: string | null;
          pdf_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          tenant_id?: string;
          invoice_number?: string;
          period_start?: string;
          period_end?: string;
          total_amount?: number;
          total_tokens?: number;
          status?: string;
          stripe_invoice_id?: string | null;
          pdf_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      [_ in never]: never;
    };
  };
}
