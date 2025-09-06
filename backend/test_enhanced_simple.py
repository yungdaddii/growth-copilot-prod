#!/usr/bin/env python3
"""
Simple test for enhanced analyzers
"""

import asyncio
from app.analyzers.enhanced_seo import EnhancedSEOAnalyzer


async def test_seo():
    print("\nTesting Enhanced SEO Analyzer...")
    analyzer = EnhancedSEOAnalyzer()
    
    # Test with stripe.com
    domain = "stripe.com"
    print(f"Analyzing {domain}...")
    
    try:
        results = await analyzer.analyze(domain)
        
        print(f"\n✅ SEO Score: {results.get('score', 0)}/100")
        
        # Show some key findings
        if "recommendations" in results and results["recommendations"]:
            print("\n💡 Top Recommendations:")
            for rec in results["recommendations"][:3]:
                print(f"  • {rec.get('action', rec)}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_seo())
    exit(0 if success else 1)