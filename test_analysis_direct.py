#!/usr/bin/env python3
"""Test the analysis directly to see if it returns data."""

import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# Import the analyzer
import sys
sys.path.append('backend')

from app.core.analyzer import DomainAnalyzer
from app.config import settings

async def test_analysis():
    """Test domain analysis directly."""
    
    # Create database connection
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/growthcopilot",
        echo=True
    )
    
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        analyzer = DomainAnalyzer(session)
        
        print("Starting analysis for stripe.com...")
        
        # Run analysis
        conversation_id = uuid4()
        
        def update_callback(status, message, progress=None):
            print(f"[{progress}%] {status}: {message}")
        
        try:
            result = await analyzer.analyze(
                domain="stripe.com",
                conversation_id=conversation_id,
                update_callback=lambda *args: asyncio.create_task(print_update(*args))
            )
            
            print("\n✅ Analysis completed!")
            print(f"Performance Score: {result.performance_score}")
            print(f"Conversion Score: {result.conversion_score}")
            print(f"SEO Score: {result.seo_score}")
            print(f"Mobile Score: {result.mobile_score}")
            
            if result.issues_found:
                print(f"\nFound {len(result.issues_found)} issues:")
                for issue in result.issues_found[:3]:
                    print(f"  - {issue}")
            
            if result.results:
                # Check specific data
                perf = result.results.get("performance", {})
                print(f"\nPerformance data: {json.dumps(perf, indent=2)[:500]}")
                
                comp = result.results.get("competitors", {})
                print(f"\nCompetitor data exists: {bool(comp)}")
                if comp:
                    print(f"Competitors found: {len(comp.get('competitors', []))}")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()

async def print_update(status, message, progress):
    print(f"[{progress}%] {status}: {message}")

if __name__ == "__main__":
    asyncio.run(test_analysis())