# Fix Firebase Backend Authentication

## The Problem
The backend can't verify Firebase tokens because it needs Firebase Admin SDK credentials.

## How to Get Firebase Service Account JSON

1. **Go to Firebase Console**
   - https://console.firebase.google.com
   - Select your project (keelo-5924a)

2. **Navigate to Service Accounts**
   - Click the gear icon ⚙️ next to "Project Overview"
   - Select "Project settings"
   - Click on "Service accounts" tab

3. **Generate Private Key**
   - Click "Generate new private key"
   - Confirm by clicking "Generate key"
   - A JSON file will download - save it as `firebase-service-account.json`

## Set Up Backend Locally (for testing)

Add to your `.env` file in the backend folder:
```bash
FIREBASE_SERVICE_ACCOUNT_JSON='paste the entire JSON content here as a single line'
```

OR save the file and reference it:
```bash
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-service-account.json
```

## Set Up in Docker

1. **Option 1: Add to docker-compose.yml environment**
```yaml
backend:
  environment:
    FIREBASE_SERVICE_ACCOUNT_JSON: '{"type":"service_account","project_id":"keelo-5924a",...}'
```

2. **Option 2: Use Docker secrets (more secure)**
```bash
# Create a secret
docker secret create firebase-sa firebase-service-account.json

# Reference in docker-compose
backend:
  secrets:
    - firebase-sa
  environment:
    FIREBASE_SERVICE_ACCOUNT_PATH: /run/secrets/firebase-sa
```

## Set Up in Production (Railway)

1. Go to Railway dashboard
2. Select your backend service
3. Go to Variables tab
4. Add new variable:
   - Name: `FIREBASE_SERVICE_ACCOUNT_JSON`
   - Value: Paste the entire JSON content (minified, single line)

## Test After Setup

Use the auth debug tool at http://localhost:3001/auth-debug

You should see:
- ✅ Firebase sign in successful
- ✅ Backend login successful

## Important Security Notes

⚠️ **NEVER commit the service account JSON to git**
- Add to .gitignore: `firebase-service-account.json`
- Add to .gitignore: `*-service-account.json`

⚠️ **Keep the service account secure**
- It has admin access to your Firebase project
- Rotate keys regularly
- Use environment variables or secrets management

## Quick Test Without Service Account

For development only, you can disable Firebase auth verification:

```python
# In backend/app/core/auth.py
# WARNING: ONLY FOR DEVELOPMENT
SKIP_AUTH = os.getenv("SKIP_AUTH", "false").lower() == "true"
```

But this is NOT recommended for production!