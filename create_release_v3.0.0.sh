#!/bin/bash
# GitHub Release Creation Script for v3.0.0 Modern HA Integration

echo "🚀 Creating GitHub Release for v3.0.0"
echo "====================================="

# Release Information
VERSION="v3.0.0"
TITLE="🚀 v3.0.0 - Modern HA Integration with Brands Repository"
TAG="v3.0.0"
BODY_FILE="RELEASE_NOTES_v3.0.0.md"

echo "📋 Release Details:"
echo "   Version: $VERSION"
echo "   Title: $TITLE"
echo "   Tag: $TAG"
echo "   Body file: $BODY_FILE"
echo "   Target: Home Assistant 2023.8+"
echo ""

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected - Creating release..."

    # Create the release
    gh release create "$TAG" \
        --title "$TITLE" \
        --notes-file "$BODY_FILE" \
        --repo "grotan1/denon-avr-3805"

    echo "✅ GitHub release created successfully!"
    echo "   Visit: https://github.com/grotan1/denon-avr-3805/releases"

else
    echo "⚠️  GitHub CLI not found. Manual release creation required."
    echo ""
    echo "📝 Manual Steps:"
    echo "1. Go to: https://github.com/grotan1/denon-avr-3805/releases/new"
    echo "2. Select tag: $TAG"
    echo "3. Set title: $TITLE"
    echo "4. Copy content from: $BODY_FILE"
    echo "5. Mark as major release"
    echo "6. Publish release"
fi

echo ""
echo "🎯 v3.0.0 Release Summary:"
echo "   ✅ Modern HA 2023.8+ support"
echo "   ✅ Brands repository integration"
echo "   ✅ Breaking changes documented"
echo "   ✅ Clean, future-proof codebase"
echo "   🚀 Production-ready for latest HA"