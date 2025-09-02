# Firebase Quick Setup Guide 🚀

## Step 1: Create Firebase Project

1. Go to https://console.firebase.google.com
2. Click **Create a project**
3. Enter project name: "Keelo-AI" (or your preferred name)
4. Disable Google Analytics (optional)
5. Click **Create project**

## Step 2: Enable Authentication

1. In Firebase Console, click **Authentication** in left sidebar
2. Click **Get started**
3. Go to **Sign-in method** tab
4. Enable these providers:
   - **Email/Password**: Click, toggle Enable, Save
   - **Google**: Click, toggle Enable, add project support email, Save

## Step 3: Get Your Credentials

1. Click the gear icon ⚙️ → **Project settings**
2. Scroll to **Your apps** section
3. Click **</> Web** icon
4. App nickname: "Keelo Web App"
5. Click **Register app**
6. Copy the configuration object that appears

## Step 4: Add Credentials to Frontend

1. Create file: `frontend/.env.local`
2. Add your credentials:

```bash
# Copy these values from Firebase Console
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/chat

NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyD-XXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=keelo-ai.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=keelo-ai
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=keelo-ai.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

## Step 5: Backend Setup (Optional for Local Dev)

For local development, the backend will work without additional configuration.

For production, download service account:
1. Firebase Console → Project Settings → Service Accounts
2. Click **Generate new private key**
3. Save JSON file securely
4. Add to `backend/.env`:
```bash
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json
```

## Step 6: Test It Out! 🎉

```bash
# Terminal 1 - Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Start frontend
cd frontend
npm install  # If you haven't already
npm run dev
```

1. Open http://localhost:3000
2. Click **Sign In** button in header
3. Create a new account or sign in with Google
4. You're authenticated! 🎊

## What's Working Now

✅ User registration with email/password  
✅ Google sign-in  
✅ User sessions persist across refreshes  
✅ Conversations linked to your account  
✅ Usage tracking per user  
✅ WebSocket authentication  

## Troubleshooting

### "Firebase: Error (auth/invalid-api-key)"
- Double-check your API key in `.env.local`
- Make sure there are no extra spaces or quotes

### "Firebase: Error (auth/unauthorized-domain)"
- Add `localhost` to authorized domains:
- Firebase Console → Authentication → Settings → Authorized domains
- Add `localhost`

### Cannot connect to backend
- Make sure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` is correct in `.env.local`

### Changes not taking effect
- Restart the Next.js dev server after changing `.env.local`
- Clear browser cache and cookies

## Next Steps

After basic setup works:
1. Set up email verification
2. Add password reset functionality  
3. Configure production domains
4. Set up monitoring and analytics
5. Add subscription management with Stripe