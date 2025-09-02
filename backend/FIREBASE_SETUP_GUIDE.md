# Firebase Authentication Setup for Railway

## The Issue
Your backend is failing to authenticate users because the Firebase Admin SDK cannot find the service account credentials. This is preventing the chat from working.

## Solution: Add Firebase Service Account to Railway

### Step 1: Get Your Firebase Service Account JSON

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **keelo-5924a**
3. Click the gear icon → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Download the JSON file

### Step 2: Add to Railway Environment Variables

1. Go to your Railway project
2. Select your backend service
3. Go to **Variables** tab
4. Add a new variable:
   - **Name**: `FIREBASE_SERVICE_ACCOUNT_JSON`
   - **Value**: Copy the ENTIRE content of the downloaded JSON file

The JSON should look like this:
```json
{
  "type": "service_account",
  "project_id": "keelo-5924a",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### Step 3: Also Add These Variables (if not already set)

```
GOOGLE_CLOUD_PROJECT=keelo-5924a
```

### Step 4: Redeploy

After adding the environment variable, Railway should automatically redeploy your service.

## Verification

Once deployed, you can verify it's working by:

1. Check the Railway logs for: `"Firebase Admin SDK initialized from JSON env var"`
2. Try signing in again from your frontend
3. The chat should now work properly

## Alternative: Using SERVICE_ACCOUNT_JSON

If `FIREBASE_SERVICE_ACCOUNT_JSON` doesn't work, try using `SERVICE_ACCOUNT_JSON` instead (some deployments use this name).

## Security Note

⚠️ **NEVER** commit the service account JSON to your repository. Always use environment variables.

## Troubleshooting

If you still see errors after adding the JSON:

1. **Check JSON is valid**: Make sure you copied the ENTIRE JSON content including the opening `{` and closing `}`
2. **Check for line breaks**: The private_key field should have `\n` characters, not actual line breaks
3. **Check logs**: Look for specific error messages in Railway logs
4. **Try redeploying**: Sometimes Railway needs a manual redeploy to pick up new env vars

## Current Status

The backend code has been updated to:
- Check for both `FIREBASE_SERVICE_ACCOUNT_JSON` and `SERVICE_ACCOUNT_JSON` environment variables
- Provide better error messages when credentials are missing
- Handle missing credentials gracefully

Once you add the Firebase service account JSON to Railway, authentication will work and the chat responses will start flowing properly.