#!/usr/bin/env python3
"""Add user_id and session_id columns to conversations table."""

import psycopg2
import os
import sys

def add_user_columns():
    """Add user_id and session_id columns to conversations table."""
    
    # Get DATABASE_URL from environment or Railway
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("Getting DATABASE_URL from Railway...")
        import subprocess
        result = subprocess.run(['railway', 'variables', '-k'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith('DATABASE_URL='):
                db_url = line.split('=', 1)[1]
                break
    
    if not db_url:
        print("ERROR: Could not get DATABASE_URL")
        sys.exit(1)
    
    # Convert asyncpg to postgresql
    if 'asyncpg' in db_url:
        db_url = db_url.replace('postgresql+asyncpg', 'postgresql')
    
    print(f"Connecting to database...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        # Check if columns already exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'conversations'
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        
        # Add user_id column if it doesn't exist
        if 'user_id' not in existing_columns:
            print("Adding user_id column to conversations table...")
            cur.execute("""
                ALTER TABLE conversations 
                ADD COLUMN user_id UUID 
                REFERENCES users(id) ON DELETE CASCADE
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id)
            """)
            print("✅ Added user_id column")
        else:
            print("user_id column already exists")
        
        # Add session_id column if it doesn't exist
        if 'session_id' not in existing_columns:
            print("Adding session_id column to conversations table...")
            cur.execute("""
                ALTER TABLE conversations 
                ADD COLUMN session_id VARCHAR
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
                ON conversations(session_id)
            """)
            print("✅ Added session_id column")
        else:
            print("session_id column already exists")
        
        # Also add user_id to analyses table if needed
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'analyses'
        """)
        analyses_columns = [row[0] for row in cur.fetchall()]
        
        if 'user_id' not in analyses_columns:
            print("Adding user_id column to analyses table...")
            cur.execute("""
                ALTER TABLE analyses 
                ADD COLUMN user_id UUID 
                REFERENCES users(id) ON DELETE CASCADE
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_analyses_user_id 
                ON analyses(user_id)
            """)
            print("✅ Added user_id column to analyses table")
        
        conn.commit()
        print("\n✅ Database schema updated successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    add_user_columns()