#!/usr/bin/env python3
"""Test if the app can start without errors"""

import sys
import os

# Add backend to path
sys.path.insert(0, '/app/backend')

try:
    print("Testing imports...")
    
    # Test core imports
    print("- Importing FastAPI...")
    from fastapi import FastAPI
    
    print("- Importing app.config...")
    from app.config import settings
    
    print("- Importing app.database...")
    from app.database import engine
    
    print("- Importing app.main...")
    from app.main import app
    
    print("\n✅ All imports successful!")
    print(f"App name: {settings.APP_NAME}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL configured: {'Yes' if settings.DATABASE_URL else 'No'}")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)