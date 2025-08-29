#!/bin/bash

# Setup script for Playwright browsers
echo "🎭 Installing Playwright browsers for real-time website analysis..."

# Install Python dependencies
pip install playwright

# Install Chromium browser for headless testing
python -m playwright install chromium

# Install dependencies (for Linux servers)
python -m playwright install-deps

echo "✅ Playwright setup complete!"
echo "Keelo can now perform real-time browser analysis to detect:"
echo "  - JavaScript errors users actually experience"
echo "  - Dynamic content issues"
echo "  - Form validation problems"
echo "  - Mobile-specific issues"