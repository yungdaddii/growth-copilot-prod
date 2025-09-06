"""
Enhanced Performance Analyzer with Deep Insights
Provides comprehensive performance analysis including resource waterfall,
third-party impact, and real user metrics simulation.
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import structlog
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse, urljoin
import json

from app.utils.cache import cache_result, get_cached_result
from app.config import settings

logger = structlog.get_logger()


class EnhancedPerformanceAnalyzer:
    def __init__(self):
        self.pagespeed_api_key = settings.GOOGLE_PAGESPEED_API_KEY
        self.pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        # Performance thresholds based on Core Web Vitals
        self.thresholds = {
            'lcp': {'good': 2.5, 'needs_improvement': 4.0},  # Largest Contentful Paint
            'fid': {'good': 100, 'needs_improvement': 300},   # First Input Delay
            'cls': {'good': 0.1, 'needs_improvement': 0.25},  # Cumulative Layout Shift
            'fcp': {'good': 1.8, 'needs_improvement': 3.0},   # First Contentful Paint
            'ttfb': {'good': 0.8, 'needs_improvement': 1.8},  # Time to First Byte
            'tti': {'good': 3.8, 'needs_improvement': 7.3}    # Time to Interactive
        }
        
        # Known third-party domains and their categories
        self.third_party_categories = {
            'analytics': ['google-analytics.com', 'googletagmanager.com', 'segment.com', 'mixpanel.com', 'amplitude.com', 'heap.io'],
            'advertising': ['doubleclick.net', 'googlesyndication.com', 'facebook.com', 'amazon-adsystem.com'],
            'cdn': ['cloudflare.com', 'cloudfront.net', 'fastly.net', 'akamaihd.net', 'jsdelivr.net'],
            'social': ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'pinterest.com'],
            'fonts': ['fonts.googleapis.com', 'fonts.gstatic.com', 'typekit.net', 'use.typekit.net'],
            'customer_support': ['intercom.io', 'drift.com', 'zendesk.com', 'livechat.com', 'tawk.to'],
            'video': ['youtube.com', 'vimeo.com', 'wistia.com', 'vidyard.com'],
            'payments': ['stripe.com', 'paypal.com', 'square.com', 'checkout.com']
        }
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        cache_key = f"enhanced_performance:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "score": 0,
            "core_web_vitals": {},
            "resource_analysis": {},
            "third_party_impact": {},
            "network_analysis": {},
            "javascript_analysis": {},
            "image_optimization": {},
            "caching_analysis": {},
            "recommendations": [],
            "performance_budget": {},
            "competitive_benchmark": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Run multiple analyses in parallel
                tasks = [
                    self._get_pagespeed_insights(client, domain),
                    self._analyze_resource_loading(client, domain),
                    self._analyze_third_party_scripts(client, domain),
                    self._analyze_network_protocols(client, domain),
                    self._simulate_mobile_performance(client, domain)
                ]
                
                pagespeed_data, resource_data, third_party_data, network_data, mobile_data = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process PageSpeed Insights data if available
                if not isinstance(pagespeed_data, Exception) and pagespeed_data:
                    results["core_web_vitals"] = self._extract_core_web_vitals(pagespeed_data)
                    results["score"] = pagespeed_data.get("score", 0)
                    results["opportunities"] = self._extract_opportunities(pagespeed_data)
                
                # Add resource analysis
                if not isinstance(resource_data, Exception):
                    results["resource_analysis"] = resource_data
                
                # Add third-party impact
                if not isinstance(third_party_data, Exception):
                    results["third_party_impact"] = third_party_data
                
                # Add network analysis
                if not isinstance(network_data, Exception):
                    results["network_analysis"] = network_data
                
                # Add mobile performance
                if not isinstance(mobile_data, Exception):
                    results["mobile_performance"] = mobile_data
                
                # Calculate performance budget recommendations
                results["performance_budget"] = self._calculate_performance_budget(results)
                
                # Generate prioritized recommendations
                results["recommendations"] = self._generate_performance_recommendations(results)
                
                # Add competitive benchmarks
                results["competitive_benchmark"] = self._get_competitive_benchmarks(results)
                
                await cache_result(cache_key, results, ttl=3600)
                
        except Exception as e:
            logger.error(f"Enhanced performance analysis failed for {domain}", error=str(e))
            results["error"] = str(e)
        
        return results
    
    async def _get_pagespeed_insights(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Get detailed PageSpeed Insights data"""
        if not self.pagespeed_api_key:
            return {"error": "No PageSpeed API key configured"}
        
        try:
            params = {
                "url": f"https://{domain}",
                "key": self.pagespeed_api_key,
                "category": ["performance", "accessibility", "best-practices", "seo"],
                "strategy": "desktop"
            }
            
            response = await client.get(self.pagespeed_url, params=params, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                lighthouse = data.get("lighthouseResult", {})
                
                return {
                    "score": int(lighthouse.get("categories", {}).get("performance", {}).get("score", 0) * 100),
                    "audits": lighthouse.get("audits", {}),
                    "metrics": lighthouse.get("audits", {}).get("metrics", {}).get("details", {}).get("items", [{}])[0],
                    "opportunities": self._extract_opportunities(data),
                    "diagnostics": self._extract_diagnostics(data)
                }
            
            return {"error": f"PageSpeed API returned {response.status_code}"}
            
        except Exception as e:
            logger.error(f"PageSpeed Insights failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    def _extract_core_web_vitals(self, pagespeed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and evaluate Core Web Vitals"""
        metrics = pagespeed_data.get("metrics", {})
        audits = pagespeed_data.get("audits", {})
        
        cwv = {
            "lcp": {
                "value": 0,
                "score": "poor",
                "percentile": 0,
                "recommendations": []
            },
            "fid": {
                "value": 0,
                "score": "poor",
                "percentile": 0,
                "recommendations": []
            },
            "cls": {
                "value": 0,
                "score": "poor",
                "percentile": 0,
                "recommendations": []
            },
            "overall_score": "poor"
        }
        
        # LCP - Largest Contentful Paint
        if "largest-contentful-paint" in audits:
            lcp_value = audits["largest-contentful-paint"].get("numericValue", 0) / 1000
            cwv["lcp"]["value"] = round(lcp_value, 2)
            cwv["lcp"]["score"] = self._evaluate_metric(lcp_value, self.thresholds["lcp"])
            
            if cwv["lcp"]["score"] != "good":
                cwv["lcp"]["recommendations"] = [
                    "Optimize server response time (TTFB)",
                    "Use a CDN for static assets",
                    "Optimize critical rendering path",
                    "Preload key resources"
                ]
        
        # FID - First Input Delay (using TBT as proxy)
        if "total-blocking-time" in audits:
            tbt_value = audits["total-blocking-time"].get("numericValue", 0)
            cwv["fid"]["value"] = tbt_value
            cwv["fid"]["score"] = self._evaluate_metric(tbt_value, self.thresholds["fid"])
            
            if cwv["fid"]["score"] != "good":
                cwv["fid"]["recommendations"] = [
                    "Break up long JavaScript tasks",
                    "Use web workers for heavy computations",
                    "Reduce JavaScript execution time",
                    "Minimize main thread work"
                ]
        
        # CLS - Cumulative Layout Shift
        if "cumulative-layout-shift" in audits:
            cls_value = audits["cumulative-layout-shift"].get("numericValue", 0)
            cwv["cls"]["value"] = round(cls_value, 3)
            cwv["cls"]["score"] = self._evaluate_metric(cls_value, self.thresholds["cls"])
            
            if cwv["cls"]["score"] != "good":
                cwv["cls"]["recommendations"] = [
                    "Specify image dimensions",
                    "Reserve space for dynamic content",
                    "Avoid inserting content above existing content",
                    "Use CSS transform for animations"
                ]
        
        # Calculate overall CWV score
        scores = [cwv["lcp"]["score"], cwv["fid"]["score"], cwv["cls"]["score"]]
        if all(s == "good" for s in scores):
            cwv["overall_score"] = "good"
        elif any(s == "poor" for s in scores):
            cwv["overall_score"] = "poor"
        else:
            cwv["overall_score"] = "needs_improvement"
        
        return cwv
    
    def _evaluate_metric(self, value: float, thresholds: Dict[str, float]) -> str:
        """Evaluate metric against thresholds"""
        if value <= thresholds["good"]:
            return "good"
        elif value <= thresholds["needs_improvement"]:
            return "needs_improvement"
        else:
            return "poor"
    
    async def _analyze_resource_loading(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze resource loading patterns and waterfall"""
        try:
            start_time = time.time()
            response = await client.get(f"https://{domain}")
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Analyze different resource types
            resources = {
                "css": [],
                "js": [],
                "images": [],
                "fonts": [],
                "total_size_estimate": 0,
                "critical_resources": [],
                "render_blocking": [],
                "async_resources": [],
                "deferred_resources": []
            }
            
            # CSS Analysis
            css_links = soup.find_all('link', rel='stylesheet')
            for css in css_links:
                href = css.get('href', '')
                resources["css"].append({
                    "url": href,
                    "render_blocking": not css.get('media') or css.get('media') == 'all',
                    "critical": 'critical' in href.lower() or not css.get('media')
                })
                
                if not css.get('media') or css.get('media') == 'all':
                    resources["render_blocking"].append(f"CSS: {href[:50]}...")
            
            # JavaScript Analysis
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                src = script.get('src', '')
                is_async = script.get('async') is not None
                is_defer = script.get('defer') is not None
                
                resources["js"].append({
                    "url": src,
                    "loading": "async" if is_async else "defer" if is_defer else "blocking",
                    "render_blocking": not is_async and not is_defer
                })
                
                if is_async:
                    resources["async_resources"].append(f"JS: {src[:50]}...")
                elif is_defer:
                    resources["deferred_resources"].append(f"JS: {src[:50]}...")
                elif src:
                    resources["render_blocking"].append(f"JS: {src[:50]}...")
            
            # Image Analysis
            images = soup.find_all('img')
            for img in images:
                src = img.get('src', '')
                resources["images"].append({
                    "url": src,
                    "lazy_loading": img.get('loading') == 'lazy',
                    "has_dimensions": bool(img.get('width') and img.get('height')),
                    "alt_text": bool(img.get('alt'))
                })
            
            # Font Analysis
            style_tags = soup.find_all('style')
            for style in style_tags:
                if '@font-face' in style.text:
                    resources["fonts"].append({
                        "inline": True,
                        "preloaded": False
                    })
            
            # Check for font preloading
            preload_links = soup.find_all('link', rel='preload')
            for link in preload_links:
                if link.get('as') == 'font':
                    resources["fonts"].append({
                        "url": link.get('href', ''),
                        "preloaded": True
                    })
            
            # Identify critical resources
            if resources["render_blocking"]:
                resources["critical_resources"] = resources["render_blocking"][:5]
            
            # Calculate resource metrics
            resource_metrics = {
                "total_css_files": len(resources["css"]),
                "total_js_files": len(resources["js"]),
                "total_images": len(resources["images"]),
                "render_blocking_count": len(resources["render_blocking"]),
                "lazy_loaded_images": sum(1 for img in resources["images"] if img["lazy_loading"]),
                "optimization_score": 100
            }
            
            # Deduct points for issues
            if resource_metrics["render_blocking_count"] > 3:
                resource_metrics["optimization_score"] -= 20
            if resource_metrics["total_css_files"] > 5:
                resource_metrics["optimization_score"] -= 10
            if resource_metrics["total_js_files"] > 10:
                resource_metrics["optimization_score"] -= 15
            if resource_metrics["lazy_loaded_images"] < resource_metrics["total_images"] * 0.5:
                resource_metrics["optimization_score"] -= 10
            
            resources["metrics"] = resource_metrics
            resources["load_time"] = round(load_time, 2)
            
            return resources
            
        except Exception as e:
            logger.error(f"Resource analysis failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    async def _analyze_third_party_scripts(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze third-party script impact"""
        try:
            response = await client.get(f"https://{domain}")
            soup = BeautifulSoup(response.text, 'lxml')
            
            third_party_analysis = {
                "total_third_party": 0,
                "by_category": {},
                "performance_impact": "low",
                "blocking_scripts": [],
                "recommendations": [],
                "estimated_impact_ms": 0
            }
            
            # Find all external scripts
            scripts = soup.find_all('script', src=True)
            domain_parsed = urlparse(f"https://{domain}")
            
            for script in scripts:
                src = script.get('src', '')
                if src.startswith('http'):
                    script_domain = urlparse(src).netloc
                    
                    # Check if third-party
                    if domain_parsed.netloc not in script_domain:
                        third_party_analysis["total_third_party"] += 1
                        
                        # Categorize the script
                        category = "other"
                        for cat, domains in self.third_party_categories.items():
                            if any(d in script_domain for d in domains):
                                category = cat
                                break
                        
                        if category not in third_party_analysis["by_category"]:
                            third_party_analysis["by_category"][category] = []
                        
                        is_blocking = not script.get('async') and not script.get('defer')
                        
                        third_party_analysis["by_category"][category].append({
                            "domain": script_domain,
                            "blocking": is_blocking,
                            "url": src[:100]
                        })
                        
                        if is_blocking:
                            third_party_analysis["blocking_scripts"].append(script_domain)
                            third_party_analysis["estimated_impact_ms"] += 100  # Rough estimate
            
            # Calculate performance impact
            if third_party_analysis["total_third_party"] > 15:
                third_party_analysis["performance_impact"] = "high"
                third_party_analysis["recommendations"].append("Too many third-party scripts (>15) - consider reducing")
            elif third_party_analysis["total_third_party"] > 8:
                third_party_analysis["performance_impact"] = "medium"
                third_party_analysis["recommendations"].append("Moderate third-party scripts - optimize loading")
            
            # Category-specific recommendations
            if "analytics" in third_party_analysis["by_category"] and len(third_party_analysis["by_category"]["analytics"]) > 2:
                third_party_analysis["recommendations"].append("Multiple analytics tools detected - consider consolidating")
            
            if "advertising" in third_party_analysis["by_category"]:
                third_party_analysis["recommendations"].append("Ad scripts detected - ensure they load asynchronously")
            
            if "customer_support" in third_party_analysis["by_category"]:
                third_party_analysis["recommendations"].append("Chat widgets impact performance - consider lazy loading")
            
            # Add facade recommendations
            if third_party_analysis["blocking_scripts"]:
                third_party_analysis["recommendations"].append(
                    f"Make {len(third_party_analysis['blocking_scripts'])} blocking scripts async/defer"
                )
            
            return third_party_analysis
            
        except Exception as e:
            logger.error(f"Third-party analysis failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    async def _analyze_network_protocols(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze network protocols and optimizations"""
        try:
            response = await client.get(f"https://{domain}")
            headers = response.headers
            
            network_analysis = {
                "http_version": response.http_version,
                "http2_enabled": response.http_version == "HTTP/2",
                "http3_enabled": False,  # Would need special detection
                "compression": "none",
                "cdn_detected": False,
                "cdn_provider": None,
                "security_headers": {},
                "caching_headers": {},
                "recommendations": []
            }
            
            # Check compression
            if 'content-encoding' in headers:
                network_analysis["compression"] = headers['content-encoding']
            else:
                network_analysis["recommendations"].append("Enable Gzip/Brotli compression")
            
            # Check for CDN
            cdn_headers = ['x-cdn', 'x-served-by', 'x-cache', 'cf-ray', 'x-amz-cf-id']
            for header in cdn_headers:
                if header in headers:
                    network_analysis["cdn_detected"] = True
                    if 'cloudflare' in headers.get(header, '').lower() or 'cf-ray' in headers:
                        network_analysis["cdn_provider"] = "Cloudflare"
                    elif 'cloudfront' in headers.get(header, '').lower():
                        network_analysis["cdn_provider"] = "CloudFront"
                    elif 'fastly' in headers.get(header, '').lower():
                        network_analysis["cdn_provider"] = "Fastly"
                    break
            
            if not network_analysis["cdn_detected"]:
                network_analysis["recommendations"].append("Consider using a CDN for global performance")
            
            # Check caching headers
            cache_headers = ['cache-control', 'expires', 'etag', 'last-modified']
            for header in cache_headers:
                if header in headers:
                    network_analysis["caching_headers"][header] = headers[header]
            
            if 'cache-control' not in headers:
                network_analysis["recommendations"].append("Add Cache-Control headers for better caching")
            elif 'no-cache' in headers.get('cache-control', ''):
                network_analysis["recommendations"].append("Homepage has no-cache - consider caching strategy")
            
            # Check security headers
            security_headers = [
                'strict-transport-security',
                'x-content-type-options',
                'x-frame-options',
                'content-security-policy',
                'x-xss-protection'
            ]
            
            for header in security_headers:
                network_analysis["security_headers"][header] = header in headers
            
            # HTTP/2 and HTTP/3 recommendations
            if not network_analysis["http2_enabled"]:
                network_analysis["recommendations"].append("Enable HTTP/2 for multiplexing and better performance")
            
            # Calculate network score
            network_score = 100
            if not network_analysis["http2_enabled"]:
                network_score -= 20
            if network_analysis["compression"] == "none":
                network_score -= 20
            if not network_analysis["cdn_detected"]:
                network_score -= 15
            if not network_analysis["caching_headers"]:
                network_score -= 15
            
            network_analysis["score"] = max(0, network_score)
            
            return network_analysis
            
        except Exception as e:
            logger.error(f"Network analysis failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    async def _simulate_mobile_performance(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Simulate mobile performance characteristics"""
        try:
            # Simulate mobile user agent
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            }
            
            start_time = time.time()
            response = await client.get(f"https://{domain}", headers=mobile_headers)
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            mobile_analysis = {
                "load_time": round(load_time, 2),
                "viewport_configured": False,
                "text_readability": True,
                "tap_targets": True,
                "responsive_images": False,
                "mobile_specific_issues": [],
                "estimated_3g_load_time": round(load_time * 3.5, 2),  # Rough 3G estimate
                "estimated_4g_load_time": round(load_time * 1.5, 2),  # Rough 4G estimate
                "recommendations": []
            }
            
            # Check viewport meta tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport:
                mobile_analysis["viewport_configured"] = True
                content = viewport.get('content', '')
                if 'user-scalable=no' in content:
                    mobile_analysis["mobile_specific_issues"].append("Viewport disables zooming - accessibility issue")
            else:
                mobile_analysis["mobile_specific_issues"].append("No viewport meta tag - critical for mobile")
            
            # Check for responsive images
            images = soup.find_all('img')
            responsive_count = sum(1 for img in images if img.get('srcset') or img.get('sizes'))
            if images and responsive_count > len(images) * 0.3:
                mobile_analysis["responsive_images"] = True
            elif images:
                mobile_analysis["recommendations"].append("Use responsive images with srcset for mobile optimization")
            
            # Check font sizes (basic heuristic)
            styles = soup.find_all('style')
            small_font_detected = False
            for style in styles:
                if 'font-size' in style.text:
                    # Check for very small fonts
                    if re.search(r'font-size:\s*[0-9]px', style.text) or re.search(r'font-size:\s*0\.[0-9]+rem', style.text):
                        small_font_detected = True
                        break
            
            if small_font_detected:
                mobile_analysis["text_readability"] = False
                mobile_analysis["mobile_specific_issues"].append("Small font sizes detected - may be hard to read on mobile")
            
            # Mobile performance recommendations based on load time
            if mobile_analysis["estimated_3g_load_time"] > 10:
                mobile_analysis["recommendations"].append("Critical: Site too slow on 3G (>10s) - implement aggressive optimization")
            elif mobile_analysis["estimated_3g_load_time"] > 5:
                mobile_analysis["recommendations"].append("Slow on 3G networks - consider AMP or lite version")
            
            if mobile_analysis["estimated_4g_load_time"] > 3:
                mobile_analysis["recommendations"].append("Could be faster on 4G - optimize critical rendering path")
            
            # Calculate mobile score
            mobile_score = 100
            if not mobile_analysis["viewport_configured"]:
                mobile_score -= 30
            if not mobile_analysis["text_readability"]:
                mobile_score -= 15
            if not mobile_analysis["responsive_images"]:
                mobile_score -= 10
            if mobile_analysis["estimated_4g_load_time"] > 3:
                mobile_score -= 20
            
            mobile_analysis["score"] = max(0, mobile_score)
            
            return mobile_analysis
            
        except Exception as e:
            logger.error(f"Mobile performance simulation failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    def _extract_opportunities(self, pagespeed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and prioritize optimization opportunities"""
        opportunities = []
        
        if "lighthouseResult" in pagespeed_data:
            audits = pagespeed_data["lighthouseResult"].get("audits", {})
            
            # Define opportunity audits with their impact
            opportunity_audits = [
                ("uses-optimized-images", "Optimize images", "high"),
                ("unused-css-rules", "Remove unused CSS", "medium"),
                ("unused-javascript", "Remove unused JavaScript", "medium"),
                ("uses-text-compression", "Enable text compression", "high"),
                ("uses-responsive-images", "Serve responsive images", "medium"),
                ("offscreen-images", "Defer offscreen images", "medium"),
                ("render-blocking-resources", "Eliminate render-blocking resources", "high"),
                ("unminified-css", "Minify CSS", "low"),
                ("unminified-javascript", "Minify JavaScript", "low"),
                ("efficient-animated-content", "Use video formats for animated content", "medium"),
                ("duplicated-javascript", "Remove duplicate JavaScript", "medium"),
                ("legacy-javascript", "Avoid serving legacy JavaScript", "medium")
            ]
            
            for audit_id, description, impact in opportunity_audits:
                if audit_id in audits:
                    audit = audits[audit_id]
                    if audit.get("score", 1) < 0.9:  # Opportunity exists
                        savings = audit.get("details", {}).get("overallSavingsMs", 0)
                        
                        opportunities.append({
                            "id": audit_id,
                            "title": description,
                            "description": audit.get("description", ""),
                            "impact": impact,
                            "estimated_savings_ms": savings,
                            "score": audit.get("score", 0)
                        })
            
            # Sort by impact and savings
            impact_order = {"high": 3, "medium": 2, "low": 1}
            opportunities.sort(
                key=lambda x: (impact_order.get(x["impact"], 0), x["estimated_savings_ms"]),
                reverse=True
            )
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def _extract_diagnostics(self, pagespeed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract diagnostic information"""
        diagnostics = []
        
        if "lighthouseResult" in pagespeed_data:
            audits = pagespeed_data["lighthouseResult"].get("audits", {})
            
            diagnostic_audits = [
                "font-display",
                "critical-request-chains",
                "redirects",
                "mainthread-work-breakdown",
                "bootup-time",
                "uses-rel-preconnect",
                "server-response-time"
            ]
            
            for audit_id in diagnostic_audits:
                if audit_id in audits:
                    audit = audits[audit_id]
                    if audit.get("score", 1) < 1:
                        diagnostics.append({
                            "id": audit_id,
                            "title": audit.get("title", ""),
                            "description": audit.get("description", ""),
                            "displayValue": audit.get("displayValue", "")
                        })
        
        return diagnostics
    
    def _calculate_performance_budget(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate recommended performance budget"""
        budget = {
            "javascript": {
                "current": 0,
                "recommended": 170,  # KB
                "over_budget": False
            },
            "css": {
                "current": 0,
                "recommended": 50,  # KB
                "over_budget": False
            },
            "images": {
                "current": 0,
                "recommended": 500,  # KB
                "over_budget": False
            },
            "fonts": {
                "current": 0,
                "recommended": 100,  # KB
                "over_budget": False
            },
            "total_requests": {
                "current": 0,
                "recommended": 50,
                "over_budget": False
            },
            "time_to_interactive": {
                "current": 0,
                "recommended": 3.8,  # seconds
                "over_budget": False
            }
        }
        
        # Update with actual values if available
        if "resource_analysis" in results:
            resources = results["resource_analysis"]
            budget["javascript"]["current"] = len(resources.get("js", [])) * 30  # Rough estimate
            budget["css"]["current"] = len(resources.get("css", [])) * 20  # Rough estimate
            budget["images"]["current"] = len(resources.get("images", [])) * 50  # Rough estimate
            
            total_requests = (
                len(resources.get("js", [])) +
                len(resources.get("css", [])) +
                len(resources.get("images", [])) +
                len(resources.get("fonts", []))
            )
            budget["total_requests"]["current"] = total_requests
        
        # Check if over budget
        for category in budget:
            if budget[category]["current"] > budget[category]["recommended"]:
                budget[category]["over_budget"] = True
        
        return budget
    
    def _generate_performance_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized performance recommendations"""
        recommendations = []
        
        # Core Web Vitals recommendations
        if "core_web_vitals" in results:
            cwv = results["core_web_vitals"]
            
            if cwv.get("lcp", {}).get("score") != "good":
                recommendations.append({
                    "priority": 1,
                    "category": "Core Web Vitals",
                    "metric": "LCP",
                    "issue": f"LCP is {cwv['lcp']['value']}s (should be <2.5s)",
                    "impact": "Critical - affects ranking",
                    "solutions": cwv["lcp"].get("recommendations", [])
                })
            
            if cwv.get("cls", {}).get("score") != "good":
                recommendations.append({
                    "priority": 1,
                    "category": "Core Web Vitals",
                    "metric": "CLS",
                    "issue": f"CLS is {cwv['cls']['value']} (should be <0.1)",
                    "impact": "Critical - affects user experience",
                    "solutions": cwv["cls"].get("recommendations", [])
                })
        
        # Third-party script recommendations
        if "third_party_impact" in results:
            third_party = results["third_party_impact"]
            
            if third_party.get("performance_impact") == "high":
                recommendations.append({
                    "priority": 2,
                    "category": "Third-Party Scripts",
                    "metric": "Script Count",
                    "issue": f"{third_party['total_third_party']} third-party scripts detected",
                    "impact": "High - significant performance impact",
                    "solutions": third_party.get("recommendations", [])
                })
        
        # Resource loading recommendations
        if "resource_analysis" in results:
            resources = results["resource_analysis"]
            metrics = resources.get("metrics", {})
            
            if metrics.get("render_blocking_count", 0) > 3:
                recommendations.append({
                    "priority": 2,
                    "category": "Resource Loading",
                    "metric": "Render Blocking",
                    "issue": f"{metrics['render_blocking_count']} render-blocking resources",
                    "impact": "High - delays page rendering",
                    "solutions": [
                        "Inline critical CSS",
                        "Defer non-critical JavaScript",
                        "Use async attribute for third-party scripts",
                        "Implement resource hints (preload, prefetch)"
                    ]
                })
        
        # Mobile performance recommendations
        if "mobile_performance" in results:
            mobile = results["mobile_performance"]
            
            if mobile.get("estimated_3g_load_time", 0) > 5:
                recommendations.append({
                    "priority": 3,
                    "category": "Mobile Performance",
                    "metric": "3G Load Time",
                    "issue": f"Estimated 3G load time is {mobile['estimated_3g_load_time']}s",
                    "impact": "Medium - affects mobile users",
                    "solutions": mobile.get("recommendations", [])
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _get_competitive_benchmarks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Provide competitive benchmarks for the industry"""
        score = results.get("score", 0)
        
        benchmarks = {
            "your_score": score,
            "industry_average": 50,
            "top_performers": 85,
            "percentile": 0,
            "competitive_analysis": "",
            "improvement_potential": []
        }
        
        # Calculate percentile
        if score >= 85:
            benchmarks["percentile"] = 90
            benchmarks["competitive_analysis"] = "Excellent - Top 10% of websites"
        elif score >= 70:
            benchmarks["percentile"] = 75
            benchmarks["competitive_analysis"] = "Good - Above average performance"
        elif score >= 50:
            benchmarks["percentile"] = 50
            benchmarks["competitive_analysis"] = "Average - Room for improvement"
        elif score >= 30:
            benchmarks["percentile"] = 25
            benchmarks["competitive_analysis"] = "Below average - Significant optimization needed"
        else:
            benchmarks["percentile"] = 10
            benchmarks["competitive_analysis"] = "Poor - Critical performance issues"
        
        # Improvement potential
        if score < benchmarks["industry_average"]:
            benchmarks["improvement_potential"].append(
                f"Improve by {benchmarks['industry_average'] - score} points to reach industry average"
            )
        
        if score < benchmarks["top_performers"]:
            benchmarks["improvement_potential"].append(
                f"Improve by {benchmarks['top_performers'] - score} points to match top performers"
            )
        
        # Specific competitive advantages
        if score >= 70:
            benchmarks["competitive_advantages"] = [
                "Faster load times increase conversion rates",
                "Better Core Web Vitals improve SEO rankings",
                "Superior mobile experience captures more users"
            ]
        
        return benchmarks