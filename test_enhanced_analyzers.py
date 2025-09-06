#!/usr/bin/env python3
"""
Test script for enhanced analyzers
Tests the new deep-insight analyzers with real domains
"""

import asyncio
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.analyzers.enhanced_seo import EnhancedSEOAnalyzer
from app.analyzers.enhanced_performance import EnhancedPerformanceAnalyzer
from app.analyzers.enhanced_conversion import EnhancedConversionAnalyzer


async def test_enhanced_seo():
    """Test Enhanced SEO Analyzer"""
    print("\n" + "="*60)
    print("Testing Enhanced SEO Analyzer")
    print("="*60)
    
    analyzer = EnhancedSEOAnalyzer()
    
    # Test with a real domain
    domain = "stripe.com"
    print(f"\nAnalyzing {domain}...")
    
    results = await analyzer.analyze(domain)
    
    # Display key insights
    print(f"\n✅ SEO Score: {results.get('score', 0)}/100")
    
    # Technical SEO
    if "technical_seo" in results:
        tech = results["technical_seo"]
        print("\n📊 Technical SEO:")
        if "robots_txt" in tech and tech["robots_txt"].get("ai_crawlers_blocked"):
            print(f"  ⚠️  AI Crawlers Blocked: {', '.join(tech['robots_txt']['ai_crawlers_blocked'])}")
        if "sitemap" in tech:
            print(f"  • Sitemap: {'✅ Found' if tech['sitemap'].get('exists') else '❌ Missing'}")
        if "security" in tech:
            print(f"  • HTTPS: {'✅ Enabled' if tech['security'].get('https') else '❌ Not secure'}")
    
    # Content Analysis
    if "content_quality" in results:
        content = results["content_quality"]
        print(f"\n📝 Content Analysis:")
        print(f"  • Word Count: {content.get('word_count', 0)}")
        print(f"  • Content Depth Score: {content.get('content_depth_score', 0)}/100")
        print(f"  • Readability Score: {content.get('readability_score', 0)}/100")
    
    # Keyword Intelligence
    if "keyword_intelligence" in results:
        keywords = results["keyword_intelligence"]
        print(f"\n🔑 Keyword Intelligence:")
        if keywords.get("top_keywords"):
            print("  Top Keywords:")
            for kw in keywords["top_keywords"][:5]:
                status = "✅" if kw["optimal"] else "⚠️"
                print(f"    {status} {kw['keyword']}: {kw['density']}% density")
    
    # Recommendations
    if "recommendations" in results:
        print(f"\n💡 Top Recommendations:")
        for rec in results["recommendations"][:3]:
            print(f"  • [{rec['priority']}] {rec['category']}: {rec['action']}")
            print(f"    Impact: {rec.get('impact', 'Unknown')}, Effort: {rec.get('effort', 'Unknown')}")
    
    return results


async def test_enhanced_performance():
    """Test Enhanced Performance Analyzer"""
    print("\n" + "="*60)
    print("Testing Enhanced Performance Analyzer")
    print("="*60)
    
    analyzer = EnhancedPerformanceAnalyzer()
    
    domain = "stripe.com"
    print(f"\nAnalyzing {domain}...")
    
    results = await analyzer.analyze(domain)
    
    print(f"\n✅ Performance Score: {results.get('score', 0)}/100")
    
    # Core Web Vitals
    if "core_web_vitals" in results:
        cwv = results["core_web_vitals"]
        print("\n🎯 Core Web Vitals:")
        
        if "lcp" in cwv:
            lcp_status = "🟢" if cwv["lcp"]["score"] == "good" else "🟡" if cwv["lcp"]["score"] == "needs_improvement" else "🔴"
            print(f"  {lcp_status} LCP: {cwv['lcp']['value']}s ({cwv['lcp']['score']})")
        
        if "fid" in cwv:
            fid_status = "🟢" if cwv["fid"]["score"] == "good" else "🟡" if cwv["fid"]["score"] == "needs_improvement" else "🔴"
            print(f"  {fid_status} FID: {cwv['fid']['value']}ms ({cwv['fid']['score']})")
        
        if "cls" in cwv:
            cls_status = "🟢" if cwv["cls"]["score"] == "good" else "🟡" if cwv["cls"]["score"] == "needs_improvement" else "🔴"
            print(f"  {cls_status} CLS: {cwv['cls']['value']} ({cwv['cls']['score']})")
    
    # Third-party Impact
    if "third_party_impact" in results:
        third_party = results["third_party_impact"]
        print(f"\n🔌 Third-Party Scripts:")
        print(f"  • Total: {third_party.get('total_third_party', 0)} scripts")
        print(f"  • Impact: {third_party.get('performance_impact', 'Unknown')}")
        if third_party.get("by_category"):
            print("  • Categories:")
            for cat, scripts in third_party["by_category"].items():
                print(f"    - {cat}: {len(scripts)} scripts")
    
    # Network Analysis
    if "network_analysis" in results:
        network = results["network_analysis"]
        print(f"\n🌐 Network Optimization:")
        print(f"  • HTTP/2: {'✅ Enabled' if network.get('http2_enabled') else '❌ Disabled'}")
        print(f"  • CDN: {'✅ ' + network.get('cdn_provider', 'Detected') if network.get('cdn_detected') else '❌ Not detected'}")
        print(f"  • Compression: {network.get('compression', 'Unknown')}")
    
    # Performance Budget
    if "performance_budget" in results:
        budget = results["performance_budget"]
        print(f"\n📊 Performance Budget:")
        for category in ["javascript", "css", "images"]:
            if category in budget:
                current = budget[category]["current"]
                recommended = budget[category]["recommended"]
                status = "⚠️" if budget[category]["over_budget"] else "✅"
                print(f"  {status} {category.capitalize()}: {current}KB (recommended: {recommended}KB)")
    
    return results


