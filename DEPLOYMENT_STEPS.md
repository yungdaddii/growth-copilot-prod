# Deployment Steps - Firebase Authentication 🚀

## ✅ Completed Steps:
1. Created feature branch: `feature/firebase-auth`
2. Committed all authentication changes
3. Pushed to GitHub

## 📍 Next Steps:

### 1. Railway Staging Deployment

Go to your Railway dashboard and:

#### Option A: Use Railway's PR Preview (Recommended)
1. Go to: https://github.com/yungdaddii/growth-copilot-prod/pull/new/feature/firebase-auth
2. Create a Pull Request to `main` branch
3. Railway will automatically create a preview environment
4. You'll get a unique URL like: `keelo-pr-1.up.railway.app`

#### Option B: Create Staging Service Manually
1. Go to Railway Dashboard
2. Click "New" → "GitHub Repo"
3. Select `growth-copilot-prod` repository
4. Choose branch: `feature/firebase-auth`
5. Name it: `keelo-staging`

### 2. Add Environment Variables to Railway Staging

In your Railway staging/preview environment, add these NEW variables:

```env
# Firebase configuration
FIREBASE_PROJECT_ID=keelo-5924a

# Get this from Firebase Console > Project Settings > Service Accounts
# Generate new private key and copy the entire JSON content
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"keelo-5924a"...}

# Update CORS to include staging URLs
CORS_ORIGINS=["https://keelo-pr-1.up.railway.app","https://keelo-staging.vercel.app","http://localhost:3000","http://localhost:3001"]
```

### 3. Vercel Frontend Deployment

Deploy frontend to Vercel staging:

```bash
# Option A: Using Vercel CLI
cd frontend
npx vercel --no-prod

# Option B: Using Vercel Dashboard
# 1. Go to https://vercel.com/new
# 2. Import: growth-copilot-prod
# 3. Select branch: feature/firebase-auth
# 4. Root directory: frontend
# 5. Deploy
```

### 4. Add Environment Variables to Vercel

In Vercel dashboard for your preview deployment:

```env
# Backend URLs (use your Railway staging URL)
NEXT_PUBLIC_API_URL=https://keelo-pr-1.up.railway.app
NEXT_PUBLIC_WS_URL=wss://keelo-pr-1.up.railway.app/ws/chat

# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCgmwHYJ1m3bqxWfnf29c8SSTtzyfWH74Q
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=keelo-5924a.firebaseapp.com
NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://keelo-5924a-default-rtdb.firebaseio.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=keelo-5924a
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=keelo-5924a.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=146204271487
NEXT_PUBLIC_FIREBASE_APP_ID=1:146204271487:web:76aa00c87a940ba2aef04a
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-VLB1J1F72L
```

### 5. Run Database Migration (Staging Only!)

After Railway staging is deployed:

```bash
# Use Railway CLI to run migration on staging
railway link
railway run --service=keelo-staging alembic upgrade head

# Or use Railway's web terminal
# Go to staging service > Settings > Terminal
# Run: cd backend && alembic upgrade head
```

### 6. Firebase Console Setup

1. Go to [Firebase Console](https://console.firebase.google.com/project/keelo-5924a/authentication/providers)
2. Enable Email/Password authentication
3. Enable Google authentication
4. Add authorized domains:
   - Your staging URLs (e.g., `keelo-staging.vercel.app`)
   - Your preview URLs from Railway

### 7. Test Everything on Staging

Test these features on your staging environment:
- [ ] Chat still works (anonymous)
- [ ] Sign up with email/password
- [ ] Sign in with Google
- [ ] User stays logged in
- [ ] WebSocket works with auth
- [ ] Sign out works
- [ ] Rate limiting (10 analyses for free users)

### 8. After Successful Testing

Once everything works on staging:

1. **Merge PR to main**:
   - Go to the PR on GitHub
   - Click "Merge pull request"
   - Railway will auto-deploy to production

2. **Update Production Environment Variables**:
   - Add the same Firebase variables to production
   - Update CORS_ORIGINS for production domains

3. **Run Migration on Production**:
   ```bash
   # BACKUP FIRST!
   railway run pg_dump $DATABASE_URL > backup_before_auth.sql
   
   # Then run migration
   railway run alembic upgrade head
   ```

## 🔗 Useful Links:

- PR: https://github.com/yungdaddii/growth-copilot-prod/pull/new/feature/firebase-auth
- Firebase Console: https://console.firebase.google.com/project/keelo-5924a
- Railway Dashboard: https://railway.app/dashboard
- Vercel Dashboard: https://vercel.com/dashboard

## 🆘 If Something Goes Wrong:

1. **Railway**: Use "Rollback" button in dashboard
2. **Vercel**: Use "Instant Rollback" in dashboard
3. **Database**: `railway run alembic downgrade -1`
4. **Git**: `git revert HEAD && git push`

## 📝 Notes:
- All existing functionality remains intact
- Anonymous users still work
- Auth is optional - not required to use the app
- No changes to existing data or tables