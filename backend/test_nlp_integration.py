"""
Test Enhanced NLP Integration Locally
This script tests the enhanced NLP without affecting production
"""

import asyncio
import json
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_enhanced_nlp_flow():
    """Test the complete enhanced NLP flow"""
    
    print("\n" + "="*60)
    print("TESTING ENHANCED NLP INTEGRATION")
    print("="*60)
    
    # Test 1: Import Test
    print("\n1. Testing imports...")
    try:
        from app.core.conversation_context import ConversationContext
        from app.core.enhanced_nlp import EnhancedNLPProcessor
        print("✅ Imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Context Creation without Redis
    print("\n2. Testing context creation without Redis...")
    try:
        context = ConversationContext("test-session", redis_client=None)
        print("✅ Context created without Redis")
    except Exception as e:
        print(f"❌ Context creation failed: {e}")
        return False
    
    # Test 3: Enhanced NLP with Mock Analysis
    print("\n3. Testing enhanced NLP with mock data...")
    try:
        # Create mock analysis
        mock_analysis = Mock()
        mock_analysis.results = {
            "performance": {
                "score": 75,
                "load_time": 3.2,
                "first_contentful_paint": 1.8
            },
            "conversion": {
                "form_fields": 8,
                "required_fields": ["email", "name", "company", "phone"],
                "cta_text": "Submit",
                "has_free_trial": False,
                "has_pricing": True
            },
            "competitors": {
                "competitors": [
                    {"name": "Competitor1", "domain": "comp1.com", "features": ["free_trial", "api"]},
                    {"name": "Competitor2", "domain": "comp2.com", "features": ["pricing_page"]}
                ]
            },
            "recommendations": [
                {
                    "category": "conversion",
                    "issue": "Form has too many fields",
                    "priority": "high",
                    "action": "Remove phone and company fields",
                    "impact": "21% increase in conversions"
                }
            ],
            "quick_wins": []
        }
        mock_analysis.domain = "test.com"
        mock_analysis.industry = "SaaS"
        mock_analysis.performance_score = 75
        mock_analysis.conversion_score = 60
        mock_analysis.seo_score = 80
        mock_analysis.quick_wins = []
        
        # Create enhanced NLP processor
        nlp = EnhancedNLPProcessor(context=context)
        
        # Test intent detection
        intent = await nlp.detect_intent("analyze test.com")
        assert intent["type"] == "analyze_domain", f"Wrong intent: {intent['type']}"
        print("✅ Intent detection working")
        
        # Test response generation (without OpenAI)
        nlp.client = None  # Force fallback mode
        response = await nlp.generate_analysis_response(
            "test.com",
            mock_analysis,
            "analyze test.com"
        )
        
        assert "content" in response, "No content in response"
        print("✅ Response generation working")
        print(f"   Response preview: {response['content'][:100]}...")
        
    except Exception as e:
        print(f"❌ Enhanced NLP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: WebSocket Handler Import
    print("\n4. Testing WebSocket handler...")
    try:
        from app.api.websocket_enhanced import websocket_endpoint
        print("✅ Enhanced WebSocket handler imports successfully")
    except ImportError as e:
        print(f"❌ WebSocket import failed: {e}")
        return False
    
    # Test 5: Feature Flags
    print("\n5. Testing feature flags...")
    try:
        from app.utils.feature_flags import FeatureFlags
        
        # Test disabled
        os.environ["ENABLE_ENHANCED_NLP"] = "false"
        assert not FeatureFlags.is_enabled("enhanced_nlp")
        
        # Test enabled
        os.environ["ENABLE_ENHANCED_NLP"] = "true"
        assert FeatureFlags.is_enabled("enhanced_nlp")
        
        print("✅ Feature flags working")
    except Exception as e:
        print(f"❌ Feature flag test failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - Enhanced NLP is ready for testing")
    print("="*60)
    return True


async def test_with_real_analyzer():
    """Test with real analyzer if database is available"""
    print("\n" + "="*60)
    print("TESTING WITH REAL ANALYZER")
    print("="*60)
    
    try:
        from app.core.analyzer import DomainAnalyzer
        from app.database import get_db_context
        from app.core.enhanced_nlp import EnhancedNLPProcessor
        from app.core.conversation_context import ConversationContext
        
        print("\n1. Creating context and NLP processor...")
        context = ConversationContext("real-test", redis_client=None)
        nlp = EnhancedNLPProcessor(context=context)
        
        print("\n2. Testing with a simple domain...")
        # Use a fast-loading site for testing
        test_domain = "example.com"
        
        async with get_db_context() as db:
            analyzer = DomainAnalyzer(db)
            
            print(f"   Analyzing {test_domain}...")
            analysis = await analyzer.analyze(
                domain=test_domain,
                progress_callback=lambda msg, prog: print(f"   [{prog}%] {msg}")
            )
            
            print("\n3. Generating enhanced response...")
            response = await nlp.generate_analysis_response(
                test_domain,
                analysis,
                f"analyze {test_domain}"
            )
            
            print(f"\n✅ Response generated successfully!")
            print(f"   Length: {len(response.get('content', ''))} characters")
            print(f"   Has metadata: {bool(response.get('metadata'))}")
            
            # Check response quality
            content = response.get('content', '')
            if len(content) < 100:
                print("⚠️  Warning: Response seems too short")
            if "specific" not in content.lower() and "recommend" not in content.lower():
                print("⚠️  Warning: Response might be generic")
                
    except Exception as e:
        print(f"❌ Real analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Run all tests"""
    
    # Basic tests
    success = await test_enhanced_nlp_flow()
    
    if not success:
        print("\n❌ Basic tests failed. Fix these before proceeding.")
        return
    
    # Test with real analyzer if available
    print("\nDo you want to test with real analyzer? (requires database)")
    print("This will make actual API calls and may take 30-60 seconds.")
    
    # For automated testing, skip real analyzer
    # Uncomment the next line to test with real analyzer
    # await test_with_real_analyzer()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Run with Docker to test full integration:")
    print("   docker-compose up --build")
    print("\n2. Test with feature flag:")
    print("   ENABLE_ENHANCED_NLP=true docker-compose up")
    print("\n3. Monitor logs for:")
    print("   - '🚀 ENHANCED NLP ENABLED'")
    print("   - Any error messages")
    print("\n4. Test in browser:")
    print("   - Send 'analyze example.com'")
    print("   - Check if response is specific and contextual")


if __name__ == "__main__":
    asyncio.run(main())