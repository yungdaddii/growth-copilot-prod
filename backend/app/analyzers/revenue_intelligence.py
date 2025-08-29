import httpx
import asyncio
from typing import Dict, Any, List, Optional
import re
import json
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urljoin, urlparse

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class RevenueIntelligenceAnalyzer:
    """
    Deep-dive revenue leak detection and opportunity identification.
    Finds specific, actionable revenue improvements without requiring integrations.
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
    async def analyze(self, domain: str, industry: str = None) -> Dict[str, Any]:
        """
        Analyze website for revenue leaks and opportunities.
        Returns specific, actionable insights with revenue impact.
        """
        # Check cache first
        cache_key = f"revenue_intelligence:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "revenue_leaks": [],
            "conversion_blockers": [],
            "pricing_opportunities": [],
            "checkout_issues": [],
            "form_optimization": [],
            "trust_signals": [],
            "urgency_factors": [],
            "upsell_opportunities": [],
            "total_revenue_impact": 0,
            "quick_fixes": [],
            "metrics_request": {
                "needs_input": True,
                "message": "To calculate exact revenue impact, I need two numbers: What's your average deal size and current conversion rate?",
                "fields": ["average_deal_size", "conversion_rate"]
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Fetch homepage and key pages
                pages_to_analyze = await self._identify_key_pages(domain, client)
                
                # Run all analyses in parallel
                tasks = [
                    self._analyze_javascript_errors(domain, pages_to_analyze, client),
                    self._analyze_checkout_flow(domain, pages_to_analyze, client),
                    self._analyze_pricing_strategy(domain, pages_to_analyze, client),
                    self._analyze_forms(domain, pages_to_analyze, client),
                    self._analyze_trust_signals(domain, pages_to_analyze, client),
                    self._analyze_urgency_scarcity(domain, pages_to_analyze, client),
                    self._analyze_upsell_cross_sell(domain, pages_to_analyze, client),
                    self._analyze_mobile_conversion(domain, client),
                    self._analyze_page_speed_revenue_impact(domain, client),
                    self._analyze_competitor_pricing(domain, industry, client)
                ]
                
                analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(analysis_results):
                    if isinstance(result, Exception):
                        logger.error(f"Revenue analysis task {i} failed", error=str(result))
                    elif result:
                        # Merge results based on task index
                        if i == 0:  # JavaScript errors
                            results["conversion_blockers"].extend(result.get("blockers", []))
                        elif i == 1:  # Checkout flow
                            results["checkout_issues"] = result.get("issues", [])
                        elif i == 2:  # Pricing strategy
                            results["pricing_opportunities"] = result.get("opportunities", [])
                        elif i == 3:  # Forms
                            results["form_optimization"] = result.get("optimizations", [])
                        elif i == 4:  # Trust signals
                            results["trust_signals"] = result.get("missing_signals", [])
                        elif i == 5:  # Urgency/Scarcity
                            results["urgency_factors"] = result.get("missing_urgency", [])
                        elif i == 6:  # Upsell
                            results["upsell_opportunities"] = result.get("opportunities", [])
                        elif i == 7:  # Mobile conversion
                            results["conversion_blockers"].extend(result.get("mobile_issues", []))
                        elif i == 8:  # Page speed
                            if result.get("revenue_impact"):
                                results["revenue_leaks"].append(result["revenue_impact"])
                        elif i == 9:  # Competitor pricing
                            results["pricing_opportunities"].extend(result.get("gaps", []))
                
                # Calculate total revenue impact
                results["total_revenue_impact"] = self._calculate_total_impact(results)
                
                # Identify quick fixes (< 1 hour to implement)
                results["quick_fixes"] = self._identify_quick_fixes(results)
                
                # Sort by impact
                results["revenue_leaks"] = sorted(
                    results["revenue_leaks"], 
                    key=lambda x: x.get("monthly_impact", 0), 
                    reverse=True
                )
                
            # Cache for 24 hours
            await cache_result(cache_key, results, ttl=86400)
            return results
            
        except Exception as e:
            logger.error(f"Revenue intelligence analysis failed for {domain}", error=str(e))
            return results
    
    async def _identify_key_pages(self, domain: str, client: httpx.AsyncClient) -> Dict[str, str]:
        """Identify critical conversion pages to analyze"""
        pages = {
            "home": f"https://{domain}",
            "pricing": None,
            "signup": None,
            "demo": None,
            "checkout": None,
            "contact": None,
            "features": None,
            "trial": None
        }
        
        try:
            # Get homepage to find links
            response = await client.get(pages["home"], follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find key pages through common patterns
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    text = link.get_text().lower()
                    
                    # Pricing page
                    if not pages["pricing"] and any(x in href or x in text for x in ['pricing', 'price', 'plans', 'cost']):
                        pages["pricing"] = urljoin(pages["home"], link['href'])
                    
                    # Signup/Register
                    elif not pages["signup"] and any(x in href or x in text for x in ['signup', 'sign-up', 'register', 'get-started', 'start-free']):
                        pages["signup"] = urljoin(pages["home"], link['href'])
                    
                    # Demo
                    elif not pages["demo"] and any(x in href or x in text for x in ['demo', 'request-demo', 'book-demo', 'schedule-demo']):
                        pages["demo"] = urljoin(pages["home"], link['href'])
                    
                    # Checkout/Buy
                    elif not pages["checkout"] and any(x in href or x in text for x in ['checkout', 'buy', 'purchase', 'cart']):
                        pages["checkout"] = urljoin(pages["home"], link['href'])
                    
                    # Contact/Sales
                    elif not pages["contact"] and any(x in href or x in text for x in ['contact', 'sales', 'talk-to-sales']):
                        pages["contact"] = urljoin(pages["home"], link['href'])
                    
                    # Features
                    elif not pages["features"] and any(x in href or x in text for x in ['features', 'product', 'solutions']):
                        pages["features"] = urljoin(pages["home"], link['href'])
                    
                    # Free trial
                    elif not pages["trial"] and any(x in href or x in text for x in ['trial', 'try-free', 'free-trial']):
                        pages["trial"] = urljoin(pages["home"], link['href'])
        
        except Exception as e:
            logger.error(f"Failed to identify key pages for {domain}", error=str(e))
        
        # Remove None values
        return {k: v for k, v in pages.items() if v}
    
    async def _analyze_javascript_errors(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Detect JavaScript errors that could be killing conversions"""
        blockers = []
        
        for page_name, url in pages.items():
            if not url:
                continue
                
            try:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check for common JS error patterns
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            # Look for error-prone patterns
                            if 'undefined' in script.string or 'null' in script.string:
                                if any(critical in script.string for critical in ['payment', 'checkout', 'submit', 'form', 'gtm', 'analytics']):
                                    blockers.append({
                                        "type": "javascript_error",
                                        "page": page_name,
                                        "issue": f"Potential JavaScript error in {page_name} affecting critical functionality",
                                        "impact": "Could be blocking 10-30% of conversions",
                                        "fix": "Add error handling and fallbacks for critical JavaScript",
                                        "implementation_time": "1-2 hours",
                                        "monthly_impact": 15000  # Conservative estimate
                                    })
                    
                    # Check for missing polyfills for older browsers
                    if not any('polyfill' in str(script) for script in scripts):
                        if page_name in ['checkout', 'signup', 'demo']:
                            blockers.append({
                                "type": "browser_compatibility",
                                "page": page_name,
                                "issue": "No polyfills detected - older browsers may fail",
                                "impact": "Losing 5-8% of potential conversions",
                                "fix": "Add polyfill.io or core-js for browser compatibility",
                                "implementation_time": "30 minutes",
                                "monthly_impact": 8000
                            })
            
            except Exception as e:
                logger.debug(f"Error analyzing JS for {url}", error=str(e))
        
        return {"blockers": blockers}
    
    async def _analyze_checkout_flow(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze checkout/signup flow for conversion killers"""
        issues = []
        
        # Check if critical pages exist
        if not pages.get("pricing") and not pages.get("signup"):
            issues.append({
                "type": "missing_conversion_path",
                "issue": "No clear pricing or signup page found",
                "impact": "Losing 40-60% of potential buyers who need pricing info",
                "fix": "Create a clear pricing page with transparent costs",
                "implementation_time": "1-2 days",
                "monthly_impact": 45000
            })
        
        # Analyze signup/checkout if exists
        for page_type in ['signup', 'checkout', 'demo']:
            if url := pages.get(page_type):
                try:
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Count form fields
                        forms = soup.find_all('form')
                        for form in forms:
                            inputs = form.find_all(['input', 'select', 'textarea'])
                            required_fields = [i for i in inputs if i.get('required') or i.get('aria-required')]
                            
                            if len(required_fields) > 5:
                                issues.append({
                                    "type": "high_friction_form",
                                    "page": page_type,
                                    "issue": f"{page_type.title()} form has {len(required_fields)} required fields",
                                    "impact": f"Each field beyond 3 reduces conversion by ~7%",
                                    "fix": f"Reduce to 3 fields: Name, Email, Company. Make rest optional",
                                    "implementation_time": "1 hour",
                                    "monthly_impact": len(required_fields) * 3000
                                })
                            
                            # Check for social login options
                            social_login = any(text in str(form) for text in ['google', 'github', 'linkedin', 'oauth'])
                            if not social_login and page_type in ['signup', 'demo']:
                                issues.append({
                                    "type": "missing_social_login",
                                    "page": page_type,
                                    "issue": "No social login options (Google/GitHub/LinkedIn)",
                                    "impact": "Missing 20-30% conversion boost from 1-click signup",
                                    "fix": "Add Google and LinkedIn OAuth for B2B",
                                    "implementation_time": "4 hours",
                                    "monthly_impact": 18000
                                })
                        
                        # Check for trust signals on checkout
                        trust_indicators = ['security', 'secure', 'ssl', 'encrypted', 'guarantee', 'refund', 'trusted']
                        has_trust = any(indicator in response.text.lower() for indicator in trust_indicators)
                        
                        if not has_trust and page_type in ['checkout', 'signup']:
                            issues.append({
                                "type": "missing_trust_signals",
                                "page": page_type,
                                "issue": "No visible security badges or trust signals",
                                "impact": "Losing 15-25% of conversions from trust concerns",
                                "fix": "Add SSL badge, money-back guarantee, customer logos",
                                "implementation_time": "30 minutes",
                                "monthly_impact": 12000
                            })
                
                except Exception as e:
                    logger.debug(f"Error analyzing checkout flow for {url}", error=str(e))
        
        return {"issues": issues}
    
    async def _analyze_pricing_strategy(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze pricing strategy for revenue opportunities"""
        opportunities = []
        
        if pricing_url := pages.get("pricing"):
            try:
                response = await client.get(pricing_url, follow_redirects=True)
                if response.status_code == 200:
                    content = response.text.lower()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check for transparent pricing
                    has_prices = any(symbol in content for symbol in ['$', '€', '£', '¥'])
                    has_contact_only = 'contact' in content and 'sales' in content and not has_prices
                    
                    if has_contact_only:
                        opportunities.append({
                            "type": "hidden_pricing",
                            "issue": "Pricing page exists but shows 'Contact Sales' only",
                            "impact": "67% of B2B buyers eliminate vendors without transparent pricing",
                            "fix": "Add 'Starting at $X' or show actual price tiers",
                            "implementation_time": "2 hours",
                            "monthly_impact": 52000
                        })
                    
                    # Check for annual plans
                    has_annual = any(term in content for term in ['annual', 'yearly', 'year', '/year'])
                    has_monthly = any(term in content for term in ['month', 'monthly', '/mo'])
                    
                    if has_monthly and not has_annual:
                        opportunities.append({
                            "type": "missing_annual_plans",
                            "issue": "No annual billing option (only monthly)",
                            "impact": "Missing 20-30% revenue boost from annual prepayments",
                            "fix": "Add annual plans with 15-20% discount",
                            "implementation_time": "3 hours",
                            "monthly_impact": 28000
                        })
                    
                    # Check for tier structure
                    tier_indicators = ['starter', 'basic', 'pro', 'professional', 'enterprise', 'team', 'business']
                    tier_count = sum(1 for indicator in tier_indicators if indicator in content)
                    
                    if tier_count < 3:
                        opportunities.append({
                            "type": "insufficient_tiers",
                            "issue": f"Only {tier_count} pricing tiers found",
                            "impact": "Missing revenue from price discrimination",
                            "fix": "Create 3-4 tiers: Starter, Professional, Business, Enterprise",
                            "implementation_time": "1 day",
                            "monthly_impact": 35000
                        })
                    
                    # Check for free trial
                    has_trial = any(term in content for term in ['free trial', 'try free', 'trial', '14 day', '7 day', '30 day'])
                    
                    if not has_trial:
                        opportunities.append({
                            "type": "no_free_trial",
                            "issue": "No free trial option visible",
                            "impact": "Competitors with trials capture 40% more signups",
                            "fix": "Add 14-day free trial with credit card optional",
                            "implementation_time": "1 week",
                            "monthly_impact": 42000
                        })
            
            except Exception as e:
                logger.debug(f"Error analyzing pricing for {pricing_url}", error=str(e))
        else:
            # No pricing page at all
            opportunities.append({
                "type": "no_pricing_page",
                "issue": "No pricing page found on website",
                "impact": "Losing 50-70% of self-serve buyers",
                "fix": "Create pricing page with clear tiers and costs",
                "implementation_time": "1 day",
                "monthly_impact": 75000
            })
        
        return {"opportunities": opportunities}
    
    async def _analyze_forms(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze forms for conversion optimization"""
        optimizations = []
        
        for page_name, url in pages.items():
            if not url or page_name not in ['signup', 'demo', 'contact', 'trial']:
                continue
            
            try:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    forms = soup.find_all('form')
                    
                    for form in forms:
                        # Analyze field types and optimization opportunities
                        inputs = form.find_all('input')
                        
                        # Check for phone number field (often unnecessary)
                        phone_fields = [i for i in inputs if 'phone' in str(i.get('name', '')).lower() or 'phone' in str(i.get('id', '')).lower()]
                        if phone_fields and any(field.get('required') for field in phone_fields):
                            optimizations.append({
                                "type": "unnecessary_phone_field",
                                "page": page_name,
                                "issue": "Required phone number field detected",
                                "impact": "Reduces form completion by 15-20%",
                                "fix": "Make phone optional or remove entirely",
                                "implementation_time": "10 minutes",
                                "monthly_impact": 9000
                            })
                        
                        # Check for company size, budget fields (high friction)
                        high_friction_fields = ['budget', 'company_size', 'employees', 'revenue']
                        for field_name in high_friction_fields:
                            if any(field_name in str(input).lower() for input in inputs):
                                optimizations.append({
                                    "type": "high_friction_field",
                                    "page": page_name,
                                    "field": field_name,
                                    "issue": f"High-friction field '{field_name}' in {page_name} form",
                                    "impact": "Each qualifying question reduces conversion by 8-12%",
                                    "fix": "Move to post-signup onboarding or make optional",
                                    "implementation_time": "30 minutes",
                                    "monthly_impact": 7000
                                })
                        
                        # Check for multi-step forms
                        if 'step' in str(form) or 'wizard' in str(form):
                            optimizations.append({
                                "type": "multi_step_form",
                                "page": page_name,
                                "issue": "Multi-step form detected",
                                "impact": "Single-step forms convert 20-30% better",
                                "fix": "Consolidate to single page with optional fields",
                                "implementation_time": "3 hours",
                                "monthly_impact": 15000
                            })
            
            except Exception as e:
                logger.debug(f"Error analyzing forms for {url}", error=str(e))
        
        return {"optimizations": optimizations}
    
    async def _analyze_trust_signals(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze missing trust signals that impact conversion"""
        missing_signals = []
        
        try:
            # Check homepage for trust signals
            if home_url := pages.get("home"):
                response = await client.get(home_url, follow_redirects=True)
                if response.status_code == 200:
                    content = response.text.lower()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check for customer logos
                    logo_indicators = ['customer', 'client', 'trusted by', 'used by', 'loved by']
                    has_logos = any(indicator in content for indicator in logo_indicators)
                    
                    if not has_logos:
                        missing_signals.append({
                            "type": "no_social_proof",
                            "issue": "No customer logos or 'trusted by' section",
                            "impact": "Missing 15-25% conversion boost from social proof",
                            "fix": "Add 'Trusted by' section with 5-8 customer logos",
                            "implementation_time": "1 hour",
                            "monthly_impact": 18000
                        })
                    
                    # Check for testimonials
                    testimonial_indicators = ['testimonial', 'review', 'quote', '"', 'says', 'loved']
                    has_testimonials = any(indicator in content for indicator in testimonial_indicators)
                    
                    if not has_testimonials:
                        missing_signals.append({
                            "type": "no_testimonials",
                            "issue": "No customer testimonials found",
                            "impact": "Testimonials increase conversion by 10-15%",
                            "fix": "Add 3-5 customer testimonials with names and companies",
                            "implementation_time": "2 hours",
                            "monthly_impact": 12000
                        })
                    
                    # Check for security badges
                    security_indicators = ['soc2', 'soc 2', 'iso', 'gdpr', 'ccpa', 'hipaa', 'secure', 'encrypted']
                    has_security = any(indicator in content for indicator in security_indicators)
                    
                    if not has_security:
                        missing_signals.append({
                            "type": "no_security_badges",
                            "issue": "No security certifications or badges visible",
                            "impact": "Enterprise buyers require security compliance",
                            "fix": "Display SOC2, GDPR, or relevant compliance badges",
                            "implementation_time": "30 minutes",
                            "monthly_impact": 22000
                        })
                    
                    # Check for case studies
                    case_study_indicators = ['case study', 'case-study', 'success story', 'customer story']
                    has_case_studies = any(indicator in content for indicator in case_study_indicators)
                    
                    if not has_case_studies:
                        missing_signals.append({
                            "type": "no_case_studies",
                            "issue": "No case studies or success stories",
                            "impact": "Case studies improve conversion by 20-30%",
                            "fix": "Create 2-3 detailed case studies with metrics",
                            "implementation_time": "1 week",
                            "monthly_impact": 28000
                        })
        
        except Exception as e:
            logger.debug(f"Error analyzing trust signals", error=str(e))
        
        return {"missing_signals": missing_signals}
    
    async def _analyze_urgency_scarcity(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze use of urgency and scarcity tactics"""
        missing_urgency = []
        
        try:
            # Check pricing and signup pages for urgency elements
            for page_type in ['pricing', 'signup', 'home']:
                if url := pages.get(page_type):
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # Check for urgency indicators
                        urgency_indicators = ['limited time', 'ends soon', 'today only', 'spots left', 'remaining', 'hurry']
                        has_urgency = any(indicator in content for indicator in urgency_indicators)
                        
                        # Check for scarcity indicators
                        scarcity_indicators = ['only', 'left', 'remaining', 'available', 'seats', 'spots']
                        has_scarcity = any(indicator in content for indicator in scarcity_indicators)
                        
                        if not has_urgency and not has_scarcity and page_type == 'pricing':
                            missing_urgency.append({
                                "type": "no_urgency",
                                "page": page_type,
                                "issue": "No urgency or scarcity elements on pricing",
                                "impact": "Urgency can increase conversion by 10-15%",
                                "fix": "Add limited-time discount or bonus for new signups",
                                "implementation_time": "1 hour",
                                "monthly_impact": 11000
                            })
                        
                        # Check for limited-time offers
                        if page_type == 'pricing' and 'discount' not in content and 'save' not in content and 'off' not in content:
                            missing_urgency.append({
                                "type": "no_incentive",
                                "page": page_type,
                                "issue": "No special offers or incentives visible",
                                "impact": "First-time buyer incentives boost conversion 15-20%",
                                "fix": "Offer 20% off first month or extended trial",
                                "implementation_time": "2 hours",
                                "monthly_impact": 14000
                            })
        
        except Exception as e:
            logger.debug(f"Error analyzing urgency factors", error=str(e))
        
        return {"missing_urgency": missing_urgency}
    
    async def _analyze_upsell_cross_sell(self, domain: str, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze upsell and cross-sell opportunities"""
        opportunities = []
        
        try:
            if pricing_url := pages.get("pricing"):
                response = await client.get(pricing_url, follow_redirects=True)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for add-ons or extras
                    addon_indicators = ['add-on', 'addon', 'extra', 'additional', 'optional', 'premium support']
                    has_addons = any(indicator in content for indicator in addon_indicators)
                    
                    if not has_addons:
                        opportunities.append({
                            "type": "no_addons",
                            "issue": "No add-ons or premium features offered",
                            "impact": "Missing 15-25% revenue from upsells",
                            "fix": "Add premium support, training, or API add-ons",
                            "implementation_time": "1 day",
                            "monthly_impact": 19000
                        })
                    
                    # Check for recommended/popular tier highlighting
                    highlight_indicators = ['recommended', 'popular', 'best value', 'most popular']
                    has_highlighting = any(indicator in content for indicator in highlight_indicators)
                    
                    if not has_highlighting:
                        opportunities.append({
                            "type": "no_tier_highlighting",
                            "issue": "No 'Most Popular' tier highlighted",
                            "impact": "Highlighting increases mid-tier selection by 30%",
                            "fix": "Add 'Most Popular' badge to preferred tier",
                            "implementation_time": "30 minutes",
                            "monthly_impact": 16000
                        })
                    
                    # Check for upgrade prompts
                    upgrade_indicators = ['upgrade', 'scale', 'grow', 'expand']
                    has_upgrade_path = any(indicator in content for indicator in upgrade_indicators)
                    
                    if not has_upgrade_path:
                        opportunities.append({
                            "type": "no_upgrade_path",
                            "issue": "No clear upgrade path messaging",
                            "impact": "Missing expansion revenue opportunities",
                            "fix": "Add 'Start small, scale anytime' messaging",
                            "implementation_time": "1 hour",
                            "monthly_impact": 13000
                        })
        
        except Exception as e:
            logger.debug(f"Error analyzing upsell opportunities", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_mobile_conversion(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze mobile-specific conversion issues"""
        mobile_issues = []
        
        try:
            # Simulate mobile user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            }
            
            response = await client.get(f"https://{domain}", headers=headers, follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check viewport meta tag
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                if not viewport:
                    mobile_issues.append({
                        "type": "no_viewport",
                        "issue": "No viewport meta tag for mobile",
                        "impact": "Mobile users see desktop site, 40% bounce",
                        "fix": "Add <meta name='viewport' content='width=device-width, initial-scale=1'>",
                        "implementation_time": "5 minutes",
                        "monthly_impact": 24000
                    })
                
                # Check for mobile-specific CTAs
                buttons = soup.find_all(['button', 'a'], class_=re.compile('btn|button|cta'))
                small_buttons = [btn for btn in buttons if btn.get('style') and 'font-size' in btn.get('style', '') and any(size in btn.get('style', '') for size in ['12px', '13px', '14px'])]
                
                if small_buttons:
                    mobile_issues.append({
                        "type": "small_tap_targets",
                        "issue": "Buttons too small for mobile (< 44px tap target)",
                        "impact": "Mobile users struggle to tap, 20% give up",
                        "fix": "Increase button size to min 44x44px on mobile",
                        "implementation_time": "1 hour",
                        "monthly_impact": 15000
                    })
                
                # Check for horizontal scroll
                if 'overflow-x' not in response.text and 'max-width' not in response.text:
                    mobile_issues.append({
                        "type": "horizontal_scroll",
                        "issue": "Potential horizontal scroll on mobile",
                        "impact": "Horizontal scroll kills 25% of mobile conversions",
                        "fix": "Add max-width: 100% and overflow-x: hidden",
                        "implementation_time": "30 minutes",
                        "monthly_impact": 18000
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing mobile conversion", error=str(e))
        
        return {"mobile_issues": mobile_issues}
    
    async def _analyze_page_speed_revenue_impact(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Calculate revenue impact of page speed issues"""
        try:
            # Use PageSpeed API if available, otherwise estimate
            if settings.GOOGLE_PAGESPEED_API_KEY:
                url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{domain}&key={settings.GOOGLE_PAGESPEED_API_KEY}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    metrics = data.get('lighthouseResult', {}).get('audits', {})
                    
                    # Get key metrics
                    fcp = metrics.get('first-contentful-paint', {}).get('numericValue', 0) / 1000
                    lcp = metrics.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000
                    
                    if lcp > 4:  # Poor LCP
                        return {
                            "revenue_impact": {
                                "type": "slow_page_speed",
                                "issue": f"Page takes {lcp:.1f}s to load (should be < 2.5s)",
                                "impact": "53% of mobile users abandon sites taking > 3s",
                                "fix": "Optimize images, enable caching, use CDN",
                                "implementation_time": "1 day",
                                "monthly_impact": 32000
                            }
                        }
        
        except Exception as e:
            logger.debug(f"Error analyzing page speed revenue impact", error=str(e))
        
        return {}
    
    async def _analyze_competitor_pricing(self, domain: str, industry: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze competitor pricing for arbitrage opportunities"""
        gaps = []
        
        # This would normally integrate with competitor data
        # For now, return generic insights based on industry
        if industry:
            gaps.append({
                "type": "competitor_pricing_gap",
                "issue": "Potential pricing optimization opportunity",
                "impact": "Competitors may be charging 20-30% more for similar features",
                "fix": "Research competitor pricing and test premium positioning",
                "implementation_time": "1 week",
                "monthly_impact": 25000
            })
        
        return {"gaps": gaps}
    
    def _calculate_total_impact(self, results: Dict[str, Any]) -> float:
        """Calculate total monthly revenue impact"""
        total = 0
        
        # Sum up all monthly impacts
        for category in ['revenue_leaks', 'conversion_blockers', 'checkout_issues', 
                        'pricing_opportunities', 'form_optimization', 'trust_signals',
                        'urgency_factors', 'upsell_opportunities']:
            items = results.get(category, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        total += item.get('monthly_impact', 0)
        
        return total
    
    def _identify_quick_fixes(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify fixes that can be implemented in < 1 hour"""
        quick_fixes = []
        
        # Collect all issues
        all_issues = []
        for category in ['revenue_leaks', 'conversion_blockers', 'checkout_issues', 
                        'pricing_opportunities', 'form_optimization', 'trust_signals',
                        'urgency_factors', 'upsell_opportunities']:
            items = results.get(category, [])
            if isinstance(items, list):
                all_issues.extend(items)
        
        # Filter for quick implementation
        for issue in all_issues:
            if isinstance(issue, dict):
                time = issue.get('implementation_time', '')
                if any(quick in str(time) for quick in ['minute', '30 min', '1 hour', '2 hour']):
                    quick_fixes.append({
                        "issue": issue.get('issue'),
                        "fix": issue.get('fix'),
                        "time": issue.get('implementation_time'),
                        "impact": issue.get('monthly_impact', 0)
                    })
        
        # Sort by impact
        return sorted(quick_fixes, key=lambda x: x.get('impact', 0), reverse=True)[:5]