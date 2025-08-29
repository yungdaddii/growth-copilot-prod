# Fix Railway Database Connection

## The Issue
Railway can't reach Supabase's direct connection (port 5432) - getting "Network is unreachable"

## Solution: Use Pooler Connection

Set this DATABASE_URL in Railway:

```
postgresql+asyncpg://postgres.evfltcejtkodoqrshizs:GyND6conm8NqiFTv@aws-1-us-east-2.pooler.supabase.com:6543/postgres?prepared_statement_cache_size=0
```

This uses:
- Transaction pooler (port 6543) 
- AWS endpoint (reachable from Railway)
- Disabled prepared statements via URL parameter

## Alternative If Still Failing

Use the Session pooler instead (port 5432 on pooler endpoint):

```
postgresql+asyncpg://postgres.evfltcejtkodoqrshizs:GyND6conm8NqiFTv@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

## How to Update

1. Go to Railway dashboard
2. Click on your service
3. Go to Variables tab
4. Update DATABASE_URL
5. Railway will auto-redeploy

The code is already updated to handle pooler connections properly!