import httpx
import hashlib
import hmac
from typing import Dict, Any, List
from urllib.parse import urlencode
import structlog

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class VisualAnalyzer:
    def __init__(self):
        self.api_key = settings.URLBOX_API_KEY
        self.api_secret = settings.URLBOX_API_SECRET
        self.base_url = "https://api.urlbox.io/v1"
        self.enabled = bool(self.api_key and self.api_secret)
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        if not self.enabled:
            logger.info("Visual analysis skipped - Urlbox not configured")
            return {
                "screenshots": [],
                "visual_issues": [],
                "has_screenshots": False
            }
        
        cache_key = f"visual:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "screenshots": [],
            "visual_issues": [],
            "responsive_scores": {},
            "has_hero": False,
            "has_cta_above_fold": False,
            "visual_hierarchy": "unknown",
            "has_screenshots": False
        }
        
        try:
            # Generate screenshots for different viewports
            screenshots = await self._capture_screenshots(domain)
            results["screenshots"] = screenshots
            results["has_screenshots"] = len(screenshots) > 0
            
            # Analyze visual issues (basic heuristics)
            if screenshots:
                results["visual_issues"] = self._analyze_visual_issues(screenshots)
            
            await cache_result(cache_key, results, ttl=86400)  # Cache for 24 hours
            
        except Exception as e:
            logger.error("Visual analysis failed", domain=domain, error=str(e))
        
        return results
    
    async def _capture_screenshots(self, domain: str) -> List[Dict]:
        screenshots = []
        
        # Define viewports to test
        viewports = [
            {"name": "desktop", "width": 1920, "height": 1080},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "mobile", "width": 375, "height": 812},
        ]
        
        for viewport in viewports:
            try:
                screenshot_url = await self._get_screenshot_url(
                    url=f"https://{domain}",
                    width=viewport["width"],
                    height=viewport["height"],
                    full_page=False  # Above the fold only for performance
                )
                
                screenshots.append({
                    "device": viewport["name"],
                    "url": screenshot_url,
                    "width": viewport["width"],
                    "height": viewport["height"]
                })
                
            except Exception as e:
                logger.error(f"Failed to capture {viewport['name']} screenshot", error=str(e))
        
        return screenshots
    
    async def _get_screenshot_url(
        self,
        url: str,
        width: int = 1920,
        height: int = 1080,
        full_page: bool = False
    ) -> str:
        # Urlbox parameters
        params = {
            "url": url,
            "width": width,
            "height": height,
            "full_page": full_page,
            "block_ads": True,
            "hide_cookie_banners": True,
            "retina": False,  # Save on bandwidth for MVP
            "quality": 80,
            "format": "jpg",
            "ttl": 86400,  # Cache for 24 hours
        }
        
        # Generate HMAC token for authentication
        query_string = urlencode(sorted(params.items()))
        token = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Construct the URL
        screenshot_url = f"{self.base_url}/{self.api_key}/{token}/jpg?{query_string}"
        
        return screenshot_url
    
    def _analyze_visual_issues(self, screenshots: List[Dict]) -> List[Dict]:
        issues = []
        
        # Check if we have all viewport screenshots
        has_mobile = any(s["device"] == "mobile" for s in screenshots)
        has_tablet = any(s["device"] == "tablet" for s in screenshots)
        has_desktop = any(s["device"] == "desktop" for s in screenshots)
        
        if not has_mobile:
            issues.append({
                "type": "screenshot",
                "severity": "medium",
                "message": "Could not capture mobile screenshot - site may have issues"
            })
        
        # In a production version, we could:
        # 1. Use AI vision models to analyze the screenshots
        # 2. Check for visual regressions
        # 3. Detect missing elements
        # 4. Check color contrast
        # 5. Verify CTA visibility
        
        return issues


class ScreenshotComparer:
    """Compare screenshots with competitors"""
    
    @staticmethod
    async def compare_with_competitor(
        domain: str,
        competitor_domain: str,
        visual_analyzer: VisualAnalyzer
    ) -> Dict[str, Any]:
        comparison = {
            "domain": domain,
            "competitor": competitor_domain,
            "differences": []
        }
        
        try:
            # Get screenshots for both
            domain_shots = await visual_analyzer.analyze(domain)
            competitor_shots = await visual_analyzer.analyze(competitor_domain)
            
            # Basic comparison
            if domain_shots["has_screenshots"] and competitor_shots["has_screenshots"]:
                # In production, use computer vision to compare:
                # - Layout differences
                # - Color schemes
                # - CTA prominence
                # - Content density
                
                comparison["differences"] = [
                    {
                        "aspect": "screenshots_available",
                        "domain_value": len(domain_shots["screenshots"]),
                        "competitor_value": len(competitor_shots["screenshots"])
                    }
                ]
            
        except Exception as e:
            logger.error("Screenshot comparison failed", error=str(e))
        
        return comparison