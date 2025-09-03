# 🚀 Deployment Guide - Critical Fixes

## What's Being Deployed

### Critical Fixes:
1. ✅ **Firebase Authentication** - Fixed credential handling for production
2. ✅ **User Registration** - Added success feedback and proper data handling
3. ✅ **Chat Analysis** - Now provides real revenue leak analysis instead of generic responses
4. ✅ **Health Endpoints** - Added `/health/firebase` and `/health/config` for debugging

## Deployment Steps

### 1. Railway Backend (Automatic)
Railway should automatically deploy from GitHub push. Monitor at:
- https://railway.app/project/[your-project-id]

**Required Environment Variables:**
```env
# Firebase (CRITICAL - Auth won't work without this!)
FIREBASE_SERVICE_ACCOUNT_JSON=<paste entire JSON from Firebase console>
GOOGLE_CLOUD_PROJECT=keelo-5924a

# Database (should already be set)
DATABASE_URL=postgresql://...

# Redis (should already be set)  
REDIS_URL=redis://...

# OpenAI (should already be set)
OPENAI_API_KEY=sk-...

# Frontend URL
FRONTEND_URL=https://keelo-ai.vercel.app
CORS_ORIGINS=["https://keelo-ai.vercel.app", "http://localhost:3000"]
```

### 2. Get Firebase Service Account JSON

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **keelo-5924a**
3. Click gear icon → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Copy the ENTIRE JSON content

### 3. Add to Railway

1. Go to Railway dashboard
2. Select backend service
3. Go to **Variables** tab
4. Add new variable:
   - Name: `FIREBASE_SERVICE_ACCOUNT_JSON`
   - Value: Paste the entire JSON
5. Also ensure `GOOGLE_CLOUD_PROJECT=keelo-5924a` is set
6. Railway will auto-redeploy

### 4. Vercel Frontend (Automatic)
Vercel should automatically deploy from GitHub. Monitor at:
- https://vercel.com/dashboard

**Required Environment Variables:**
```env
NEXT_PUBLIC_API_URL=https://growth-copilot-prod-production.up.railway.app
NEXT_PUBLIC_WS_URL=wss://growth-copilot-prod-production.up.railway.app
NEXT_PUBLIC_FIREBASE_API_KEY=<your-key>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=keelo-5924a.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=keelo-5924a
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=keelo-5924a.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<your-id>
NEXT_PUBLIC_FIREBASE_APP_ID=<your-id>
```

## Verification Steps

### 1. Check Backend Health
```bash
# Check if backend is running
curl https://growth-copilot-prod-production.up.railway.app/health

# Check Firebase configuration
curl https://growth-copilot-prod-production.up.railway.app/health/firebase

# Check overall config
curl https://growth-copilot-prod-production.up.railway.app/health/config
```

### 2. Test Authentication
1. Go to https://keelo-ai.vercel.app/auth-debug
2. Click "Test Backend Health"
3. Should show Firebase as "operational" if configured correctly
4. Try "Test Sign Up" with test credentials

### 3. Test Chat Analysis
1. Go to https://keelo-ai.vercel.app
2. Type: "Find revenue leaks on shopify.com"
3. Should get detailed analysis with:
   - Speed issues
   - Mobile problems
   - SEO gaps
   - Conversion opportunities
   - Revenue impact estimates

## Troubleshooting

### Problem: "Authentication service not configured"
**Solution:** Add `FIREBASE_SERVICE_ACCOUNT_JSON` to Railway

### Problem: Sign up works but chat doesn't respond
**Solution:** Check Railway logs for WebSocket errors

### Problem: "Invalid authentication token"
**Solution:** Firebase credentials may be wrong - regenerate and update

### Problem: CORS errors
**Solution:** Update `CORS_ORIGINS` in Railway to include your frontend URL

## Monitoring

### Railway Logs
```bash
railway logs --service backend --tail
```

### Key Metrics to Watch
- WebSocket connections
- Authentication success rate
- Analysis completion time
- Error rates

## Success Criteria

✅ `/health/firebase` returns "operational"
✅ Users can sign up and see success message
✅ Users can sign in and see welcome message
✅ Chat provides real analysis for domains
✅ No authentication errors in logs

## Support

If issues persist after deployment:
1. Check Railway logs for specific errors
2. Use `/auth-debug` page to test each component
3. Verify all environment variables are set correctly
4. Ensure Firebase project matches configuration

## Next Steps After Deployment

1. Monitor user registrations
2. Track analysis quality
3. Review chat conversation logs
4. Optimize response times
5. Add more analyzer modules for deeper insights