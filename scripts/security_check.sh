#!/bin/bash
# Security Check Script
# This script checks for exposed secrets and API keys

echo "🔒 Security Check for Exposed Secrets"
echo "====================================="
echo ""

# Check for common API key patterns
echo "Checking for exposed API keys..."
echo ""

# Check for BuildBuddy API keys
if grep -r "buildbuddy.*api.*key" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.venv 2>/dev/null; then
    echo "❌ Found potential BuildBuddy API key exposure"
    echo "   Please remove API keys from configuration files"
    echo "   Use environment variables instead"
    echo ""
fi

# Check for other common API key patterns
if grep -r -E "(api[_-]?key|secret[_-]?key|access[_-]?token)" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.venv 2>/dev/null; then
    echo "❌ Found potential API key patterns"
    echo "   Please review and remove if they contain actual keys"
    echo ""
fi

# Check for environment variable usage
echo "✅ Checking for proper environment variable usage..."
if grep -r "BUILD_BUDDY_API_KEY" . --exclude-dir=.git 2>/dev/null; then
    echo "✅ Found proper environment variable usage"
else
    echo "❌ No environment variable usage found"
fi

echo ""
echo "🛡️  Security Recommendations:"
echo "1. Use environment variables for all API keys"
echo "2. Never commit secrets to version control"
echo "3. Use tools like git-secrets to prevent future exposures"
echo "4. Regularly audit your repository for secrets"
echo "5. Rotate API keys if they've been exposed"
echo ""
echo "To set up BuildBuddy securely:"
echo "  ./scripts/setup_buildbuddy.sh"
