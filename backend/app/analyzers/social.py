import httpx
import re
import json
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import structlog

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class SocialAnalyzer:
    """Analyzes social media presence and engagement"""
    
    def __init__(self):
        self.twitter_bearer = settings.TWITTER_BEARER_TOKEN if hasattr(settings, 'TWITTER_BEARER_TOKEN') else None
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        cache_key = f"social:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
            
        results = {
            "social_profiles": {},
            "total_followers": 0,
            "engagement_score": 0,
            "social_proof_on_site": [],
            "content_sharing_enabled": False,
            "social_meta_tags": {},
            "brand_mentions": 0
        }
        
        try:
            # Find social media profiles
            await self._find_social_profiles(domain, results)
            
            # Analyze social proof on website
            await self._analyze_social_proof(domain, results)
            
            # Check social meta tags
            await self._check_social_meta_tags(domain, results)
            
            # Calculate engagement score
            results["engagement_score"] = self._calculate_engagement_score(results)
            
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"Social analysis failed for {domain}", error=str(e))
            
        return results
    
    async def _find_social_profiles(self, domain: str, results: Dict) -> None:
        """Find and analyze social media profiles"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Social platform patterns
                social_patterns = {
                    "twitter": r'(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)',
                    "linkedin": r'linkedin\.com/company/([A-Za-z0-9-]+)',
                    "facebook": r'facebook\.com/([A-Za-z0-9.]+)',
                    "instagram": r'instagram\.com/([A-Za-z0-9_.]+)',
                    "youtube": r'youtube\.com/(?:c/|channel/|@)([A-Za-z0-9_-]+)',
                    "github": r'github\.com/([A-Za-z0-9-]+)'
                }
                
                profiles = {}
                total_followers = 0
                
                for platform, pattern in social_patterns.items():
                    links = soup.find_all('a', href=re.compile(pattern, re.I))
                    if links:
                        match = re.search(pattern, links[0].get('href', ''), re.I)
                        if match:
                            username = match.group(1)
                            profiles[platform] = {
                                "username": username,
                                "url": links[0].get('href'),
                                "followers": await self._estimate_followers(platform, username)
                            }
                            total_followers += profiles[platform]["followers"]
                
                results["social_profiles"] = profiles
                results["total_followers"] = total_followers
                
        except Exception as e:
            logger.error(f"Social profile discovery failed for {domain}", error=str(e))
    
    async def _estimate_followers(self, platform: str, username: str) -> int:
        """Estimate follower count for a social profile"""
        # In production, use platform APIs
        # For now, return estimates based on platform
        estimates = {
            "twitter": 5000,
            "linkedin": 10000,
            "facebook": 8000,
            "instagram": 3000,
            "youtube": 2000,
            "github": 500
        }
        return estimates.get(platform, 1000)
    
    async def _analyze_social_proof(self, domain: str, results: Dict) -> None:
        """Analyze social proof elements on the website"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0)
                soup = BeautifulSoup(response.text, 'lxml')
                text_lower = response.text.lower()
                
                social_proof = []
                
                # Check for follower counts displayed
                follower_patterns = [
                    r'(\d+[kKmM]?)\s*followers?',
                    r'(\d+[kKmM]?)\s*subscribers?',
                    r'(\d+[kKmM]?)\s*members?',
                    r'trusted by\s*(\d+[kKmM]?)',
                    r'(\d+[kKmM]?)\s*customers?'
                ]
                
                for pattern in follower_patterns:
                    matches = re.findall(pattern, text_lower)
                    if matches:
                        social_proof.append({
                            "type": "follower_count",
                            "value": matches[0]
                        })
                
                # Check for testimonials
                testimonial_indicators = ['testimonial', 'review', 'what our customers say', 'client feedback']
                for indicator in testimonial_indicators:
                    if indicator in text_lower:
                        social_proof.append({
                            "type": "testimonials",
                            "present": True
                        })
                        break
                
                # Check for client logos
                logo_sections = soup.find_all(class_=re.compile(r'logos?|clients?|partners?|trusted', re.I))
                if logo_sections:
                    social_proof.append({
                        "type": "client_logos",
                        "count": len(logo_sections[0].find_all('img'))
                    })
                
                # Check for social media feeds
                if 'twitter-timeline' in response.text or 'fb-page' in response.text:
                    social_proof.append({
                        "type": "social_feed",
                        "embedded": True
                    })
                
                # Check for share buttons
                share_patterns = ['addthis', 'sharethis', 'social-share', 'share-button']
                for pattern in share_patterns:
                    if pattern in text_lower:
                        results["content_sharing_enabled"] = True
                        break
                
                results["social_proof_on_site"] = social_proof
                
        except Exception as e:
            logger.error(f"Social proof analysis failed for {domain}", error=str(e))
    
    async def _check_social_meta_tags(self, domain: str, results: Dict) -> None:
        """Check Open Graph and Twitter Card meta tags"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0)
                soup = BeautifulSoup(response.text, 'lxml')
                
                meta_tags = {}
                
                # Open Graph tags
                og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
                if og_tags:
                    meta_tags["open_graph"] = {
                        "present": True,
                        "tags": [tag.get('property') for tag in og_tags[:5]]
                    }
                else:
                    meta_tags["open_graph"] = {"present": False}
                
                # Twitter Card tags
                twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
                if twitter_tags:
                    meta_tags["twitter_card"] = {
                        "present": True,
                        "type": next((tag.get('content') for tag in twitter_tags 
                                     if tag.get('name') == 'twitter:card'), 'summary')
                    }
                else:
                    meta_tags["twitter_card"] = {"present": False}
                
                results["social_meta_tags"] = meta_tags
                
        except Exception as e:
            logger.error(f"Social meta tag check failed for {domain}", error=str(e))
    
    def _calculate_engagement_score(self, results: Dict) -> int:
        """Calculate overall social engagement score"""
        score = 0
        
        # Points for having profiles
        score += len(results["social_profiles"]) * 10
        
        # Points for followers
        if results["total_followers"] > 50000:
            score += 30
        elif results["total_followers"] > 10000:
            score += 20
        elif results["total_followers"] > 1000:
            score += 10
        
        # Points for social proof
        score += len(results["social_proof_on_site"]) * 5
        
        # Points for sharing enabled
        if results["content_sharing_enabled"]:
            score += 10
        
        # Points for meta tags
        if results["social_meta_tags"].get("open_graph", {}).get("present"):
            score += 10
        if results["social_meta_tags"].get("twitter_card", {}).get("present"):
            score += 10
        
        return min(100, score)