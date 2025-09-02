# Firebase Setup Complete! 🎉

Your Firebase credentials have been configured. Here's what to do next:

## 1. Enable Authentication Methods in Firebase

Go to [Firebase Console](https://console.firebase.google.com/project/keelo-5924a/authentication/providers) and enable:

1. **Email/Password**
   - Click on Email/Password
   - Toggle "Enable" 
   - Save

2. **Google Sign-In**
   - Click on Google
   - Toggle "Enable"
   - Add a project support email
   - Save

## 2. Configure Authorized Domains

In Firebase Console > Authentication > Settings > Authorized domains:
- `localhost` should already be there
- Add your production domain when ready (e.g., `keelo.ai`)

## 3. Test the Setup

```bash
# Terminal 1 - Start Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start Frontend
cd frontend
npm run dev
```

Visit http://localhost:3000 and test:
1. Click "Sign In" button in header
2. Try creating an account with email/password
3. Or sign in with Google

## 4. Optional: Backend Service Account (For Production)

For production deployment, you should use a service account:

1. Go to [Service Accounts](https://console.firebase.google.com/project/keelo-5924a/settings/serviceaccounts/adminsdk)
2. Click "Generate new private key"
3. Save the JSON file securely
4. Update `backend/.env`:
```env
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/keelo-5924a-firebase-adminsdk-xxxxx.json
```

## 5. Database Migration

If you haven't run the migration yet:

```bash
cd backend
# Install psycopg2 if needed
pip install psycopg2-binary

# Run migration
python -m alembic upgrade head
```

## Your Firebase Project Info

- **Project ID**: keelo-5924a
- **Auth Domain**: keelo-5924a.firebaseapp.com
- **Database URL**: https://keelo-5924a-default-rtdb.firebaseio.com
- **Console**: https://console.firebase.google.com/project/keelo-5924a

## Features Now Available

✅ User registration with email/password  
✅ Google OAuth sign-in  
✅ Persistent user sessions  
✅ User profiles with company info  
✅ Subscription tiers (Free, Starter, Pro, Enterprise)  
✅ Usage tracking (10 free analyses/month)  
✅ Conversations linked to users  
✅ WebSocket authentication  

## Common Issues

### "auth/operation-not-allowed"
- You need to enable the authentication method in Firebase Console

### "auth/unauthorized-domain"  
- Add your domain to authorized domains in Firebase Console

### Backend not verifying tokens
- The backend works without explicit Firebase config for local dev
- For production, add the service account JSON

## What's Next?

1. **Email Verification**: Add email verification flow
2. **Password Reset**: Implement forgot password
3. **Profile Management**: Let users update their profile
4. **Subscription Management**: Integrate Stripe for paid tiers
5. **Admin Dashboard**: Build admin panel for user management