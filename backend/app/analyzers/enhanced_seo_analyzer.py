"""
Enhanced SEO Analyzer with Keyword Opportunities and Content Recommendations
Provides specific, actionable content creation strategies based on gaps and opportunities
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import re
import json
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urlparse, urljoin
from collections import Counter

from app.utils.cache import cache_result, get_cached_result
from app.config import settings

logger = structlog.get_logger()


class EnhancedSEOAnalyzer:
    """
    Advanced SEO analysis focusing on:
    - Keyword opportunity identification
    - Content gap analysis
    - Specific content recommendations (blogs, comparisons, guides)
    - Competitor content strategy
    - Search intent matching
    - Topical authority building
    """
    
    def __init__(self):
        self.ai_crawlers = ['GPTBot', 'ChatGPT-User', 'CCBot', 'Claude-Web', 'PerplexityBot', 'Amazonbot']
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
        # High-value keyword patterns by intent
        self.keyword_patterns = {
            "commercial": ["best", "top", "review", "compare", "vs", "versus", "alternative"],
            "transactional": ["buy", "price", "cost", "cheap", "deal", "discount", "coupon"],
            "informational": ["how to", "what is", "why", "guide", "tutorial", "learn"],
            "navigational": ["login", "sign in", "dashboard", "portal", "app"],
            "comparison": ["vs", "versus", "compare", "difference between", "alternative to"],
            "problem_aware": ["fix", "solve", "issue", "problem", "error", "troubleshoot"]
        }
        
        # Content type templates
        self.content_templates = {
            "comparison": {
                "pattern": "{product} vs {competitor}",
                "sections": ["Features", "Pricing", "Pros/Cons", "Use Cases", "Verdict"],
                "avg_word_count": 2500
            },
            "alternative": {
                "pattern": "Top {number} {product} Alternatives",
                "sections": ["Overview", "Features", "Pricing", "When to Use", "Comparison Table"],
                "avg_word_count": 3000
            },
            "how_to": {
                "pattern": "How to {action} with {product}",
                "sections": ["Introduction", "Prerequisites", "Step-by-Step", "Tips", "Common Issues"],
                "avg_word_count": 1500
            },
            "ultimate_guide": {
                "pattern": "Ultimate Guide to {topic}",
                "sections": ["What is X", "Why Important", "How it Works", "Best Practices", "Tools", "FAQs"],
                "avg_word_count": 4000
            },
            "listicle": {
                "pattern": "{number} Ways to {achieve_outcome}",
                "sections": ["Introduction", "Method Details", "Examples", "Conclusion"],
                "avg_word_count": 2000
            },
            "case_study": {
                "pattern": "How {company} {achieved} with {product}",
                "sections": ["Challenge", "Solution", "Implementation", "Results", "Key Takeaways"],
                "avg_word_count": 1800
            }
        }
        
        # Industry-specific keyword modifiers
        self.industry_modifiers = {
            "saas": ["software", "tool", "platform", "app", "solution", "system", "service"],
            "ecommerce": ["shop", "store", "buy", "order", "shipping", "cart", "checkout"],
            "b2b": ["enterprise", "business", "corporate", "team", "organization", "company"],
            "marketplace": ["sellers", "vendors", "suppliers", "providers", "listings"],
            "agency": ["services", "consulting", "strategy", "campaign", "management"]
        }
    
    async def analyze(self, domain: str, competitors: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive SEO analysis with keyword opportunities and content recommendations
        """
        cache_key = f"enhanced_seo:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "technical_seo": {},
            "keyword_opportunities": [],
            "content_gaps": [],
            "content_recommendations": [],
            "competitor_content_analysis": {},
            "search_visibility_score": 0,
            "topical_authority_gaps": [],
            "quick_wins": [],
            "long_term_strategy": [],
            "estimated_traffic_potential": 0,
            "ai_search_readiness": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Run all analyses in parallel
                tasks = [
                    self._analyze_technical_seo(domain, client),
                    self._identify_keyword_opportunities(domain, client),
                    self._analyze_content_gaps(domain, client),
                    self._generate_content_recommendations(domain, client),
                    self._analyze_existing_content(domain, client),
                    self._check_serp_features(domain, client),
                    self._analyze_internal_linking(domain, client),
                    self._analyze_competitor_content(domain, competitors, client) if competitors else None,
                    self._identify_topical_gaps(domain, client),
                    self._analyze_search_intent_coverage(domain, client)
                ]
                
                # Filter out None tasks
                tasks = [t for t in tasks if t is not None]
                
                analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(analysis_results):
                    if isinstance(result, Exception):
                        logger.error(f"SEO analysis task {i} failed", error=str(result))
                    elif result:
                        # Merge results based on task type
                        if i == 0:  # Technical SEO
                            results["technical_seo"] = result
                        elif i == 1:  # Keyword opportunities
                            results["keyword_opportunities"] = result.get("opportunities", [])
                            results["estimated_traffic_potential"] = result.get("traffic_potential", 0)
                        elif i == 2:  # Content gaps
                            results["content_gaps"] = result.get("gaps", [])
                        elif i == 3:  # Content recommendations
                            results["content_recommendations"] = result.get("recommendations", [])
                        elif i == 4:  # Existing content analysis
                            results["existing_content_quality"] = result
                        elif i == 5:  # SERP features
                            results["serp_opportunities"] = result
                        elif i == 6:  # Internal linking
                            results["internal_linking_health"] = result
                        elif i == 7 and competitors:  # Competitor content
                            results["competitor_content_analysis"] = result
                        elif i == 8:  # Topical gaps
                            results["topical_authority_gaps"] = result.get("gaps", [])
                        elif i == 9:  # Search intent
                            results["search_intent_coverage"] = result
                
                # Calculate comprehensive search visibility score
                results["search_visibility_score"] = self._calculate_visibility_score(results)
                
                # Generate prioritized quick wins
                results["quick_wins"] = self._identify_quick_wins(results)
                
                # Create long-term content strategy
                results["long_term_strategy"] = self._create_content_strategy(results)
                
                # AI search readiness check
                results["ai_search_readiness"] = await self._check_ai_search_readiness(domain, client)
                
                # Cache for 24 hours
                await cache_result(cache_key, results, ttl=86400)
                
        except Exception as e:
            logger.error(f"Enhanced SEO analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _identify_keyword_opportunities(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Identify high-value keyword opportunities based on domain analysis"""
        opportunities = []
        
        try:
            # Get homepage content
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.get_text().lower()
                
                # Extract current keywords from title and headings
                current_keywords = set()
                if soup.title:
                    current_keywords.update(soup.title.text.lower().split())
                for heading in soup.find_all(['h1', 'h2', 'h3']):
                    current_keywords.update(heading.get_text().lower().split())
                
                # Identify industry from content
                industry = self._detect_industry(content)
                industry_modifiers = self.industry_modifiers.get(industry, [])
                
                # Find brand/product name
                brand_name = self._extract_brand_name(soup, domain)
                
                # Generate keyword opportunities
                for intent, patterns in self.keyword_patterns.items():
                    for pattern in patterns:
                        for modifier in industry_modifiers:
                            keyword = f"{pattern} {modifier}"
                            if keyword not in content:
                                opportunities.append({
                                    "keyword": keyword,
                                    "intent": intent,
                                    "difficulty": "medium",
                                    "search_volume": "high" if intent in ["commercial", "transactional"] else "medium",
                                    "priority": "high" if intent in ["commercial", "comparison"] else "medium",
                                    "content_type": self._suggest_content_type(keyword, intent),
                                    "title_suggestion": self._generate_title(keyword, brand_name),
                                    "url_suggestion": f"/{keyword.replace(' ', '-')}",
                                    "estimated_traffic": self._estimate_traffic(intent)
                                })
                
                # Add competitor comparison keywords
                if brand_name:
                    comparison_keywords = [
                        f"{brand_name} alternatives",
                        f"{brand_name} competitors",
                        f"{brand_name} vs",
                        f"is {brand_name} worth it",
                        f"{brand_name} review",
                        f"{brand_name} pricing"
                    ]
                    
                    for kw in comparison_keywords:
                        if kw not in content:
                            opportunities.append({
                                "keyword": kw,
                                "intent": "commercial",
                                "difficulty": "low",
                                "search_volume": "high",
                                "priority": "critical",
                                "content_type": "comparison page",
                                "title_suggestion": self._generate_title(kw, brand_name),
                                "url_suggestion": f"/{kw.replace(' ', '-')}",
                                "estimated_traffic": 500
                            })
                
                # Add long-tail opportunities
                long_tail_opportunities = self._generate_long_tail_keywords(
                    brand_name, industry, current_keywords
                )
                opportunities.extend(long_tail_opportunities)
                
                # Sort by priority and estimated traffic
                opportunities = sorted(
                    opportunities, 
                    key=lambda x: (
                        {"critical": 3, "high": 2, "medium": 1, "low": 0}[x["priority"]],
                        x["estimated_traffic"]
                    ),
                    reverse=True
                )[:30]  # Top 30 opportunities
                
                # Calculate total traffic potential
                total_traffic = sum(opp["estimated_traffic"] for opp in opportunities)
                
                return {
                    "opportunities": opportunities,
                    "traffic_potential": total_traffic,
                    "quick_wins": [opp for opp in opportunities if opp["difficulty"] == "low"][:5]
                }
                
        except Exception as e:
            logger.error(f"Keyword opportunity identification failed", error=str(e))
            return {"opportunities": [], "traffic_potential": 0}
    
    async def _analyze_content_gaps(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Identify content gaps and missing page types"""
        gaps = []
        
        try:
            # Check for essential pages
            essential_pages = {
                "pricing": ["pricing", "plans", "cost"],
                "features": ["features", "capabilities", "benefits"],
                "about": ["about", "story", "team"],
                "blog": ["blog", "resources", "articles"],
                "comparison": ["compare", "vs", "alternatives"],
                "case_studies": ["case-study", "success-story", "customer"],
                "integrations": ["integrations", "apps", "connect"],
                "api_docs": ["api", "developers", "docs"],
                "faq": ["faq", "questions", "help"],
                "demo": ["demo", "trial", "try"],
                "contact": ["contact", "support", "help"]
            }
            
            # Get sitemap or crawl site structure
            existing_pages = await self._get_site_structure(domain, client)
            
            for page_type, patterns in essential_pages.items():
                found = False
                for pattern in patterns:
                    if any(pattern in page.lower() for page in existing_pages):
                        found = True
                        break
                
                if not found:
                    gap = {
                        "page_type": page_type,
                        "priority": self._get_page_priority(page_type),
                        "impact": self._estimate_page_impact(page_type),
                        "implementation": self._get_implementation_guide(page_type),
                        "examples": self._get_page_examples(page_type),
                        "estimated_traffic": self._estimate_page_traffic(page_type),
                        "conversion_impact": self._estimate_conversion_impact(page_type)
                    }
                    gaps.append(gap)
            
            # Check for content depth
            content_depth_gaps = await self._analyze_content_depth(domain, existing_pages, client)
            gaps.extend(content_depth_gaps)
            
            # Sort by priority and impact
            gaps = sorted(
                gaps,
                key=lambda x: (
                    {"critical": 3, "high": 2, "medium": 1, "low": 0}[x["priority"]],
                    x["estimated_traffic"]
                ),
                reverse=True
            )
            
            return {"gaps": gaps}
            
        except Exception as e:
            logger.error(f"Content gap analysis failed", error=str(e))
            return {"gaps": []}
    
    async def _generate_content_recommendations(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Generate specific content recommendations with titles and outlines"""
        recommendations = []
        
        try:
            # Get homepage and analyze business type
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.get_text().lower()
                
                brand_name = self._extract_brand_name(soup, domain)
                industry = self._detect_industry(content)
                
                # Generate comparison content recommendations
                comparison_recs = self._generate_comparison_content(brand_name, industry)
                recommendations.extend(comparison_recs)
                
                # Generate how-to guide recommendations
                howto_recs = self._generate_howto_content(brand_name, industry, content)
                recommendations.extend(howto_recs)
                
                # Generate ultimate guide recommendations
                guide_recs = self._generate_ultimate_guides(brand_name, industry)
                recommendations.extend(guide_recs)
                
                # Generate listicle recommendations
                listicle_recs = self._generate_listicles(brand_name, industry)
                recommendations.extend(listicle_recs)
                
                # Generate problem-solving content
                problem_recs = self._generate_problem_content(brand_name, industry)
                recommendations.extend(problem_recs)
                
                # Add specific details to each recommendation
                for rec in recommendations:
                    rec["outline"] = self._create_content_outline(rec["type"], rec["title"])
                    rec["keywords_to_target"] = self._identify_target_keywords(rec["title"])
                    rec["internal_links"] = self._suggest_internal_links(rec["type"])
                    rec["cta_suggestions"] = self._suggest_ctas(rec["type"])
                    rec["estimated_time_to_write"] = self._estimate_writing_time(rec.get("word_count", 2000))
                    rec["potential_ranking_difficulty"] = self._assess_ranking_difficulty(rec["keywords_to_target"])
                
                # Prioritize recommendations
                recommendations = sorted(
                    recommendations,
                    key=lambda x: x["estimated_monthly_traffic"],
                    reverse=True
                )[:20]  # Top 20 recommendations
                
                return {"recommendations": recommendations}
                
        except Exception as e:
            logger.error(f"Content recommendation generation failed", error=str(e))
            return {"recommendations": []}
    
    def _generate_comparison_content(self, brand_name: str, industry: str) -> List[Dict[str, Any]]:
        """Generate comparison and alternative content recommendations"""
        recommendations = []
        
        # Get common competitors for the industry
        competitor_sets = {
            "saas": ["Salesforce", "HubSpot", "Monday.com", "Asana", "Slack", "Zoom", "Notion"],
            "ecommerce": ["Shopify", "WooCommerce", "BigCommerce", "Magento", "Squarespace"],
            "marketing": ["Mailchimp", "Constant Contact", "SendGrid", "ConvertKit", "ActiveCampaign"],
            "analytics": ["Google Analytics", "Mixpanel", "Amplitude", "Heap", "Segment"],
            "payment": ["Stripe", "PayPal", "Square", "Braintree", "Authorize.net"]
        }
        
        # Find relevant competitors
        competitors = competitor_sets.get(industry, ["Competitor A", "Competitor B", "Competitor C"])
        
        # Generate comparison pages
        for competitor in competitors[:5]:
            recommendations.append({
                "type": "comparison",
                "title": f"{brand_name} vs {competitor}: In-Depth Comparison ({self._get_current_year()})",
                "url": f"/{brand_name.lower()}-vs-{competitor.lower().replace(' ', '-')}",
                "word_count": 2500,
                "estimated_monthly_traffic": 800,
                "conversion_potential": "high",
                "priority": "critical",
                "sections": [
                    "Quick Verdict",
                    "Feature Comparison Table",
                    "Pricing Breakdown",
                    "Ease of Use",
                    "Customer Support",
                    "Integrations",
                    "Pros and Cons",
                    "Who Should Choose Which",
                    "Migration Guide",
                    "FAQs"
                ]
            })
        
        # Generate alternatives page
        recommendations.append({
            "type": "alternatives",
            "title": f"Top 10 {brand_name} Alternatives & Competitors ({self._get_current_year()})",
            "url": f"/{brand_name.lower()}-alternatives",
            "word_count": 3500,
            "estimated_monthly_traffic": 1200,
            "conversion_potential": "medium",
            "priority": "high",
            "sections": [
                "Why Look for Alternatives",
                "Quick Comparison Table",
                "Detailed Reviews (10 alternatives)",
                "Pricing Comparison",
                "Feature Matrix",
                "How to Choose",
                "Migration Tips",
                "Conclusion"
            ]
        })
        
        return recommendations
    
    def _generate_howto_content(self, brand_name: str, industry: str, content: str) -> List[Dict[str, Any]]:
        """Generate how-to guide recommendations"""
        recommendations = []
        
        # Industry-specific how-to topics
        howto_topics = {
            "saas": [
                "get started",
                "import data",
                "integrate with",
                "automate workflow",
                "collaborate with team",
                "set up dashboard",
                "create reports"
            ],
            "ecommerce": [
                "set up store",
                "add products",
                "configure shipping",
                "process payments",
                "handle returns",
                "optimize checkout",
                "increase sales"
            ],
            "general": [
                "use advanced features",
                "troubleshoot common issues",
                "optimize performance",
                "secure account",
                "manage users",
                "export data"
            ]
        }
        
        topics = howto_topics.get(industry, howto_topics["general"])
        
        for topic in topics[:7]:
            recommendations.append({
                "type": "how_to",
                "title": f"How to {topic.title()} with {brand_name}: Step-by-Step Guide",
                "url": f"/how-to-{topic.replace(' ', '-')}-{brand_name.lower()}",
                "word_count": 1500,
                "estimated_monthly_traffic": 400,
                "conversion_potential": "medium",
                "priority": "medium",
                "sections": [
                    "Overview",
                    "Prerequisites",
                    "Step-by-Step Instructions",
                    "Screenshots/Videos",
                    "Pro Tips",
                    "Common Mistakes to Avoid",
                    "Troubleshooting",
                    "Next Steps"
                ]
            })
        
        return recommendations
    
    def _generate_ultimate_guides(self, brand_name: str, industry: str) -> List[Dict[str, Any]]:
        """Generate ultimate guide recommendations"""
        recommendations = []
        
        # High-value guide topics by industry
        guide_topics = {
            "saas": [
                f"Complete Guide to {industry.title()} Software",
                f"Ultimate {brand_name} Tutorial for Beginners",
                f"Enterprise {industry.title()} Implementation Guide",
                f"ROI Calculator and Business Case for {brand_name}"
            ],
            "ecommerce": [
                "Complete E-commerce Setup Guide",
                "Conversion Optimization Masterclass",
                "Scaling Your Online Store",
                "Multi-channel Selling Strategy"
            ],
            "general": [
                f"Everything You Need to Know About {brand_name}",
                f"Master {brand_name} in 30 Days",
                f"Advanced {brand_name} Techniques",
                f"{brand_name} Best Practices Guide"
            ]
        }
        
        topics = guide_topics.get(industry, guide_topics["general"])
        
        for topic in topics[:3]:
            recommendations.append({
                "type": "ultimate_guide",
                "title": topic,
                "url": f"/guide/{topic.lower().replace(' ', '-')}",
                "word_count": 4000,
                "estimated_monthly_traffic": 600,
                "conversion_potential": "high",
                "priority": "high",
                "sections": [
                    "Executive Summary",
                    "Chapter 1: Fundamentals",
                    "Chapter 2: Getting Started",
                    "Chapter 3: Advanced Features",
                    "Chapter 4: Best Practices",
                    "Chapter 5: Case Studies",
                    "Chapter 6: Troubleshooting",
                    "Resources and Tools",
                    "Glossary",
                    "FAQs"
                ]
            })
        
        return recommendations
    
    def _generate_listicles(self, brand_name: str, industry: str) -> List[Dict[str, Any]]:
        """Generate listicle content recommendations"""
        recommendations = []
        
        listicle_templates = [
            f"21 {brand_name} Tips Every User Should Know",
            f"15 Hidden {brand_name} Features You're Not Using",
            f"10 Ways to Get More Value from {brand_name}",
            f"25 {brand_name} Shortcuts to Save Hours",
            f"7 Common {brand_name} Mistakes (And How to Fix Them)",
            f"30 {brand_name} Integrations to Supercharge Your Workflow",
            f"12 {brand_name} Success Stories from Real Users"
        ]
        
        for title in listicle_templates[:4]:
            recommendations.append({
                "type": "listicle",
                "title": title,
                "url": f"/blog/{title.lower().replace(' ', '-')}",
                "word_count": 2000,
                "estimated_monthly_traffic": 350,
                "conversion_potential": "medium",
                "priority": "medium",
                "sections": [
                    "Introduction",
                    "The List (with details for each item)",
                    "Bonus Tips",
                    "Conclusion",
                    "Related Resources"
                ]
            })
        
        return recommendations
    
    def _generate_problem_content(self, brand_name: str, industry: str) -> List[Dict[str, Any]]:
        """Generate problem-solving content recommendations"""
        recommendations = []
        
        # Common problems by industry
        problems = {
            "saas": [
                "data migration issues",
                "integration problems",
                "performance optimization",
                "user adoption challenges",
                "scaling limitations"
            ],
            "ecommerce": [
                "cart abandonment",
                "low conversion rates",
                "shipping complications",
                "inventory management",
                "customer retention"
            ],
            "general": [
                "setup difficulties",
                "feature confusion",
                "billing questions",
                "security concerns",
                "team collaboration"
            ]
        }
        
        problem_list = problems.get(industry, problems["general"])
        
        for problem in problem_list[:3]:
            recommendations.append({
                "type": "problem_solving",
                "title": f"How to Fix {problem.title()} in {brand_name}",
                "url": f"/solve/{problem.replace(' ', '-')}",
                "word_count": 1800,
                "estimated_monthly_traffic": 450,
                "conversion_potential": "high",
                "priority": "high",
                "sections": [
                    "Understanding the Problem",
                    "Quick Diagnosis",
                    "Solution Steps",
                    "Prevention Tips",
                    "When to Get Help",
                    "Related Issues"
                ]
            })
        
        return recommendations
    
    async def _analyze_competitor_content(self, domain: str, competitors: List[str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze competitor content strategies"""
        competitor_analysis = {}
        
        for competitor in competitors[:3]:  # Analyze top 3 competitors
            try:
                response = await client.get(f"https://{competitor}", follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract content signals
                    analysis = {
                        "domain": competitor,
                        "blog_detected": bool(soup.find('a', href=re.compile(r'blog|articles|resources'))),
                        "content_types": self._detect_content_types(soup),
                        "estimated_pages": len(soup.find_all('a', href=True)),
                        "has_comparison_pages": self._check_comparison_pages(soup),
                        "has_case_studies": self._check_case_studies(soup),
                        "has_pricing_page": self._check_pricing_page(soup),
                        "content_freshness": self._check_content_freshness(soup),
                        "keyword_focus": self._extract_keyword_focus(soup)
                    }
                    
                    competitor_analysis[competitor] = analysis
                    
            except Exception as e:
                logger.debug(f"Competitor analysis failed for {competitor}: {e}")
        
        return competitor_analysis
    
    def _detect_content_types(self, soup: BeautifulSoup) -> List[str]:
        """Detect types of content present on site"""
        content_types = []
        
        patterns = {
            "blog": r'blog|articles|posts',
            "case_studies": r'case-stud|success-stor|customer-stor',
            "whitepapers": r'whitepaper|ebook|download',
            "webinars": r'webinar|event|workshop',
            "videos": r'video|youtube|vimeo|watch',
            "podcasts": r'podcast|episode|listen',
            "tools": r'calculator|tool|generator|checker',
            "templates": r'template|worksheet|checklist'
        }
        
        for content_type, pattern in patterns.items():
            if soup.find('a', href=re.compile(pattern, re.I)):
                content_types.append(content_type)
        
        return content_types
    
    def _create_content_outline(self, content_type: str, title: str) -> List[Dict[str, Any]]:
        """Create detailed content outline"""
        outline = []
        
        if content_type == "comparison":
            outline = [
                {"section": "Introduction", "word_count": 200, "key_points": ["Brief overview", "Why compare"]},
                {"section": "Quick Verdict", "word_count": 150, "key_points": ["Best for X", "Best for Y"]},
                {"section": "Feature Comparison", "word_count": 800, "key_points": ["Core features", "Unique features", "Missing features"]},
                {"section": "Pricing Analysis", "word_count": 400, "key_points": ["Plan comparison", "Value for money", "Hidden costs"]},
                {"section": "User Experience", "word_count": 300, "key_points": ["Ease of use", "Learning curve", "Support quality"]},
                {"section": "Pros and Cons", "word_count": 400, "key_points": ["Advantages", "Disadvantages", "Deal breakers"]},
                {"section": "Final Recommendation", "word_count": 250, "key_points": ["Who should choose", "Migration advice"]}
            ]
        elif content_type == "how_to":
            outline = [
                {"section": "Introduction", "word_count": 150, "key_points": ["What you'll learn", "Prerequisites"]},
                {"section": "Step 1", "word_count": 300, "key_points": ["Action", "Screenshot", "Tip"]},
                {"section": "Step 2", "word_count": 300, "key_points": ["Action", "Screenshot", "Warning"]},
                {"section": "Step 3", "word_count": 300, "key_points": ["Action", "Screenshot", "Alternative"]},
                {"section": "Troubleshooting", "word_count": 200, "key_points": ["Common issues", "Solutions"]},
                {"section": "Next Steps", "word_count": 150, "key_points": ["What to do next", "Related guides"]}
            ]
        elif content_type == "ultimate_guide":
            outline = [
                {"section": "Executive Summary", "word_count": 300, "key_points": ["Key takeaways", "Who this is for"]},
                {"section": "Chapter 1: Basics", "word_count": 800, "key_points": ["Fundamentals", "Terminology", "Concepts"]},
                {"section": "Chapter 2: Implementation", "word_count": 1000, "key_points": ["Setup", "Configuration", "Best practices"]},
                {"section": "Chapter 3: Advanced", "word_count": 800, "key_points": ["Pro features", "Optimization", "Automation"]},
                {"section": "Chapter 4: Case Studies", "word_count": 600, "key_points": ["Real examples", "Results", "Lessons"]},
                {"section": "Resources", "word_count": 200, "key_points": ["Tools", "Further reading", "Community"]}
            ]
        
        return outline
    
    def _identify_quick_wins(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify quick SEO wins that can be implemented immediately"""
        quick_wins = []
        
        # Technical quick wins
        if results.get("technical_seo", {}).get("missing_meta_description"):
            quick_wins.append({
                "task": "Add meta descriptions to key pages",
                "effort": "1 hour",
                "impact": "high",
                "specific_action": "Write unique 155-character descriptions for top 10 pages",
                "expected_result": "10-15% increase in CTR from search results"
            })
        
        # Content quick wins
        for opp in results.get("keyword_opportunities", [])[:3]:
            if opp.get("difficulty") == "low":
                quick_wins.append({
                    "task": f"Create content for '{opp['keyword']}'",
                    "effort": "2-3 hours",
                    "impact": "high",
                    "specific_action": f"Write {opp['word_count']}-word {opp['content_type']}",
                    "expected_result": f"{opp['estimated_traffic']} monthly visitors within 3 months"
                })
        
        # Schema markup quick wins
        if not results.get("technical_seo", {}).get("has_schema"):
            quick_wins.append({
                "task": "Add Organization schema markup",
                "effort": "30 minutes",
                "impact": "medium",
                "specific_action": "Add JSON-LD script to homepage header",
                "expected_result": "Enhanced search appearance and knowledge panel"
            })
        
        return quick_wins[:10]  # Top 10 quick wins
    
    def _create_content_strategy(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a long-term content strategy based on analysis"""
        strategy = []
        
        # Month 1: Foundation
        strategy.append({
            "phase": "Month 1: Foundation",
            "focus": "Fill critical content gaps",
            "tasks": [
                "Create comparison pages for top 3 competitors",
                "Write ultimate guide for main topic",
                "Add FAQ schema to existing pages",
                "Fix all technical SEO issues"
            ],
            "expected_traffic": 500
        })
        
        # Month 2: Expansion
        strategy.append({
            "phase": "Month 2: Expansion",
            "focus": "Target commercial keywords",
            "tasks": [
                "Publish 5 how-to guides",
                "Create alternatives page",
                "Add case studies section",
                "Build internal linking structure"
            ],
            "expected_traffic": 1500
        })
        
        # Month 3: Authority
        strategy.append({
            "phase": "Month 3: Authority Building",
            "focus": "Establish topical authority",
            "tasks": [
                "Launch blog with weekly posts",
                "Create resource hub",
                "Publish industry report",
                "Start link building campaign"
            ],
            "expected_traffic": 3000
        })
        
        return strategy
    
    # Helper methods
    def _detect_industry(self, content: str) -> str:
        """Detect industry from content"""
        industries = {
            "saas": ["software", "platform", "dashboard", "api", "integration", "subscription"],
            "ecommerce": ["shop", "cart", "product", "checkout", "shipping", "order"],
            "marketing": ["campaign", "email", "social media", "content", "seo", "advertising"],
            "finance": ["payment", "invoice", "accounting", "budget", "transaction", "banking"],
            "healthcare": ["patient", "medical", "health", "clinic", "diagnosis", "treatment"]
        }
        
        scores = {}
        for industry, keywords in industries.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[industry] = score
        
        return max(scores, key=scores.get) if scores else "general"
    
    def _extract_brand_name(self, soup: BeautifulSoup, domain: str) -> str:
        """Extract brand name from page"""
        # Try meta tags first
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name:
            return og_site_name.get('content', '').strip()
        
        # Try title
        if soup.title:
            title_parts = soup.title.text.split('|')
            if title_parts:
                return title_parts[-1].strip()
        
        # Fallback to domain name
        return domain.split('.')[0].title()
    
    def _get_current_year(self) -> str:
        """Get current year for content freshness"""
        from datetime import datetime
        return str(datetime.now().year)
    
    def _estimate_traffic(self, intent: str) -> int:
        """Estimate traffic based on search intent"""
        traffic_estimates = {
            "commercial": 500,
            "transactional": 300,
            "informational": 800,
            "navigational": 200,
            "comparison": 600,
            "problem_aware": 400
        }
        return traffic_estimates.get(intent, 250)
    
    def _suggest_content_type(self, keyword: str, intent: str) -> str:
        """Suggest content type based on keyword and intent"""
        if "vs" in keyword or "compare" in keyword:
            return "comparison page"
        elif "how to" in keyword:
            return "how-to guide"
        elif "best" in keyword or "top" in keyword:
            return "listicle"
        elif intent == "commercial":
            return "product page"
        elif intent == "informational":
            return "blog post"
        else:
            return "landing page"
    
    def _generate_title(self, keyword: str, brand_name: str) -> str:
        """Generate SEO-optimized title"""
        year = self._get_current_year()
        
        if "vs" in keyword:
            return f"{keyword.title()}: Detailed Comparison ({year})"
        elif "how to" in keyword:
            return f"{keyword.title()}: Step-by-Step Guide"
        elif "best" in keyword:
            return f"{keyword.title()} ({year} Updated)"
        elif "alternatives" in keyword:
            return f"{keyword.title()}: Top 10 Options Compared"
        else:
            return f"{keyword.title()} - {brand_name}"
    
    def _generate_long_tail_keywords(self, brand_name: str, industry: str, current_keywords: set) -> List[Dict[str, Any]]:
        """Generate long-tail keyword opportunities"""
        long_tail = []
        
        # Question-based long-tail
        questions = [
            f"what is {brand_name} used for",
            f"how much does {brand_name} cost",
            f"is {brand_name} free",
            f"does {brand_name} integrate with",
            f"can {brand_name} do",
            f"why use {brand_name}",
            f"when to use {brand_name}",
            f"who uses {brand_name}"
        ]
        
        for question in questions:
            if question not in str(current_keywords):
                long_tail.append({
                    "keyword": question,
                    "intent": "informational",
                    "difficulty": "low",
                    "search_volume": "medium",
                    "priority": "medium",
                    "content_type": "FAQ page",
                    "title_suggestion": question.title() + "?",
                    "url_suggestion": f"/faq/{question.replace(' ', '-')}",
                    "estimated_traffic": 150
                })
        
        return long_tail
    
    async def _get_site_structure(self, domain: str, client: httpx.AsyncClient) -> List[str]:
        """Get site structure from sitemap or crawling"""
        pages = []
        
        # Try sitemap first
        try:
            sitemap_response = await client.get(f"https://{domain}/sitemap.xml", timeout=5.0)
            if sitemap_response.status_code == 200:
                # Parse sitemap
                soup = BeautifulSoup(sitemap_response.text, 'xml')
                urls = soup.find_all('url')
                for url in urls:
                    loc = url.find('loc')
                    if loc:
                        pages.append(loc.text)
        except:
            pass
        
        # Fallback to homepage crawl
        if not pages:
            try:
                response = await client.get(f"https://{domain}", follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/') or domain in href:
                            pages.append(href)
            except:
                pass
        
        return list(set(pages))  # Remove duplicates
    
    async def _analyze_content_depth(self, domain: str, existing_pages: List[str], client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Analyze content depth and identify thin content"""
        gaps = []
        
        # Check if existing pages have sufficient depth
        for page in existing_pages[:10]:  # Check top 10 pages
            try:
                if page.startswith('/'):
                    url = f"https://{domain}{page}"
                else:
                    url = page
                
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    word_count = len(text.split())
                    
                    if word_count < 300:
                        gaps.append({
                            "page_type": "thin_content",
                            "url": page,
                            "current_word_count": word_count,
                            "recommended_word_count": 800,
                            "priority": "high",
                            "impact": "Improve rankings and user engagement",
                            "implementation": f"Expand content to at least 800 words with valuable information",
                            "estimated_traffic": 200,
                            "conversion_impact": "medium"
                        })
            except:
                continue
        
        return gaps
    
    def _get_page_priority(self, page_type: str) -> str:
        """Get priority for missing page type"""
        priorities = {
            "pricing": "critical",
            "features": "critical",
            "comparison": "critical",
            "demo": "high",
            "blog": "high",
            "case_studies": "high",
            "about": "medium",
            "integrations": "medium",
            "api_docs": "medium",
            "faq": "medium",
            "contact": "low"
        }
        return priorities.get(page_type, "medium")
    
    def _estimate_page_impact(self, page_type: str) -> str:
        """Estimate impact of adding page type"""
        impacts = {
            "pricing": "50% increase in qualified leads",
            "comparison": "30% better conversion for comparison shoppers",
            "features": "25% reduction in sales questions",
            "demo": "40% increase in trial signups",
            "blog": "200% increase in organic traffic over 6 months",
            "case_studies": "35% increase in enterprise conversions"
        }
        return impacts.get(page_type, "Improved user experience and SEO")
    
    def _get_implementation_guide(self, page_type: str) -> str:
        """Get implementation guide for page type"""
        guides = {
            "pricing": "Create transparent pricing tiers with clear feature comparisons",
            "comparison": "Build detailed comparisons with your top 3-5 competitors",
            "features": "List all features with benefits, use cases, and screenshots",
            "demo": "Offer both self-serve demo and guided demo options",
            "blog": "Start with 10 cornerstone pieces, then publish weekly",
            "case_studies": "Document 3-5 customer success stories with metrics"
        }
        return guides.get(page_type, "Create comprehensive content addressing user needs")
    
    def _get_page_examples(self, page_type: str) -> List[str]:
        """Get examples of good implementations"""
        examples = {
            "pricing": ["stripe.com/pricing", "slack.com/pricing"],
            "comparison": ["monday.com/compare", "hubspot.com/comparisons"],
            "features": ["notion.so/product", "airtable.com/features"],
            "demo": ["calendly.com/demo", "loom.com/demo"],
            "blog": ["intercom.com/blog", "buffer.com/resources"],
            "case_studies": ["shopify.com/success-stories", "zendesk.com/customer-stories"]
        }
        return examples.get(page_type, [])
    
    def _estimate_page_traffic(self, page_type: str) -> int:
        """Estimate monthly traffic for page type"""
        traffic = {
            "pricing": 1000,
            "comparison": 800,
            "features": 600,
            "demo": 500,
            "blog": 2000,
            "case_studies": 400,
            "about": 300,
            "integrations": 350,
            "api_docs": 250,
            "faq": 450,
            "contact": 200
        }
        return traffic.get(page_type, 250)
    
    def _estimate_conversion_impact(self, page_type: str) -> str:
        """Estimate conversion impact of page"""
        impacts = {
            "pricing": "high",
            "comparison": "high",
            "features": "medium",
            "demo": "high",
            "blog": "low",
            "case_studies": "high",
            "about": "low",
            "integrations": "medium",
            "api_docs": "low",
            "faq": "medium",
            "contact": "medium"
        }
        return impacts.get(page_type, "medium")
    
    def _check_comparison_pages(self, soup: BeautifulSoup) -> bool:
        """Check if site has comparison pages"""
        comparison_indicators = ['vs', 'versus', 'compare', 'comparison', 'alternative']
        for indicator in comparison_indicators:
            if soup.find('a', href=re.compile(indicator, re.I)):
                return True
        return False
    
    def _check_case_studies(self, soup: BeautifulSoup) -> bool:
        """Check if site has case studies"""
        case_study_indicators = ['case-study', 'success-story', 'customer-story', 'testimonial']
        for indicator in case_study_indicators:
            if soup.find('a', href=re.compile(indicator, re.I)):
                return True
        return False
    
    def _check_pricing_page(self, soup: BeautifulSoup) -> bool:
        """Check if site has pricing page"""
        return bool(soup.find('a', href=re.compile(r'pric|plan|cost', re.I)))
    
    def _check_content_freshness(self, soup: BeautifulSoup) -> str:
        """Check content freshness indicators"""
        import datetime
        current_year = str(datetime.datetime.now().year)
        
        if current_year in soup.get_text():
            return "current"
        elif str(int(current_year) - 1) in soup.get_text():
            return "recent"
        else:
            return "outdated"
    
    def _extract_keyword_focus(self, soup: BeautifulSoup) -> List[str]:
        """Extract main keywords from competitor"""
        keywords = []
        
        # Extract from title
        if soup.title:
            keywords.extend(soup.title.text.lower().split()[:5])
        
        # Extract from H1
        h1 = soup.find('h1')
        if h1:
            keywords.extend(h1.get_text().lower().split()[:3])
        
        # Extract from meta keywords (if present)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords.extend(meta_keywords.get('content', '').lower().split(',')[:5])
        
        return list(set(keywords))[:10]  # Top 10 unique keywords
    
    def _suggest_internal_links(self, content_type: str) -> List[str]:
        """Suggest internal links for content type"""
        suggestions = {
            "comparison": ["/features", "/pricing", "/demo", "/alternatives"],
            "how_to": ["/features", "/support", "/documentation", "/tutorials"],
            "ultimate_guide": ["/get-started", "/features", "/pricing", "/case-studies"],
            "listicle": ["/features", "/blog", "/resources", "/demo"],
            "problem_solving": ["/support", "/documentation", "/contact", "/features"]
        }
        return suggestions.get(content_type, ["/features", "/pricing", "/demo"])
    
    def _suggest_ctas(self, content_type: str) -> List[str]:
        """Suggest CTAs for content type"""
        ctas = {
            "comparison": ["Start Free Trial", "Book a Demo", "See Full Comparison"],
            "how_to": ["Try It Yourself", "Get Started Free", "Download Guide"],
            "ultimate_guide": ["Start Learning", "Download PDF Version", "Join Community"],
            "listicle": ["Explore Features", "Start Free Trial", "Learn More"],
            "problem_solving": ["Get Help Now", "Contact Support", "Try Solution"]
        }
        return ctas.get(content_type, ["Learn More", "Get Started", "Contact Us"])
    
    def _estimate_writing_time(self, word_count: int) -> str:
        """Estimate time to write content"""
        # Assuming 250 words per hour including research
        hours = word_count / 250
        if hours < 1:
            return "30-45 minutes"
        elif hours < 4:
            return f"{int(hours)}-{int(hours)+1} hours"
        elif hours < 8:
            return "1 day"
        else:
            return f"{int(hours/8)} days"
    
    def _assess_ranking_difficulty(self, keywords: List[str]) -> str:
        """Assess difficulty of ranking for keywords"""
        # Simplified assessment based on keyword competitiveness
        competitive_terms = ["best", "top", "review", "software", "tool", "platform"]
        
        competitive_count = sum(1 for kw in keywords if any(term in kw.lower() for term in competitive_terms))
        
        if competitive_count >= 3:
            return "high"
        elif competitive_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _identify_target_keywords(self, title: str) -> List[str]:
        """Identify target keywords from title"""
        # Remove common words and extract key terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by"}
        words = title.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Add variations
        variations = []
        for kw in keywords[:3]:
            variations.append(kw)
            variations.append(kw + "s")  # Plural
            variations.append(kw + "ing")  # Gerund
        
        return list(set(variations))[:8]
    
    async def _analyze_technical_seo(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze technical SEO factors"""
        results = {
            "crawlability": {},
            "indexability": {},
            "site_architecture": {},
            "page_speed": {},
            "mobile_friendliness": {},
            "security": {},
            "structured_data": {}
        }
        
        try:
            # Check robots.txt
            robots_response = await client.get(f"https://{domain}/robots.txt", timeout=5.0)
            results["crawlability"]["has_robots_txt"] = robots_response.status_code == 200
            
            if robots_response.status_code == 200:
                robots_content = robots_response.text.lower()
                results["crawlability"]["blocks_important_pages"] = "disallow: /" in robots_content
                results["crawlability"]["has_sitemap_reference"] = "sitemap:" in robots_content
            
            # Check sitemap
            sitemap_response = await client.get(f"https://{domain}/sitemap.xml", timeout=5.0)
            results["crawlability"]["has_xml_sitemap"] = sitemap_response.status_code == 200
            
            # Check homepage technical factors
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check meta robots
                meta_robots = soup.find('meta', attrs={'name': 'robots'})
                if meta_robots:
                    content = meta_robots.get('content', '').lower()
                    results["indexability"]["meta_robots"] = content
                    results["indexability"]["is_indexable"] = "noindex" not in content
                else:
                    results["indexability"]["is_indexable"] = True
                
                # Check canonical
                canonical = soup.find('link', rel='canonical')
                results["indexability"]["has_canonical"] = bool(canonical)
                
                # Check hreflang (international SEO)
                hreflang = soup.find_all('link', rel='alternate', hreflang=True)
                results["indexability"]["has_hreflang"] = len(hreflang) > 0
                
                # Check HTTPS
                results["security"]["uses_https"] = str(response.url).startswith("https://")
                
                # Check viewport meta
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                results["mobile_friendliness"]["has_viewport_meta"] = bool(viewport)
                
                # Count schema types
                schema_scripts = soup.find_all('script', type='application/ld+json')
                results["structured_data"]["schema_count"] = len(schema_scripts)
                
                if schema_scripts:
                    schema_types = []
                    for script in schema_scripts:
                        try:
                            data = json.loads(script.string)
                            if '@type' in data:
                                schema_types.append(data['@type'])
                        except:
                            pass
                    results["structured_data"]["schema_types"] = schema_types
        
        except Exception as e:
            logger.error(f"Technical SEO analysis failed", error=str(e))
        
        return results
    
    async def _check_serp_features(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Check for SERP feature opportunities"""
        opportunities = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for FAQ content
                faq_indicators = ['frequently asked', 'faq', 'questions']
                has_faq_content = any(indicator in soup.get_text().lower() for indicator in faq_indicators)
                
                if has_faq_content:
                    # Check if FAQ schema is implemented
                    has_faq_schema = False
                    schema_scripts = soup.find_all('script', type='application/ld+json')
                    for script in schema_scripts:
                        if 'FAQPage' in script.string:
                            has_faq_schema = True
                            break
                    
                    if not has_faq_schema:
                        opportunities.append({
                            "feature": "FAQ Rich Results",
                            "opportunity": "Add FAQ schema to existing FAQ content",
                            "implementation": "Add FAQPage structured data",
                            "impact": "Increase SERP real estate by 2-3x"
                        })
                
                # Check for review opportunities
                if 'review' in soup.get_text().lower() or 'rating' in soup.get_text().lower():
                    opportunities.append({
                        "feature": "Review Stars",
                        "opportunity": "Add Review or AggregateRating schema",
                        "implementation": "Implement review structured data",
                        "impact": "17% higher CTR with star ratings"
                    })
                
                # Check for how-to opportunities
                if 'step' in soup.get_text().lower() or 'how to' in soup.get_text().lower():
                    opportunities.append({
                        "feature": "How-To Rich Results",
                        "opportunity": "Add HowTo schema for guides",
                        "implementation": "Structure guides with HowTo markup",
                        "impact": "Enhanced visibility for tutorial searches"
                    })
        
        except Exception as e:
            logger.error(f"SERP feature analysis failed", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_internal_linking(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze internal linking structure"""
        results = {
            "total_internal_links": 0,
            "orphan_pages": [],
            "link_depth": {},
            "anchor_text_diversity": 0
        }
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                internal_links = []
                anchor_texts = []
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/') or domain in href:
                        internal_links.append(href)
                        anchor_texts.append(link.get_text().strip())
                
                results["total_internal_links"] = len(internal_links)
                results["unique_internal_links"] = len(set(internal_links))
                results["anchor_text_diversity"] = len(set(anchor_texts)) / len(anchor_texts) if anchor_texts else 0
                
                # Check if key pages are linked from homepage
                key_pages = ['/pricing', '/features', '/about', '/contact', '/blog']
                linked_key_pages = [page for page in key_pages if any(page in link for link in internal_links)]
                results["key_pages_linked"] = len(linked_key_pages)
                results["missing_key_page_links"] = [page for page in key_pages if page not in linked_key_pages]
        
        except Exception as e:
            logger.error(f"Internal linking analysis failed", error=str(e))
        
        return results
    
    async def _identify_topical_gaps(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Identify topical authority gaps"""
        gaps = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Define topic clusters by industry
                topic_clusters = {
                    "getting_started": ["setup", "installation", "onboarding", "quick start", "tutorial"],
                    "features": ["capabilities", "functionality", "tools", "modules", "components"],
                    "use_cases": ["examples", "scenarios", "applications", "case studies", "success stories"],
                    "integrations": ["connect", "integrate", "api", "webhook", "plugins"],
                    "troubleshooting": ["error", "issue", "problem", "fix", "solve"],
                    "best_practices": ["tips", "guide", "strategy", "optimize", "improve"],
                    "comparisons": ["vs", "versus", "compare", "alternative", "competitor"],
                    "pricing": ["cost", "price", "plan", "subscription", "billing"]
                }
                
                for cluster_name, keywords in topic_clusters.items():
                    cluster_coverage = sum(1 for kw in keywords if kw in content)
                    
                    if cluster_coverage < len(keywords) * 0.3:  # Less than 30% coverage
                        gaps.append({
                            "topic_cluster": cluster_name,
                            "coverage": f"{int(cluster_coverage / len(keywords) * 100)}%",
                            "missing_subtopics": [kw for kw in keywords if kw not in content],
                            "recommended_content": self._get_cluster_content_recommendations(cluster_name),
                            "priority": "high" if cluster_name in ["getting_started", "features", "pricing"] else "medium",
                            "estimated_pages_needed": 5 if cluster_coverage == 0 else 3
                        })
        
        except Exception as e:
            logger.error(f"Topical gap analysis failed", error=str(e))
        
        return {"gaps": gaps}
    
    def _get_cluster_content_recommendations(self, cluster_name: str) -> List[str]:
        """Get content recommendations for topic cluster"""
        recommendations = {
            "getting_started": [
                "Complete Setup Guide",
                "Quick Start Tutorial",
                "Video Walkthrough",
                "Common Setup Issues",
                "First Day Checklist"
            ],
            "features": [
                "Feature Overview Page",
                "Feature Comparison Matrix",
                "Feature Deep Dives (per feature)",
                "Feature Updates/Changelog",
                "Feature Request Process"
            ],
            "use_cases": [
                "Industry-Specific Use Cases",
                "Role-Based Scenarios",
                "Customer Success Stories",
                "ROI Calculator",
                "Implementation Examples"
            ],
            "integrations": [
                "Integration Directory",
                "API Documentation",
                "Webhook Guide",
                "Integration Tutorials",
                "Partner Ecosystem"
            ],
            "troubleshooting": [
                "Common Issues Database",
                "Error Code Reference",
                "Troubleshooting Flowchart",
                "Debug Guide",
                "Support Resources"
            ]
        }
        return recommendations.get(cluster_name, [])
    
    async def _analyze_search_intent_coverage(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze how well the site covers different search intents"""
        coverage = {
            "informational": 0,
            "commercial": 0,
            "transactional": 0,
            "navigational": 0
        }
        
        try:
            # Get site structure
            pages = await self._get_site_structure(domain, client)
            
            for page in pages[:50]:  # Analyze top 50 pages
                page_lower = page.lower()
                
                # Categorize by intent
                if any(term in page_lower for term in ['blog', 'guide', 'how-to', 'what-is', 'tips']):
                    coverage["informational"] += 1
                elif any(term in page_lower for term in ['compare', 'vs', 'review', 'best', 'alternative']):
                    coverage["commercial"] += 1
                elif any(term in page_lower for term in ['buy', 'pricing', 'checkout', 'cart', 'order']):
                    coverage["transactional"] += 1
                elif any(term in page_lower for term in ['login', 'signin', 'account', 'dashboard']):
                    coverage["navigational"] += 1
            
            # Calculate coverage scores
            total_pages = sum(coverage.values())
            if total_pages > 0:
                for intent in coverage:
                    coverage[intent] = int((coverage[intent] / total_pages) * 100)
            
            # Identify gaps
            gaps = []
            if coverage["informational"] < 30:
                gaps.append("Need more educational content (blogs, guides)")
            if coverage["commercial"] < 20:
                gaps.append("Need more comparison and review content")
            if coverage["transactional"] < 10:
                gaps.append("Need clearer conversion paths")
            
            return {
                "coverage": coverage,
                "gaps": gaps,
                "recommendation": self._get_intent_balance_recommendation(coverage)
            }
        
        except Exception as e:
            logger.error(f"Search intent analysis failed", error=str(e))
            return {"coverage": coverage, "gaps": []}
    
    def _get_intent_balance_recommendation(self, coverage: Dict[str, int]) -> str:
        """Get recommendation for search intent balance"""
        if coverage["informational"] < 30:
            return "Focus on creating educational content to attract top-of-funnel traffic"
        elif coverage["commercial"] < 20:
            return "Add comparison pages and reviews to capture buyers in research mode"
        elif coverage["transactional"] < 10:
            return "Optimize conversion paths and add clear CTAs"
        else:
            return "Good balance of content types - focus on depth and quality"
    
    async def _analyze_existing_content(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze quality and optimization of existing content"""
        results = {
            "thin_content_pages": [],
            "missing_meta_descriptions": [],
            "duplicate_titles": [],
            "optimization_opportunities": []
        }
        
        try:
            pages = await self._get_site_structure(domain, client)
            titles_seen = {}
            
            for page in pages[:20]:  # Analyze top 20 pages
                try:
                    if page.startswith('/'):
                        url = f"https://{domain}{page}"
                    else:
                        url = page
                    
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Check content length
                        text = soup.get_text()
                        word_count = len(text.split())
                        if word_count < 300:
                            results["thin_content_pages"].append({
                                "url": page,
                                "word_count": word_count,
                                "recommendation": "Expand to at least 800 words"
                            })
                        
                        # Check meta description
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if not meta_desc or not meta_desc.get('content'):
                            results["missing_meta_descriptions"].append(page)
                        
                        # Check for duplicate titles
                        title = soup.find('title')
                        if title:
                            title_text = title.text.strip()
                            if title_text in titles_seen:
                                results["duplicate_titles"].append({
                                    "title": title_text,
                                    "pages": [titles_seen[title_text], page]
                                })
                            else:
                                titles_seen[title_text] = page
                
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Existing content analysis failed", error=str(e))
        
        return results
    
    async def _check_ai_search_readiness(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Check readiness for AI search engines"""
        readiness = {
            "score": 0,
            "issues": [],
            "opportunities": []
        }
        
        try:
            # Check robots.txt for AI crawlers
            robots_response = await client.get(f"https://{domain}/robots.txt", timeout=5.0)
            if robots_response.status_code == 200:
                robots_txt = robots_response.text.lower()
                
                for crawler in self.ai_crawlers:
                    if crawler.lower() in robots_txt and 'disallow' in robots_txt:
                        readiness["issues"].append(f"Blocking {crawler} crawler")
                        readiness["score"] -= 20
            
            # Check for llms.txt
            llms_response = await client.get(f"https://{domain}/llms.txt", timeout=5.0)
            if llms_response.status_code == 200:
                readiness["score"] += 20
            else:
                readiness["opportunities"].append({
                    "task": "Create llms.txt file",
                    "impact": "Help AI understand your business",
                    "template": "Company: [Name]\nDescription: [What you do]\nProducts: [List]\nPricing: [Info]\nContact: [Email]"
                })
            
            # Check for structured data
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                schema_scripts = soup.find_all('script', type='application/ld+json')
                
                if schema_scripts:
                    readiness["score"] += 30
                else:
                    readiness["opportunities"].append({
                        "task": "Add structured data",
                        "impact": "Help AI extract key information",
                        "types": ["Organization", "Product", "FAQPage"]
                    })
            
            # Calculate final score
            readiness["score"] = max(0, min(100, readiness["score"] + 50))
        
        except Exception as e:
            logger.error(f"AI search readiness check failed", error=str(e))
        
        return readiness
    
    def _calculate_visibility_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall search visibility score"""
        score = 50  # Base score
        
        # Technical SEO factors
        tech_seo = results.get("technical_seo", {})
        if tech_seo.get("crawlability", {}).get("has_robots_txt"):
            score += 5
        if tech_seo.get("crawlability", {}).get("has_xml_sitemap"):
            score += 5
        if tech_seo.get("security", {}).get("uses_https"):
            score += 10
        if tech_seo.get("structured_data", {}).get("schema_count", 0) > 0:
            score += 10
        
        # Content factors
        if len(results.get("content_gaps", [])) < 5:
            score += 10
        if len(results.get("keyword_opportunities", [])) > 10:
            score += 5
        
        # AI search readiness
        ai_score = results.get("ai_search_readiness", {}).get("score", 0)
        score += int(ai_score / 10)
        
        # Penalties
        if results.get("technical_seo", {}).get("crawlability", {}).get("blocks_important_pages"):
            score -= 20
        
        return max(0, min(100, score))