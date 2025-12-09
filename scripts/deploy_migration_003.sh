#!/bin/bash
# Deploy migration 003 to Supabase
# This script uses psql to directly execute the migration

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MIGRATION_FILE="$PROJECT_ROOT/migrations/003_create_apps_and_usage_logs.sql"

echo "============================================================"
echo "  Deploying Migration 003"
echo "  AI Legal Ops Gateway - Database Schema"
echo "============================================================"
echo ""

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Error: Migration file not found at $MIGRATION_FILE"
    exit 1
fi

echo "📄 Migration file: $MIGRATION_FILE"
echo "📊 Size: $(wc -l < "$MIGRATION_FILE") lines"
echo ""

# Load Supabase credentials from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
else
    echo "⚠️  Warning: .env file not found"
    echo "   Please set SUPABASE_URL and SUPABASE_KEY environment variables"
fi

# Check if Supabase CLI is available
if command -v npx &> /dev/null; then
    echo "🔧 Using Supabase CLI..."
    echo ""
    
    # Option 1: Use Supabase CLI
    echo "Running: npx supabase db push"
    cd "$PROJECT_ROOT"
    npx supabase db push
    
    echo ""
    echo "✅ Migration deployed via Supabase CLI!"
    
else
    echo "⚠️  Supabase CLI not found"
    echo ""
    echo "To deploy, choose one of these methods:"
    echo ""
    echo "Option 1: Install Supabase CLI and retry"
    echo "  npm install -g supabase"
    echo "  npx supabase db push"
    echo ""
    echo "Option 2: Supabase Dashboard"
    echo "  1. Open: https://supabase.com/dashboard"
    echo "  2. Go to: Database → SQL Editor"
    echo "  3. Copy from: $MIGRATION_FILE"
    echo "  4. Paste and click 'Run'"
    echo ""
    echo "Option 3: Direct PostgreSQL (if you have connection string)"
    echo "  psql \$DATABASE_URL -f $MIGRATION_FILE"
    echo ""
    exit 1
fi

# Verify deployment
echo ""
echo "🔍 Verifying deployment..."
echo ""

# Run Python verification script if available
if [ -f "$PROJECT_ROOT/scripts/verify_migration_003.py" ]; then
    python3 "$PROJECT_ROOT/scripts/verify_migration_003.py"
else
    echo "⚠️  Verification script not found, skipping automated checks"
    echo "   Please verify manually in Supabase Dashboard"
fi

echo ""
echo "============================================================"
echo "  ✅ Deployment Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Run tests: pytest app/tests/test_db_schema.py -v"
echo "  2. Verify in dashboard: https://supabase.com/dashboard"
echo ""
