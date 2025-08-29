import httpx
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urljoin, urlparse

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class AISearchAnalyzer:
    """
    Analyzes website optimization for AI-powered search platforms.
    Critical for 2025+ as AI search becomes dominant.
    """
    
    # AI crawlers to check for
    AI_CRAWLERS = {
        "GPTBot": "OpenAI ChatGPT",
        "ChatGPT-User": "ChatGPT Browser", 
        "Claude-Web": "Anthropic Claude",
        "PerplexityBot": "Perplexity AI",
        "CCBot": "Common Crawl (AI training)",
        "Bytespider": "ByteDance AI",
        "YouBot": "You.com AI Search",
        "Diffbot": "Diffbot Knowledge Graph",
        "FacebookBot": "Meta AI",
        "Google-Extended": "Google Bard/Gemini"
    }
    
    # Schema types important for AI understanding
    AI_FRIENDLY_SCHEMAS = [
        "FAQPage", "HowTo", "Article", "Product", 
        "Service", "SoftwareApplication", "Organization",
        "BreadcrumbList", "VideoObject", "Course"
    ]
    
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Comprehensive AI search optimization analysis"""
        cache_key = f"ai_search:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "ai_visibility_score": 0,
            "blocked_crawlers": [],
            "allowed_crawlers": [],
            "has_llms_txt": False,
            "schema_types_found": [],
            "ai_friendly_content": {},
            "recommendations": [],
            "competitive_advantage": {},
            "content_structure_score": 0
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Check robots.txt for AI crawler access
                await self._check_robots_txt(domain, client, results)
                
                # Check for llms.txt (new standard for AI instructions)
                await self._check_llms_txt(domain, client, results)
                
                # Analyze homepage for AI-friendly content
                await self._analyze_content_structure(domain, client, results)
                
                # Check schema markup
                await self._analyze_schema_markup(domain, client, results)
                
                # Generate AI-specific recommendations
                await self._generate_ai_recommendations(domain, results)
                
                # Calculate overall AI visibility score
                self._calculate_ai_score(results)
                
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"AI search analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _check_robots_txt(self, domain: str, client: httpx.AsyncClient, results: Dict) -> None:
        """Check robots.txt for AI crawler permissions"""
        try:
            response = await client.get(f"https://{domain}/robots.txt", timeout=10.0)
            if response.status_code == 200:
                robots_content = response.text.lower()
                
                for crawler, name in self.AI_CRAWLERS.items():
                    crawler_lower = crawler.lower()
                    
                    # Check if crawler is explicitly blocked
                    if f"user-agent: {crawler_lower}" in robots_content:
                        # Look for disallow directive after this user-agent
                        lines = robots_content.split('\n')
                        for i, line in enumerate(lines):
                            if f"user-agent: {crawler_lower}" in line:
                                # Check next few lines for disallow
                                for j in range(i+1, min(i+5, len(lines))):
                                    if "disallow: /" in lines[j]:
                                        results["blocked_crawlers"].append({
                                            "bot": crawler,
                                            "platform": name,
                                            "impact": "high"
                                        })
                                        break
                                    elif "user-agent:" in lines[j]:
                                        # Next user-agent section, not blocked
                                        results["allowed_crawlers"].append(crawler)
                                        break
                    
                    # Check for wildcard blocking
                    elif "user-agent: *" in robots_content and "disallow: /" in robots_content:
                        # All bots blocked by default
                        if crawler_lower not in robots_content:
                            results["blocked_crawlers"].append({
                                "bot": crawler,
                                "platform": name,
                                "impact": "high"
                            })
                
        except Exception as e:
            logger.error(f"Failed to check robots.txt for {domain}", error=str(e))
    
    async def _check_llms_txt(self, domain: str, client: httpx.AsyncClient, results: Dict) -> None:
        """Check for llms.txt file (AI-specific instructions)"""
        try:
            response = await client.get(f"https://{domain}/llms.txt", timeout=5.0)
            if response.status_code == 200:
                results["has_llms_txt"] = True
                content = response.text[:500]  # First 500 chars
                
                # Analyze llms.txt quality
                quality_indicators = {
                    "has_description": "description:" in content.lower(),
                    "has_capabilities": "capabilities:" in content.lower(),
                    "has_limitations": "limitations:" in content.lower(),
                    "has_contact": "contact:" in content.lower() or "email:" in content.lower()
                }
                
                results["llms_txt_quality"] = quality_indicators
                
        except Exception as e:
            results["has_llms_txt"] = False
    
    async def _analyze_content_structure(self, domain: str, client: httpx.AsyncClient, results: Dict) -> None:
        """Analyze content structure for AI comprehension"""
        try:
            response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
            soup = BeautifulSoup(response.text, 'lxml')
            
            ai_friendly = {
                "has_clear_headings": False,
                "has_faq_section": False,
                "has_structured_lists": False,
                "has_definitions": False,
                "content_depth": 0,
                "readability_score": 0,
                "has_comparison_content": False,
                "has_how_to_content": False
            }
            
            # Check heading structure
            headings = soup.find_all(['h1', 'h2', 'h3'])
            if len(headings) > 5:
                ai_friendly["has_clear_headings"] = True
            
            # Check for FAQ patterns
            faq_patterns = [
                'faq', 'frequently asked', 'common questions',
                'q&a', 'questions and answers'
            ]
            text_lower = response.text.lower()
            for pattern in faq_patterns:
                if pattern in text_lower:
                    ai_friendly["has_faq_section"] = True
                    break
            
            # Check for structured lists (good for AI extraction)
            lists = soup.find_all(['ul', 'ol'])
            if len(lists) > 3:
                ai_friendly["has_structured_lists"] = True
            
            # Check for definition/glossary content
            if soup.find(['dl', 'dt', 'dd']) or 'definition' in text_lower or 'glossary' in text_lower:
                ai_friendly["has_definitions"] = True
            
            # Check for comparison content (vs, versus, compared to)
            comparison_patterns = [' vs ', ' versus ', 'compared to', 'comparison', 'alternative']
            for pattern in comparison_patterns:
                if pattern in text_lower:
                    ai_friendly["has_comparison_content"] = True
                    break
            
            # Check for how-to content
            if 'how to' in text_lower or 'step by step' in text_lower or 'tutorial' in text_lower:
                ai_friendly["has_how_to_content"] = True
            
            # Calculate content depth (word count)
            text = soup.get_text()
            word_count = len(text.split())
            ai_friendly["content_depth"] = word_count
            
            # Simple readability check (sentence length)
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            if avg_sentence_length < 20:
                ai_friendly["readability_score"] = 80
            elif avg_sentence_length < 30:
                ai_friendly["readability_score"] = 60
            else:
                ai_friendly["readability_score"] = 40
            
            results["ai_friendly_content"] = ai_friendly
            
        except Exception as e:
            logger.error(f"Failed to analyze content structure for {domain}", error=str(e))
    
    async def _analyze_schema_markup(self, domain: str, client: httpx.AsyncClient, results: Dict) -> None:
        """Check for schema markup that helps AI understanding"""
        try:
            response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
            soup = BeautifulSoup(response.text, 'lxml')
            
            schema_found = []
            
            # Check for JSON-LD schema
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    import json
                    schema_data = json.loads(script.string)
                    if isinstance(schema_data, dict):
                        schema_type = schema_data.get('@type', '')
                        if schema_type:
                            schema_found.append(schema_type)
                    elif isinstance(schema_data, list):
                        for item in schema_data:
                            if isinstance(item, dict):
                                schema_type = item.get('@type', '')
                                if schema_type:
                                    schema_found.append(schema_type)
                except:
                    continue
            
            # Check for microdata
            microdata_items = soup.find_all(attrs={'itemscope': True})
            for item in microdata_items:
                item_type = item.get('itemtype', '')
                if 'schema.org' in item_type:
                    schema_type = item_type.split('/')[-1]
                    schema_found.append(schema_type)
            
            results["schema_types_found"] = list(set(schema_found))
            
            # Check for AI-friendly schemas
            ai_friendly_found = [s for s in schema_found if s in self.AI_FRIENDLY_SCHEMAS]
            results["ai_friendly_schemas"] = ai_friendly_found
            
        except Exception as e:
            logger.error(f"Failed to analyze schema markup for {domain}", error=str(e))
    
    async def _generate_ai_recommendations(self, domain: str, results: Dict) -> None:
        """Generate specific recommendations for AI search optimization"""
        recommendations = []
        
        # Check crawler blocking
        if results["blocked_crawlers"]:
            blocked_names = [b["platform"] for b in results["blocked_crawlers"][:3]]
            recommendations.append({
                "priority": "critical",
                "issue": f"Blocking AI crawlers: {', '.join(blocked_names)}",
                "impact": "Invisible to AI-powered search and recommendations",
                "fix": f"Update robots.txt to allow: {', '.join([b['bot'] for b in results['blocked_crawlers'][:3]])}",
                "effort": "5 minutes",
                "code_snippet": self._generate_robots_fix(results["blocked_crawlers"])
            })
        
        # Check llms.txt
        if not results["has_llms_txt"]:
            recommendations.append({
                "priority": "high",
                "issue": "No llms.txt file for AI instructions",
                "impact": "AI systems lack context about your business",
                "fix": "Create /llms.txt with company description and capabilities",
                "effort": "30 minutes",
                "code_snippet": self._generate_llms_txt_template(domain)
            })
        
        # Check schema markup
        if not results["schema_types_found"]:
            recommendations.append({
                "priority": "high",
                "issue": "No structured data (schema markup)",
                "impact": "AI can't understand your content structure",
                "fix": "Add Organization and FAQPage schema markup",
                "effort": "1 hour",
                "code_snippet": self._generate_schema_template()
            })
        elif "FAQPage" not in results["schema_types_found"]:
            recommendations.append({
                "priority": "medium",
                "issue": "No FAQ schema for common questions",
                "impact": "Missing opportunity for AI-powered Q&A",
                "fix": "Add FAQPage schema markup",
                "effort": "45 minutes",
                "code_snippet": self._generate_faq_schema()
            })
        
        # Check content structure
        ai_content = results.get("ai_friendly_content", {})
        if not ai_content.get("has_faq_section"):
            recommendations.append({
                "priority": "high",
                "issue": "No FAQ section on site",
                "impact": "AI can't extract answers to common questions",
                "fix": "Create FAQ page with 10-15 common customer questions",
                "effort": "2 hours"
            })
        
        if not ai_content.get("has_comparison_content"):
            recommendations.append({
                "priority": "medium",
                "issue": "No comparison/alternative content",
                "impact": "AI won't recommend you in comparison queries",
                "fix": "Create 'vs competitor' or 'alternatives to X' pages",
                "effort": "4 hours"
            })
        
        if ai_content.get("content_depth", 0) < 500:
            recommendations.append({
                "priority": "medium",
                "issue": "Thin content (low word count)",
                "impact": "AI prefers comprehensive, authoritative content",
                "fix": "Expand homepage to 1000+ words with detailed descriptions",
                "effort": "3 hours"
            })
        
        results["recommendations"] = recommendations
    
    def _calculate_ai_score(self, results: Dict) -> None:
        """Calculate overall AI visibility score (0-100)"""
        score = 0
        max_score = 100
        
        # Crawler access (40 points)
        blocked_count = len(results["blocked_crawlers"])
        if blocked_count == 0:
            score += 40
        elif blocked_count <= 2:
            score += 20
        elif blocked_count <= 4:
            score += 10
        
        # llms.txt presence (10 points)
        if results["has_llms_txt"]:
            score += 10
        
        # Schema markup (20 points)
        schema_count = len(results["schema_types_found"])
        if schema_count >= 3:
            score += 20
        elif schema_count >= 1:
            score += 10
        
        # Content structure (30 points)
        ai_content = results.get("ai_friendly_content", {})
        content_score = 0
        if ai_content.get("has_clear_headings"):
            content_score += 5
        if ai_content.get("has_faq_section"):
            content_score += 10
        if ai_content.get("has_structured_lists"):
            content_score += 5
        if ai_content.get("has_comparison_content"):
            content_score += 5
        if ai_content.get("content_depth", 0) > 1000:
            content_score += 5
        
        score += content_score
        
        results["ai_visibility_score"] = min(score, max_score)
        
        # Add interpretation
        if score >= 80:
            results["ai_readiness"] = "excellent"
        elif score >= 60:
            results["ai_readiness"] = "good"
        elif score >= 40:
            results["ai_readiness"] = "needs_improvement"
        else:
            results["ai_readiness"] = "poor"
    
    def _generate_robots_fix(self, blocked_crawlers: List[Dict]) -> str:
        """Generate robots.txt fix for AI crawlers"""
        fix = "# Allow AI crawlers\n"
        for crawler in blocked_crawlers[:5]:
            fix += f"User-agent: {crawler['bot']}\n"
            fix += "Allow: /\n\n"
        return fix
    
    def _generate_llms_txt_template(self, domain: str) -> str:
        """Generate llms.txt template"""
        return f"""# LLMs.txt for {domain}

## Description
[Your company description - what you do, who you serve]

## Capabilities
- [Key feature 1]
- [Key feature 2]
- [Key feature 3]

## Pricing
[Pricing structure or "Contact for pricing"]

## Integration
[How to integrate or use your product]

## Support
Email: support@{domain}
Docs: https://{domain}/docs

## Last Updated
{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _generate_schema_template(self) -> str:
        """Generate basic schema markup template"""
        return '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Company Name",
  "url": "https://yoursite.com",
  "description": "What your company does",
  "sameAs": [
    "https://twitter.com/yourcompany",
    "https://linkedin.com/company/yourcompany"
  ]
}
</script>'''
    
    def _generate_faq_schema(self) -> str:
        """Generate FAQ schema template"""
        return '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is your product?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Our product is..."
    }
  }]
}
</script>'''