async def test_enhanced_conversion():
    """Test Enhanced Conversion Analyzer"""
    print("\n" + "="*60)
    print("Testing Enhanced Conversion Analyzer")
    print("="*60)
    
    analyzer = EnhancedConversionAnalyzer()
    
    domain = "stripe.com"
    print(f"\nAnalyzing {domain}...")
    
    results = await analyzer.analyze(domain)
    
    print(f"\n✅ Conversion Score: {results.get('conversion_score', 0)}/100")
    
    # Psychological Triggers
    if "psychological_triggers" in results:
        psych = results["psychological_triggers"]
        print("\n🧠 Psychological Triggers:")
        if "triggers" in psych:
            for trigger_type, data in psych["triggers"].items():
                status = "✅" if data["found"] else "❌"
                print(f"  {status} {trigger_type.capitalize()}: Score {data['score']}/100")
    
    # CTA Analysis
    if "cta_analysis" in results:
        cta = results["cta_analysis"]
        print(f"\n🎯 Call-to-Action Analysis:")
        print(f"  • Total CTAs: {cta.get('total_ctas', 0)}")
        print(f"  • Optimization Score: {cta.get('optimization_score', 0)}/100")
        if cta.get("recommendations"):
            print("  • Issues:")
            for rec in cta["recommendations"][:2]:
                print(f"    - {rec}")
    
    # Trust Signals
    if "trust_signals" in results:
        trust = results["trust_signals"]
        print(f"\n🛡️ Trust Signals:")
        print(f"  • Trust Score: {trust.get('trust_score', 0)}/100")
        if trust.get("security_badges"):
            print(f"  • Security Badges: {', '.join(trust['security_badges'])}")
        if trust.get("certifications"):
            print(f"  • Certifications: {', '.join(trust['certifications'])}")
    
    # Friction Analysis
    if "friction_points" in results:
        friction = results["friction_points"]
        print(f"\n⚡ Friction Analysis:")
        print(f"  • Friction Score: {friction.get('friction_score', 0)} (lower is better)")
        if friction.get("friction_points"):
            print("  • Friction Points:")
            for point in friction["friction_points"][:3]:
                print(f"    - {point}")
        if friction.get("smooth_elements"):
            print("  • Smooth Elements:")
            for element in friction["smooth_elements"]:
                print(f"    + {element}")
    
    # A/B Test Opportunities
    if "ab_test_opportunities" in results:
        print(f"\n🔬 A/B Test Opportunities:")
        for test in results["ab_test_opportunities"][:2]:
            print(f"  • {test['test_name']}:")
            print(f"    - Hypothesis: {test['hypothesis']}")
            print(f"    - Expected Impact: {test['expected_impact']}")
    
    # Quick Wins
    if "quick_wins" in results:
        print(f"\n⚡ Quick Wins:")
        for win in results["quick_wins"][:3]:
            print(f"  • {win['action']}:")
            print(f"    - Effort: {win['effort']}")
            print(f"    - Impact: {win['expected_impact']}")
    
    return results


async def main():
    """Run all enhanced analyzer tests"""
    print("\n🚀 Testing Enhanced Analyzers with Deep Insights")
    print("="*60)
    
    try:
        # Test SEO Analyzer
        seo_results = await test_enhanced_seo()
        
        # Test Performance Analyzer
        perf_results = await test_enhanced_performance()
        
        # Test Conversion Analyzer
        conv_results = await test_enhanced_conversion()
        
        print("\n" + "="*60)
        print("✅ All Enhanced Analyzer Tests Complete!")
        print("="*60)
        
        # Summary
        print("\n📊 Summary:")
        print(f"  • SEO Score: {seo_results.get('score', 0)}/100")
        print(f"  • Performance Score: {perf_results.get('score', 0)}/100")
        print(f"  • Conversion Score: {conv_results.get('conversion_score', 0)}/100")
        
        overall_score = (
            seo_results.get('score', 0) + 
            perf_results.get('score', 0) + 
            conv_results.get('conversion_score', 0)
        ) // 3
        
        print(f"\n🎯 Overall Score: {overall_score}/100")
        
        if overall_score >= 80:
            print("  Excellent! This site is well-optimized.")
        elif overall_score >= 60:
            print("  Good, but there's room for improvement.")
        else:
            print("  Significant optimization opportunities available.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())