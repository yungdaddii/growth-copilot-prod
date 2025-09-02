# Google Ads API Setup Guide

## Required Environment Variables

Add these to your `.env` file (locally) and Railway environment variables:

```bash
# Google Ads OAuth Application
GOOGLE_ADS_CLIENT_ID=your-oauth-client-id
GOOGLE_ADS_CLIENT_SECRET=your-oauth-client-secret

# Google Ads Developer Token
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token

# Optional: Manager Account ID (if using manager account)
GOOGLE_ADS_MANAGER_CUSTOMER_ID=your-manager-id
```

## Step 1: Get Google Ads Developer Token

1. Go to https://ads.google.com/home/tools/manager-accounts/
2. Create or access your Manager Account
3. Go to Tools & Settings > Setup > API Center
4. Apply for API access if you haven't already
5. Copy your Developer Token

**Note**: For testing, you can use a TEST developer token, but it only works with test accounts.

## Step 2: Create OAuth 2.0 Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable the Google Ads API:
   - Go to APIs & Services > Library
   - Search for "Google Ads API"
   - Click Enable

4. Create OAuth 2.0 credentials:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: Web application
   - Add authorized redirect URIs:
     - For local: `http://localhost:8000/api/integrations/google-ads/oauth/callback`
     - For Railway: `https://your-railway-app.up.railway.app/api/integrations/google-ads/oauth/callback`
   - Copy the Client ID and Client Secret

## Step 3: Set Environment Variables

### Locally (.env file):
```bash
GOOGLE_ADS_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=GOCSPX-xyz123
GOOGLE_ADS_DEVELOPER_TOKEN=abcd1234
```

### On Railway:
1. Go to your Railway project
2. Click on the service
3. Go to Variables tab
4. Add each variable:
   - `GOOGLE_ADS_CLIENT_ID`
   - `GOOGLE_ADS_CLIENT_SECRET`
   - `GOOGLE_ADS_DEVELOPER_TOKEN`

## Step 4: Complete OAuth Flow

1. After setting environment variables, restart your app
2. Visit the OAuth URL endpoint to start authentication:
   - Local: `http://localhost:8000/api/integrations/google-ads/auth-url`
   - Railway: `https://your-app.railway.app/api/integrations/google-ads/auth-url`
3. Complete the Google sign-in
4. Grant permissions to access Google Ads
5. You'll be redirected back to your app

## Step 5: Verify Connection

Check if the integration is working:
```bash
# Run the troubleshooting script
python3 troubleshoot_google_ads.py

# Or check the status endpoint
curl https://your-app.railway.app/api/integrations/google-ads/status?session_id=your-session-id
```

## Common Issues

### 404 Errors on API Calls
- **Cause**: Wrong API version or endpoint format
- **Solution**: The code now uses v18 which should work. If not, try v19 or v20.

### 401 Unauthorized
- **Cause**: OAuth token expired or invalid
- **Solution**: Re-authenticate through OAuth flow

### 403 Forbidden
- **Cause**: Developer token not approved or invalid
- **Solution**: Check your developer token in Google Ads API Center

### No Accessible Customers
- **Cause**: The authenticated account doesn't have access to any Google Ads accounts
- **Solution**: Make sure you're signing in with an account that has Google Ads access

## Testing the Integration

Once everything is set up, you can test with:

```python
# Test script
python3 test_google_ads_endpoints.py

# Or use the main app
# The Google Ads data should appear when you analyze a domain
```

## API Version Compatibility

Current supported versions (as of 2024):
- v18 ✅ (Currently used)
- v19 ✅ 
- v20 ✅
- v21 ✅ (Latest)
- v17 ⚠️ (Deprecated, sunset June 2025)

The app is configured to use v18 for stability, but can be updated to v19-v21 if needed.