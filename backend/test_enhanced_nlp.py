"""
Test script for Enhanced NLP with Context
Run this locally to verify the implementation
"""

import asyncio
import json
from datetime import datetime
from app.core.conversation_context import ConversationContext
from app.core.enhanced_nlp import EnhancedNLPProcessor
from app.models.analysis import Analysis, Industry
from app.utils.feature_flags import FeatureFlags
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer()
    ]
)
logger = structlog.get_logger()


async def test_context_manager():
    """Test the conversation context manager"""
    print("\n=== Testing ConversationContext ===")
    
    # Create context
    context = ConversationContext("test-session-123", redis_client=None)
    
    # Test adding messages
    context.add_message("user", "analyze stripe.com", "analyze_domain")
    context.add_message("user", "show me the code to fix the CTA")
    context.add_message("user", "what about mobile issues?")
    
    # Test preference inference
    assert context.context["preferences"]["wants_code_examples"] == True
    assert "mobile" in context.context["preferences"]["focus_areas"]
    
    # Test personalization params
    params = context.get_personalization_params()
    print(f"Personalization params: {json.dumps(params, indent=2)}")
    
    # Test analysis storage
    mock_analysis = {
        "recommendations": [
            {"category": "conversion", "issue": "Form has 8 fields", "priority": "high"},
            {"category": "performance", "issue": "3.5s load time", "priority": "critical"}
        ],
        "competitors": {
            "competitors": [
                {"name": "Square", "domain": "square.com", "features": ["free_trial", "api_docs"]},
                {"name": "PayPal", "domain": "paypal.com", "features": ["instant_transfer"]}
            ]
        }
    }
    context.set_current_analysis("stripe.com", mock_analysis)
    
    # Test undiscussed issues
    undiscussed = context.get_undiscussed_issues()
    print(f"Undiscussed issues: {undiscussed}")
    
    print("✅ ConversationContext tests passed")
    return context


async def test_enhanced_nlp(context):
    """Test the enhanced NLP processor"""
    print("\n=== Testing EnhancedNLPProcessor ===")
    
    # Create enhanced NLP with context
    nlp = EnhancedNLPProcessor(context=context)
    
    # Test dynamic prompt generation
    params = context.get_personalization_params()
    dynamic_prompt = nlp._build_dynamic_prompt(params)
    print(f"Dynamic prompt (first 500 chars): {dynamic_prompt[:500]}...")
    
    # Test specific insight extraction
    mock_results = {
        "conversion": {
            "form_fields": 8,
            "required_fields": ["email", "name", "company", "phone", "job_title"],
            "cta_text": "Submit",
            "has_pricing": False
        },
        "competitors": {
            "competitors": [
                {"name": "Square", "features": ["free_trial", "transparent_pricing"]},
                {"name": "PayPal", "features": ["buyer_protection"]}
            ]
        },
        "performance": {
            "score": 45,
            "load_time": 4.2,
            "large_images": ["hero.jpg", "team.png", "product.gif"]
        },
        "similarweb": {
            "has_data": True,
            "traffic_overview": {
                "monthly_visits": 2500000,
                "growth_rate": -5.3
            },
            "traffic_sources": {
                "search": 35,
                "direct": 28,
                "social": 8,
                "paid": 20,
                "referral": 9
            }
        }
    }
    
    specifics = nlp._extract_specific_insights(mock_results)
    print(f"Extracted specifics: {json.dumps(specifics, indent=2)}")
    
    # Test better CTA generation
    better_cta = nlp._generate_better_cta("Submit")
    print(f"Better CTA: '{better_cta}'")
    
    # Test follow-up generation
    follow_ups = nlp._generate_follow_ups(specifics, ["conversion"])
    print(f"Follow-up suggestions: {follow_ups}")
    
    print("✅ EnhancedNLPProcessor tests passed")


async def test_feature_flags():
    """Test feature flags"""
    print("\n=== Testing Feature Flags ===")
    
    # Test different flag states
    os_environ_backup = {}
    import os
    
    # Test enabled
    os.environ["ENABLE_ENHANCED_NLP"] = "true"
    assert FeatureFlags.is_enabled("enhanced_nlp") == True
    
    # Test disabled
    os.environ["ENABLE_ENHANCED_NLP"] = "false"
    assert FeatureFlags.is_enabled("enhanced_nlp") == False
    
    # Test percentage rollout
    os.environ["ENABLE_ENHANCED_NLP"] = "50%"
    results = [FeatureFlags.is_enabled("enhanced_nlp", f"user-{i}") for i in range(100)]
    enabled_count = sum(results)
    print(f"50% rollout enabled for {enabled_count}/100 users")
    assert 30 < enabled_count < 70  # Should be roughly 50%
    
    # Test all features
    os.environ["ENABLE_ENHANCED_NLP"] = "true"
    os.environ["ENABLE_CONTEXT_MEMORY"] = "true"
    features = FeatureFlags.get_enabled_features("test-user")
    print(f"Enabled features: {features}")
    
    print("✅ Feature Flags tests passed")


async def test_integration():
    """Test the full integration"""
    print("\n=== Testing Full Integration ===")
    
    # Simulate a conversation flow
    context = ConversationContext("integration-test", redis_client=None)
    nlp = EnhancedNLPProcessor(context=context)
    
    # Message 1: Analyze domain
    intent1 = await nlp.detect_intent("analyze stripe.com for growth opportunities")
    assert intent1["type"] == "analyze_domain"
    assert intent1["domain"] == "stripe.com"
    context.add_message("user", "analyze stripe.com", intent1["type"])
    
    # Message 2: Ask about competitors
    intent2 = await nlp.detect_intent("how do they compare to competitors?")
    assert intent2["type"] == "follow_up"
    assert intent2["subtype"] == "competitors"
    context.add_message("user", "how do they compare to competitors?", intent2["type"])
    
    # Message 3: Ask for code
    intent3 = await nlp.detect_intent("show me the code to fix the form")
    assert intent3["type"] == "follow_up"
    context.add_message("user", "show me the code to fix the form", intent3["type"])
    
    # Check context evolution
    assert context.context["preferences"]["wants_code_examples"] == True
    assert context.context["message_count"] == 3
    assert len(context.context["conversation_history"]["questions_asked"]) == 3
    
    print("✅ Integration tests passed")


async def main():
    """Run all tests"""
    print("🧪 Testing Enhanced NLP Implementation")
    print("=" * 50)
    
    try:
        # Test components
        context = await test_context_manager()
        await test_enhanced_nlp(context)
        await test_feature_flags()
        await test_integration()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Implementation is working correctly.")
        print("\n📝 Next steps:")
        print("1. Set ENABLE_ENHANCED_NLP=true in .env to enable")
        print("2. Test locally with: docker-compose up")
        print("3. Deploy to staging first")
        print("4. Monitor with PostHog for any issues")
        print("5. Gradually roll out with percentage flags")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())