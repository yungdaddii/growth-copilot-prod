# Safe Production Deployment Guide 🛡️

## ⚠️ IMPORTANT: Pre-Deployment Checklist

Before deploying, ensure:
- [ ] Current production is working and stable
- [ ] You have backups of your database
- [ ] You're deploying to a staging environment first
- [ ] All changes are committed to a separate branch (not main/master)

## Step 1: Create a Safe Deployment Branch

```bash
# Create a new branch for authentication features
git checkout -b feature/firebase-auth

# Add and commit all authentication changes
git add .
git commit -m "Add Firebase authentication system"

# Push to GitHub
git push origin feature/firebase-auth
```

## Step 2: Test on Railway Staging (RECOMMENDED)

### Option A: Create a Staging Service on Railway
1. Go to Railway Dashboard
2. Create a **NEW** service (don't modify production!)
3. Name it: `keelo-staging` or `keelo-auth-test`
4. Deploy from branch: `feature/firebase-auth`
5. Copy all environment variables from production
6. Add new Firebase variables (see below)

### Option B: Use Preview Environments
Railway automatically creates preview environments for pull requests:
1. Create a PR from `feature/firebase-auth` to `main`
2. Railway will create a preview deployment
3. Test everything there first

## Step 3: Environment Variables (Add to STAGING First!)

### Backend (Railway Staging)
```env
# ADD these new variables (don't remove existing ones!)
FIREBASE_PROJECT_ID=keelo-5924a

# Optional but recommended for production
FIREBASE_SERVICE_ACCOUNT_JSON=<paste-entire-service-account-json>

# Update CORS to include your staging/preview URLs
CORS_ORIGINS=["https://keelo-staging.up.railway.app", "https://keelo-auth-test.vercel.app", "http://localhost:3000"]
```

### Frontend (Vercel Preview)
```env
# Your staging/preview backend URL
NEXT_PUBLIC_API_URL=https://keelo-staging.up.railway.app
NEXT_PUBLIC_WS_URL=wss://keelo-staging.up.railway.app/ws/chat

# Firebase (same as local)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCgmwHYJ1m3bqxWfnf29c8SSTtzyfWH74Q
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=keelo-5924a.firebaseapp.com
NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://keelo-5924a-default-rtdb.firebaseio.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=keelo-5924a
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=keelo-5924a.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=146204271487
NEXT_PUBLIC_FIREBASE_APP_ID=1:146204271487:web:76aa00c87a940ba2aef04a
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-VLB1J1F72L
```

## Step 4: Deploy Frontend to Vercel (Staging)

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Deploy to preview (NOT production)
cd frontend
vercel --no-prod

# This creates a preview deployment with a unique URL
# e.g., keelo-abc123.vercel.app
```

Or use Vercel Dashboard:
1. Import repository
2. Select `feature/firebase-auth` branch
3. Set root directory to `frontend`
4. Add environment variables
5. Deploy as preview

## Step 5: Database Migration (STAGING ONLY)

**⚠️ CRITICAL**: Only run on staging database!

```bash
# SSH into your Railway staging service
railway run --service=keelo-staging bash

# Inside the container
cd backend
alembic upgrade head

# Verify tables were created
railway run --service=keelo-staging railway exec "psql $DATABASE_URL -c '\dt'"
```

## Step 6: Testing Checklist

Test on staging environment:
- [ ] Existing features still work (chat, analysis)
- [ ] Registration with email/password works
- [ ] Google sign-in works
- [ ] User sessions persist
- [ ] WebSocket connections work with auth
- [ ] Rate limiting works (10 analyses for free users)
- [ ] Sign out works
- [ ] Database has new user tables

## Step 7: Production Deployment (After Staging Success)

### A. Backend (Railway)
1. **BACKUP YOUR DATABASE FIRST**:
   ```bash
   railway run railway exec "pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql"
   ```

2. **Merge to main branch**:
   ```bash
   git checkout main
   git merge feature/firebase-auth
   git push origin main
   ```

3. **Add environment variables** (Railway Dashboard):
   - Add only the NEW variables
   - Update CORS_ORIGINS to include production frontend

4. **Run migration**:
   ```bash
   railway run alembic upgrade head
   ```

### B. Frontend (Vercel)
1. In Vercel Dashboard, promote preview to production
2. Or redeploy main branch with new env vars

## Step 8: Rollback Plan

If anything goes wrong:

### Quick Rollback:
1. **Railway**: Redeploy previous commit
   ```bash
   railway up --detach <previous-commit-hash>
   ```

2. **Vercel**: Instant rollback button in dashboard

3. **Database**: If migration caused issues
   ```bash
   railway run alembic downgrade -1
   ```

### Full Rollback:
```bash
git revert HEAD
git push origin main
```

## Step 9: Monitor After Deployment

Watch for:
- Error rates in Railway logs
- Firebase Authentication dashboard for sign-ups
- WebSocket connection stability
- Database query performance

## Production URLs to Update

After successful deployment, update:

1. **Firebase Authorized Domains**:
   - Add your production domain (e.g., keelo.ai)
   - Add Vercel domain (e.g., keelo.vercel.app)

2. **Railway CORS_ORIGINS**:
   ```env
   CORS_ORIGINS=["https://keelo.ai", "https://www.keelo.ai", "https://keelo.vercel.app"]
   ```

3. **Frontend Environment**:
   ```env
   NEXT_PUBLIC_API_URL=https://your-railway-production-url
   NEXT_PUBLIC_WS_URL=wss://your-railway-production-url/ws/chat
   ```

## Emergency Contacts

- Railway Status: https://status.railway.app
- Vercel Status: https://vercel-status.com
- Firebase Status: https://status.firebase.google.com

## DO NOT:
- ❌ Deploy directly to production without testing
- ❌ Run migrations on production without backup
- ❌ Delete or modify existing environment variables
- ❌ Change database schema without migration
- ❌ Deploy during peak hours

## DO:
- ✅ Test everything on staging first
- ✅ Keep existing features working
- ✅ Backup before any database changes
- ✅ Monitor after deployment
- ✅ Have a rollback plan ready