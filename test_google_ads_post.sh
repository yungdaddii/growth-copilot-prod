#!/bin/bash

echo "Testing Google Ads API with POST method..."
echo "=========================================="

# You'll need to get an access token from a successful OAuth flow
# For testing, you can get it from Redis after connecting through the UI

ACCESS_TOKEN="YOUR_ACCESS_TOKEN_HERE"
DEVELOPER_TOKEN="kmnhAER2lmBDbboSpM1evA"

echo "Testing listAccessibleCustomers with POST (correct method):"
curl -X POST \
  https://googleads.googleapis.com/v17/customers:listAccessibleCustomers \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "developer-token: $DEVELOPER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -v

echo ""
echo "=========================================="
echo "Expected results:"
echo "- With valid token: 200 OK with list of customer IDs"
echo "- With invalid token: 401 Unauthorized"
echo "- Without developer token: 403 Forbidden"
echo ""
echo "The 404 error we were getting means we were using GET instead of POST!"