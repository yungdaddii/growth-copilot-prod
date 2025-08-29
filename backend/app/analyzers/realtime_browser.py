"""
Real-time browser-based website analyzer using Playwright
Captures what users actually experience including JavaScript errors,
dynamic content, and actual page behavior
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import json
from bs4 import BeautifulSoup

# Make Playwright optional for Railway deployment
try:
    from playwright.async_api import async_playwright, Page, Browser, Error
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Page = None
    Browser = None
    Error = Exception

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class RealtimeBrowserAnalyzer:
    """
    Uses headless browser to capture real user experience including:
    - JavaScript errors that actually occur
    - Dynamic content that loads after initial HTML
    - Actual form validation behavior
    - Real page load performance
    - Interactive element detection
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.js_errors: List[Dict] = []
        self.console_errors: List[str] = []
        self.network_errors: List[Dict] = []
        self.page_timings: Dict[str, float] = {}
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Perform real-time browser-based analysis of website
        This sees what users actually see, not just static HTML
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "timestamp": datetime.now().isoformat(),
                "is_realtime": False,
                "javascript_errors": [],
                "dynamic_content": {},
                "forms": [],
                "load_metrics": {},
                "interactions": [],
                "console_logs": [],
                "network_errors": [],
                "error": "Browser analysis not available in production environment"
            }
        
        # Use shorter cache for real-time analysis (1 hour)
        cache_key = f"realtime_browser:{domain}:{datetime.now().strftime('%Y%m%d%H')}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "is_realtime": True,
            "javascript_errors": [],
            "console_errors": [],
            "network_failures": [],
            "dynamic_content_issues": [],
            "form_validation_problems": [],
            "interactive_elements": {},
            "actual_load_metrics": {},
            "popup_modals_detected": [],
            "rage_click_areas": [],
            "broken_features": [],
            "third_party_failures": [],
            "rendering_issues": [],
            "mobile_specific_issues": []
        }
        
        playwright = None
        browser = None
        
        try:
            playwright = await async_playwright().start()
            
            # Desktop analysis
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Analyze desktop version
            desktop_results = await self._analyze_viewport(
                browser, domain, "desktop",
                {"width": 1920, "height": 1080}
            )
            results.update(desktop_results)
            
            # Analyze mobile version
            mobile_results = await self._analyze_viewport(
                browser, domain, "mobile",
                {"width": 390, "height": 844},  # iPhone 14 Pro
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
            )
            
            # Add mobile-specific issues
            results["mobile_specific_issues"] = mobile_results.get("mobile_issues", [])
            
            # Cache for 1 hour (real-time data)
            await cache_result(cache_key, results, ttl=3600)
            
        except Exception as e:
            logger.error(f"Real-time browser analysis failed for {domain}", error=str(e))
            results["error"] = str(e)
        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
        
        return results
    
    async def _analyze_viewport(
        self, 
        browser: Browser, 
        domain: str, 
        viewport_type: str,
        viewport_size: Dict[str, int],
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze website in specific viewport (desktop/mobile)"""
        
        context_options = {"viewport": viewport_size}
        if user_agent:
            context_options["user_agent"] = user_agent
            
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        
        # Reset error collectors
        self.js_errors = []
        self.console_errors = []
        self.network_errors = []
        
        # Set up error listeners
        page.on("pageerror", lambda e: self.js_errors.append({
            "message": str(e),
            "viewport": viewport_type,
            "timestamp": datetime.now().isoformat()
        }))
        
        page.on("console", lambda msg: self._handle_console(msg, viewport_type))
        
        page.on("requestfailed", lambda request: self.network_errors.append({
            "url": request.url,
            "method": request.method,
            "failure": request.failure,
            "viewport": viewport_type
        }))
        
        results = {}
        
        try:
            # Navigate and wait for dynamic content
            start_time = datetime.now()
            response = await page.goto(
                f"https://{domain}",
                wait_until="networkidle",
                timeout=30000
            )
            load_time = (datetime.now() - start_time).total_seconds()
            
            # Wait a bit more for lazy-loaded content
            await page.wait_for_timeout(2000)
            
            # Collect timing metrics
            timing_metrics = await page.evaluate("""
                () => {
                    const perf = performance.getEntriesByType('navigation')[0];
                    return {
                        dns: perf.domainLookupEnd - perf.domainLookupStart,
                        tcp: perf.connectEnd - perf.connectStart,
                        request: perf.responseStart - perf.requestStart,
                        response: perf.responseEnd - perf.responseStart,
                        dom: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                        load: perf.loadEventEnd - perf.loadEventStart,
                        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                    };
                }
            """)
            
            results["actual_load_metrics"] = {
                "total_load_time": load_time,
                "timing_breakdown": timing_metrics,
                "viewport": viewport_type
            }
            
            # Detect JavaScript errors in execution
            results["javascript_errors"] = self.js_errors
            results["console_errors"] = self.console_errors
            results["network_failures"] = self.network_errors
            
            # Analyze forms with actual interaction
            form_issues = await self._analyze_form_validation(page, viewport_type)
            results["form_validation_problems"] = form_issues
            
            # Detect popups/modals
            popups = await self._detect_popups(page)
            results["popup_modals_detected"] = popups
            
            # Find broken interactive elements
            broken_elements = await self._find_broken_elements(page)
            results["broken_features"] = broken_elements
            
            # Detect dynamic content issues
            dynamic_issues = await self._check_dynamic_content(page)
            results["dynamic_content_issues"] = dynamic_issues
            
            # Check third-party script failures
            third_party_issues = await self._check_third_party_scripts(page)
            results["third_party_failures"] = third_party_issues
            
            # Mobile-specific checks
            if viewport_type == "mobile":
                mobile_issues = await self._check_mobile_issues(page)
                results["mobile_issues"] = mobile_issues
            
            # Detect rage click areas (elements that look clickable but aren't)
            rage_areas = await self._detect_rage_click_areas(page)
            results["rage_click_areas"] = rage_areas
            
        except Exception as e:
            logger.error(f"Error analyzing {viewport_type} viewport", error=str(e))
            results["error"] = str(e)
        finally:
            await context.close()
        
        return results
    
    def _handle_console(self, msg, viewport_type: str):
        """Handle console messages and filter for errors"""
        if msg.type in ["error", "warning"]:
            self.console_errors.append({
                "type": msg.type,
                "text": msg.text,
                "viewport": viewport_type,
                "location": msg.location
            })
    
    async def _analyze_form_validation(self, page: Page, viewport_type: str) -> List[Dict]:
        """Test actual form validation behavior"""
        issues = []
        
        try:
            # Find all forms
            forms = await page.query_selector_all("form")
            
            for i, form in enumerate(forms[:3]):  # Test first 3 forms
                form_issues = {}
                
                # Check email field validation
                email_field = await form.query_selector("input[type='email']")
                if email_field:
                    # Test with valid but unusual email
                    test_email = "test+tag@subdomain.example.co.uk"
                    await email_field.fill(test_email)
                    await page.wait_for_timeout(100)
                    
                    # Check if validation error appears
                    error_visible = await page.evaluate("""
                        (email) => {
                            const input = document.querySelector(email);
                            return !input.validity.valid || 
                                   document.querySelector('.error:visible') !== null;
                        }
                    """, "input[type='email']")
                    
                    if error_visible:
                        form_issues["rejects_valid_email"] = True
                        issues.append({
                            "form_index": i,
                            "issue": "Email validation too strict",
                            "detail": f"Rejects valid email format: {test_email}",
                            "viewport": viewport_type,
                            "impact": "Losing 5-10% of users with valid emails"
                        })
                
                # Check required fields
                required_fields = await form.query_selector_all("[required]")
                if len(required_fields) > 5:
                    issues.append({
                        "form_index": i,
                        "issue": "Too many required fields",
                        "count": len(required_fields),
                        "viewport": viewport_type,
                        "impact": f"Each field beyond 3 reduces conversion by ~7%"
                    })
                
                # Check for password complexity indicators
                password_field = await form.query_selector("input[type='password']")
                if password_field:
                    # Look for complexity requirements
                    page_text = await page.content()
                    if any(req in page_text.lower() for req in 
                           ["8 characters", "uppercase", "special character", "number"]):
                        issues.append({
                            "form_index": i,
                            "issue": "Complex password requirements",
                            "viewport": viewport_type,
                            "impact": "20% of users abandon due to password complexity"
                        })
        
        except Exception as e:
            logger.debug(f"Error analyzing forms: {e}")
        
        return issues
    
    async def _detect_popups(self, page: Page) -> List[Dict]:
        """Detect intrusive popups and modals"""
        popups = []
        
        try:
            # Wait for common popup triggers
            await page.wait_for_timeout(3000)
            
            # Check for modal overlays
            modals = await page.query_selector_all(
                "[class*='modal'], [class*='popup'], [class*='overlay'], " +
                "[id*='modal'], [id*='popup'], [role='dialog']"
            )
            
            for modal in modals:
                is_visible = await modal.is_visible()
                if is_visible:
                    modal_text = await modal.text_content()
                    popups.append({
                        "type": "modal",
                        "timing": "within_3_seconds",
                        "content_preview": modal_text[:100] if modal_text else "",
                        "impact": "40% of users leave due to immediate popups"
                    })
            
            # Check for cookie banners taking too much space
            cookie_elements = await page.query_selector_all(
                "[class*='cookie'], [id*='cookie'], [class*='consent'], [id*='gdpr']"
            )
            
            for cookie_el in cookie_elements:
                if await cookie_el.is_visible():
                    bbox = await cookie_el.bounding_box()
                    if bbox and bbox.get("height", 0) > 200:
                        popups.append({
                            "type": "cookie_banner",
                            "issue": "Oversized cookie banner",
                            "height": bbox["height"],
                            "impact": "Blocks content, increases bounce rate"
                        })
        
        except Exception as e:
            logger.debug(f"Error detecting popups: {e}")
        
        return popups
    
    async def _find_broken_elements(self, page: Page) -> List[Dict]:
        """Find broken interactive elements"""
        broken = []
        
        try:
            # Check all buttons and links
            buttons = await page.query_selector_all("button, a[href], [role='button']")
            
            for element in buttons[:20]:  # Check first 20 elements
                try:
                    # Check if element triggers JavaScript error when clicked
                    error_count_before = len(self.js_errors)
                    
                    # Try to click (with very short timeout)
                    await element.click(timeout=100, trial=True)
                    
                    error_count_after = len(self.js_errors)
                    
                    if error_count_after > error_count_before:
                        element_text = await element.text_content()
                        broken.append({
                            "element": element_text[:50] if element_text else "Unknown",
                            "type": "javascript_error_on_click",
                            "error": self.js_errors[-1]["message"] if self.js_errors else "Unknown error"
                        })
                except:
                    pass  # Element might not be clickable, that's ok
            
            # Check for 404 links
            links = await page.query_selector_all("a[href]")
            for link in links[:20]:  # Check first 20 links
                href = await link.get_attribute("href")
                if href and href.startswith("http"):
                    # This would need actual checking
                    # For now, we'll check in network_errors
                    if any(err["url"] == href for err in self.network_errors):
                        broken.append({
                            "type": "broken_link",
                            "url": href,
                            "impact": "Damages trust and SEO"
                        })
        
        except Exception as e:
            logger.debug(f"Error finding broken elements: {e}")
        
        return broken
    
    async def _check_dynamic_content(self, page: Page) -> List[Dict]:
        """Check for dynamic content loading issues"""
        issues = []
        
        try:
            # Check for infinite scroll issues
            initial_height = await page.evaluate("document.body.scrollHeight")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            new_height = await page.evaluate("document.body.scrollHeight")
            
            if new_height > initial_height * 3:
                issues.append({
                    "type": "infinite_scroll",
                    "issue": "Excessive content loading",
                    "impact": "Page becomes sluggish, high memory usage"
                })
            
            # Check for loading spinners still visible
            spinners = await page.query_selector_all(
                "[class*='spinner'], [class*='loader'], [class*='loading']"
            )
            
            for spinner in spinners:
                if await spinner.is_visible():
                    issues.append({
                        "type": "stuck_loader",
                        "issue": "Loading indicator still visible after page load",
                        "impact": "Users think page is broken"
                    })
            
            # Check for lazy loading failures
            images = await page.query_selector_all("img[loading='lazy']")
            for img in images[:10]:
                src = await img.get_attribute("src")
                if not src or src.startswith("data:"):
                    issues.append({
                        "type": "lazy_load_failure",
                        "issue": "Images not loading properly",
                        "impact": "Missing visual content"
                    })
                    break
        
        except Exception as e:
            logger.debug(f"Error checking dynamic content: {e}")
        
        return issues
    
    async def _check_third_party_scripts(self, page: Page) -> List[Dict]:
        """Identify failing third-party scripts"""
        failures = []
        
        # Group network errors by domain
        third_party_errors = {}
        for error in self.network_errors:
            url = error.get("url", "")
            if url and not url.startswith(f"https://{page.url}"):
                domain = url.split("/")[2] if "/" in url else url
                if domain not in third_party_errors:
                    third_party_errors[domain] = []
                third_party_errors[domain].append(error)
        
        # Identify critical failures
        critical_services = {
            "googleapis.com": "Google APIs",
            "stripe.com": "Payment processing",
            "googletagmanager.com": "Google Tag Manager",
            "google-analytics.com": "Google Analytics",
            "facebook.com": "Facebook SDK",
            "intercom.io": "Customer support chat",
            "hotjar.com": "User analytics",
            "segment.com": "Analytics platform"
        }
        
        for domain, errors in third_party_errors.items():
            for service_domain, service_name in critical_services.items():
                if service_domain in domain:
                    failures.append({
                        "service": service_name,
                        "domain": domain,
                        "error_count": len(errors),
                        "impact": f"{service_name} functionality broken",
                        "critical": service_name in ["Payment processing", "Customer support chat"]
                    })
        
        return failures
    
    async def _check_mobile_issues(self, page: Page) -> List[Dict]:
        """Check mobile-specific issues"""
        issues = []
        
        try:
            # Check for horizontal scroll
            has_horizontal_scroll = await page.evaluate("""
                () => document.documentElement.scrollWidth > document.documentElement.clientWidth
            """)
            
            if has_horizontal_scroll:
                issues.append({
                    "type": "horizontal_scroll",
                    "issue": "Page has horizontal scroll on mobile",
                    "impact": "Poor mobile experience, 30% higher bounce rate"
                })
            
            # Check for text too small
            small_text = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('p, span, div');
                    let tooSmall = 0;
                    for (let el of elements) {
                        const style = window.getComputedStyle(el);
                        if (parseInt(style.fontSize) < 12) {
                            tooSmall++;
                        }
                    }
                    return tooSmall;
                }
            """)
            
            if small_text > 10:
                issues.append({
                    "type": "small_text",
                    "issue": f"{small_text} elements with text too small for mobile",
                    "impact": "Text unreadable without zooming"
                })
            
            # Check for tap targets too close
            buttons = await page.query_selector_all("button, a, input")
            close_targets = []
            
            for i, button1 in enumerate(buttons[:10]):
                for button2 in buttons[i+1:i+2]:
                    box1 = await button1.bounding_box()
                    box2 = await button2.bounding_box()
                    
                    if box1 and box2:
                        distance = abs(box1["y"] - box2["y"])
                        if distance < 48:  # Google recommends 48px minimum
                            close_targets.append(distance)
            
            if close_targets:
                issues.append({
                    "type": "tap_targets",
                    "issue": f"{len(close_targets)} tap targets too close together",
                    "impact": "Users tap wrong elements, frustration"
                })
        
        except Exception as e:
            logger.debug(f"Error checking mobile issues: {e}")
        
        return issues
    
    async def _detect_rage_click_areas(self, page: Page) -> List[Dict]:
        """Detect elements that look clickable but aren't"""
        rage_areas = []
        
        try:
            # Find elements that look like they should be clickable
            potential_clickables = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    const clickable = [];
                    
                    for (let el of elements) {
                        const style = window.getComputedStyle(el);
                        const text = el.textContent || '';
                        
                        // Looks clickable if:
                        // - Has pointer cursor
                        // - Is underlined
                        // - Looks like a button (has border, background)
                        // - Contains action words
                        
                        const hasPointerCursor = style.cursor === 'pointer';
                        const isUnderlined = style.textDecoration.includes('underline');
                        const looksLikeButton = style.border !== 'none' || 
                                                style.backgroundColor !== 'rgba(0, 0, 0, 0)';
                        const hasActionWords = /click|learn|view|see|get|download|start/i.test(text);
                        
                        if ((hasPointerCursor || isUnderlined || 
                            (looksLikeButton && hasActionWords)) &&
                            !el.onclick && !el.href && el.tagName !== 'BUTTON' && 
                            el.tagName !== 'A' && el.tagName !== 'INPUT') {
                            clickable.push({
                                text: text.substring(0, 50),
                                tagName: el.tagName,
                                className: el.className
                            });
                        }
                    }
                    
                    return clickable.slice(0, 10);
                }
            """)
            
            for element in potential_clickables:
                rage_areas.append({
                    "element": element["text"],
                    "type": "non_clickable_with_clickable_style",
                    "impact": "User frustration, perceived broken functionality"
                })
        
        except Exception as e:
            logger.debug(f"Error detecting rage click areas: {e}")
        
        return rage_areas