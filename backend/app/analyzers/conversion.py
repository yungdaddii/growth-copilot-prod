import httpx
from typing import Dict, Any, List
import structlog
from bs4 import BeautifulSoup
import re

from app.models.analysis import Industry
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class ConversionAnalyzer:
    def __init__(self):
        self.conversion_patterns = {
            "demo": ["demo", "get demo", "request demo", "book demo", "schedule demo"],
            "trial": ["free trial", "start trial", "try free", "try it free", "14-day trial"],
            "signup": ["sign up", "get started", "create account", "start now", "join"],
            "contact": ["contact us", "get in touch", "talk to sales", "contact sales"],
            "pricing": ["pricing", "plans", "see pricing", "view pricing", "price"]
        }
    
    async def analyze(self, domain: str, industry: Industry) -> Dict[str, Any]:
        cache_key = f"conversion:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "score": 0,
            "form_fields": 0,
            "has_free_trial": False,
            "has_demo": False,
            "has_pricing": False,
            "cta_clarity": "weak",
            "cta_text": "",
            "conversion_paths": [],
            "friction_points": [],
            "trust_signals": [],
            "weak_cta": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Analyze forms
                forms_data = self._analyze_forms(soup)
                results.update(forms_data)
                
                # Analyze CTAs
                cta_data = self._analyze_ctas(soup)
                results.update(cta_data)
                
                # Analyze conversion paths
                paths_data = self._analyze_conversion_paths(soup, industry)
                results.update(paths_data)
                
                # Analyze trust signals
                trust_data = self._analyze_trust_signals(soup)
                results.update(trust_data)
                
                # Calculate overall score
                results["score"] = self._calculate_conversion_score(results, industry)
                
                await cache_result(cache_key, results, ttl=3600)
                
        except Exception as e:
            logger.error("Conversion analysis failed", domain=domain, error=str(e))
        
        return results
    
    def _analyze_forms(self, soup: BeautifulSoup) -> Dict:
        results = {
            "form_fields": 0,
            "required_fields": [],
            "form_issues": []
        }
        
        forms = soup.find_all('form')
        if forms:
            # Analyze the most prominent form (usually the first one)
            main_form = forms[0]
            
            # Count input fields
            inputs = main_form.find_all(['input', 'textarea', 'select'])
            visible_inputs = [i for i in inputs if i.get('type') not in ['hidden', 'submit', 'button']]
            results["form_fields"] = len(visible_inputs)
            
            # Check required fields
            required = [i.get('name', i.get('id', 'unnamed')) for i in visible_inputs if i.get('required')]
            results["required_fields"] = required
            
            # Common form issues
            if results["form_fields"] > 6:
                results["form_issues"].append("Too many fields")
            
            if any('phone' in str(i).lower() for i in visible_inputs):
                if not any('optional' in str(i).lower() for i in visible_inputs):
                    results["form_issues"].append("Phone required without being optional")
            
            # Check for progressive disclosure
            if not main_form.find_all(['div', 'section'], class_=re.compile(r'step|stage|progress')):
                if results["form_fields"] > 8:
                    results["form_issues"].append("Long form without progressive disclosure")
        
        return results
    
    def _analyze_ctas(self, soup: BeautifulSoup) -> Dict:
        results = {
            "cta_clarity": "weak",
            "cta_text": "",
            "weak_cta": False,
            "cta_count": 0,
            "primary_cta": ""
        }
        
        # Find all CTAs (buttons and prominent links)
        ctas = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta', re.I))
        results["cta_count"] = len(ctas)
        
        if ctas:
            # Get primary CTA (usually the first prominent one)
            primary_cta = ctas[0].get_text(strip=True)
            results["primary_cta"] = primary_cta
            results["cta_text"] = primary_cta
            
            # Analyze CTA clarity
            strong_cta_words = ["start", "get", "try", "demo", "free", "now", "instant"]
            weak_cta_words = ["submit", "send", "next", "continue", "learn more"]
            
            cta_lower = primary_cta.lower()
            
            if any(word in cta_lower for word in strong_cta_words):
                results["cta_clarity"] = "strong"
            elif any(word in cta_lower for word in weak_cta_words):
                results["cta_clarity"] = "weak"
                results["weak_cta"] = True
            else:
                results["cta_clarity"] = "medium"
        
        # Check for free trial
        page_text = soup.get_text().lower()
        results["has_free_trial"] = any(pattern in page_text for pattern in self.conversion_patterns["trial"])
        results["has_demo"] = any(pattern in page_text for pattern in self.conversion_patterns["demo"])
        results["has_pricing"] = any(pattern in page_text for pattern in self.conversion_patterns["pricing"])
        
        return results
    
    def _analyze_conversion_paths(self, soup: BeautifulSoup, industry: Industry) -> Dict:
        results = {
            "conversion_paths": [],
            "friction_points": []
        }
        
        # Identify main conversion paths
        paths = []
        
        # Check navigation for conversion pages
        nav = soup.find(['nav', 'header'])
        if nav:
            nav_links = nav.find_all('a')
            for link in nav_links:
                text = link.get_text(strip=True).lower()
                for path_type, patterns in self.conversion_patterns.items():
                    if any(p in text for p in patterns):
                        paths.append({
                            "type": path_type,
                            "text": link.get_text(strip=True),
                            "visible": True
                        })
        
        results["conversion_paths"] = paths
        
        # Identify friction points
        friction = []
        
        # Check if pricing is hidden
        if not results.get("has_pricing") and industry == Industry.SAAS:
            friction.append("Pricing not transparent")
        
        # Check if demo is the only option (no trial)
        if results.get("has_demo") and not results.get("has_free_trial") and industry == Industry.SAAS:
            friction.append("Demo-only approach (no self-serve)")
        
        # Check for social proof above fold
        first_section = soup.find(['section', 'div'], class_=re.compile(r'hero|banner|header'))
        if first_section:
            logos = first_section.find_all(['img'], alt=re.compile(r'logo|client|customer', re.I))
            if len(logos) < 3:
                friction.append("No social proof above fold")
        
        results["friction_points"] = friction
        
        return results
    
    def _analyze_trust_signals(self, soup: BeautifulSoup) -> Dict:
        results = {
            "trust_signals": [],
            "trust_score": 0
        }
        
        signals = []
        score = 0
        
        # Check for testimonials
        if soup.find_all(class_=re.compile(r'testimonial|review|quote', re.I)):
            signals.append("testimonials")
            score += 10
        
        # Check for client logos
        if soup.find_all(['img'], alt=re.compile(r'logo|client|customer', re.I)):
            signals.append("client_logos")
            score += 10
        
        # Check for security badges
        security_terms = ['soc2', 'iso', 'gdpr', 'hipaa', 'secure', 'encrypted']
        page_text = soup.get_text().lower()
        for term in security_terms:
            if term in page_text:
                signals.append(f"{term}_compliant")
                score += 5
                break
        
        # Check for ratings/badges
        if soup.find_all(['img', 'div'], class_=re.compile(r'rating|badge|award', re.I)):
            signals.append("ratings_badges")
            score += 10
        
        # Check for case studies
        if soup.find_all(['a'], text=re.compile(r'case study|success story', re.I)):
            signals.append("case_studies")
            score += 10
        
        results["trust_signals"] = signals
        results["trust_score"] = min(score, 50)  # Cap at 50
        
        return results
    
    def _calculate_conversion_score(self, data: Dict, industry: Industry) -> int:
        score = 50  # Base score
        
        # Form optimization
        if data["form_fields"] <= 4:
            score += 20
        elif data["form_fields"] <= 6:
            score += 10
        elif data["form_fields"] > 10:
            score -= 20
        
        # CTA clarity
        if data["cta_clarity"] == "strong":
            score += 10
        elif data["cta_clarity"] == "weak":
            score -= 10
        
        # Trust signals
        score += data.get("trust_score", 0) // 2
        
        # Conversion paths
        if data["has_free_trial"] and industry == Industry.SAAS:
            score += 15
        if data["has_pricing"]:
            score += 10
        
        # Friction points
        score -= len(data.get("friction_points", [])) * 5
        
        return max(0, min(100, score))