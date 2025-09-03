# 🚨 CRITICAL: Database Migration Required After Deployment

## Immediate Actions Required:

### 1. Railway is Auto-Deploying Now
Since we pushed to GitHub, Railway is automatically deploying the backend changes.

### 2. Run Database Migration (REQUIRED!)
Once Railway finishes deploying, you MUST run this SQL on your production database:

Go to Railway Dashboard → Postgres Database → Query Tab and run:

```sql
-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add missing columns to conversations table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='user_id') THEN
        ALTER TABLE conversations ADD COLUMN user_id UUID;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='session_id') THEN
        ALTER TABLE conversations ADD COLUMN session_id VARCHAR;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='share_slug') THEN
        ALTER TABLE conversations ADD COLUMN share_slug VARCHAR(16);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='meta_data') THEN
        ALTER TABLE conversations ADD COLUMN meta_data JSON DEFAULT '{}';
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

-- Add missing columns to messages table  
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='messages' AND column_name='meta_data') THEN
        ALTER TABLE messages ADD COLUMN meta_data JSON DEFAULT '{}';
    END IF;
END $$;

-- Add missing columns to analyses table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='analyses' AND column_name='user_id') THEN
        ALTER TABLE analyses ADD COLUMN user_id UUID;
    END IF;
END $$;
```

### 3. Vercel Will Auto-Deploy Frontend
No action needed - Vercel will automatically deploy from the GitHub push.

## What We Fixed:
✅ Database schema mismatch (missing columns)
✅ WebSocket message processing errors  
✅ Model relationship loading issues
✅ Response quality restored with real analysis data

## Verify It's Working:
1. Check Railway logs for successful deployment
2. Test the chat with "analyze stripe.com"
3. Responses should now include real analysis data

The deployment is happening automatically now since we pushed to GitHub!