# Firebase Authentication Architecture for Keelo.ai

## Overview
Implementing a complete user authentication system using Firebase Auth with email/password and Google OAuth.

## Architecture Components

### 1. Backend (FastAPI)
```
backend/
├── app/
│   ├── models/
│   │   └── user.py              # User model (new)
│   ├── schemas/
│   │   └── auth.py              # Auth schemas (new)
│   ├── api/
│   │   └── auth.py              # Auth endpoints (new)
│   ├── middleware/
│   │   └── firebase_auth.py     # Firebase verification (new)
│   └── services/
│       └── firebase_admin.py    # Firebase Admin SDK (new)
```

### 2. Frontend (Next.js)
```
frontend/
├── app/
│   ├── (auth)/                  # Auth group (new)
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── (protected)/              # Protected routes (new)
│   │   └── dashboard/
├── components/
│   └── auth/                    # Auth components (new)
│       ├── LoginForm.tsx
│       ├── RegisterForm.tsx
│       └── AuthGuard.tsx
├── contexts/
│   └── AuthContext.tsx          # Auth context (new)
└── lib/
    └── firebase.ts              # Firebase client (new)
```

## Data Flow

### Registration Flow
1. User enters email/password on frontend
2. Frontend calls Firebase Auth `createUserWithEmailAndPassword`
3. Firebase returns user token
4. Frontend sends token to backend `/api/auth/register`
5. Backend verifies token with Firebase Admin SDK
6. Backend creates User record in PostgreSQL
7. Backend returns user profile
8. Frontend stores user in context and redirects to dashboard

### Login Flow
1. User enters credentials or clicks Google sign-in
2. Firebase Auth authenticates user
3. Frontend receives ID token
4. Frontend sends token to backend `/api/auth/login`
5. Backend verifies token and fetches/creates user
6. Backend returns user profile with session
7. WebSocket connections now include auth token

### Protected Routes
- Frontend: AuthGuard component checks Firebase auth state
- Backend: firebase_auth middleware verifies tokens
- WebSocket: Upgraded to require authentication

## Database Schema

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True)
    firebase_uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    display_name = Column(String)
    photo_url = Column(String, nullable=True)
    
    # User preferences
    company_name = Column(String, nullable=True)
    company_website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    role = Column(String, nullable=True)
    
    # Subscription
    subscription_tier = Column(String, default="free")
    subscription_status = Column(String, default="active")
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Relations
    contexts = relationship("UserContext", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")
```

### Updated UserContext
```python
class UserContext(Base):
    # ... existing fields ...
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="contexts")
```

## Implementation Steps

### Phase 1: Backend Setup
1. Install Firebase Admin SDK
2. Create User model and migration
3. Implement auth endpoints
4. Add Firebase middleware
5. Update WebSocket to require auth

### Phase 2: Frontend Auth
1. Install Firebase client SDK
2. Create AuthContext
3. Build login/register pages
4. Add AuthGuard component
5. Update navigation with user menu

### Phase 3: Migration
1. Update existing models with user relations
2. Migrate anonymous sessions to user accounts
3. Add data privacy controls
4. Implement user data export

## Security Considerations

### Token Management
- ID tokens expire after 1 hour
- Refresh tokens handled by Firebase SDK
- Backend validates every request
- WebSocket reconnects with new token

### Data Access
- All queries filtered by user_id
- Row-level security in database
- API rate limiting per user
- Audit logging for sensitive operations

### Privacy
- GDPR compliance with data export
- User data deletion on account removal
- Encrypted sensitive data
- No password storage (handled by Firebase)

## Environment Variables

### Backend (.env)
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
```

### Frontend (.env.local)
```
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

## Benefits

1. **Secure Authentication**: Industry-standard OAuth 2.0
2. **Social Login**: Google, GitHub, etc.
3. **No Password Management**: Firebase handles it
4. **Scalable**: Works with millions of users
5. **Real-time Auth State**: Automatic session management
6. **Multi-platform**: Same auth for web, mobile
7. **Built-in Features**: Password reset, email verification

## Migration Strategy

### For Existing Sessions
1. Show "Claim your account" prompt
2. Allow linking session to new account
3. Transfer all session data to user
4. Delete old session records

### Gradual Rollout
1. Start with optional registration
2. Show benefits of having an account
3. Eventually require auth for new features
4. Full migration after 30 days