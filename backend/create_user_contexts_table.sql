-- Create user_contexts table if it doesn't exist
-- This table stores user context information for chat sessions

CREATE TABLE IF NOT EXISTS user_contexts (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    primary_domain VARCHAR(255),
    competitors TEXT[],
    industry VARCHAR(255),
    company_size VARCHAR(50),
    monitoring_sites TEXT[],
    preferences JSONB,
    last_analysis TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_contexts_session_id ON user_contexts(session_id);

-- Add comment
COMMENT ON TABLE user_contexts IS 'Stores user context and preferences for chat sessions';