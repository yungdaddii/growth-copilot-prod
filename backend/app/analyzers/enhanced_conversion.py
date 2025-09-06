"""
Enhanced Conversion Analyzer with Psychological Insights
Provides deep conversion optimization analysis including friction detection,
psychological triggers, and behavioral insights.
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import structlog
from bs4 import BeautifulSoup
import re
from collections import Counter
import json

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class EnhancedConversionAnalyzer:
    def __init__(self):
        # Psychological trigger patterns
        self.psychological_triggers = {
            'urgency': [
                'limited time', 'only', 'today', 'now', 'hurry', 'last chance',
                'deadline', 'expires', 'countdown', 'remaining', 'left in stock'
            ],
            'scarcity': [
                'limited', 'exclusive', 'rare', 'few left', 'selling fast',
                'in stock', 'available', 'spots left', 'seats remaining'
            ],
            'social_proof': [
                'testimonial', 'review', 'rating', 'customer', 'trusted by',
                'used by', 'loved by', 'join', 'million users', 'companies use'
            ],
            'authority': [
                'expert', 'certified', 'award', 'featured in', 'as seen on',
                'recommended', 'endorsed', 'professional', 'industry leader'
            ],
            'reciprocity': [
                'free', 'gift', 'bonus', 'complimentary', 'no cost',
                'trial', 'sample', 'download', 'get started'
            ],
            'risk_reversal': [
                'guarantee', 'money back', 'no risk', 'refund', 'warranty',
                'secure', 'safe', 'protected', 'no obligation', 'cancel anytime'
            ]
        }
        
        # Trust signal indicators
        self.trust_signals = {
            'security_badges': ['ssl', 'secure', 'verified', 'mcafee', 'norton', 'trustwave'],
            'payment_badges': ['visa', 'mastercard', 'paypal', 'stripe', 'american express'],
            'certifications': ['certified', 'accredited', 'licensed', 'registered', 'approved'],
            'guarantees': ['guarantee', 'warranty', 'return policy', 'refund'],
            'contact_info': ['phone', 'email', 'address', 'contact us', 'support']
        }
        
        # Friction indicators
        self.friction_patterns = {
            'form_complexity': {
                'high': 10,  # More than 10 fields
                'medium': 6,  # 6-10 fields
                'low': 3     # 3-5 fields
            },
            'required_fields': {
                'critical': ['email', 'password'],
                'important': ['name', 'phone'],
                'optional': ['company', 'title', 'address']
            }
        }
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive conversion optimization analysis"""
        cache_key = f"enhanced_conversion:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "conversion_score": 0,
            "friction_analysis": {},
            "psychological_triggers": {},
            "trust_signals": {},
            "cta_analysis": {},
            "form_analysis": {},
            "checkout_analysis": {},
            "value_proposition": {},
            "ab_test_opportunities": [],
            "quick_wins": [],
            "recommendations": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Analyze multiple pages for comprehensive insights
                tasks = [
                    self._analyze_homepage(client, domain),
                    self._analyze_forms(client, domain),
                    self._analyze_checkout_flow(client, domain),
                    self._analyze_pricing_page(client, domain),
                    self._analyze_trust_indicators(client, domain)
                ]
                
                homepage, forms, checkout, pricing, trust = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process homepage analysis
                if not isinstance(homepage, Exception):
                    results.update(homepage)
                
                # Add form analysis
                if not isinstance(forms, Exception):
                    results["form_analysis"] = forms
                
                # Add checkout analysis
                if not isinstance(checkout, Exception):
                    results["checkout_analysis"] = checkout
                
                # Add pricing analysis
                if not isinstance(pricing, Exception):
                    results["pricing_analysis"] = pricing
                
                # Add trust analysis
                if not isinstance(trust, Exception):
                    results["trust_signals"] = trust
                
                # Calculate conversion score
                results["conversion_score"] = self._calculate_conversion_score(results)
                
                # Generate A/B test opportunities
                results["ab_test_opportunities"] = self._identify_ab_tests(results)
                
                # Identify quick wins
                results["quick_wins"] = self._identify_quick_wins(results)
                
                # Generate recommendations
                results["recommendations"] = self._generate_conversion_recommendations(results)
                
                await cache_result(cache_key, results, ttl=3600)
                
        except Exception as e:
            logger.error(f"Enhanced conversion analysis failed for {domain}", error=str(e))
            results["error"] = str(e)
        
        return results
    
    async def _analyze_homepage(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze homepage for conversion elements"""
        try:
            response = await client.get(f"https://{domain}")
            soup = BeautifulSoup(response.text, 'lxml')
            text_content = soup.get_text(separator=' ', strip=True).lower()
            
            results = {
                "psychological_triggers": self._detect_psychological_triggers(text_content),
                "cta_analysis": self._analyze_ctas(soup),
                "value_proposition": self._analyze_value_proposition(soup, text_content),
                "friction_points": self._detect_friction_points(soup),
                "social_proof": self._analyze_social_proof(soup, text_content),
                "urgency_scarcity": self._analyze_urgency_scarcity(text_content)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Homepage analysis failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    def _detect_psychological_triggers(self, text_content: str) -> Dict[str, Any]:
        """Detect psychological triggers in content"""
        triggers_found = {
            "urgency": {"found": False, "instances": [], "score": 0},
            "scarcity": {"found": False, "instances": [], "score": 0},
            "social_proof": {"found": False, "instances": [], "score": 0},
            "authority": {"found": False, "instances": [], "score": 0},
            "reciprocity": {"found": False, "instances": [], "score": 0},
            "risk_reversal": {"found": False, "instances": [], "score": 0}
        }
        
        for trigger_type, keywords in self.psychological_triggers.items():
            for keyword in keywords:
                if keyword in text_content:
                    triggers_found[trigger_type]["found"] = True
                    triggers_found[trigger_type]["instances"].append(keyword)
            
            # Calculate score based on instances
            instance_count = len(triggers_found[trigger_type]["instances"])
            if instance_count > 0:
                triggers_found[trigger_type]["score"] = min(100, instance_count * 20)
        
        # Overall psychological optimization score
        total_triggers = sum(1 for t in triggers_found.values() if t["found"])
        psychological_score = min(100, total_triggers * 15)
        
        return {
            "triggers": triggers_found,
            "overall_score": psychological_score,
            "missing_triggers": [k for k, v in triggers_found.items() if not v["found"]],
            "recommendations": self._generate_trigger_recommendations(triggers_found)
        }
    
    def _generate_trigger_recommendations(self, triggers: Dict) -> List[str]:
        """Generate recommendations for psychological triggers"""
        recommendations = []
        
        if not triggers["urgency"]["found"]:
            recommendations.append("Add urgency: Use limited-time offers or countdown timers")
        
        if not triggers["scarcity"]["found"]:
            recommendations.append("Show scarcity: Display stock levels or limited availability")
        
        if not triggers["social_proof"]["found"]:
            recommendations.append("Add social proof: Include testimonials, reviews, or user counts")
        
        if not triggers["authority"]["found"]:
            recommendations.append("Build authority: Show certifications, awards, or media mentions")
        
        if not triggers["risk_reversal"]["found"]:
            recommendations.append("Reduce risk: Add money-back guarantee or free trial")
        
        return recommendations
    
    def _analyze_ctas(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze Call-to-Action buttons and links"""
        cta_analysis = {
            "total_ctas": 0,
            "above_fold_ctas": 0,
            "cta_clarity": [],
            "cta_contrast": [],
            "cta_placement": [],
            "recommendations": [],
            "optimization_score": 0
        }
        
        # Common CTA patterns
        cta_patterns = [
            'get started', 'start free', 'try free', 'sign up', 'register',
            'buy now', 'shop now', 'learn more', 'download', 'book demo',
            'contact us', 'request', 'subscribe', 'join', 'claim'
        ]
        
        # Find all buttons and links that might be CTAs
        buttons = soup.find_all(['button', 'a'])
        
        for element in buttons:
            text = element.get_text(strip=True).lower()
            
            # Check if it's a CTA
            is_cta = any(pattern in text for pattern in cta_patterns)
            
            if is_cta or 'btn' in element.get('class', []) or 'button' in element.get('class', []):
                cta_analysis["total_ctas"] += 1
                
                # Analyze CTA clarity
                if len(text.split()) <= 3:
                    cta_analysis["cta_clarity"].append({"text": text, "clear": True})
                else:
                    cta_analysis["cta_clarity"].append({"text": text, "clear": False})
                    cta_analysis["recommendations"].append(f"Simplify CTA: '{text[:30]}...' is too long")
                
                # Check for action-oriented language
                action_verbs = ['get', 'start', 'try', 'download', 'book', 'claim', 'join']
                if not any(verb in text for verb in action_verbs):
                    cta_analysis["recommendations"].append(f"Use action verb in CTA: '{text}'")
        
        # Analyze CTA optimization
        if cta_analysis["total_ctas"] == 0:
            cta_analysis["recommendations"].append("No clear CTAs found - add prominent call-to-action buttons")
            cta_analysis["optimization_score"] = 0
        elif cta_analysis["total_ctas"] < 3:
            cta_analysis["recommendations"].append("Limited CTAs - consider adding more conversion opportunities")
            cta_analysis["optimization_score"] = 60
        elif cta_analysis["total_ctas"] > 10:
            cta_analysis["recommendations"].append("Too many CTAs may cause decision paralysis - focus on 3-5 primary actions")
            cta_analysis["optimization_score"] = 70
        else:
            cta_analysis["optimization_score"] = 85
        
        # Check for CTA hierarchy
        primary_ctas = [cta for cta in cta_analysis["cta_clarity"] if 'start' in cta["text"] or 'try' in cta["text"]]
        if not primary_ctas:
            cta_analysis["recommendations"].append("Add primary CTA with 'Start Free Trial' or similar")
        
        return cta_analysis
    
    def _analyze_value_proposition(self, soup: BeautifulSoup, text_content: str) -> Dict[str, Any]:
        """Analyze value proposition clarity and strength"""
        value_prop = {
            "headline_found": False,
            "headline_text": "",
            "clarity_score": 0,
            "benefit_focused": False,
            "unique_differentiator": False,
            "target_audience_clear": False,
            "recommendations": []
        }
        
        # Find main headline (H1)
        h1 = soup.find('h1')
        if h1:
            value_prop["headline_found"] = True
            value_prop["headline_text"] = h1.get_text(strip=True)
            
            # Analyze headline effectiveness
            headline_lower = value_prop["headline_text"].lower()
            
            # Check for benefit-focused language
            benefit_keywords = ['save', 'increase', 'improve', 'boost', 'grow', 'reduce', 'eliminate', 'transform']
            if any(keyword in headline_lower for keyword in benefit_keywords):
                value_prop["benefit_focused"] = True
                value_prop["clarity_score"] += 30
            else:
                value_prop["recommendations"].append("Make headline benefit-focused (what's in it for the user)")
            
            # Check for specificity
            if any(char.isdigit() for char in value_prop["headline_text"]):
                value_prop["clarity_score"] += 20  # Contains numbers (specific)
            
            # Check length
            word_count = len(value_prop["headline_text"].split())
            if 4 <= word_count <= 10:
                value_prop["clarity_score"] += 20
            else:
                value_prop["recommendations"].append("Optimize headline length (aim for 4-10 words)")
        else:
            value_prop["recommendations"].append("No H1 headline found - add clear value proposition")
        
        # Look for supporting value proposition elements
        h2_tags = soup.find_all('h2')[:3]  # First 3 H2s
        if h2_tags:
            for h2 in h2_tags:
                h2_text = h2.get_text(strip=True).lower()
                if 'why' in h2_text or 'how' in h2_text or 'what' in h2_text:
                    value_prop["clarity_score"] += 10
        
        # Check for unique differentiators
        differentiator_keywords = ['only', 'first', 'best', 'unique', 'exclusive', 'patented', 'award-winning']
        if any(keyword in text_content for keyword in differentiator_keywords):
            value_prop["unique_differentiator"] = True
            value_prop["clarity_score"] += 20
        else:
            value_prop["recommendations"].append("Highlight unique differentiators - what makes you different?")
        
        # Check for target audience clarity
        audience_indicators = ['for', 'helps', 'designed for', 'built for', 'perfect for']
        if any(indicator in text_content for indicator in audience_indicators):
            value_prop["target_audience_clear"] = True
            value_prop["clarity_score"] += 10
        else:
            value_prop["recommendations"].append("Clarify target audience - who is this for?")
        
        return value_prop
    
    def _detect_friction_points(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Detect conversion friction points"""
        friction_analysis = {
            "friction_points": [],
            "friction_score": 0,  # Higher is worse
            "smooth_elements": [],
            "recommendations": []
        }
        
        # Check for popup/modal indicators
        popup_indicators = ['modal', 'popup', 'overlay', 'lightbox']
        for indicator in popup_indicators:
            elements = soup.find_all(class_=re.compile(indicator, re.I))
            if elements:
                friction_analysis["friction_points"].append(f"Potential popup/modal detected ({indicator})")
                friction_analysis["friction_score"] += 10
        
        # Check for required registration before value
        login_required = soup.find_all(text=re.compile(r'sign up|register|create account', re.I))
        if login_required and not soup.find(text=re.compile(r'free trial|demo|sample', re.I)):
            friction_analysis["friction_points"].append("Registration required without clear value proposition")
            friction_analysis["friction_score"] += 15
        
        # Check for excessive form fields
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all(['input', 'select', 'textarea'])
            visible_inputs = [i for i in inputs if i.get('type') not in ['hidden', 'submit', 'button']]
            
            if len(visible_inputs) > 5:
                friction_analysis["friction_points"].append(f"Long form detected ({len(visible_inputs)} fields)")
                friction_analysis["friction_score"] += 20
                friction_analysis["recommendations"].append("Reduce form fields or use progressive disclosure")
        
        # Check for missing trust signals near CTAs
        cta_buttons = soup.find_all(['button', 'a'], text=re.compile(r'buy|purchase|subscribe|start', re.I))
        for cta in cta_buttons:
            # Check if trust signals are nearby
            parent = cta.parent
            if parent:
                parent_text = parent.get_text(strip=True).lower()
                if not any(trust in parent_text for trust in ['secure', 'safe', 'guarantee', 'ssl']):
                    friction_analysis["friction_points"].append("CTA without nearby trust signals")
                    friction_analysis["friction_score"] += 5
        
        # Check for smooth elements
        if soup.find(text=re.compile(r'no credit card', re.I)):
            friction_analysis["smooth_elements"].append("No credit card required")
            friction_analysis["friction_score"] -= 10
        
        if soup.find(text=re.compile(r'instant|immediate|quick|fast', re.I)):
            friction_analysis["smooth_elements"].append("Speed/instant gratification emphasized")
            friction_analysis["friction_score"] -= 5
        
        if soup.find(text=re.compile(r'cancel anytime|no commitment', re.I)):
            friction_analysis["smooth_elements"].append("Easy cancellation mentioned")
            friction_analysis["friction_score"] -= 5
        
        # Ensure friction score doesn't go below 0
        friction_analysis["friction_score"] = max(0, friction_analysis["friction_score"])
        
        # Generate recommendations based on friction score
        if friction_analysis["friction_score"] > 30:
            friction_analysis["recommendations"].append("High friction detected - significant conversion barriers")
        elif friction_analysis["friction_score"] > 15:
            friction_analysis["recommendations"].append("Moderate friction - optimize user flow")
        
        return friction_analysis
    
    def _analyze_social_proof(self, soup: BeautifulSoup, text_content: str) -> Dict[str, Any]:
        """Analyze social proof elements"""
        social_proof = {
            "testimonials_found": False,
            "reviews_found": False,
            "ratings_found": False,
            "customer_logos": False,
            "user_count": False,
            "case_studies": False,
            "social_proof_score": 0,
            "recommendations": []
        }
        
        # Check for testimonials
        testimonial_indicators = ['testimonial', 'review', 'feedback', 'what our customers say', 'success story']
        for indicator in testimonial_indicators:
            if indicator in text_content:
                social_proof["testimonials_found"] = True
                social_proof["social_proof_score"] += 20
                break
        
        # Check for ratings/stars
        if re.search(r'⭐|★|star|rating', text_content):
            social_proof["ratings_found"] = True
            social_proof["social_proof_score"] += 15
        
        # Check for customer logos
        if 'trusted by' in text_content or 'used by' in text_content or 'clients' in text_content:
            social_proof["customer_logos"] = True
            social_proof["social_proof_score"] += 20
        
        # Check for user count
        user_count_pattern = r'\d+[,\d]*\s*(user|customer|company|companies|client|download|install)'
        if re.search(user_count_pattern, text_content):
            social_proof["user_count"] = True
            social_proof["social_proof_score"] += 15
        
        # Check for case studies
        if 'case study' in text_content or 'case studies' in text_content:
            social_proof["case_studies"] = True
            social_proof["social_proof_score"] += 20
        
        # Generate recommendations
        if not social_proof["testimonials_found"]:
            social_proof["recommendations"].append("Add customer testimonials for credibility")
        
        if not social_proof["ratings_found"]:
            social_proof["recommendations"].append("Display ratings or review scores")
        
        if not social_proof["customer_logos"]:
            social_proof["recommendations"].append("Show logos of notable customers or partners")
        
        if not social_proof["user_count"]:
            social_proof["recommendations"].append("Display user/customer count for social validation")
        
        return social_proof
    
    def _analyze_urgency_scarcity(self, text_content: str) -> Dict[str, Any]:
        """Analyze urgency and scarcity elements"""
        urgency_scarcity = {
            "urgency_elements": [],
            "scarcity_elements": [],
            "time_limited": False,
            "quantity_limited": False,
            "countdown_timer": False,
            "effectiveness_score": 0,
            "recommendations": []
        }
        
        # Check for urgency elements
        urgency_patterns = [
            r'limited time',
            r'offer expires',
            r'ends (today|tomorrow|soon)',
            r'last chance',
            r'hurry',
            r'act now',
            r'don\'t miss'
        ]
        
        for pattern in urgency_patterns:
            if re.search(pattern, text_content, re.I):
                urgency_scarcity["urgency_elements"].append(pattern)
                urgency_scarcity["time_limited"] = True
                urgency_scarcity["effectiveness_score"] += 15
        
        # Check for scarcity elements
        scarcity_patterns = [
            r'\d+\s*left',
            r'only\s*\d+',
            r'limited (spots|seats|quantity)',
            r'selling fast',
            r'almost (gone|sold out)',
            r'low stock'
        ]
        
        for pattern in scarcity_patterns:
            if re.search(pattern, text_content, re.I):
                urgency_scarcity["scarcity_elements"].append(pattern)
                urgency_scarcity["quantity_limited"] = True
                urgency_scarcity["effectiveness_score"] += 15
        
        # Check for countdown timer (common class names)
        countdown_indicators = ['countdown', 'timer', 'clock', 'deadline']
        for indicator in countdown_indicators:
            if indicator in str(soup):
                urgency_scarcity["countdown_timer"] = True
                urgency_scarcity["effectiveness_score"] += 20
                break
        
        # Generate recommendations
        if not urgency_scarcity["time_limited"] and not urgency_scarcity["quantity_limited"]:
            urgency_scarcity["recommendations"].append("Add urgency or scarcity to drive action")
        
        if urgency_scarcity["time_limited"] and not urgency_scarcity["countdown_timer"]:
            urgency_scarcity["recommendations"].append("Add countdown timer to reinforce urgency")
        
        if urgency_scarcity["effectiveness_score"] > 30:
            urgency_scarcity["recommendations"].append("Be careful not to overuse urgency - maintain credibility")
        
        return urgency_scarcity
    
    async def _analyze_forms(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze form optimization"""
        try:
            response = await client.get(f"https://{domain}")
            soup = BeautifulSoup(response.text, 'lxml')
            
            forms_analysis = {
                "forms_found": 0,
                "form_details": [],
                "optimization_score": 0,
                "conversion_rate_impact": "",
                "recommendations": []
            }
            
            forms = soup.find_all('form')
            forms_analysis["forms_found"] = len(forms)
            
            for form in forms:
                form_detail = self._analyze_single_form(form)
                forms_analysis["form_details"].append(form_detail)
            
            # Calculate overall form optimization score
            if forms_analysis["form_details"]:
                avg_score = sum(f["optimization_score"] for f in forms_analysis["form_details"]) / len(forms_analysis["form_details"])
                forms_analysis["optimization_score"] = avg_score
                
                # Estimate conversion impact
                if avg_score < 50:
                    forms_analysis["conversion_rate_impact"] = "Losing 30-50% of potential conversions"
                elif avg_score < 70:
                    forms_analysis["conversion_rate_impact"] = "Could improve conversions by 15-20%"
                else:
                    forms_analysis["conversion_rate_impact"] = "Well-optimized for conversions"
            
            return forms_analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_single_form(self, form) -> Dict[str, Any]:
        """Analyze a single form for optimization"""
        form_analysis = {
            "field_count": 0,
            "required_fields": 0,
            "optional_fields": 0,
            "field_types": [],
            "has_labels": False,
            "has_placeholders": False,
            "has_validation": False,
            "has_progress_indicator": False,
            "optimization_score": 100,
            "issues": []
        }
        
        # Count fields
        inputs = form.find_all(['input', 'select', 'textarea'])
        visible_inputs = [i for i in inputs if i.get('type') not in ['hidden', 'submit', 'button']]
        
        form_analysis["field_count"] = len(visible_inputs)
        
        for input_field in visible_inputs:
            # Check if required
            if input_field.get('required') or input_field.get('aria-required') == 'true':
                form_analysis["required_fields"] += 1
            else:
                form_analysis["optional_fields"] += 1
            
            # Track field types
            field_type = input_field.get('type', 'text')
            form_analysis["field_types"].append(field_type)
            
            # Check for labels
            field_id = input_field.get('id')
            if field_id and form.find('label', {'for': field_id}):
                form_analysis["has_labels"] = True
            
            # Check for placeholders
            if input_field.get('placeholder'):
                form_analysis["has_placeholders"] = True
        
        # Optimization scoring
        if form_analysis["field_count"] > 7:
            form_analysis["optimization_score"] -= 30
            form_analysis["issues"].append(f"Too many fields ({form_analysis['field_count']}) - reduces conversion")
        elif form_analysis["field_count"] > 5:
            form_analysis["optimization_score"] -= 15
            form_analysis["issues"].append("Consider reducing fields to 5 or fewer")
        
        if not form_analysis["has_labels"] and not form_analysis["has_placeholders"]:
            form_analysis["optimization_score"] -= 20
            form_analysis["issues"].append("Missing labels or placeholders - poor UX")
        
        if form_analysis["required_fields"] > form_analysis["optional_fields"]:
            form_analysis["optimization_score"] -= 10
            form_analysis["issues"].append("Too many required fields - increase friction")
        
        # Check for password field (indicates registration)
        if 'password' in form_analysis["field_types"]:
            form_analysis["optimization_score"] -= 10
            form_analysis["issues"].append("Registration form - consider social login options")
        
        return form_analysis
    
    async def _analyze_checkout_flow(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze checkout or conversion flow"""
        checkout_analysis = {
            "checkout_accessible": False,
            "guest_checkout": False,
            "payment_options": [],
            "trust_signals": [],
            "progress_indicator": False,
            "optimization_score": 0,
            "recommendations": []
        }
        
        try:
            # Try common checkout URLs
            checkout_urls = [
                f"https://{domain}/checkout",
                f"https://{domain}/cart",
                f"https://{domain}/pricing",
                f"https://{domain}/plans",
                f"https://{domain}/subscribe"
            ]
            
            for url in checkout_urls:
                try:
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        checkout_analysis["checkout_accessible"] = True
                        soup = BeautifulSoup(response.text, 'lxml')
                        text_content = soup.get_text(separator=' ', strip=True).lower()
                        
                        # Check for guest checkout
                        if 'guest' in text_content or 'without account' in text_content:
                            checkout_analysis["guest_checkout"] = True
                            checkout_analysis["optimization_score"] += 20
                        
                        # Check payment options
                        payment_methods = ['paypal', 'stripe', 'apple pay', 'google pay', 'visa', 'mastercard', 'amex']
                        for method in payment_methods:
                            if method in text_content:
                                checkout_analysis["payment_options"].append(method)
                        
                        if len(checkout_analysis["payment_options"]) >= 3:
                            checkout_analysis["optimization_score"] += 20
                        
                        # Check for trust signals
                        trust_indicators = ['secure', 'ssl', 'encrypted', 'guarantee', 'refund', 'privacy']
                        for indicator in trust_indicators:
                            if indicator in text_content:
                                checkout_analysis["trust_signals"].append(indicator)
                        
                        if len(checkout_analysis["trust_signals"]) >= 2:
                            checkout_analysis["optimization_score"] += 20
                        
                        # Check for progress indicator
                        if 'step' in text_content or 'progress' in str(soup):
                            checkout_analysis["progress_indicator"] = True
                            checkout_analysis["optimization_score"] += 15
                        
                        break
                        
                except:
                    continue
            
            # Generate recommendations
            if not checkout_analysis["guest_checkout"]:
                checkout_analysis["recommendations"].append("Enable guest checkout to reduce friction")
            
            if len(checkout_analysis["payment_options"]) < 3:
                checkout_analysis["recommendations"].append("Add more payment options (PayPal, Apple Pay, etc.)")
            
            if len(checkout_analysis["trust_signals"]) < 2:
                checkout_analysis["recommendations"].append("Add trust badges and security indicators")
            
            if not checkout_analysis["progress_indicator"]:
                checkout_analysis["recommendations"].append("Add progress indicator for multi-step checkout")
            
        except Exception as e:
            logger.error(f"Checkout analysis failed for {domain}", error=str(e))
        
        return checkout_analysis
    
    async def _analyze_pricing_page(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze pricing page optimization"""
        pricing_analysis = {
            "pricing_found": False,
            "pricing_clarity": 0,
            "comparison_table": False,
            "recommended_plan": False,
            "free_trial": False,
            "money_back_guarantee": False,
            "optimization_score": 0,
            "recommendations": []
        }
        
        try:
            # Try common pricing URLs
            pricing_urls = [
                f"https://{domain}/pricing",
                f"https://{domain}/plans",
                f"https://{domain}/price"
            ]
            
            for url in pricing_urls:
                try:
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        pricing_analysis["pricing_found"] = True
                        soup = BeautifulSoup(response.text, 'lxml')
                        text_content = soup.get_text(separator=' ', strip=True).lower()
                        
                        # Check for pricing clarity (currency symbols)
                        if '$' in response.text or '€' in response.text or '£' in response.text:
                            pricing_analysis["pricing_clarity"] += 30
                        
                        # Check for comparison table
                        tables = soup.find_all('table')
                        if tables or 'compare' in text_content:
                            pricing_analysis["comparison_table"] = True
                            pricing_analysis["optimization_score"] += 20
                        
                        # Check for recommended plan
                        if 'recommended' in text_content or 'popular' in text_content or 'best value' in text_content:
                            pricing_analysis["recommended_plan"] = True
                            pricing_analysis["optimization_score"] += 15
                        
                        # Check for free trial
                        if 'free trial' in text_content or 'try free' in text_content:
                            pricing_analysis["free_trial"] = True
                            pricing_analysis["optimization_score"] += 25
                        
                        # Check for money-back guarantee
                        if 'money back' in text_content or 'refund' in text_content or 'guarantee' in text_content:
                            pricing_analysis["money_back_guarantee"] = True
                            pricing_analysis["optimization_score"] += 20
                        
                        break
                        
                except:
                    continue
            
            # Generate recommendations
            if not pricing_analysis["pricing_found"]:
                pricing_analysis["recommendations"].append("Create a clear pricing page")
            
            if not pricing_analysis["comparison_table"]:
                pricing_analysis["recommendations"].append("Add comparison table to help decision making")
            
            if not pricing_analysis["recommended_plan"]:
                pricing_analysis["recommendations"].append("Highlight a recommended plan to guide choice")
            
            if not pricing_analysis["free_trial"]:
                pricing_analysis["recommendations"].append("Offer free trial to reduce purchase friction")
            
            if not pricing_analysis["money_back_guarantee"]:
                pricing_analysis["recommendations"].append("Add money-back guarantee for risk reversal")
            
        except Exception as e:
            logger.error(f"Pricing analysis failed for {domain}", error=str(e))
        
        return pricing_analysis
    
    async def _analyze_trust_indicators(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze trust indicators and credibility signals"""
        try:
            response = await client.get(f"https://{domain}")
            soup = BeautifulSoup(response.text, 'lxml')
            text_content = soup.get_text(separator=' ', strip=True).lower()
            
            trust_analysis = {
                "trust_score": 0,
                "security_badges": [],
                "certifications": [],
                "contact_visibility": {},
                "about_page": False,
                "privacy_policy": False,
                "terms_of_service": False,
                "social_media_links": [],
                "recommendations": []
            }
            
            # Check for security badges
            for badge in self.trust_signals["security_badges"]:
                if badge in text_content or badge in str(soup):
                    trust_analysis["security_badges"].append(badge)
                    trust_analysis["trust_score"] += 10
            
            # Check for certifications
            for cert in self.trust_signals["certifications"]:
                if cert in text_content:
                    trust_analysis["certifications"].append(cert)
                    trust_analysis["trust_score"] += 10
            
            # Check contact visibility
            contact_found = {
                "phone": bool(re.search(r'\+?\d{1,4}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}', response.text)),
                "email": bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', response.text)),
                "address": 'address' in text_content or 'headquarters' in text_content,
                "live_chat": any(chat in text_content for chat in ['chat', 'support', 'help'])
            }
            
            trust_analysis["contact_visibility"] = contact_found
            trust_analysis["trust_score"] += sum(10 for visible in contact_found.values() if visible)
            
            # Check for important pages
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                if 'about' in href or 'about' in text:
                    trust_analysis["about_page"] = True
                    trust_analysis["trust_score"] += 10
                
                if 'privacy' in href or 'privacy' in text:
                    trust_analysis["privacy_policy"] = True
                    trust_analysis["trust_score"] += 10
                
                if 'terms' in href or 'terms' in text:
                    trust_analysis["terms_of_service"] = True
                    trust_analysis["trust_score"] += 10
            
            # Check for social media links
            social_platforms = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube']
            for platform in social_platforms:
                if platform in str(soup):
                    trust_analysis["social_media_links"].append(platform)
                    trust_analysis["trust_score"] += 5
            
            # Generate recommendations
            if not trust_analysis["security_badges"]:
                trust_analysis["recommendations"].append("Add security badges (SSL, Norton, McAfee)")
            
            if not contact_found["phone"] and not contact_found["email"]:
                trust_analysis["recommendations"].append("Display contact information prominently")
            
            if not trust_analysis["about_page"]:
                trust_analysis["recommendations"].append("Create an About Us page to build credibility")
            
            if not trust_analysis["privacy_policy"]:
                trust_analysis["recommendations"].append("Add Privacy Policy - required for trust and compliance")
            
            if len(trust_analysis["social_media_links"]) < 2:
                trust_analysis["recommendations"].append("Add social media links for social proof")
            
            return trust_analysis
            
        except Exception as e:
            logger.error(f"Trust analysis failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    def _calculate_conversion_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall conversion optimization score"""
        scores = []
        
        # Psychological triggers score
        if "psychological_triggers" in results:
            scores.append(results["psychological_triggers"].get("overall_score", 0))
        
        # CTA optimization score
        if "cta_analysis" in results:
            scores.append(results["cta_analysis"].get("optimization_score", 0))
        
        # Value proposition score
        if "value_proposition" in results:
            scores.append(results["value_proposition"].get("clarity_score", 0))
        
        # Form optimization score
        if "form_analysis" in results:
            scores.append(results["form_analysis"].get("optimization_score", 0))
        
        # Trust score
        if "trust_signals" in results:
            scores.append(min(100, results["trust_signals"].get("trust_score", 0)))
        
        # Friction score (inverse - less friction is better)
        if "friction_points" in results:
            friction = results["friction_points"].get("friction_score", 0)
            scores.append(max(0, 100 - friction * 2))
        
        # Calculate weighted average
        if scores:
            return min(95, sum(scores) // len(scores))
        
        return 0
    
    def _identify_ab_tests(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify A/B testing opportunities"""
        ab_tests = []
        
        # CTA tests
        if "cta_analysis" in results:
            cta = results["cta_analysis"]
            if cta.get("total_ctas", 0) > 0:
                ab_tests.append({
                    "test_name": "CTA Button Copy",
                    "hypothesis": "Action-oriented CTA copy will increase clicks",
                    "variations": [
                        "Current: Generic CTA",
                        "Test A: Start Free Trial",
                        "Test B: Get Instant Access"
                    ],
                    "expected_impact": "15-25% increase in CTA clicks",
                    "difficulty": "Easy"
                })
        
        # Headline tests
        if "value_proposition" in results:
            value_prop = results["value_proposition"]
            if not value_prop.get("benefit_focused"):
                ab_tests.append({
                    "test_name": "Headline Value Proposition",
                    "hypothesis": "Benefit-focused headline will improve engagement",
                    "variations": [
                        "Current: Feature-focused",
                        "Test A: Benefit-focused with numbers",
                        "Test B: Problem/solution format"
                    ],
                    "expected_impact": "10-20% increase in time on page",
                    "difficulty": "Easy"
                })
        
        # Form length tests
        if "form_analysis" in results:
            forms = results["form_analysis"]
            if forms.get("form_details"):
                max_fields = max(f["field_count"] for f in forms["form_details"])
                if max_fields > 5:
                    ab_tests.append({
                        "test_name": "Form Field Reduction",
                        "hypothesis": "Fewer form fields will increase completions",
                        "variations": [
                            f"Current: {max_fields} fields",
                            "Test A: 3-field form (essential only)",
                            "Test B: Progressive disclosure"
                        ],
                        "expected_impact": "25-40% increase in form completions",
                        "difficulty": "Medium"
                    })
        
        # Social proof tests
        social = results.get("social_proof", {})
        if not social.get("testimonials_found"):
            ab_tests.append({
                "test_name": "Social Proof Addition",
                "hypothesis": "Adding testimonials will increase trust and conversions",
                "variations": [
                    "Current: No testimonials",
                    "Test A: 3 text testimonials",
                    "Test B: Video testimonial"
                ],
                "expected_impact": "8-15% increase in conversions",
                "difficulty": "Medium"
            })
        
        # Urgency tests
        urgency = results.get("urgency_scarcity", {})
        if not urgency.get("time_limited"):
            ab_tests.append({
                "test_name": "Urgency Elements",
                "hypothesis": "Time-limited offers will drive immediate action",
                "variations": [
                    "Current: No urgency",
                    "Test A: 24-hour countdown timer",
                    "Test B: Limited spots remaining"
                ],
                "expected_impact": "20-35% increase in conversion rate",
                "difficulty": "Easy"
            })
        
        return ab_tests[:5]  # Return top 5 test opportunities
    
    def _identify_quick_wins(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify quick conversion wins"""
        quick_wins = []
        
        # Missing CTAs
        if "cta_analysis" in results:
            cta = results["cta_analysis"]
            if cta.get("total_ctas", 0) < 3:
                quick_wins.append({
                    "action": "Add more CTAs",
                    "implementation": "Add CTA buttons above fold and after value props",
                    "effort": "30 minutes",
                    "expected_impact": "5-10% conversion increase"
                })
        
        # Trust signals
        if "trust_signals" in results:
            trust = results["trust_signals"]
            if not trust.get("security_badges"):
                quick_wins.append({
                    "action": "Add security badges",
                    "implementation": "Display SSL, payment security badges near CTAs",
                    "effort": "1 hour",
                    "expected_impact": "3-7% conversion increase"
                })
        
        # Form optimization
        if "form_analysis" in results:
            forms = results["form_analysis"]
            if forms.get("form_details"):
                for form in forms["form_details"]:
                    if not form.get("has_placeholders"):
                        quick_wins.append({
                            "action": "Add form placeholders",
                            "implementation": "Add helpful placeholder text to all form fields",
                            "effort": "30 minutes",
                            "expected_impact": "2-5% form completion increase"
                        })
                        break
        
        # Value proposition
        if "value_proposition" in results:
            value_prop = results["value_proposition"]
            if not value_prop.get("headline_found"):
                quick_wins.append({
                    "action": "Add clear headline",
                    "implementation": "Create benefit-focused H1 above fold",
                    "effort": "1 hour",
                    "expected_impact": "8-12% engagement increase"
                })
        
        # Loading speed CTA
        if "friction_points" in results:
            friction = results["friction_points"]
            if friction.get("friction_score", 0) > 20:
                quick_wins.append({
                    "action": "Reduce form friction",
                    "implementation": "Remove optional fields, add 'No credit card required'",
                    "effort": "2 hours",
                    "expected_impact": "15-25% conversion increase"
                })
        
        return quick_wins
    
    def _generate_conversion_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized conversion recommendations"""
        recommendations = []
        
        # Score-based prioritization
        conversion_score = results.get("conversion_score", 0)
        
        if conversion_score < 40:
            recommendations.append({
                "priority": 1,
                "category": "Critical",
                "issue": "Poor conversion optimization",
                "action": "Complete conversion audit and redesign",
                "impact": "Could double conversion rates"
            })
        
        # Psychological triggers
        psych = results.get("psychological_triggers", {})
        if psych.get("missing_triggers"):
            missing = psych["missing_triggers"][:3]
            recommendations.append({
                "priority": 2,
                "category": "Psychology",
                "issue": f"Missing triggers: {', '.join(missing)}",
                "action": "Implement psychological triggers throughout funnel",
                "impact": "15-30% conversion increase"
            })
        
        # Form optimization
        if "form_analysis" in results:
            forms = results["form_analysis"]
            if forms.get("optimization_score", 100) < 70:
                recommendations.append({
                    "priority": 2,
                    "category": "Forms",
                    "issue": "Suboptimal form design",
                    "action": "Reduce fields, add progress indicators, optimize layout",
                    "impact": "20-40% form completion increase"
                })
        
        # Trust and credibility
        if "trust_signals" in results:
            trust = results["trust_signals"]
            if trust.get("trust_score", 0) < 50:
                recommendations.append({
                    "priority": 3,
                    "category": "Trust",
                    "issue": "Insufficient trust signals",
                    "action": "Add testimonials, badges, guarantees, contact info",
                    "impact": "10-20% conversion increase"
                })
        
        # Mobile optimization
        if conversion_score < 70:
            recommendations.append({
                "priority": 3,
                "category": "Mobile",
                "issue": "Check mobile conversion flow",
                "action": "Optimize forms, CTAs, and checkout for mobile",
                "impact": "Mobile conversions could increase 30-50%"
            })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])
        
        return recommendations[:10]