import httpx
import asyncio
from typing import Dict, Any, Optional
import structlog
from bs4 import BeautifulSoup

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class PerformanceAnalyzer:
    def __init__(self):
        self.pagespeed_api_key = settings.GOOGLE_PAGESPEED_API_KEY
        self.pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        # Check cache first
        cache_key = f"performance:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "score": None,  # Use None to indicate no data
            "load_time": 0,
            "first_contentful_paint": 0,
            "time_to_interactive": 0,
            "total_blocking_time": 0,
            "cumulative_layout_shift": 0,
            "issues": [],
            "unoptimized_images": 0,
            "unused_css": 0,
            "unused_js": 0,
            "render_blocking_resources": 0,
            "api_failed": False
        }
        
        try:
            # Try PageSpeed Insights API first
            if self.pagespeed_api_key:
                pagespeed_data = await self._get_pagespeed_data(domain)
                if pagespeed_data:
                    parsed = self._parse_pagespeed_data(pagespeed_data)
                    if parsed:
                        results.update(parsed)
                        results["api_failed"] = False
                    else:
                        logger.warning(f"PageSpeed API returned no data for {domain}, using fallback")
                        results["api_failed"] = True
                        fallback = await self._basic_performance_check(domain)
                        results.update(fallback)
                else:
                    logger.warning(f"PageSpeed API failed for {domain}, using fallback")
                    results["api_failed"] = True
                    fallback = await self._basic_performance_check(domain)
                    results.update(fallback)
            else:
                # No API key, use fallback
                logger.info(f"No PageSpeed API key, using basic check for {domain}")
                fallback = await self._basic_performance_check(domain)
                results.update(fallback)
            
            # Cache results
            await cache_result(cache_key, results, ttl=3600)
            
            return results
            
        except Exception as e:
            logger.error("Performance analysis failed", domain=domain, error=str(e))
            # Try fallback even on exception
            try:
                fallback = await self._basic_performance_check(domain)
                results.update(fallback)
            except:
                pass
            return results
    
    async def _get_pagespeed_data(self, domain: str) -> Dict:
        async with httpx.AsyncClient() as client:
            params = {
                "url": f"https://{domain}",
                "key": self.pagespeed_api_key,
                "category": ["performance", "accessibility", "best-practices", "seo"],
                "strategy": "desktop"
            }
            
            try:
                logger.info(f"Calling PageSpeed API for {domain}")
                response = await client.get(
                    self.pagespeed_url,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"PageSpeed API success for {domain}")
                    return data
                else:
                    error_text = response.text
                    logger.warning(f"PageSpeed API failed for {domain}", 
                                 status=response.status_code, 
                                 error=error_text[:200])
                    return {}
            except Exception as e:
                logger.error(f"PageSpeed API exception for {domain}", error=str(e))
                return {}
    
    def _parse_pagespeed_data(self, data: Dict) -> Dict:
        if not data:
            return {}
        
        results = {}
        
        # Get lighthouse data
        lighthouse = data.get("lighthouseResult", {})
        
        # Overall score
        categories = lighthouse.get("categories", {})
        perf_category = categories.get("performance", {})
        score = perf_category.get("score")
        results["score"] = int(score * 100) if score is not None else 0
        
        # Core Web Vitals
        audits = lighthouse.get("audits", {})
        
        # Load time metrics
        if "first-contentful-paint" in audits:
            fcp_value = audits["first-contentful-paint"].get("numericValue")
            results["first_contentful_paint"] = (fcp_value / 1000) if fcp_value is not None else 0
        
        if "interactive" in audits:
            tti_value = audits["interactive"].get("numericValue")
            results["time_to_interactive"] = (tti_value / 1000) if tti_value is not None else 0
        
        if "total-blocking-time" in audits:
            tbt_value = audits["total-blocking-time"].get("numericValue")
            results["total_blocking_time"] = tbt_value if tbt_value is not None else 0
        
        if "cumulative-layout-shift" in audits:
            cls_value = audits["cumulative-layout-shift"].get("numericValue")
            results["cumulative_layout_shift"] = cls_value if cls_value is not None else 0
        
        # Calculate estimated load time
        if "speed-index" in audits:
            si_value = audits["speed-index"].get("numericValue")
            results["load_time"] = (si_value / 1000) if si_value is not None else 0
        
        # Optimization opportunities
        if "uses-optimized-images" in audits:
            img_audit = audits["uses-optimized-images"]
            if img_audit.get("details", {}).get("items"):
                results["unoptimized_images"] = len(img_audit["details"]["items"])
        
        if "unused-css-rules" in audits:
            css_audit = audits["unused-css-rules"]
            css_value = css_audit.get("numericValue")
            results["unused_css"] = (css_value / 1024) if css_value is not None else 0  # Convert to KB
        
        if "unused-javascript" in audits:
            js_audit = audits["unused-javascript"]
            js_value = js_audit.get("numericValue")
            results["unused_js"] = (js_value / 1024) if js_value is not None else 0  # Convert to KB
        
        if "render-blocking-resources" in audits:
            blocking_audit = audits["render-blocking-resources"]
            if blocking_audit.get("details", {}).get("items"):
                results["render_blocking_resources"] = len(blocking_audit["details"]["items"])
        
        # Issues from opportunities
        opportunities = []
        for key, audit in audits.items():
            if audit.get("score", 1) < 0.9 and audit.get("description"):
                opportunities.append({
                    "id": key,
                    "title": audit.get("title", key),
                    "description": audit.get("description"),
                    "impact": audit.get("numericValue", 0)
                })
        
        results["issues"] = sorted(opportunities, key=lambda x: x["impact"], reverse=True)[:5]
        
        return results
    
    async def _basic_performance_check(self, domain: str) -> Dict:
        """Fallback performance check without PageSpeed API"""
        results = {}
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                # Measure basic load time with proper headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                logger.info(f"Running basic performance check for {domain}")
                start = asyncio.get_event_loop().time()
                response = await client.get(f"https://{domain}", timeout=15.0, headers=headers)
                load_time = asyncio.get_event_loop().time() - start
                
                results["load_time"] = round(load_time, 2)
                logger.info(f"Basic check for {domain}: load_time={load_time:.2f}s, status={response.status_code}")
                
                # Parse HTML for basic checks
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Count images without loading attribute
                images = soup.find_all('img')
                unoptimized = sum(1 for img in images if not img.get('loading'))
                results["unoptimized_images"] = unoptimized
                
                # Count render-blocking resources
                scripts = soup.find_all('script', src=True)
                blocking_scripts = sum(1 for s in scripts if not s.get('async') and not s.get('defer'))
                results["render_blocking_resources"] = blocking_scripts
                
                # Count CSS files
                css_links = soup.find_all('link', rel='stylesheet')
                results["css_files"] = len(css_links)
                
                # Check for large images
                large_images = 0
                for img in images:
                    src = img.get('src', '')
                    if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                        if not any(opt in src.lower() for opt in ['thumb', 'small', 'icon', 'logo']):
                            large_images += 1
                results["large_images"] = large_images
                
                # More realistic score estimation based on multiple factors
                score = 100
                
                # Deduct for load time
                if load_time > 5:
                    score -= 40
                elif load_time > 3:
                    score -= 25
                elif load_time > 2:
                    score -= 10
                
                # Deduct for unoptimized images
                if unoptimized > 10:
                    score -= 15
                elif unoptimized > 5:
                    score -= 10
                elif unoptimized > 0:
                    score -= 5
                
                # Deduct for render-blocking resources
                if blocking_scripts > 5:
                    score -= 20
                elif blocking_scripts > 2:
                    score -= 10
                elif blocking_scripts > 0:
                    score -= 5
                
                # Deduct for too many CSS files
                if css_links and len(css_links) > 10:
                    score -= 10
                elif css_links and len(css_links) > 5:
                    score -= 5
                
                results["score"] = max(0, score)
                
                # Add basic estimated metrics
                results["first_contentful_paint"] = load_time * 0.3  # Rough estimate
                results["time_to_interactive"] = load_time * 0.8  # Rough estimate
                
                logger.info(f"Basic performance score for {domain}: {results['score']}/100")
                
        except httpx.TimeoutException:
            logger.error(f"Timeout while checking {domain}")
            results["score"] = 10
            results["load_time"] = 15.0
            results["error"] = "Site took too long to respond"
        except Exception as e:
            logger.error(f"Basic performance check failed for {domain}", error=str(e))
            results["score"] = None
            results["load_time"] = 0
            results["error"] = str(e)
        
        return results