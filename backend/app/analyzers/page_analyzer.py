import httpx
import re
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urljoin, urlparse
import asyncio

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class PageAnalyzer:
    """
    Deep analysis of specific critical pages on a website.
    Focuses on conversion-critical pages: landing, pricing, demo, signup.
    """
    
    # Critical pages to analyze
    CRITICAL_PAGES = {
        "pricing": ["pricing", "plans", "cost", "price", "subscribe"],
        "demo": ["demo", "trial", "try", "get-started", "start", "signup", "sign-up"],
        "about": ["about", "company", "team", "story"],
        "features": ["features", "product", "solutions", "platform"],
        "contact": ["contact", "talk", "sales", "support"],
        "blog": ["blog", "resources", "learn", "articles", "news"]
    }
    
    def __init__(self):
        self.client = None
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Comprehensive page-specific analysis"""
        cache_key = f"page_analysis:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "pages_found": [],
            "page_analysis": {},
            "conversion_paths": [],
            "critical_issues": [],
            "opportunities": [],
            "form_analysis": {},
            "cta_analysis": {},
            "trust_signals": {},
            "page_recommendations": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                self.client = client
                
                # First, discover critical pages
                pages = await self._discover_pages(domain)
                results["pages_found"] = pages
                
                # Analyze each critical page in parallel
                tasks = []
                for page_type, url in pages.items():
                    if url:
                        tasks.append(self._analyze_page(url, page_type, domain))
                
                if tasks:
                    page_analyses = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for analysis in page_analyses:
                        if isinstance(analysis, dict):
                            page_type = analysis.get("page_type")
                            if page_type:
                                results["page_analysis"][page_type] = analysis
                                
                                # Aggregate critical issues
                                if analysis.get("issues"):
                                    results["critical_issues"].extend(analysis["issues"])
                                
                                # Aggregate opportunities
                                if analysis.get("opportunities"):
                                    results["opportunities"].extend(analysis["opportunities"])
                
                # Analyze conversion paths
                results["conversion_paths"] = await self._analyze_conversion_paths(pages, domain)
                
                # Generate page-specific recommendations
                results["page_recommendations"] = self._generate_recommendations(results)
                
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"Page analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _discover_pages(self, domain: str) -> Dict[str, Optional[str]]:
        """Discover critical pages on the website"""
        pages = {}
        
        try:
            # Get homepage first
            response = await self.client.get(f"https://{domain}")
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for page_type, keywords in self.CRITICAL_PAGES.items():
                found_url = None
                
                # Check each link for keywords
                for link in links:
                    href = link.get('href', '').lower()
                    text = link.get_text(strip=True).lower()
                    
                    # Check if any keyword matches
                    for keyword in keywords:
                        if keyword in href or keyword in text:
                            # Construct full URL
                            if href.startswith('http'):
                                found_url = href
                            elif href.startswith('/'):
                                found_url = f"https://{domain}{href}"
                            else:
                                found_url = urljoin(f"https://{domain}", href)
                            break
                    
                    if found_url:
                        break
                
                pages[page_type] = found_url
                
                # Special handling for pricing - also check footer
                if page_type == "pricing" and not found_url:
                    footer = soup.find(['footer', 'div'], class_=re.compile(r'footer', re.I))
                    if footer:
                        footer_links = footer.find_all('a', href=True)
                        for link in footer_links:
                            if 'pricing' in link.get('href', '').lower():
                                href = link.get('href')
                                if href.startswith('http'):
                                    pages["pricing"] = href
                                else:
                                    pages["pricing"] = f"https://{domain}{href}"
                                break
            
            # If critical pages not found in links, try common URL patterns
            # This catches pages that exist but aren't linked
            if not pages.get("pricing"):
                # Try common pricing URLs
                for pattern in ["/pricing", "/plans", "/price", "/pricing-plans"]:
                    try:
                        test_url = f"https://{domain}{pattern}"
                        test_response = await self.client.head(test_url, follow_redirects=True)
                        if test_response.status_code == 200:
                            pages["pricing"] = test_url
                            break
                    except:
                        continue
            
            if not pages.get("demo"):
                # Try common demo/trial URLs
                for pattern in ["/demo", "/trial", "/get-started", "/free-trial", "/try", "/start"]:
                    try:
                        test_url = f"https://{domain}{pattern}"
                        test_response = await self.client.head(test_url, follow_redirects=True)
                        if test_response.status_code == 200:
                            pages["demo"] = test_url
                            break
                    except:
                        continue
            
        except Exception as e:
            logger.error(f"Failed to discover pages for {domain}", error=str(e))
        
        return pages
    
    async def _analyze_page(self, url: str, page_type: str, domain: str) -> Dict[str, Any]:
        """Deep analysis of a specific page"""
        analysis = {
            "page_type": page_type,
            "url": url,
            "issues": [],
            "opportunities": [],
            "metrics": {}
        }
        
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            content = response.text.lower()
            
            # Page-specific analysis based on type
            if page_type == "pricing":
                analysis.update(self._analyze_pricing_page(soup, content))
            elif page_type == "demo":
                analysis.update(self._analyze_demo_page(soup, content))
            elif page_type == "features":
                analysis.update(self._analyze_features_page(soup, content))
            elif page_type == "about":
                analysis.update(self._analyze_about_page(soup, content))
            
            # Common analysis for all pages
            analysis["forms"] = self._analyze_forms(soup)
            analysis["ctas"] = self._analyze_ctas(soup)
            analysis["trust_signals"] = self._analyze_trust_signals(soup, content)
            analysis["load_size"] = len(response.text)
            analysis["images"] = len(soup.find_all('img'))
            analysis["videos"] = len(soup.find_all(['video', 'iframe']))
            
            # Check for A/B testing
            analysis["has_ab_testing"] = self._detect_ab_testing(content)
            
            # Mobile responsiveness check
            analysis["mobile_friendly"] = self._check_mobile_friendly(soup)
            
        except Exception as e:
            logger.error(f"Failed to analyze page {url}", error=str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_pricing_page(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Specific analysis for pricing pages"""
        analysis = {
            "pricing_analysis": {},
            "issues": [],
            "opportunities": []
        }
        
        pricing = analysis["pricing_analysis"]
        
        # Check for pricing tiers
        tier_indicators = ['starter', 'pro', 'enterprise', 'basic', 'premium', 'free']
        tiers_found = sum(1 for tier in tier_indicators if tier in content)
        pricing["tier_count"] = tiers_found
        
        # Check for pricing display
        price_patterns = [r'\$\d+', r'usd', r'eur', r'pricing', r'/mo', r'/month', r'/year']
        has_prices = any(re.search(pattern, content) for pattern in price_patterns)
        pricing["shows_prices"] = has_prices
        
        # Check for free trial
        pricing["has_free_trial"] = 'free trial' in content or 'try free' in content
        
        # Check for money-back guarantee
        pricing["has_guarantee"] = 'guarantee' in content or 'refund' in content
        
        # Check for feature comparison
        tables = soup.find_all('table')
        pricing["has_comparison_table"] = len(tables) > 0
        
        # Check for FAQ section
        pricing["has_faq"] = 'faq' in content or 'frequently asked' in content
        
        # Generate issues and opportunities
        if not has_prices:
            analysis["issues"].append({
                "severity": "high",
                "issue": "No transparent pricing displayed",
                "impact": "67% of B2B buyers eliminate vendors without pricing",
                "fix": "Display starting prices or price ranges"
            })
        
        if tiers_found < 3:
            analysis["opportunities"].append({
                "type": "pricing_optimization",
                "opportunity": "Add more pricing tiers",
                "impact": "Capture different customer segments",
                "effort": "medium"
            })
        
        if not pricing["has_free_trial"]:
            analysis["issues"].append({
                "severity": "high",
                "issue": "No free trial option visible",
                "impact": "Free trials increase conversion by 2.5x",
                "fix": "Add prominent free trial CTA"
            })
        
        if not pricing["has_comparison_table"]:
            analysis["opportunities"].append({
                "type": "ux_improvement",
                "opportunity": "Add feature comparison table",
                "impact": "Help buyers understand tier differences",
                "effort": "low"
            })
        
        return analysis
    
    def _analyze_demo_page(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Specific analysis for demo/signup pages"""
        analysis = {
            "demo_analysis": {},
            "issues": [],
            "opportunities": []
        }
        
        demo = analysis["demo_analysis"]
        
        # Find forms
        forms = soup.find_all('form')
        if forms:
            main_form = forms[0]
            
            # Count form fields
            inputs = main_form.find_all(['input', 'select', 'textarea'])
            visible_inputs = [i for i in inputs if i.get('type') != 'hidden']
            demo["field_count"] = len(visible_inputs)
            
            # Check for required fields
            required_fields = [i for i in visible_inputs if i.get('required')]
            demo["required_fields"] = len(required_fields)
            
            # Check field types
            field_types = []
            for inp in visible_inputs:
                field_name = inp.get('name', '') or inp.get('id', '')
                field_type = inp.get('type', 'text')
                placeholder = inp.get('placeholder', '')
                
                # Identify field purpose
                field_lower = f"{field_name} {placeholder}".lower()
                if 'email' in field_lower:
                    field_types.append('email')
                elif 'phone' in field_lower or 'tel' in field_lower:
                    field_types.append('phone')
                elif 'company' in field_lower:
                    field_types.append('company')
                elif 'name' in field_lower:
                    field_types.append('name')
                elif 'password' in field_lower:
                    field_types.append('password')
                else:
                    field_types.append('other')
            
            demo["field_types"] = field_types
            
            # Check for social login
            demo["has_social_login"] = 'google' in content or 'linkedin' in content or 'github' in content
            
            # Issues and opportunities
            if demo["field_count"] > 5:
                analysis["issues"].append({
                    "severity": "critical",
                    "issue": f"Form has {demo['field_count']} fields (optimal is 3-4)",
                    "impact": f"Each extra field reduces conversion by ~7%",
                    "fix": "Remove non-essential fields, make others optional"
                })
            
            if 'phone' in field_types and 'phone' in [f for i, f in enumerate(field_types) if i < len(required_fields)]:
                analysis["issues"].append({
                    "severity": "high",
                    "issue": "Phone number is required",
                    "impact": "Reduces form completion by 37%",
                    "fix": "Make phone number optional"
                })
            
            if not demo["has_social_login"]:
                analysis["opportunities"].append({
                    "type": "conversion_optimization",
                    "opportunity": "Add social login options",
                    "impact": "Reduce friction for 40% of users",
                    "effort": "medium"
                })
        else:
            analysis["issues"].append({
                "severity": "critical",
                "issue": "No form found on demo/signup page",
                "impact": "Cannot capture leads",
                "fix": "Add clear signup or demo request form"
            })
        
        # Check for trust signals
        if 'testimonial' not in content and 'customer' not in content:
            analysis["opportunities"].append({
                "type": "trust_building",
                "opportunity": "Add customer testimonials near form",
                "impact": "Increase form completion by 18%",
                "effort": "low"
            })
        
        return analysis
    
    def _analyze_features_page(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Specific analysis for features/product pages"""
        analysis = {
            "features_analysis": {},
            "issues": [],
            "opportunities": []
        }
        
        features = analysis["features_analysis"]
        
        # Check for feature list
        feature_lists = soup.find_all(['ul', 'ol'])
        features["feature_lists"] = len(feature_lists)
        
        # Check for screenshots/demos
        images = soup.find_all('img')
        features["screenshots"] = len([img for img in images if img.get('alt', '').lower() in ['screenshot', 'demo', 'feature', 'product']])
        
        # Check for video demos
        features["has_video"] = bool(soup.find_all(['video', 'iframe']))
        
        # Check for interactive demos
        features["has_interactive_demo"] = 'demo' in content and ('try' in content or 'interactive' in content)
        
        # Check for use cases
        features["has_use_cases"] = 'use case' in content or 'example' in content
        
        # Issues and opportunities
        if not features["has_video"]:
            analysis["opportunities"].append({
                "type": "engagement",
                "opportunity": "Add product demo video",
                "impact": "Increase time on page by 88%",
                "effort": "medium"
            })
        
        if features["screenshots"] < 3:
            analysis["issues"].append({
                "severity": "medium",
                "issue": "Limited product screenshots",
                "impact": "Users can't visualize the product",
                "fix": "Add 5-8 annotated screenshots showing key features"
            })
        
        if not features["has_use_cases"]:
            analysis["opportunities"].append({
                "type": "content",
                "opportunity": "Add specific use case examples",
                "impact": "Help visitors see themselves using the product",
                "effort": "low"
            })
        
        return analysis
    
    def _analyze_about_page(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Specific analysis for about/company pages"""
        analysis = {
            "about_analysis": {},
            "issues": [],
            "opportunities": []
        }
        
        about = analysis["about_analysis"]
        
        # Check for team info
        about["has_team"] = 'team' in content or 'founder' in content
        
        # Check for company story
        about["has_story"] = 'story' in content or 'founded' in content or 'mission' in content
        
        # Check for social proof
        about["has_investors"] = 'investor' in content or 'backed by' in content
        about["has_customers"] = 'customer' in content or 'client' in content
        
        # Check for values/culture
        about["has_values"] = 'value' in content or 'culture' in content
        
        if not about["has_team"]:
            analysis["opportunities"].append({
                "type": "trust_building",
                "opportunity": "Add team section with photos",
                "impact": "Build trust with potential customers",
                "effort": "low"
            })
        
        return analysis
    
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analyze all forms on a page"""
        forms_analysis = []
        
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                "fields": [],
                "action": form.get('action', ''),
                "method": form.get('method', 'get').upper()
            }
            
            # Analyze each field
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                if inp.get('type') != 'hidden':
                    field = {
                        "type": inp.get('type', 'text'),
                        "name": inp.get('name', ''),
                        "required": inp.get('required') is not None,
                        "placeholder": inp.get('placeholder', '')
                    }
                    form_data["fields"].append(field)
            
            form_data["field_count"] = len(form_data["fields"])
            form_data["required_count"] = sum(1 for f in form_data["fields"] if f["required"])
            
            forms_analysis.append(form_data)
        
        return forms_analysis
    
    def _analyze_ctas(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze call-to-action buttons"""
        cta_analysis = {
            "total_ctas": 0,
            "primary_ctas": [],
            "cta_clarity": "weak"
        }
        
        # Find all buttons and links that look like CTAs
        buttons = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta', re.I))
        
        cta_texts = []
        for btn in buttons:
            text = btn.get_text(strip=True)
            if text and len(text) < 50:  # Reasonable CTA length
                cta_texts.append(text)
        
        cta_analysis["total_ctas"] = len(cta_texts)
        cta_analysis["primary_ctas"] = cta_texts[:5]  # Top 5 CTAs
        
        # Evaluate CTA clarity
        strong_cta_words = ['start', 'try', 'get', 'demo', 'free', 'now', 'today']
        weak_cta_words = ['submit', 'click', 'learn more', 'continue']
        
        if any(word in ' '.join(cta_texts).lower() for word in strong_cta_words):
            cta_analysis["cta_clarity"] = "strong"
        elif any(word in ' '.join(cta_texts).lower() for word in weak_cta_words):
            cta_analysis["cta_clarity"] = "weak"
        else:
            cta_analysis["cta_clarity"] = "moderate"
        
        return cta_analysis
    
    def _analyze_trust_signals(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Analyze trust signals on the page"""
        trust = {
            "has_testimonials": False,
            "has_logos": False,
            "has_security_badges": False,
            "has_certifications": False,
            "has_reviews": False,
            "has_case_studies": False,
            "trust_score": 0
        }
        
        # Check for testimonials
        if 'testimonial' in content or 'what our customers say' in content:
            trust["has_testimonials"] = True
            trust["trust_score"] += 20
        
        # Check for customer logos
        if 'customer' in content and ('logo' in content or soup.find_all('img', alt=re.compile(r'customer|client|logo', re.I))):
            trust["has_logos"] = True
            trust["trust_score"] += 20
        
        # Check for security badges
        security_terms = ['ssl', 'secure', 'encrypted', 'soc2', 'iso', 'gdpr', 'compliant']
        if any(term in content for term in security_terms):
            trust["has_security_badges"] = True
            trust["trust_score"] += 15
        
        # Check for certifications
        cert_terms = ['certified', 'accredited', 'award', 'recognized']
        if any(term in content for term in cert_terms):
            trust["has_certifications"] = True
            trust["trust_score"] += 15
        
        # Check for reviews
        if 'review' in content or 'rating' in content or '★' in content:
            trust["has_reviews"] = True
            trust["trust_score"] += 20
        
        # Check for case studies
        if 'case study' in content or 'case studies' in content or 'success story' in content:
            trust["has_case_studies"] = True
            trust["trust_score"] += 10
        
        return trust
    
    def _detect_ab_testing(self, content: str) -> bool:
        """Detect if the page has A/B testing"""
        ab_indicators = ['optimizely', 'google optimize', 'vwo', 'ab tasty', 'split.io', 'variant']
        return any(indicator in content for indicator in ab_indicators)
    
    def _check_mobile_friendly(self, soup: BeautifulSoup) -> bool:
        """Check if page appears mobile-friendly"""
        # Check for viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport and 'width=device-width' in viewport.get('content', ''):
            return True
        return False
    
    async def _analyze_conversion_paths(self, pages: Dict[str, str], domain: str) -> List[Dict[str, Any]]:
        """Analyze conversion paths between pages"""
        paths = []
        
        # Common conversion paths to check
        common_paths = [
            {"from": "homepage", "to": "pricing", "path_type": "evaluation"},
            {"from": "homepage", "to": "demo", "path_type": "trial"},
            {"from": "features", "to": "pricing", "path_type": "evaluation"},
            {"from": "pricing", "to": "demo", "path_type": "conversion"},
            {"from": "blog", "to": "demo", "path_type": "nurture"}
        ]
        
        for path in common_paths:
            from_page = path["from"]
            to_page = path["to"]
            
            # Check if both pages exist
            from_url = pages.get(from_page) or (f"https://{domain}" if from_page == "homepage" else None)
            to_url = pages.get(to_page)
            
            if from_url and to_url:
                path_analysis = {
                    "from": from_page,
                    "to": to_page,
                    "type": path["path_type"],
                    "exists": True,
                    "optimized": False
                }
                
                # Check if there's a clear path (link from one to the other)
                # This would require checking if from_page has links to to_page
                # For now, we'll mark as existing if both pages exist
                
                paths.append(path_analysis)
        
        return paths
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate page-specific recommendations"""
        recommendations = []
        
        # Analyze pricing page issues
        if "pricing" in results["page_analysis"]:
            pricing = results["page_analysis"]["pricing"]
            
            if not pricing.get("pricing_analysis", {}).get("shows_prices"):
                recommendations.append({
                    "priority": "critical",
                    "page": "pricing",
                    "issue": "No transparent pricing",
                    "fix": "Add starting prices or price ranges",
                    "impact": "Stop losing 67% of price-conscious buyers",
                    "effort": "1 hour"
                })
            
            if not pricing.get("pricing_analysis", {}).get("has_free_trial"):
                recommendations.append({
                    "priority": "high",
                    "page": "pricing",
                    "issue": "No free trial option",
                    "fix": "Add prominent 'Start Free Trial' CTA",
                    "impact": "2.5x higher conversion than demo-only",
                    "effort": "2 hours"
                })
        
        # Analyze demo page issues
        if "demo" in results["page_analysis"]:
            demo = results["page_analysis"]["demo"]
            demo_analysis = demo.get("demo_analysis", {})
            
            if demo_analysis.get("field_count", 0) > 5:
                recommendations.append({
                    "priority": "critical",
                    "page": "demo",
                    "issue": f"Form has {demo_analysis['field_count']} fields",
                    "fix": "Reduce to 3-4 fields (email, name, company)",
                    "impact": f"Increase conversions by {(demo_analysis['field_count'] - 4) * 7}%",
                    "effort": "30 minutes"
                })
            
            if 'phone' in demo_analysis.get("field_types", []):
                recommendations.append({
                    "priority": "high",
                    "page": "demo",
                    "issue": "Phone number field in form",
                    "fix": "Remove or make optional",
                    "impact": "37% more form completions",
                    "effort": "15 minutes"
                })
        
        # Check for missing critical pages
        if not results["pages_found"].get("pricing"):
            recommendations.append({
                "priority": "critical",
                "page": "site",
                "issue": "No pricing page found",
                "fix": "Create dedicated pricing page",
                "impact": "Essential for buyer evaluation",
                "effort": "1 day"
            })
        
        # Trust signal recommendations
        for page_type, analysis in results["page_analysis"].items():
            trust = analysis.get("trust_signals", {})
            if trust.get("trust_score", 0) < 50:
                recommendations.append({
                    "priority": "high",
                    "page": page_type,
                    "issue": "Weak trust signals",
                    "fix": "Add testimonials, logos, or security badges",
                    "impact": "18% higher conversion with social proof",
                    "effort": "2 hours"
                })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return recommendations[:10]  # Top 10 recommendations