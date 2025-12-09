#!/bin/bash

# Install Test Dependencies for AI Legal Ops Frontend
# This script installs MSW and other testing dependencies

set -e

echo "📦 Installing MSW (Mock Service Worker) and related dependencies..."

cd "$(dirname "$0")"

# Install MSW for API mocking
npm install --save-dev msw@latest

# Install @vitest/coverage-v8 for coverage reports
npm install --save-dev @vitest/coverage-v8

echo ""
echo "✅ Test dependencies installed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Initialize MSW for browser usage (optional, for dev mode):"
echo "   npx msw init public/ --save"
echo ""
echo "2. Run tests:"
echo "   npm test              # Run unit tests"
echo "   npm run test:coverage # Run with coverage"
echo "   npm run test:e2e      # Run E2E tests"
echo ""
echo "📚 See TESTING.md for full documentation"
