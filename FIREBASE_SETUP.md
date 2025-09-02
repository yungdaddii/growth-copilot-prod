# Firebase Authentication Setup Guide

## Overview
This guide explains how to set up Firebase Authentication for Keelo.ai (formerly Growth Co-pilot).

## Prerequisites
- Firebase project created at https://console.firebase.google.com
- Node.js and Python installed
- PostgreSQL database running

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install firebase-admin==6.5.0
```

### 2. Configure Environment Variables
Add to `backend/.env`:
```env
# Firebase Admin SDK (optional - for service account)
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json

# Or use default credentials in Google Cloud
```

### 3. Apply Database Migrations
```bash
cd backend
python3 -m alembic upgrade head
```

This creates:
- `users` table with Firebase UID and subscription management
- Foreign key relationships to link users with conversations and analyses
- User context tables for personalization

### 4. Backend Authentication Flow
The backend implements:
- `/api/auth/login` - Verify Firebase token and create/get user
- `/api/auth/me` - Get current user profile
- `/api/auth/logout` - Revoke refresh tokens
- WebSocket authentication via token parameter

## Frontend Setup

### 1. Install Firebase SDK
```bash
cd frontend
npm install firebase
```

### 2. Configure Environment Variables
Create `frontend/.env.local`:
```env
# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/chat

# Firebase Configuration (from Firebase Console)
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-storage-bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your-measurement-id
```

### 3. Get Firebase Configuration
1. Go to Firebase Console > Project Settings
2. Under "Your apps", click on Web app (or create one)
3. Copy the configuration values

## Features Implemented

### User Authentication
- Email/password registration and login
- Google OAuth sign-in
- Persistent sessions
- Automatic token refresh

### User Management
- User profiles with company information
- Subscription tiers (Free, Starter, Pro, Enterprise)
- Usage tracking and limits
- Feature flags per tier

### Data Association
- Conversations linked to authenticated users
- Analyses tracked per user
- User context for personalization
- Anonymous session support for non-authenticated users

### Security
- Firebase ID token verification
- Protected API endpoints
- WebSocket authentication
- Rate limiting based on subscription tier

## Usage

### Frontend Components

**AuthModal** - Modal for login/registration
```tsx
import AuthModal from '@/components/auth/AuthModal'

<AuthModal isOpen={showAuth} onClose={() => setShowAuth(false)} />
```

**useAuth Hook** - Access authentication state
```tsx
import { useAuth } from '@/hooks/useAuth'

const { user, profile, login, logout } = useAuth()
```

### Backend Authentication

**Protect API Endpoints**
```python
from app.core.auth import get_current_user, User
from fastapi import Depends

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.email}
```

**Optional Authentication**
```python
from app.core.auth import get_optional_user

@router.get("/public")
async def public_route(user: Optional[User] = Depends(get_optional_user)):
    if user:
        return {"message": f"Hello {user.email}"}
    return {"message": "Hello anonymous"}
```

## Testing

### 1. Start Services
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Test Registration
1. Visit http://localhost:3000
2. Click "Sign In" in header
3. Switch to "Create Account"
4. Fill form and submit
5. Verify user created in database

### 3. Test Login
1. Click "Sign In"
2. Enter credentials
3. Verify authenticated state
4. Check WebSocket includes token

### 4. Test WebSocket Auth
```javascript
// Browser console
// Should see WebSocket URL with token parameter
// ws://localhost:8000/ws/chat?session_id=xxx&token=xxx
```

## Subscription Tiers

| Tier | Monthly Analyses | Export Data | API Access | Price |
|------|-----------------|-------------|------------|--------|
| Free | 10 | ❌ | ❌ | $0 |
| Starter | 50 | ✅ | ❌ | $29 |
| Pro | 200 | ✅ | ✅ | $99 |
| Enterprise | Unlimited | ✅ | ✅ | Custom |

## Troubleshooting

### Firebase Token Verification Failed
- Check Firebase project configuration
- Ensure Firebase Admin SDK is initialized
- Verify environment variables are set

### User Not Created in Database
- Check database connection
- Verify migrations applied
- Check backend logs for errors

### WebSocket Not Authenticated
- Ensure user is logged in
- Check token is included in WebSocket URL
- Verify backend WebSocket handler processes token

## Next Steps
1. Add email verification flow
2. Implement password reset
3. Add social login providers (GitHub, LinkedIn)
4. Implement Stripe subscription management
5. Add admin dashboard for user management