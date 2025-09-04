# Stable Version Reference

## Current Stable Release: v1.1.0-stable

**Release Date**: September 3, 2025
**Commit Hash**: 7bac584
**GitHub Release**: https://github.com/yungdaddii/growth-copilot-prod/releases/tag/v1.1.0-stable

## Quick Recovery Instructions

If you need to revert to this stable version:

```bash
# Fetch all tags
git fetch --tags

# Checkout the stable version
git checkout v1.1.0-stable

# If you need to create a new branch from stable
git checkout -b recovery-branch v1.1.0-stable

# Force push to main if needed (BE CAREFUL!)
git push origin v1.1.0-stable:main --force
```

## Verification Checklist

After deploying this version, verify:

- [ ] Backend responds at: https://growth-copilot-prod-production.up.railway.app/
- [ ] Frontend loads at: https://keelo.ai/
- [ ] Auth endpoint works: `curl -H "Authorization: Bearer test" https://growth-copilot-prod-production.up.railway.app/api/auth/me`
- [ ] Health check passes: https://growth-copilot-prod-production.up.railway.app/health
- [ ] Firebase status OK: https://growth-copilot-prod-production.up.railway.app/health/firebase
- [ ] Sign up/Sign in works on frontend
- [ ] Chat analysis works after sign in

## Key Files in This Version

### Backend Core Files
- `/backend/app/main.py` - Main FastAPI application
- `/backend/app/core/auth.py` - Authentication with AsyncSession
- `/backend/app/api/auth.py` - Auth endpoints with async/await
- `/backend/app/database.py` - Async database configuration

### Frontend Core Files
- `/frontend/app/page.tsx` - Main application page
- `/frontend/components/auth/AuthModalStyled.tsx` - Authentication modal
- `/frontend/hooks/useAuth.ts` - Firebase auth hook
- `/frontend/hooks/useWebSocket.ts` - WebSocket connection

## Critical Configuration

### Backend Requirements
- Python 3.11
- FastAPI with async support
- SQLAlchemy with AsyncSession
- Firebase Admin SDK
- All operations use `await` for database calls

### Database Operations
All database operations MUST use:
- `AsyncSession` not `Session`
- `await db.execute()` not `db.query()`
- `await db.commit()` not `db.commit()`
- `select(Model).where()` not `Model.query.filter()`

## What NOT to Change

1. **Don't modify auth imports** - The auth module is working, don't wrap in try/except
2. **Don't change AsyncSession back to Session** - This will break everything
3. **Don't remove await keywords** - All database operations are async
4. **Keep main and master branches synchronized** - Vercel deploys from master

## Recovery Commands

```bash
# If backend is broken
cd backend
git checkout v1.1.0-stable -- app/core/auth.py app/api/auth.py app/main.py

# If frontend is broken  
cd frontend
git checkout v1.1.0-stable -- app/page.tsx components/auth/

# Full recovery
git fetch --tags
git reset --hard v1.1.0-stable
git push origin main --force
git push origin main:master --force
```

## Contact for Issues

If you encounter issues with this stable version:
1. Check Railway logs: `railway logs`
2. Check Vercel logs: Vercel dashboard
3. Verify environment variables are set correctly
4. Ensure both main and master branches are synchronized

---

**Remember**: This version is FULLY WORKING. Always test new features in a separate branch before merging to main.