# Simple Deployment Steps ✅

## What Just Happened:
- ✅ Merged Firebase auth to main branch
- ✅ Pushed to GitHub
- 🔄 Railway is now auto-deploying your backend

## Quick Setup Steps:

### 1. Railway Backend (Auto-deploying now)
Go to Railway dashboard and add these environment variables:

```env
# Firebase (Optional but recommended)
FIREBASE_PROJECT_ID=keelo-5924a

# Update CORS for your production frontend
CORS_ORIGINS=["https://keelo.ai","https://www.keelo.ai","https://keelo.vercel.app","http://localhost:3000"]
```

**Optional but Recommended**: Get Firebase Service Account
1. Go to: https://console.firebase.google.com/project/keelo-5924a/settings/serviceaccounts/adminsdk
2. Click "Generate new private key"
3. Copy the entire JSON content
4. Add to Railway as: `FIREBASE_SERVICE_ACCOUNT_JSON=<paste-json-here>`

### 2. Run Database Migration
Once Railway finishes deploying:

```bash
# Using Railway CLI
railway run alembic upgrade head

# Or use Railway's web terminal
# Go to your service > Settings > Generate Domain > Terminal
# Run: cd backend && alembic upgrade head
```

### 3. Deploy Frontend to Vercel

**Quick Deploy with Vercel CLI:**
```bash
cd frontend
npx vercel --prod
```

When prompted:
- Set up and deploy? **Y**
- Which scope? **Select your account**
- Link to existing project? **N** (create new)
- Project name? **keelo-ai** (or keep default)
- Directory? **./** (current directory)
- Build settings? **Accept defaults**

### 4. Add Environment Variables in Vercel

After deployment, go to Vercel Dashboard > Your Project > Settings > Environment Variables

Add these:
```env
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
NEXT_PUBLIC_WS_URL=wss://your-railway-url.up.railway.app/ws/chat

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCgmwHYJ1m3bqxWfnf29c8SSTtzyfWH74Q
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=keelo-5924a.firebaseapp.com
NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://keelo-5924a-default-rtdb.firebaseio.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=keelo-5924a
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=keelo-5924a.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=146204271487
NEXT_PUBLIC_FIREBASE_APP_ID=1:146204271487:web:76aa00c87a940ba2aef04a
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-VLB1J1F72L
```

Then redeploy: Click "Redeploy" in Vercel dashboard

### 5. Enable Firebase Authentication

Go to: https://console.firebase.google.com/project/keelo-5924a/authentication/providers

Enable:
- ✅ Email/Password
- ✅ Google

### 6. Update Authorized Domains

In Firebase Console > Authentication > Settings > Authorized domains, add:
- Your Vercel domain (e.g., `keelo-ai.vercel.app`)
- Your custom domain if you have one (e.g., `keelo.ai`)

## That's It! 🎉

Your app now has:
- User registration/login
- Google sign-in
- User profiles
- Usage tracking (10 free analyses/month)
- All existing features still work
- Anonymous users still supported

## Test It:
1. Visit your Vercel URL
2. Click "Sign In" button
3. Create an account or use Google
4. Chat and analyze websites as a logged-in user!

## Important Notes:
- Authentication is **optional** - users can still use the app without signing in
- All existing data and features remain unchanged
- The app is backward compatible