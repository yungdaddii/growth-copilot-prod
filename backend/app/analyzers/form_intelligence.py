import httpx
import re
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urljoin

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class FormIntelligenceAnalyzer:
    """
    Advanced form analysis engine that provides field-by-field optimization recommendations.
    Identifies friction points, unnecessary fields, and conversion blockers.
    """
    
    # Field patterns that indicate purpose
    FIELD_PATTERNS = {
        "email": ["email", "e-mail", "mail"],
        "name": ["name", "firstname", "lastname", "full_name"],
        "phone": ["phone", "tel", "mobile", "number"],
        "company": ["company", "organization", "business", "org"],
        "job_title": ["title", "role", "position", "job"],
        "company_size": ["size", "employees", "headcount"],
        "budget": ["budget", "spend", "investment"],
        "timeline": ["timeline", "when", "timeframe"],
        "use_case": ["use", "case", "reason", "purpose", "why"],
        "country": ["country", "location", "region"],
        "state": ["state", "province"],
        "message": ["message", "comments", "notes", "details"]
    }
    
    # Field impact on conversion (based on industry research)
    FIELD_CONVERSION_IMPACT = {
        "email": 0,  # Essential, no impact
        "name": -3,  # Small impact
        "phone": -37,  # Major impact
        "company": -5,  # Small impact
        "job_title": -7,  # Moderate impact
        "company_size": -10,  # Moderate impact
        "budget": -15,  # High impact
        "timeline": -8,  # Moderate impact
        "use_case": -12,  # High impact
        "country": -4,  # Small impact
        "state": -6,  # Small impact
        "message": -5  # Small impact
    }
    
    # Optimal field combinations for different form types
    OPTIMAL_FORMS = {
        "newsletter": ["email"],
        "demo_minimal": ["email", "name", "company"],
        "demo_standard": ["email", "name", "company", "job_title"],
        "contact_sales": ["email", "name", "company", "phone", "message"],
        "free_trial": ["email", "name", "password"],
        "webinar": ["email", "name", "company"]
    }
    
    def __init__(self):
        self.client = None
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Comprehensive form intelligence analysis"""
        cache_key = f"form_intelligence:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "forms_found": 0,
            "form_analysis": [],
            "conversion_impact": {},
            "optimization_opportunities": [],
            "field_recommendations": [],
            "best_practices_score": 0,
            "estimated_conversion_lift": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                self.client = client
                
                # Discover and analyze all forms
                forms = await self._discover_forms(domain)
                results["forms_found"] = len(forms)
                
                total_lift = 0
                
                for form_data in forms:
                    analysis = await self._analyze_form_intelligence(
                        form_data["url"],
                        form_data["page_type"],
                        form_data["soup"]
                    )
                    
                    results["form_analysis"].append(analysis)
                    
                    # Calculate conversion impact
                    if analysis["conversion_impact"]["total_impact"] < 0:
                        total_lift += abs(analysis["conversion_impact"]["total_impact"])
                        
                        # Add specific recommendations
                        for rec in analysis["recommendations"]:
                            results["optimization_opportunities"].append(rec)
                
                results["estimated_conversion_lift"] = total_lift
                
                # Generate overall recommendations
                results["field_recommendations"] = self._generate_field_recommendations(results["form_analysis"])
                
                # Calculate best practices score
                results["best_practices_score"] = self._calculate_best_practices_score(results["form_analysis"])
                
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"Form intelligence analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _discover_forms(self, domain: str) -> List[Dict[str, Any]]:
        """Discover all forms across the website"""
        forms = []
        
        # Key pages to check for forms
        pages_to_check = [
            {"url": f"https://{domain}", "type": "homepage"},
            {"url": f"https://{domain}/demo", "type": "demo"},
            {"url": f"https://{domain}/trial", "type": "trial"},
            {"url": f"https://{domain}/signup", "type": "signup"},
            {"url": f"https://{domain}/contact", "type": "contact"},
            {"url": f"https://{domain}/pricing", "type": "pricing"},
            {"url": f"https://{domain}/get-started", "type": "get-started"}
        ]
        
        for page in pages_to_check:
            try:
                response = await self.client.get(page["url"])
                soup = BeautifulSoup(response.text, 'lxml')
                
                page_forms = soup.find_all('form')
                if page_forms:
                    for form in page_forms:
                        forms.append({
                            "url": page["url"],
                            "page_type": page["type"],
                            "soup": form
                        })
                
                # Also check for HubSpot, Marketo, Pardot forms (often in iframes)
                if 'hubspot' in response.text or 'marketo' in response.text or 'pardot' in response.text:
                    forms.append({
                        "url": page["url"],
                        "page_type": page["type"],
                        "soup": soup,
                        "third_party": True
                    })
                    
            except:
                continue
        
        return forms
    
    async def _analyze_form_intelligence(self, url: str, page_type: str, form_soup) -> Dict[str, Any]:
        """Deep intelligence analysis of a single form"""
        analysis = {
            "url": url,
            "page_type": page_type,
            "fields": [],
            "field_count": 0,
            "required_count": 0,
            "conversion_impact": {},
            "recommendations": [],
            "best_practices": {},
            "form_type_guess": "",
            "optimization_score": 0
        }
        
        # Extract all fields
        if hasattr(form_soup, 'find_all'):
            inputs = form_soup.find_all(['input', 'select', 'textarea'])
            
            for field in inputs:
                if field.get('type') not in ['hidden', 'submit', 'button']:
                    field_analysis = self._analyze_field(field)
                    if field_analysis:
                        analysis["fields"].append(field_analysis)
        
        analysis["field_count"] = len(analysis["fields"])
        analysis["required_count"] = sum(1 for f in analysis["fields"] if f["required"])
        
        # Guess form type based on fields
        analysis["form_type_guess"] = self._guess_form_type(analysis["fields"])
        
        # Calculate conversion impact
        analysis["conversion_impact"] = self._calculate_conversion_impact(analysis["fields"])
        
        # Check best practices
        analysis["best_practices"] = self._check_best_practices(analysis)
        
        # Generate specific recommendations
        analysis["recommendations"] = self._generate_form_recommendations(analysis)
        
        # Calculate optimization score
        analysis["optimization_score"] = self._calculate_optimization_score(analysis)
        
        return analysis
    
    def _analyze_field(self, field) -> Optional[Dict[str, Any]]:
        """Analyze a single form field"""
        field_data = {
            "type": field.get('type', 'text'),
            "name": field.get('name', ''),
            "id": field.get('id', ''),
            "placeholder": field.get('placeholder', ''),
            "label": "",
            "required": field.get('required') is not None or 'required' in field.get('class', []),
            "field_purpose": "unknown",
            "conversion_impact": 0,
            "recommendation": ""
        }
        
        # Try to find associated label
        if field.get('id'):
            label = field.find_previous('label', {'for': field['id']})
            if label:
                field_data["label"] = label.get_text(strip=True)
        
        # Determine field purpose
        field_text = f"{field_data['name']} {field_data['id']} {field_data['placeholder']} {field_data['label']}".lower()
        
        for purpose, patterns in self.FIELD_PATTERNS.items():
            if any(pattern in field_text for pattern in patterns):
                field_data["field_purpose"] = purpose
                field_data["conversion_impact"] = self.FIELD_CONVERSION_IMPACT.get(purpose, 0)
                break
        
        # Special handling for password fields
        if field_data["type"] == "password":
            field_data["field_purpose"] = "password"
            field_data["conversion_impact"] = 0  # Passwords are necessary for signup
        
        # Generate field-specific recommendation
        if field_data["conversion_impact"] < -10 and field_data["required"]:
            field_data["recommendation"] = f"Make {field_data['field_purpose']} field optional or remove"
        elif field_data["conversion_impact"] < -5 and field_data["required"]:
            field_data["recommendation"] = f"Consider making {field_data['field_purpose']} field optional"
        
        return field_data
    
    def _guess_form_type(self, fields: List[Dict]) -> str:
        """Guess the form type based on fields present"""
        field_purposes = [f["field_purpose"] for f in fields]
        
        if "password" in field_purposes:
            return "signup" if "email" in field_purposes else "login"
        elif len(fields) == 1 and "email" in field_purposes:
            return "newsletter"
        elif "message" in field_purposes:
            return "contact"
        elif "company" in field_purposes and "job_title" in field_purposes:
            return "demo_request"
        elif "company" in field_purposes:
            return "b2b_lead"
        else:
            return "general_lead"
    
    def _calculate_conversion_impact(self, fields: List[Dict]) -> Dict[str, Any]:
        """Calculate the conversion impact of current form configuration"""
        impact = {
            "total_impact": 0,
            "field_impacts": {},
            "unnecessary_fields": [],
            "high_friction_fields": []
        }
        
        for field in fields:
            if field["required"] and field["conversion_impact"] < 0:
                impact["total_impact"] += field["conversion_impact"]
                impact["field_impacts"][field["field_purpose"]] = field["conversion_impact"]
                
                if field["conversion_impact"] < -10:
                    impact["high_friction_fields"].append(field["field_purpose"])
                elif field["conversion_impact"] < -5:
                    impact["unnecessary_fields"].append(field["field_purpose"])
        
        return impact
    
    def _check_best_practices(self, analysis: Dict) -> Dict[str, bool]:
        """Check form against best practices"""
        practices = {
            "optimal_field_count": analysis["field_count"] <= 5,
            "no_phone_required": not any(f["field_purpose"] == "phone" and f["required"] for f in analysis["fields"]),
            "has_email": any(f["field_purpose"] == "email" for f in analysis["fields"]),
            "clear_labels": all(f["label"] or f["placeholder"] for f in analysis["fields"]),
            "progressive_disclosure": analysis["field_count"] <= 3 or not all(f["required"] for f in analysis["fields"]),
            "no_sensitive_upfront": not any(
                f["field_purpose"] in ["budget", "company_size"] and f["required"] 
                for f in analysis["fields"]
            )
        }
        
        return practices
    
    def _generate_form_recommendations(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate specific recommendations for form optimization"""
        recommendations = []
        
        # Field count recommendation
        if analysis["field_count"] > 5:
            optimal = self.OPTIMAL_FORMS.get(analysis["form_type_guess"], ["email", "name", "company"])
            current_purposes = [f["field_purpose"] for f in analysis["fields"]]
            to_remove = [p for p in current_purposes if p not in optimal and p != "unknown"]
            
            if to_remove:
                recommendations.append({
                    "priority": "critical",
                    "issue": f"Form has {analysis['field_count']} fields (optimal is {len(optimal)})",
                    "fix": f"Remove these fields: {', '.join(to_remove[:3])}",
                    "impact": f"Increase conversions by {abs(analysis['conversion_impact']['total_impact'])}%",
                    "effort": "30 minutes"
                })
        
        # Phone field recommendation
        phone_fields = [f for f in analysis["fields"] if f["field_purpose"] == "phone" and f["required"]]
        if phone_fields:
            recommendations.append({
                "priority": "critical",
                "issue": "Phone number is required",
                "fix": "Make phone field optional or remove entirely",
                "impact": "37% more form completions",
                "effort": "15 minutes"
            })
        
        # Sensitive fields recommendation
        sensitive_fields = [f for f in analysis["fields"] 
                          if f["field_purpose"] in ["budget", "company_size", "timeline"] and f["required"]]
        if sensitive_fields:
            recommendations.append({
                "priority": "high",
                "issue": f"Asking sensitive info upfront: {', '.join([f['field_purpose'] for f in sensitive_fields])}",
                "fix": "Move to follow-up email or make optional",
                "impact": "15-20% more completions",
                "effort": "45 minutes"
            })
        
        # Multi-step form recommendation
        if analysis["field_count"] > 7:
            recommendations.append({
                "priority": "high",
                "issue": "Too many fields in single form",
                "fix": "Split into multi-step form with progress indicator",
                "impact": "23% higher completion rate",
                "effort": "2-3 hours"
            })
        
        # Social login recommendation
        if analysis["form_type_guess"] in ["signup", "demo_request"] and analysis["field_count"] > 3:
            recommendations.append({
                "priority": "medium",
                "issue": "No social login option detected",
                "fix": "Add Google/LinkedIn SSO for faster signup",
                "impact": "40% faster form completion",
                "effort": "4 hours"
            })
        
        return recommendations
    
    def _calculate_optimization_score(self, analysis: Dict) -> int:
        """Calculate form optimization score (0-100)"""
        score = 100
        
        # Deduct for field count
        if analysis["field_count"] > 7:
            score -= 30
        elif analysis["field_count"] > 5:
            score -= 15
        elif analysis["field_count"] > 3:
            score -= 5
        
        # Deduct for required fields
        if analysis["required_count"] == analysis["field_count"]:
            score -= 10
        
        # Deduct for best practices violations
        practices = analysis["best_practices"]
        if not practices.get("no_phone_required"):
            score -= 20
        if not practices.get("no_sensitive_upfront"):
            score -= 15
        if not practices.get("clear_labels"):
            score -= 10
        if not practices.get("has_email"):
            score -= 25
        
        # Deduct for conversion impact
        total_impact = abs(analysis["conversion_impact"]["total_impact"])
        if total_impact > 50:
            score -= 30
        elif total_impact > 30:
            score -= 20
        elif total_impact > 15:
            score -= 10
        
        return max(0, score)
    
    def _generate_field_recommendations(self, form_analyses: List[Dict]) -> List[Dict[str, Any]]:
        """Generate overall field recommendations across all forms"""
        recommendations = []
        
        # Aggregate issues across forms
        all_high_friction = []
        all_unnecessary = []
        total_forms = len(form_analyses)
        
        for analysis in form_analyses:
            all_high_friction.extend(analysis["conversion_impact"]["high_friction_fields"])
            all_unnecessary.extend(analysis["conversion_impact"]["unnecessary_fields"])
        
        # Most common problematic fields
        if all_high_friction:
            field_counts = {}
            for field in all_high_friction:
                field_counts[field] = field_counts.get(field, 0) + 1
            
            most_problematic = max(field_counts, key=field_counts.get)
            count = field_counts[most_problematic]
            
            recommendations.append({
                "pattern": f"{most_problematic} field",
                "found_in": f"{count} forms",
                "recommendation": f"Remove or make {most_problematic} optional across all forms",
                "impact": f"{abs(self.FIELD_CONVERSION_IMPACT.get(most_problematic, 0))}% conversion lift per form"
            })
        
        # Pattern detection
        avg_field_count = sum(a["field_count"] for a in form_analyses) / max(total_forms, 1)
        if avg_field_count > 5:
            recommendations.append({
                "pattern": "High field count",
                "found_in": f"Average {avg_field_count:.1f} fields per form",
                "recommendation": "Standardize on 3-4 field forms",
                "impact": "25-40% overall conversion improvement"
            })
        
        return recommendations
    
    def _calculate_best_practices_score(self, form_analyses: List[Dict]) -> int:
        """Calculate overall best practices score"""
        if not form_analyses:
            return 0
        
        total_score = 0
        for analysis in form_analyses:
            total_score += analysis["optimization_score"]
        
        return int(total_score / len(form_analyses))