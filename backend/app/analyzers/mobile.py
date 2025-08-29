import httpx
from typing import Dict, Any
import structlog
from bs4 import BeautifulSoup

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class MobileAnalyzer:
    def __init__(self):
        pass
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        cache_key = f"mobile:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "score": 0,
            "has_viewport": False,
            "responsive_design": False,
            "tap_targets": "unknown",
            "text_size": "unknown",
            "issues": [],
            "missing_viewport": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Set mobile user agent
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
                }
                
                response = await client.get(f"https://{domain}", headers=headers, timeout=10.0)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Check viewport meta tag
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                if viewport:
                    results["has_viewport"] = True
                    viewport_content = viewport.get('content', '')
                    if 'width=device-width' in viewport_content:
                        results["responsive_design"] = True
                else:
                    results["missing_viewport"] = True
                    results["issues"].append({
                        "type": "viewport",
                        "severity": "critical",
                        "message": "Missing viewport meta tag - site won't scale on mobile"
                    })
                
                # Check for common mobile issues
                
                # Check for horizontal scroll (basic check)
                styles = soup.find_all('style')
                css_text = ' '.join([s.text for s in styles])
                if 'overflow-x: scroll' in css_text or 'overflow-x: auto' in css_text:
                    results["issues"].append({
                        "type": "layout",
                        "severity": "high",
                        "message": "Potential horizontal scrolling on mobile"
                    })
                
                # Check for fixed widths
                if 'width: 1024px' in css_text or 'width: 1200px' in css_text:
                    results["issues"].append({
                        "type": "layout",
                        "severity": "high",
                        "message": "Fixed width layouts may break on mobile"
                    })
                
                # Check for mobile-unfriendly elements
                flash_elements = soup.find_all(['object', 'embed'])
                if flash_elements:
                    results["issues"].append({
                        "type": "compatibility",
                        "severity": "critical",
                        "message": "Contains Flash/plugins not supported on mobile"
                    })
                
                # Check button/link sizes (basic heuristic)
                buttons = soup.find_all(['button', 'a'])
                small_targets = 0
                for button in buttons[:20]:  # Check first 20
                    # This is a heuristic - in production would use actual rendering
                    classes = button.get('class', [])
                    if isinstance(classes, list):
                        class_str = ' '.join(classes)
                    else:
                        class_str = classes
                    
                    if 'sm' in class_str or 'small' in class_str or 'tiny' in class_str:
                        small_targets += 1
                
                if small_targets > 5:
                    results["issues"].append({
                        "type": "usability",
                        "severity": "medium",
                        "message": "Multiple small tap targets detected"
                    })
                    results["tap_targets"] = "too_small"
                else:
                    results["tap_targets"] = "adequate"
                
                # Check text readability
                if 'font-size: 10px' in css_text or 'font-size: 11px' in css_text:
                    results["issues"].append({
                        "type": "readability",
                        "severity": "medium",
                        "message": "Text may be too small to read on mobile"
                    })
                    results["text_size"] = "too_small"
                else:
                    results["text_size"] = "adequate"
                
                # Calculate mobile score
                score = 70  # Base score
                
                if results["has_viewport"]:
                    score += 20
                if results["responsive_design"]:
                    score += 10
                
                # Deduct for issues
                for issue in results["issues"]:
                    if issue["severity"] == "critical":
                        score -= 20
                    elif issue["severity"] == "high":
                        score -= 10
                    elif issue["severity"] == "medium":
                        score -= 5
                
                results["score"] = max(0, min(100, score))
                
                await cache_result(cache_key, results, ttl=3600)
                
        except Exception as e:
            logger.error("Mobile analysis failed", domain=domain, error=str(e))
            results["score"] = 0
        
        return results