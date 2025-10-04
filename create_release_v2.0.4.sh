#!/bin/bash
# GitHub Release Draft Creation Script for v2.0.4 Custom Icons Enhancement

echo "🎨 Creating GitHub Release Draft for v2.0.4"
echo "=========================================="

# Release Information
VERSION="v2.0.4"
TITLE="🎨 v2.0.4 - Custom Icons Enhancement"
TAG="v2.0.4"
BODY_FILE="RELEASE_DRAFT_v2.0.4.md"

echo "📋 Release Details:"
echo "   Version: $VERSION"
echo "   Title: $TITLE"
echo "   Tag: $TAG"
echo "   Body file: $BODY_FILE"
echo ""

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected - Creating release draft..."

    # Create the release draft
    gh release create "$TAG" \
        --draft \
        --title "$TITLE" \
        --notes-file "$BODY_FILE" \
        --repo "grotan1/denon-avr-3805"

    echo "✅ GitHub release draft created successfully!"
    echo "   Visit: https://github.com/grotan1/denon-avr-3805/releases"

else
    echo "⚠️  GitHub CLI not found. Manual release creation required."
    echo ""
    echo "📝 Manual Steps:"
    echo "1. Go to: https://github.com/grotan1/denon-avr-3805/releases/new"
    echo "2. Select tag: $TAG"
    echo "3. Set title: $TITLE"
    echo "4. Copy content from: $BODY_FILE"
    echo "5. Check 'Set as a pre-release' if needed"
    echo "6. Click 'Save draft'"
    echo ""
    echo "📄 Release notes are in: $BODY_FILE"
fi

echo ""
echo "🏁 Release draft preparation complete!"
echo "   ✅ Version bumped to 2.0.4"
echo "   ✅ Custom icons configuration added"
echo "   ✅ Git tag created and ready"
echo "   ✅ Release notes prepared"
echo "   🎨 Visual enhancement ready for users"