import httpx
import re
import json
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import structlog

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class AdsAnalyzer:
    """Analyzes paid advertising presence and strategies"""
    
    def __init__(self):
        pass
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        cache_key = f"ads:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
            
        results = {
            "has_google_ads": False,
            "has_facebook_pixel": False,
            "has_linkedin_insight": False,
            "retargeting_enabled": False,
            "conversion_tracking": [],
            "ad_platforms_detected": [],
            "landing_pages": [],
            "utm_usage": False,
            "estimated_ad_spend": "unknown",
            "ad_strategy_signals": []
        }
        
        try:
            await self._detect_ad_platforms(domain, results)
            await self._analyze_landing_pages(domain, results)
            await self._detect_tracking_pixels(domain, results)
            await self._analyze_ad_strategy(domain, results)
            
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"Ads analysis failed for {domain}", error=str(e))
            
        return results
    
    async def _detect_ad_platforms(self, domain: str, results: Dict) -> None:
        """Detect which ad platforms are being used"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
                text = response.text.lower()
                
                # Google Ads detection
                google_ads_patterns = [
                    'googleadservices.com',
                    'google-analytics.com/collect',
                    'gtag/js',
                    'gtag(\'config\'',
                    'conversion_id',
                    'aw-'
                ]
                
                for pattern in google_ads_patterns:
                    if pattern in text:
                        results["has_google_ads"] = True
                        results["ad_platforms_detected"].append("Google Ads")
                        break
                
                # Facebook/Meta Ads detection
                fb_patterns = [
                    'facebook.com/tr',
                    'fbq(\'init\'',
                    'facebook pixel',
                    '_fbq',
                    'connect.facebook.net'
                ]
                
                for pattern in fb_patterns:
                    if pattern in text:
                        results["has_facebook_pixel"] = True
                        results["ad_platforms_detected"].append("Facebook/Meta Ads")
                        results["retargeting_enabled"] = True
                        break
                
                # LinkedIn Ads detection
                linkedin_patterns = [
                    'linkedin.com/px',
                    '_linkedin_partner_id',
                    'linkedin insight tag',
                    'snap.licdn.com'
                ]
                
                for pattern in linkedin_patterns:
                    if pattern in text:
                        results["has_linkedin_insight"] = True
                        results["ad_platforms_detected"].append("LinkedIn Ads")
                        break
                
                # Other ad platforms
                other_platforms = {
                    "Twitter Ads": ['twitter.com/i/adsct', 'twq('],
                    "Pinterest Ads": ['pintrk', 'pinterest.com/ct'],
                    "TikTok Ads": ['tiktok.com/i18n/pixel'],
                    "Snapchat Ads": ['snapchat.com/tr'],
                    "Reddit Ads": ['reddit.com/pixel'],
                    "Quora Ads": ['quora.com/pixel'],
                    "Microsoft/Bing Ads": ['bat.bing.com', 'uetq.push']
                }
                
                for platform, patterns in other_platforms.items():
                    if any(p in text for p in patterns):
                        results["ad_platforms_detected"].append(platform)
                
                # Conversion tracking detection
                conversion_patterns = {
                    "Google Ads Conversion": 'gtag.*conversion',
                    "Facebook Conversion API": 'fbq.*purchase|fbq.*lead',
                    "Enhanced Ecommerce": 'enhanced.?ecommerce|ec:addproduct',
                    "Goal Tracking": 'goal.*tracking|track.*goal'
                }
                
                for tracker, pattern in conversion_patterns.items():
                    if re.search(pattern, text, re.I):
                        results["conversion_tracking"].append(tracker)
                
        except Exception as e:
            logger.error(f"Ad platform detection failed for {domain}", error=str(e))
    
    async def _analyze_landing_pages(self, domain: str, results: Dict) -> None:
        """Analyze potential landing pages and campaign URLs"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0)
                soup = BeautifulSoup(response.text, 'lxml')
                
                landing_pages = []
                
                # Find links with UTM parameters
                all_links = soup.find_all('a', href=True)
                utm_links = []
                
                for link in all_links:
                    href = link.get('href', '')
                    if 'utm_' in href:
                        results["utm_usage"] = True
                        utm_links.append(href)
                
                # Common landing page patterns
                landing_patterns = [
                    r'/lp/',
                    r'/landing/',
                    r'/offer/',
                    r'/promo/',
                    r'/campaign/',
                    r'/get-started',
                    r'/free-trial',
                    r'/demo',
                    r'/webinar/',
                    r'/ebook/',
                    r'/whitepaper/'
                ]
                
                for link in all_links:
                    href = link.get('href', '')
                    for pattern in landing_patterns:
                        if re.search(pattern, href, re.I):
                            landing_pages.append({
                                "url": href,
                                "text": link.get_text(strip=True)[:50],
                                "type": pattern.strip('/')
                            })
                            break
                
                # Only keep unique landing pages
                seen_urls = set()
                unique_pages = []
                for page in landing_pages:
                    if page["url"] not in seen_urls:
                        seen_urls.add(page["url"])
                        unique_pages.append(page)
                
                results["landing_pages"] = unique_pages[:10]  # Top 10
                
        except Exception as e:
            logger.error(f"Landing page analysis failed for {domain}", error=str(e))
    
    async def _detect_tracking_pixels(self, domain: str, results: Dict) -> None:
        """Detect various tracking and retargeting pixels"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0)
                text = response.text.lower()
                
                # Additional pixel detection
                pixel_patterns = {
                    "Google Tag Manager": 'googletagmanager.com/gtm',
                    "Segment": 'segment.com/analytics.js|segment.io',
                    "Mixpanel": 'mixpanel.com|mxpnl.com',
                    "Amplitude": 'amplitude.com|cdn.amplitude.com',
                    "Heap Analytics": 'heap.io|heapanalytics.com',
                    "Hotjar": 'hotjar.com|hjid',
                    "FullStory": 'fullstory.com/s/fs.js',
                    "Crazy Egg": 'crazyegg.com',
                    "Lucky Orange": 'luckyorange.com',
                    "Optimizely": 'optimizely.com',
                    "VWO": 'visualwebsiteoptimizer.com|vwo'
                }
                
                tracking_tools = []
                for tool, pattern in pixel_patterns.items():
                    if re.search(pattern, text):
                        tracking_tools.append(tool)
                        if tool in ["Google Tag Manager", "Segment"]:
                            results["retargeting_enabled"] = True
                
                if tracking_tools:
                    results["conversion_tracking"].extend(tracking_tools)
                
        except Exception as e:
            logger.error(f"Tracking pixel detection failed for {domain}", error=str(e))
    
    async def _analyze_ad_strategy(self, domain: str, results: Dict) -> None:
        """Analyze signals of advertising strategy"""
        try:
            strategy_signals = []
            
            # Multi-channel strategy
            if len(results["ad_platforms_detected"]) >= 3:
                strategy_signals.append("Multi-channel advertising")
            
            # Retargeting focus
            if results["retargeting_enabled"]:
                strategy_signals.append("Retargeting campaigns active")
            
            # Conversion optimization
            if len(results["conversion_tracking"]) >= 2:
                strategy_signals.append("Advanced conversion tracking")
            
            # Landing page strategy
            if len(results["landing_pages"]) >= 5:
                strategy_signals.append("Multiple campaign landing pages")
            
            # UTM tracking
            if results["utm_usage"]:
                strategy_signals.append("Campaign attribution tracking")
            
            # Estimate ad spend tier based on signals
            signal_count = len(results["ad_platforms_detected"]) + len(strategy_signals)
            
            if signal_count >= 8:
                results["estimated_ad_spend"] = "High ($10K+/month)"
            elif signal_count >= 5:
                results["estimated_ad_spend"] = "Medium ($3K-10K/month)"
            elif signal_count >= 2:
                results["estimated_ad_spend"] = "Low ($500-3K/month)"
            elif signal_count >= 1:
                results["estimated_ad_spend"] = "Minimal (<$500/month)"
            else:
                results["estimated_ad_spend"] = "None detected"
            
            results["ad_strategy_signals"] = strategy_signals
            
        except Exception as e:
            logger.error(f"Ad strategy analysis failed for {domain}", error=str(e))