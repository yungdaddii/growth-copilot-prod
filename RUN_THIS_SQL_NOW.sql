-- CRITICAL: Run this on your Railway Postgres database NOW
-- Go to Railway Dashboard → Postgres → Query tab

-- Create users table if missing
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fix conversations table
DO $$ 
BEGIN
    -- Add user_id column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='user_id') THEN
        ALTER TABLE conversations ADD COLUMN user_id UUID;
    END IF;
    
    -- Add session_id column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='session_id') THEN
        ALTER TABLE conversations ADD COLUMN session_id VARCHAR;
    END IF;
    
    -- Add share_slug column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='share_slug') THEN
        ALTER TABLE conversations ADD COLUMN share_slug VARCHAR(16);
    END IF;
    
    -- Add meta_data column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conversations' AND column_name='meta_data') THEN
        ALTER TABLE conversations ADD COLUMN meta_data JSON DEFAULT '{}';
    END IF;
END $$;

-- Create index
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

-- Fix messages table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='messages' AND column_name='meta_data') THEN
        ALTER TABLE messages ADD COLUMN meta_data JSON DEFAULT '{}';
    END IF;
END $$;

-- Fix analyses table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='analyses' AND column_name='user_id') THEN
        ALTER TABLE analyses ADD COLUMN user_id UUID;
    END IF;
END $$;

-- Verify the changes worked
SELECT 
    'conversations' as table_name,
    column_name,
    data_type 
FROM information_schema.columns 
WHERE table_name = 'conversations' 
AND column_name IN ('user_id', 'session_id', 'share_slug', 'meta_data')

UNION ALL

SELECT 
    'messages' as table_name,
    column_name,
    data_type 
FROM information_schema.columns 
WHERE table_name = 'messages' 
AND column_name = 'meta_data'

UNION ALL

SELECT 
    'analyses' as table_name,
    column_name,
    data_type 
FROM information_schema.columns 
WHERE table_name = 'analyses' 
AND column_name = 'user_id';