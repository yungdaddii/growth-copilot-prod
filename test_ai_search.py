#!/usr/bin/env python3
"""Test AI Search Analyzer functionality"""

import asyncio
import sys
sys.path.insert(0, '/app')  # For Docker environment

from app.analyzers.ai_search import AISearchAnalyzer

async def test_ai_search():
    analyzer = AISearchAnalyzer()
    
    # Test with a domain
    domain = "stripe.com"
    print(f"\nAnalyzing AI Search optimization for {domain}...")
    
    results = await analyzer.analyze(domain)
    
    print(f"\n✓ AI Visibility Score: {results.get('ai_visibility_score')}/100")
    print(f"✓ AI Readiness: {results.get('ai_readiness')}")
    print(f"✓ Has llms.txt: {results.get('has_llms_txt')}")
    print(f"✓ Schema types found: {len(results.get('schema_types_found', []))}")
    
    blocked = results.get('blocked_crawlers', [])
    if blocked:
        print(f"\n⚠️  Blocked AI Crawlers:")
        for crawler in blocked[:3]:
            print(f"   - {crawler['platform']} ({crawler['bot']})")
    
    recommendations = results.get('recommendations', [])
    if recommendations:
        print(f"\n📋 Top Recommendations:")
        for rec in recommendations[:3]:
            print(f"\n   Priority: {rec['priority'].upper()}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Fix: {rec['fix']}")
            print(f"   Effort: {rec['effort']}")
    
    print("\n✅ AI Search Analyzer test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_ai_search())