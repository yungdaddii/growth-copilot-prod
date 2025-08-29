"""
Advanced form analyzer that detects specific conversion killers
Goes beyond basic field counting to identify actual friction points
"""

import httpx
from typing import Dict, Any, List, Optional
import re
import structlog
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class FormConversionKillerAnalyzer:
    """
    Detects specific form issues that kill conversions:
    - Password complexity requirements
    - Email validation that's too strict
    - Phone format restrictions
    - Unnecessary required fields
    - Multi-step form friction
    - Missing conveniences (remember me, social login)
    - No guest checkout options
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(20.0, connect=10.0)
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Deep analysis of forms to find conversion killers
        """
        cache_key = f"form_conversion_killers:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "forms_analyzed": 0,
            "total_conversion_impact": 0,
            "critical_issues": [],
            "form_specific_issues": [],
            "quick_fixes": [],
            "competitor_advantages": [],
            "estimated_revenue_loss": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get main pages with forms
                pages_to_check = await self._get_form_pages(domain, client)
                
                for page_name, url in pages_to_check.items():
                    if url:
                        page_issues = await self._analyze_page_forms(
                            url, page_name, client
                        )
                        if page_issues:
                            results["form_specific_issues"].extend(page_issues)
                            results["forms_analyzed"] += page_issues[0].get("forms_on_page", 1)
                
                # Calculate total impact
                results["total_conversion_impact"] = self._calculate_total_impact(
                    results["form_specific_issues"]
                )
                
                # Identify critical issues
                results["critical_issues"] = self._identify_critical_issues(
                    results["form_specific_issues"]
                )
                
                # Generate quick fixes
                results["quick_fixes"] = self._generate_quick_fixes(
                    results["form_specific_issues"]
                )
                
                # Compare to best practices
                results["competitor_advantages"] = self._compare_to_best_practices(
                    results["form_specific_issues"]
                )
                
                # Estimate revenue loss
                results["estimated_revenue_loss"] = self._estimate_revenue_loss(
                    results["total_conversion_impact"]
                )
                
                # Cache for 12 hours
                await cache_result(cache_key, results, ttl=43200)
        
        except Exception as e:
            logger.error(f"Form conversion killer analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _get_form_pages(self, domain: str, client: httpx.AsyncClient) -> Dict[str, str]:
        """Identify pages likely to have forms"""
        pages = {
            "signup": None,
            "register": None,
            "demo": None,
            "trial": None,
            "contact": None,
            "checkout": None,
            "login": None,
            "get-started": None,
            "quote": None,
            "consultation": None
        }
        
        try:
            # Get homepage
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find links to form pages
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    text = link.get_text().lower()
                    
                    for page_type in pages.keys():
                        if page_type in href or page_type in text:
                            pages[page_type] = urljoin(f"https://{domain}", link['href'])
                            break
                
                # Also check for forms on homepage
                if soup.find('form'):
                    pages["homepage"] = f"https://{domain}"
        
        except Exception as e:
            logger.debug(f"Error getting form pages for {domain}: {e}")
        
        return {k: v for k, v in pages.items() if v}
    
    async def _analyze_page_forms(
        self, url: str, page_name: str, client: httpx.AsyncClient
    ) -> List[Dict[str, Any]]:
        """Analyze all forms on a specific page"""
        issues = []
        
        try:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_content = response.text.lower()
                
                forms = soup.find_all('form')
                
                for form_index, form in enumerate(forms):
                    form_issues = {
                        "page": page_name,
                        "url": url,
                        "form_index": form_index,
                        "forms_on_page": len(forms),
                        "issues": [],
                        "conversion_impact": 0,
                        "friction_score": 0
                    }
                    
                    # Analyze each aspect of the form
                    
                    # 1. Password complexity
                    password_issues = self._check_password_complexity(form, page_content)
                    if password_issues:
                        form_issues["issues"].extend(password_issues)
                        form_issues["friction_score"] += len(password_issues) * 20
                    
                    # 2. Email validation
                    email_issues = self._check_email_validation(form, soup)
                    if email_issues:
                        form_issues["issues"].extend(email_issues)
                        form_issues["friction_score"] += len(email_issues) * 15
                    
                    # 3. Phone number requirements
                    phone_issues = self._check_phone_requirements(form)
                    if phone_issues:
                        form_issues["issues"].extend(phone_issues)
                        form_issues["friction_score"] += len(phone_issues) * 15
                    
                    # 4. Unnecessary required fields
                    field_issues = self._check_required_fields(form, page_name)
                    if field_issues:
                        form_issues["issues"].extend(field_issues)
                        form_issues["friction_score"] += len(field_issues) * 10
                    
                    # 5. Multi-step form analysis
                    multistep_issues = self._check_multistep_forms(form, soup)
                    if multistep_issues:
                        form_issues["issues"].extend(multistep_issues)
                        form_issues["friction_score"] += len(multistep_issues) * 25
                    
                    # 6. Missing conveniences
                    convenience_issues = self._check_conveniences(form, soup, page_name)
                    if convenience_issues:
                        form_issues["issues"].extend(convenience_issues)
                        form_issues["friction_score"] += len(convenience_issues) * 10
                    
                    # 7. Guest checkout (for checkout/purchase forms)
                    if page_name in ["checkout", "purchase", "buy"]:
                        guest_issues = self._check_guest_checkout(soup, page_content)
                        if guest_issues:
                            form_issues["issues"].extend(guest_issues)
                            form_issues["friction_score"] += len(guest_issues) * 30
                    
                    # 8. Field autocomplete
                    autocomplete_issues = self._check_autocomplete(form)
                    if autocomplete_issues:
                        form_issues["issues"].extend(autocomplete_issues)
                        form_issues["friction_score"] += len(autocomplete_issues) * 5
                    
                    # Calculate conversion impact
                    form_issues["conversion_impact"] = self._calculate_form_impact(
                        form_issues["friction_score"],
                        page_name
                    )
                    
                    if form_issues["issues"]:
                        issues.append(form_issues)
        
        except Exception as e:
            logger.debug(f"Error analyzing forms on {url}: {e}")
        
        return issues
    
    def _check_password_complexity(self, form: BeautifulSoup, page_content: str) -> List[Dict]:
        """Check for overly complex password requirements"""
        issues = []
        
        password_fields = form.find_all('input', type='password')
        if password_fields:
            # Look for complexity indicators in page content
            complexity_requirements = {
                "min_length": ["8 characters", "minimum 8", "at least 8"],
                "uppercase": ["uppercase", "capital letter", "upper case"],
                "lowercase": ["lowercase", "lower case"],
                "number": ["number", "digit", "numeric"],
                "special": ["special character", "symbol", "special"],
                "no_common": ["common password", "weak password"]
            }
            
            found_requirements = []
            for req_type, patterns in complexity_requirements.items():
                if any(pattern in page_content for pattern in patterns):
                    found_requirements.append(req_type)
            
            if len(found_requirements) >= 3:
                issues.append({
                    "type": "excessive_password_complexity",
                    "severity": "high",
                    "requirements_found": found_requirements,
                    "impact": "20-30% of users abandon due to password frustration",
                    "fix": "Reduce to: 8+ characters with one capital OR number",
                    "implementation": "1 hour"
                })
            
            # Check for password strength meter
            if "password-strength" in str(form) or "strength-meter" in str(form):
                if len(found_requirements) >= 4:
                    issues.append({
                        "type": "overly_strict_strength_meter",
                        "severity": "medium",
                        "impact": "Users spend 2-3x longer creating password",
                        "fix": "Simplify strength requirements",
                        "implementation": "2 hours"
                    })
            
            # Check for no "show password" option
            if not any(x in str(form) for x in ["show-password", "toggle-password", "reveal-password"]):
                issues.append({
                    "type": "no_password_visibility_toggle",
                    "severity": "low",
                    "impact": "5-10% higher error rate on mobile",
                    "fix": "Add show/hide password toggle",
                    "implementation": "30 minutes"
                })
        
        return issues
    
    def _check_email_validation(self, form: BeautifulSoup, soup: BeautifulSoup) -> List[Dict]:
        """Check for overly strict email validation"""
        issues = []
        
        email_fields = form.find_all('input', type='email')
        if not email_fields:
            email_fields = form.find_all('input', attrs={'name': re.compile(r'email', re.I)})
        
        if email_fields:
            # Check for custom validation scripts
            scripts = soup.find_all('script')
            strict_validation = False
            
            for script in scripts:
                if script.string:
                    # Look for overly strict regex patterns
                    if re.search(r'email.*regex|email.*pattern|validateEmail', script.string, re.I):
                        # Common overly strict patterns
                        if any(pattern in script.string for pattern in [
                            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$',
                            r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
                            'no plus signs', 'no special'
                        ]):
                            strict_validation = True
            
            if strict_validation:
                issues.append({
                    "type": "strict_email_validation",
                    "severity": "high",
                    "impact": "Rejects 5-10% of valid emails (with +, multiple dots, new TLDs)",
                    "fix": "Use HTML5 email validation or permissive regex",
                    "implementation": "1 hour",
                    "examples_rejected": [
                        "user+tag@example.com",
                        "name@mail.co.uk",
                        "firstname.lastname@company.io"
                    ]
                })
            
            # Check for confirmation email field
            if len(email_fields) > 1 or "confirm" in str(form).lower():
                issues.append({
                    "type": "email_confirmation_required",
                    "severity": "medium",
                    "impact": "8-12% drop in completion rate",
                    "fix": "Remove email confirmation field",
                    "implementation": "15 minutes"
                })
        
        return issues
    
    def _check_phone_requirements(self, form: BeautifulSoup) -> List[Dict]:
        """Check for phone number issues"""
        issues = []
        
        phone_fields = form.find_all('input', attrs={
            'type': 'tel'
        }) or form.find_all('input', attrs={
            'name': re.compile(r'phone|mobile|cell', re.I)
        })
        
        for field in phone_fields:
            # Check if required
            if field.get('required') or field.get('aria-required') == 'true':
                issues.append({
                    "type": "required_phone_number",
                    "severity": "high",
                    "field_name": field.get('name', 'phone'),
                    "impact": "15-25% form abandonment",
                    "fix": "Make phone number optional",
                    "implementation": "5 minutes"
                })
            
            # Check for specific format requirements
            pattern = field.get('pattern')
            if pattern and len(pattern) > 10:
                issues.append({
                    "type": "strict_phone_format",
                    "severity": "medium",
                    "pattern": pattern[:50],
                    "impact": "International users can't complete form",
                    "fix": "Accept any 10+ digit format",
                    "implementation": "30 minutes"
                })
            
            # Check for no country code selector
            form_str = str(form)
            if not any(x in form_str for x in ['country-code', 'country_code', 'dial-code']):
                if 'international' not in form_str.lower():
                    issues.append({
                        "type": "no_international_phone_support",
                        "severity": "low",
                        "impact": "Loses international leads",
                        "fix": "Add country code selector or accept any format",
                        "implementation": "2 hours"
                    })
        
        return issues
    
    def _check_required_fields(self, form: BeautifulSoup, page_name: str) -> List[Dict]:
        """Check for unnecessary required fields"""
        issues = []
        
        all_inputs = form.find_all(['input', 'select', 'textarea'])
        required_fields = [
            field for field in all_inputs 
            if field.get('required') or field.get('aria-required') == 'true'
        ]
        
        visible_required = [
            field for field in required_fields 
            if field.get('type') not in ['hidden', 'submit', 'button']
        ]
        
        # Check total count
        if len(visible_required) > 5:
            issues.append({
                "type": "too_many_required_fields",
                "severity": "high",
                "count": len(visible_required),
                "impact": f"Each field beyond 3 reduces conversion by ~7% (losing ~{(len(visible_required)-3)*7}%)",
                "fix": "Reduce to Name, Email, Company only",
                "implementation": "1 hour"
            })
        
        # Check for specific unnecessary fields
        unnecessary_fields = {
            "company_size": "Company size should be optional",
            "budget": "Budget questions kill 20% of leads",
            "revenue": "Revenue is too sensitive for initial form",
            "employees": "Employee count should be collected later",
            "industry": "Industry can be inferred or asked later",
            "job_title": "Title less important than email/name",
            "website": "Website can be inferred from email domain",
            "address": "Physical address rarely needed upfront",
            "timezone": "Can be detected automatically"
        }
        
        for field in visible_required:
            field_name = (field.get('name', '') or field.get('id', '')).lower()
            for unnecessary, reason in unnecessary_fields.items():
                if unnecessary in field_name:
                    issues.append({
                        "type": "unnecessary_required_field",
                        "severity": "medium",
                        "field": unnecessary,
                        "reason": reason,
                        "impact": "8-15% form abandonment",
                        "fix": f"Make {unnecessary} optional or remove",
                        "implementation": "10 minutes"
                    })
        
        # Check for qualifying questions in initial signup
        if page_name in ["signup", "register", "trial"]:
            qualifying_patterns = ["how did you hear", "what brings you", "primary use case", "goals"]
            form_text = str(form).lower()
            
            for pattern in qualifying_patterns:
                if pattern in form_text:
                    issues.append({
                        "type": "premature_qualification",
                        "severity": "medium",
                        "question_type": pattern,
                        "impact": "12% drop in signups",
                        "fix": "Move to onboarding after signup",
                        "implementation": "2 hours"
                    })
        
        return issues
    
    def _check_multistep_forms(self, form: BeautifulSoup, soup: BeautifulSoup) -> List[Dict]:
        """Check for problematic multi-step forms"""
        issues = []
        
        # Look for multi-step indicators
        multistep_indicators = [
            "step", "wizard", "progress", "stage", "phase",
            "next", "previous", "continue"
        ]
        
        form_str = str(form).lower()
        page_str = str(soup).lower()
        
        is_multistep = any(indicator in form_str for indicator in multistep_indicators[:5])
        
        if is_multistep:
            # Count potential steps
            step_count = len(re.findall(r'step.?[1-9]|stage.?[1-9]', form_str))
            
            if step_count > 3:
                issues.append({
                    "type": "too_many_form_steps",
                    "severity": "high",
                    "steps_detected": step_count,
                    "impact": "40-60% abandonment in multi-step forms",
                    "fix": "Consolidate to single page with optional sections",
                    "implementation": "4 hours"
                })
            
            # Check for progress indicator
            if not any(x in page_str for x in ['progress-bar', 'progress-indicator', 'step-indicator']):
                issues.append({
                    "type": "no_progress_indicator",
                    "severity": "medium",
                    "impact": "Users don't know how long form is",
                    "fix": "Add visual progress indicator",
                    "implementation": "2 hours"
                })
            
            # Check if going back loses data
            if "previous" not in form_str and "back" not in form_str:
                issues.append({
                    "type": "no_back_navigation",
                    "severity": "medium",
                    "impact": "Users can't correct mistakes",
                    "fix": "Add back button that preserves data",
                    "implementation": "3 hours"
                })
        
        return issues
    
    def _check_conveniences(self, form: BeautifulSoup, soup: BeautifulSoup, page_name: str) -> List[Dict]:
        """Check for missing convenience features"""
        issues = []
        
        form_str = str(form).lower()
        page_str = str(soup).lower()
        
        # Check for social login
        if page_name in ["signup", "register", "login"]:
            social_providers = ["google", "github", "linkedin", "microsoft", "facebook"]
            has_social = any(provider in form_str or provider in page_str for provider in social_providers)
            
            if not has_social:
                issues.append({
                    "type": "no_social_login",
                    "severity": "high",
                    "impact": "Missing 20-30% conversion boost",
                    "fix": "Add Google and LinkedIn OAuth",
                    "implementation": "4 hours",
                    "best_options": ["Google (highest adoption)", "LinkedIn (B2B)", "GitHub (developers)"]
                })
        
        # Check for remember me option on login
        if page_name == "login":
            if "remember" not in form_str and "keep" not in form_str:
                issues.append({
                    "type": "no_remember_me",
                    "severity": "low",
                    "impact": "Users must log in repeatedly",
                    "fix": "Add 'Remember me' checkbox",
                    "implementation": "30 minutes"
                })
        
        # Check for password manager compatibility
        password_fields = form.find_all('input', type='password')
        if password_fields:
            for field in password_fields:
                if field.get('autocomplete') == 'off':
                    issues.append({
                        "type": "blocks_password_managers",
                        "severity": "medium",
                        "impact": "Users can't use password managers",
                        "fix": "Remove autocomplete='off' from password fields",
                        "implementation": "5 minutes"
                    })
                    break
        
        # Check for autofocus on first field
        first_input = form.find('input', type=lambda x: x not in ['hidden', 'submit', 'button'])
        if first_input and not first_input.get('autofocus'):
            if page_name in ["login", "signup", "register"]:
                issues.append({
                    "type": "no_autofocus",
                    "severity": "low",
                    "impact": "Extra click required to start",
                    "fix": "Add autofocus to first field",
                    "implementation": "2 minutes"
                })
        
        return issues
    
    def _check_guest_checkout(self, soup: BeautifulSoup, page_content: str) -> List[Dict]:
        """Check for guest checkout option"""
        issues = []
        
        # Look for guest checkout option
        guest_patterns = [
            "guest checkout", "checkout as guest", "continue without account",
            "skip registration", "no account needed"
        ]
        
        has_guest = any(pattern in page_content for pattern in guest_patterns)
        
        if not has_guest:
            # Check if registration is required
            if any(x in page_content for x in ["create account", "register", "sign up"]):
                issues.append({
                    "type": "no_guest_checkout",
                    "severity": "critical",
                    "impact": "23% cart abandonment due to forced registration",
                    "fix": "Add prominent guest checkout option",
                    "implementation": "1 day",
                    "revenue_impact": "Immediate 15-20% increase in conversions"
                })
        
        return issues
    
    def _check_autocomplete(self, form: BeautifulSoup) -> List[Dict]:
        """Check for proper autocomplete attributes"""
        issues = []
        
        # Fields that should have autocomplete
        autocomplete_map = {
            "email": "email",
            "name": "name",
            "first": "given-name",
            "last": "family-name",
            "phone": "tel",
            "company": "organization",
            "address": "street-address",
            "city": "address-level2",
            "state": "address-level1",
            "zip": "postal-code",
            "country": "country"
        }
        
        inputs = form.find_all('input')
        missing_autocomplete = []
        
        for input_field in inputs:
            field_name = (input_field.get('name', '') or input_field.get('id', '')).lower()
            
            for key, autocomplete_value in autocomplete_map.items():
                if key in field_name and not input_field.get('autocomplete'):
                    missing_autocomplete.append({
                        "field": field_name,
                        "should_be": autocomplete_value
                    })
        
        if missing_autocomplete:
            issues.append({
                "type": "missing_autocomplete",
                "severity": "low",
                "fields": missing_autocomplete[:5],  # First 5
                "impact": "Users must type everything manually",
                "fix": "Add proper autocomplete attributes",
                "implementation": "30 minutes"
            })
        
        return issues
    
    def _calculate_form_impact(self, friction_score: int, page_name: str) -> float:
        """Calculate conversion impact based on friction score"""
        # Base impact by page type
        page_importance = {
            "checkout": 2.0,
            "signup": 1.5,
            "register": 1.5,
            "demo": 1.3,
            "trial": 1.4,
            "contact": 1.0,
            "quote": 1.2,
            "login": 0.8,
            "homepage": 1.1
        }
        
        multiplier = page_importance.get(page_name, 1.0)
        
        # Friction score to conversion impact mapping
        # Every 10 points of friction = ~5% conversion loss
        conversion_loss = (friction_score / 10) * 5
        
        # Cap at 80% (forms rarely kill ALL conversions)
        conversion_loss = min(conversion_loss, 80)
        
        return conversion_loss * multiplier
    
    def _calculate_total_impact(self, form_issues: List[Dict]) -> float:
        """Calculate total conversion impact across all forms"""
        if not form_issues:
            return 0
        
        # Weight by importance (some forms matter more)
        total_impact = sum(
            issue.get("conversion_impact", 0) 
            for issue in form_issues
        )
        
        # Average across forms but weight critical pages higher
        return min(total_impact / len(form_issues) * 1.2, 75)
    
    def _identify_critical_issues(self, form_issues: List[Dict]) -> List[Dict]:
        """Identify the most critical issues to fix"""
        critical = []
        
        for form_data in form_issues:
            for issue in form_data.get("issues", []):
                if issue.get("severity") in ["critical", "high"]:
                    critical.append({
                        "page": form_data["page"],
                        "issue": issue["type"],
                        "impact": issue["impact"],
                        "fix": issue["fix"],
                        "time": issue.get("implementation", "Unknown")
                    })
        
        # Sort by impact
        return sorted(critical, key=lambda x: x.get("severity", "") == "critical", reverse=True)[:5]
    
    def _generate_quick_fixes(self, form_issues: List[Dict]) -> List[Dict]:
        """Generate list of quick fixes (< 1 hour to implement)"""
        quick_fixes = []
        
        for form_data in form_issues:
            for issue in form_data.get("issues", []):
                time = issue.get("implementation", "")
                if any(x in time.lower() for x in ["minute", "5 min", "10 min", "15 min", "30 min", "1 hour"]):
                    quick_fixes.append({
                        "page": form_data["page"],
                        "fix": issue["fix"],
                        "time": time,
                        "impact": issue.get("impact", ""),
                        "type": issue["type"]
                    })
        
        return quick_fixes[:10]  # Top 10 quick fixes
    
    def _compare_to_best_practices(self, form_issues: List[Dict]) -> List[Dict]:
        """Compare to competitor best practices"""
        best_practices = []
        
        # Check what competitors typically do better
        issue_types = set()
        for form_data in form_issues:
            for issue in form_data.get("issues", []):
                issue_types.add(issue["type"])
        
        competitor_advantages = {
            "no_social_login": {
                "competitors": ["Slack", "Notion", "Figma"],
                "practice": "1-click signup with Google/GitHub",
                "impact": "60% faster registration"
            },
            "too_many_required_fields": {
                "competitors": ["Stripe", "Twilio", "SendGrid"],
                "practice": "3-field signup (email, name, password)",
                "impact": "40% higher completion rate"
            },
            "no_guest_checkout": {
                "competitors": ["Amazon", "Apple", "Shopify stores"],
                "practice": "Prominent guest checkout option",
                "impact": "23% less cart abandonment"
            },
            "excessive_password_complexity": {
                "competitors": ["Google", "Microsoft", "Dropbox"],
                "practice": "Simple requirements + password strength meter",
                "impact": "30% less password frustration"
            }
        }
        
        for issue_type in issue_types:
            if issue_type in competitor_advantages:
                advantage = competitor_advantages[issue_type]
                best_practices.append({
                    "issue": issue_type,
                    "competitors_doing_better": advantage["competitors"],
                    "their_approach": advantage["practice"],
                    "their_advantage": advantage["impact"]
                })
        
        return best_practices
    
    def _estimate_revenue_loss(self, conversion_impact: float) -> Dict[str, Any]:
        """Estimate revenue loss from form friction"""
        # These are estimates - would need actual traffic/conversion data
        return {
            "monthly_visitors_affected": 10000,  # Estimate
            "current_conversion_rate": 2.5,  # Industry average
            "improved_conversion_rate": 2.5 * (1 + conversion_impact/100),
            "additional_conversions_monthly": 10000 * (conversion_impact/100) * 0.025,
            "average_deal_value": 500,  # Estimate
            "monthly_revenue_loss": 10000 * (conversion_impact/100) * 0.025 * 500,
            "annual_revenue_loss": 10000 * (conversion_impact/100) * 0.025 * 500 * 12,
            "confidence": "estimate",
            "note": "Based on industry averages. Provide your traffic and conversion data for accurate calculation."
        }