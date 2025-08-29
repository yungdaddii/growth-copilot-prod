import httpx
import re
import json
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import structlog
from datetime import datetime, timedelta

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class TrafficAnalyzer:
    """Analyzes website traffic, rankings, and authority metrics"""
    
    def __init__(self):
        self.semrush_api_key = settings.SEMRUSH_API_KEY if hasattr(settings, 'SEMRUSH_API_KEY') else None
        self.similarweb_api_key = settings.SIMILARWEB_API_KEY if hasattr(settings, 'SIMILARWEB_API_KEY') else None
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        cache_key = f"traffic:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
            
        results = {
            "estimated_monthly_visits": 0,
            "domain_authority": 0,
            "organic_keywords": 0,
            "backlinks": 0,
            "referring_domains": 0,
            "traffic_sources": {},
            "top_pages": [],
            "competitor_comparison": {},
            "growth_trend": "unknown"
        }
        
        try:
            # Gather data from multiple sources
            await self._analyze_domain_authority(domain, results)
            await self._estimate_traffic(domain, results)
            await self._analyze_backlinks(domain, results)
            await self._analyze_content_velocity(domain, results)
            
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"Traffic analysis failed for {domain}", error=str(e))
            
        return results
    
    async def _analyze_domain_authority(self, domain: str, results: Dict) -> None:
        """Calculate domain authority based on multiple factors"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
                
                # Check domain age (via WHOIS or archive.org)
                # For now, use a heuristic based on content
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Factors for domain authority
                factors = {
                    "has_ssl": response.url.scheme == "https",
                    "has_sitemap": await self._check_sitemap(domain, client),
                    "page_count": len(soup.find_all(['a'], href=True)),
                    "content_depth": len(soup.get_text()) > 5000,
                    "has_blog": bool(soup.find_all(href=re.compile(r'/blog|/news|/articles', re.I))),
                    "social_links": len(soup.find_all('a', href=re.compile(r'twitter|facebook|linkedin', re.I)))
                }
                
                # Calculate authority score (0-100)
                score = 30  # Base score
                if factors["has_ssl"]: score += 10
                if factors["has_sitemap"]: score += 15
                if factors["page_count"] > 50: score += 10
                if factors["content_depth"]: score += 10
                if factors["has_blog"]: score += 15
                if factors["social_links"] > 2: score += 10
                
                results["domain_authority"] = min(100, score)
                
        except Exception as e:
            logger.error(f"Domain authority analysis failed for {domain}", error=str(e))
    
    async def _check_sitemap(self, domain: str, client: httpx.AsyncClient) -> bool:
        """Check if sitemap exists"""
        try:
            response = await client.get(f"https://{domain}/sitemap.xml", timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def _estimate_traffic(self, domain: str, results: Dict) -> None:
        """Estimate traffic based on various signals"""
        # In production, integrate with SimilarWeb, Alexa, or SEMrush APIs
        # For now, use heuristics
        
        try:
            # Factors that correlate with traffic
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Check for traffic signals
                signals = {
                    "has_analytics": bool(re.search(r'google-analytics|gtag|ga\(', response.text)),
                    "has_pixels": bool(re.search(r'facebook|pixel|fbq', response.text)),
                    "page_size": len(response.text),
                    "images": len(soup.find_all('img')),
                    "scripts": len(soup.find_all('script'))
                }
                
                # More realistic traffic estimation based on multiple factors
                # Base traffic on domain authority and signals
                da = results.get("domain_authority", 30)
                
                # Start with DA-based baseline
                if da >= 70:
                    base_traffic = 50000
                elif da >= 60:
                    base_traffic = 30000
                elif da >= 50:
                    base_traffic = 15000
                elif da >= 40:
                    base_traffic = 8000
                elif da >= 30:
                    base_traffic = 3000
                else:
                    base_traffic = 1000
                
                # Adjust based on signals
                multiplier = 1.0
                if signals["has_analytics"]: 
                    multiplier *= 1.2
                if signals["has_pixels"]: 
                    multiplier *= 1.3
                if signals["page_size"] > 100000: 
                    multiplier *= 1.1
                if signals["images"] > 20: 
                    multiplier *= 1.05
                
                # Check for blog activity
                if soup.find_all(['a'], href=re.compile(r'/blog|/news', re.I)):
                    multiplier *= 1.25
                
                # Check for e-commerce signals
                if 'cart' in response.text.lower() or 'shop' in response.text.lower():
                    multiplier *= 1.4
                
                # Enterprise/B2B sites typically have lower traffic
                if 'enterprise' in response.text.lower() or 'solutions' in response.text.lower():
                    multiplier *= 0.7
                
                results["estimated_monthly_visits"] = int(base_traffic * multiplier)
                
                # Traffic sources breakdown (estimated)
                results["traffic_sources"] = {
                    "organic": 40,
                    "direct": 30,
                    "referral": 15,
                    "social": 10,
                    "paid": 5
                }
                
        except Exception as e:
            logger.error(f"Traffic estimation failed for {domain}", error=str(e))
    
    async def _analyze_backlinks(self, domain: str, results: Dict) -> None:
        """Analyze backlink profile"""
        # In production, use Ahrefs, Moz, or Majestic APIs
        # For now, use basic detection
        
        try:
            # Check for common backlink sources
            async with httpx.AsyncClient() as client:
                # Check if listed in common directories
                directories = [
                    "producthunt.com",
                    "crunchbase.com",
                    "g2.com",
                    "capterra.com"
                ]
                
                backlink_count = 0
                referring_domains = []
                
                for directory in directories:
                    try:
                        # This is a simplified check - in production use proper APIs
                        response = await client.get(
                            f"https://www.google.com/search?q=site:{directory}+{domain}",
                            timeout=5.0
                        )
                        if domain in response.text:
                            backlink_count += 10
                            referring_domains.append(directory)
                    except:
                        continue
                
                results["backlinks"] = backlink_count
                results["referring_domains"] = len(referring_domains)
                
        except Exception as e:
            logger.error(f"Backlink analysis failed for {domain}", error=str(e))
    
    async def _analyze_content_velocity(self, domain: str, results: Dict) -> None:
        """Analyze content publishing frequency"""
        try:
            async with httpx.AsyncClient() as client:
                # Check for blog/news section
                response = await client.get(f"https://{domain}", timeout=10.0)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Find blog links
                blog_links = soup.find_all('a', href=re.compile(r'/blog|/news|/articles', re.I))
                
                if blog_links:
                    # Try to fetch blog page
                    blog_url = blog_links[0].get('href')
                    if not blog_url.startswith('http'):
                        blog_url = f"https://{domain}{blog_url}"
                    
                    blog_response = await client.get(blog_url, timeout=10.0)
                    blog_soup = BeautifulSoup(blog_response.text, 'lxml')
                    
                    # Look for dates in blog posts
                    date_patterns = [
                        r'\d{4}-\d{2}-\d{2}',
                        r'\d{1,2}/\d{1,2}/\d{4}',
                        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'
                    ]
                    
                    dates_found = []
                    for pattern in date_patterns:
                        dates = re.findall(pattern, blog_response.text)
                        dates_found.extend(dates[:10])  # Get recent dates
                    
                    if dates_found:
                        results["content_velocity"] = "active"
                        results["recent_posts"] = len(dates_found)
                    else:
                        results["content_velocity"] = "low"
                        
        except Exception as e:
            logger.error(f"Content velocity analysis failed for {domain}", error=str(e))