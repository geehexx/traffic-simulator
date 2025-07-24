#!/bin/bash
# BuildBuddy Environment Setup Script
# This script helps set up BuildBuddy API key securely

echo "🔐 BuildBuddy Security Setup"
echo "=========================="
echo ""

# Check if API key is already set
if [ -n "$BUILD_BUDDY_API_KEY" ]; then
    echo "✅ BUILD_BUDDY_API_KEY is already set"
    echo "Current value: ${BUILD_BUDDY_API_KEY:0:8}..."
    echo ""
    echo "To test BuildBuddy integration:"
    echo "  ./scripts/bazel_performance.sh remote build //..."
    exit 0
fi

echo "❌ BUILD_BUDDY_API_KEY is not set"
echo ""
echo "To set up BuildBuddy securely:"
echo ""
echo "1. Get your API key from: https://app.buildbuddy.io/settings/api-keys"
echo ""
echo "2. Set the environment variable:"
echo "   export BUILD_BUDDY_API_KEY=your_api_key_here"
echo ""
echo "3. Add to your shell profile for persistence:"
echo "   echo 'export BUILD_BUDDY_API_KEY=your_api_key_here' >> ~/.bashrc"
echo "   # or for zsh:"
echo "   echo 'export BUILD_BUDDY_API_KEY=your_api_key_here' >> ~/.zshrc"
echo ""
echo "4. Test the setup:"
echo "   ./scripts/bazel_performance.sh remote build //..."
echo ""
echo "⚠️  SECURITY WARNING:"
echo "   - Never commit API keys to version control"
echo "   - Use environment variables only"
echo "   - Keep your API keys secure and rotate them regularly"
echo ""
echo "For more security best practices, see:"
echo "   docs/BAZEL_PERFORMANCE_GUIDE.md#security-best-practices"
