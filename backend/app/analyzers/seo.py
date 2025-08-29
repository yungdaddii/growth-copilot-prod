import httpx
from typing import Dict, Any
import structlog
from bs4 import BeautifulSoup
import re

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class SEOAnalyzer:
    def __init__(self):
        self.ai_crawlers = ['GPTBot', 'ChatGPT-User', 'CCBot', 'Claude-Web', 'PerplexityBot']
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        cache_key = f"seo:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "score": 0,
            "meta_title": "",
            "meta_description": "",
            "h1_count": 0,
            "has_og_tags": False,
            "has_schema": False,
            "blocks_ai_crawlers": False,
            "ai_visibility_score": 0,
            "issues": [],
            "opportunities": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Fetch homepage
                response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Check robots.txt for AI crawler blocking
                robots_response = await client.get(f"https://{domain}/robots.txt", timeout=5.0)
                if robots_response.status_code == 200:
                    robots_txt = robots_response.text.lower()
                    for bot in self.ai_crawlers:
                        if bot.lower() in robots_txt and 'disallow' in robots_txt:
                            results["blocks_ai_crawlers"] = True
                            results["issues"].append({
                                "type": "ai_visibility",
                                "severity": "critical",
                                "message": f"Blocking {bot} - invisible to AI search"
                            })
                
                # Meta tags
                title = soup.find('title')
                if title:
                    results["meta_title"] = title.text.strip()
                    if len(results["meta_title"]) > 60:
                        results["issues"].append({
                            "type": "meta",
                            "severity": "medium",
                            "message": "Title too long (>60 chars)"
                        })
                else:
                    results["issues"].append({
                        "type": "meta",
                        "severity": "high",
                        "message": "Missing page title"
                    })
                
                # Meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    results["meta_description"] = meta_desc.get('content', '')
                    if len(results["meta_description"]) > 160:
                        results["issues"].append({
                            "type": "meta",
                            "severity": "medium",
                            "message": "Description too long (>160 chars)"
                        })
                else:
                    results["issues"].append({
                        "type": "meta",
                        "severity": "high",
                        "message": "Missing meta description"
                    })
                
                # H1 tags
                h1_tags = soup.find_all('h1')
                results["h1_count"] = len(h1_tags)
                if results["h1_count"] == 0:
                    results["issues"].append({
                        "type": "structure",
                        "severity": "high",
                        "message": "No H1 tag found"
                    })
                elif results["h1_count"] > 1:
                    results["issues"].append({
                        "type": "structure",
                        "severity": "medium",
                        "message": f"Multiple H1 tags ({results['h1_count']})"
                    })
                
                # Open Graph tags
                og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
                results["has_og_tags"] = len(og_tags) > 0
                if not results["has_og_tags"]:
                    results["opportunities"].append({
                        "type": "social",
                        "message": "Add Open Graph tags for better social sharing"
                    })
                
                # Schema markup
                schema_scripts = soup.find_all('script', type='application/ld+json')
                results["has_schema"] = len(schema_scripts) > 0
                if not results["has_schema"]:
                    results["opportunities"].append({
                        "type": "structured_data",
                        "message": "Add Schema.org markup for rich snippets"
                    })
                
                # Calculate AI visibility score
                ai_score = 100
                if results["blocks_ai_crawlers"]:
                    ai_score -= 50
                if not results["has_schema"]:
                    ai_score -= 20
                if not results["meta_description"]:
                    ai_score -= 15
                if results["h1_count"] != 1:
                    ai_score -= 15
                results["ai_visibility_score"] = max(0, ai_score)
                
                # Find additional opportunities
                # Check for advanced SEO features
                if not soup.find('link', rel='canonical'):
                    results["opportunities"].append({
                        "type": "technical",
                        "message": "Add canonical tags to prevent duplicate content issues",
                        "impact": "medium"
                    })
                
                # Check for image optimization
                images_without_alt = sum(1 for img in soup.find_all('img') if not img.get('alt'))
                if images_without_alt > 0:
                    results["opportunities"].append({
                        "type": "accessibility",
                        "message": f"{images_without_alt} images missing alt text - hurts SEO and accessibility",
                        "impact": "high"
                    })
                
                # Check for internal linking
                internal_links = [a for a in soup.find_all('a', href=True) 
                                if a['href'].startswith('/') or domain in a.get('href', '')]
                if len(internal_links) < 10:
                    results["opportunities"].append({
                        "type": "internal_linking",
                        "message": "Weak internal linking structure - add more contextual links",
                        "impact": "medium"
                    })
                
                # Check for FAQ schema
                if 'faq' not in response.text.lower() and not soup.find(attrs={'itemtype': re.compile('FAQPage')}):
                    results["opportunities"].append({
                        "type": "rich_snippets",
                        "message": "Add FAQ schema for rich snippets in search results",
                        "impact": "high"
                    })
                
                # Calculate realistic SEO score (nobody gets 100)
                score = 40  # Base score
                if results["meta_title"]:
                    score += 8
                if results["meta_description"]:
                    score += 8
                if results["h1_count"] == 1:
                    score += 8
                if results["has_og_tags"]:
                    score += 6
                if results["has_schema"]:
                    score += 10
                if not results["blocks_ai_crawlers"]:
                    score += 15
                
                # Deduct for issues and missing opportunities
                score -= len(results["issues"]) * 5
                score -= len(results["opportunities"]) * 3
                
                # Cap at 85 - perfect SEO is a myth
                results["score"] = max(20, min(85, score))
                
                await cache_result(cache_key, results, ttl=3600)
                
        except Exception as e:
            logger.error("SEO analysis failed", domain=domain, error=str(e))
        
        return results