#!/bin/bash

echo "📦 Pushing Growth Copilot to GitHub..."
echo ""
echo "This script will:"
echo "1. Create a new GitHub repository"
echo "2. Push your code to GitHub"
echo "3. Railway will automatically detect and deploy the changes"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Install it with: brew install gh"
    exit 1
fi

# Authenticate with GitHub if needed
gh auth status || gh auth login

# Create the repository
echo "Creating GitHub repository..."
gh repo create growth-copilot-prod --private --source=. --remote=origin --push

echo ""
echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "🚀 Railway will automatically detect the changes and redeploy."
echo ""
echo "Monitor deployment at: https://railway.app"
echo "GitHub repository: https://github.com/$(gh api user --jq .login)/growth-copilot-prod"