#!/usr/bin/env python3
"""
Script to manually clear Google Ads credentials from Redis.
Run this to force a clean disconnect.
"""

import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_credentials():
    """Clear all Google Ads credentials from Redis."""
    
    # Connect to Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    client = redis.from_url(redis_url, decode_responses=True)
    
    try:
        # Find all Google Ads credential keys
        keys = await client.keys("google_ads:credentials:*")
        
        if keys:
            print(f"Found {len(keys)} Google Ads credential entries:")
            for key in keys:
                print(f"  - {key}")
                await client.delete(key)
            print("✅ All Google Ads credentials cleared!")
        else:
            print("No Google Ads credentials found in Redis.")
        
        # Also clear OAuth state tokens
        oauth_keys = await client.keys("oauth:google_ads:state:*")
        if oauth_keys:
            print(f"\nClearing {len(oauth_keys)} OAuth state tokens...")
            for key in oauth_keys:
                await client.delete(key)
            print("✅ OAuth state tokens cleared!")
    
    finally:
        await client.close()

if __name__ == "__main__":
    print("🧹 Clearing Google Ads credentials from Redis...")
    asyncio.run(clear_credentials())
    print("\nYou can now reconnect Google Ads from the UI.")