# Production Deployment Guide for Keelo.ai 🚀

## Overview
- **Frontend**: Deploy to Vercel (free tier available)
- **Backend**: Deploy to Railway (already configured)
- **Database**: PostgreSQL on Railway
- **Authentication**: Firebase (already configured)

## Part 1: Backend Deployment (Railway)

### Step 1: Prepare Backend for Production

1. **Update backend environment variables on Railway**:
   ```bash
   # Go to Railway dashboard > Your project > Variables
   # Add these if not already present:
   
   # Core Settings
   ENVIRONMENT=production
   SECRET_KEY=<generate-a-secure-random-string>
   
   # Database (should already be set by Railway)
   DATABASE_URL=postgresql://...
   
   # Redis (if using Railway Redis)
   REDIS_URL=redis://...
   
   # API Keys
   OPENAI_API_KEY=<your-openai-key>
   GOOGLE_PAGESPEED_API_KEY=<optional>
   
   # Firebase (optional but recommended)
   FIREBASE_PROJECT_ID=keelo-5924a
   
   # CORS - IMPORTANT: Update with your frontend URL
   CORS_ORIGINS=["https://keelo.ai", "https://www.keelo.ai", "https://keelo-ai.vercel.app"]
   ```

2. **Get Firebase Service Account** (Recommended for production):
   - Go to [Firebase Console > Service Accounts](https://console.firebase.google.com/project/keelo-5924a/settings/serviceaccounts/adminsdk)
   - Click "Generate new private key"
   - Download the JSON file
   - In Railway, add the entire JSON content as environment variable:
     ```
     FIREBASE_SERVICE_ACCOUNT_JSON=<paste-entire-json-content>
     ```

### Step 2: Update Backend Code for Production
