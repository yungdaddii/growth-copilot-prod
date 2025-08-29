#!/usr/bin/env python3
"""Test new analyzers: Page, Form Intelligence, Content Strategy"""

import asyncio
import sys
sys.path.insert(0, '/app')

from app.analyzers.page_analyzer import PageAnalyzer
from app.analyzers.form_intelligence import FormIntelligenceAnalyzer
from app.analyzers.content_strategy import ContentStrategyAnalyzer

async def test_analyzers():
    domain = "stripe.com"
    
    print(f"\n{'='*60}")
    print(f"Testing new analyzers for {domain}")
    print(f"{'='*60}")
    
    # Test Page Analyzer
    print("\n1. PAGE-SPECIFIC ANALYSIS")
    print("-" * 30)
    page_analyzer = PageAnalyzer()
    page_results = await page_analyzer.analyze(domain)
    
    print(f"✓ Pages found: {list(page_results['pages_found'].keys())}")
    print(f"✓ Critical issues: {len(page_results['critical_issues'])}")
    
    if page_results['page_recommendations']:
        print("\nTop Page Recommendations:")
        for rec in page_results['page_recommendations'][:2]:
            print(f"  • [{rec['priority'].upper()}] {rec['page']}: {rec['issue']}")
            print(f"    Fix: {rec['fix']}")
    
    # Test Form Intelligence
    print("\n2. FORM INTELLIGENCE ANALYSIS")
    print("-" * 30)
    form_analyzer = FormIntelligenceAnalyzer()
    form_results = await form_analyzer.analyze(domain)
    
    print(f"✓ Forms found: {form_results['forms_found']}")
    print(f"✓ Best practices score: {form_results['best_practices_score']}/100")
    print(f"✓ Estimated conversion lift potential: {form_results['estimated_conversion_lift']}%")
    
    if form_results['optimization_opportunities']:
        print("\nForm Optimization Opportunities:")
        for opp in form_results['optimization_opportunities'][:2]:
            print(f"  • [{opp['priority'].upper()}] {opp['issue']}")
            print(f"    Fix: {opp['fix']}")
            print(f"    Impact: {opp['impact']}")
    
    # Test Content Strategy
    print("\n3. CONTENT STRATEGY ANALYSIS")
    print("-" * 30)
    content_analyzer = ContentStrategyAnalyzer()
    # Use some example competitors
    competitors = ["paypal.com", "square.com", "adyen.com"]
    content_results = await content_analyzer.analyze(domain, competitors)
    
    print(f"✓ Current blog posts: {content_results['current_content'].get('blog_posts', 0)}")
    print(f"✓ Content score: {content_results['content_score']}/100")
    print(f"✓ Has blog: {content_results['current_content'].get('has_blog', False)}")
    
    if content_results['content_pillars']:
        print("\nRecommended Content Pillars:")
        for pillar in content_results['content_pillars'][:2]:
            print(f"  • {pillar['name']}: {pillar['description']}")
    
    if content_results['topic_recommendations']:
        print("\nTop Topic Recommendations:")
        for topic in content_results['topic_recommendations'][:3]:
            print(f"  • [{topic['priority'].upper()}] {topic['topic']}")
            print(f"    Type: {topic['type']} | Stage: {topic['stage']}")
    
    print(f"\n{'='*60}")
    print("✅ All new analyzers working successfully!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(test_analyzers())