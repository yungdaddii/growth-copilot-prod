#!/bin/bash

echo "Checking Railway deployment status..."
echo "======================================"

# Check the root endpoint to see deployment version
echo "Fetching deployment info from Railway..."
curl -s https://growth-copilot-prod-production.up.railway.app/ | python3 -m json.tool

echo ""
echo "======================================"
echo "WHAT TO LOOK FOR:"
echo "1. deployment should show: v2.1-POST-FIX-2024-01-09"
echo "2. google_ads_fix should show: POST method for listAccessibleCustomers"
echo ""
echo "If you see these values, the new code is deployed!"
echo "If not, Railway is still deploying or there's a build issue."