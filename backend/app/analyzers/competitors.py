import httpx
from typing import Dict, Any, List, Optional
import structlog
from bs4 import BeautifulSoup
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.analysis import Industry, CompetitorCache
from app.utils.cache import cache_result, get_cached_result
from app.config import settings
from app.core.ai_providers import AIProviderFactory

logger = structlog.get_logger()


class CompetitorAnalyzer:
    def __init__(self):
        # Use the new AI provider factory
        self.ai_provider = AIProviderFactory.create_provider()
    
    async def analyze(
        self, 
        domain: str, 
        industry: Industry,
        db: AsyncSession
    ) -> Dict[str, Any]:
        cache_key = f"competitors:{domain}:{industry.value}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "competitors": [],
            "your_features": [],
            "missing_features": [],
            "competitive_advantages": [],
            "competitive_gaps": [],
            "industry": industry.value
        }
        
        try:
            # First, analyze the target site to understand what it does
            your_analysis = await self._analyze_your_site(domain)
            results["your_features"] = your_analysis.get("features", [])
            results["your_description"] = your_analysis.get("description", "")
            
            # Identify actual competitors based on the site's content
            competitors = await self._identify_competitors(
                domain, 
                your_analysis.get("description", ""),
                your_analysis.get("keywords", []),
                industry
            )
            
            # Analyze each competitor
            for comp_domain in competitors[:3]:  # Top 3 competitors
                comp_analysis = await self._analyze_competitor(comp_domain, db)
                if comp_analysis:
                    results["competitors"].append(comp_analysis)
            
            # Find gaps and advantages
            if results["competitors"]:
                all_competitor_features = set()
                for comp in results["competitors"]:
                    all_competitor_features.update(comp.get("features", []))
                
                your_features_set = set(results["your_features"])
                results["missing_features"] = list(all_competitor_features - your_features_set)
                results["competitive_advantages"] = list(your_features_set - all_competitor_features)
                
                # Analyze specific gaps with competitor details
                results["competitive_gaps"] = self._analyze_gaps(
                    your_features_set,
                    all_competitor_features,
                    results["competitors"]
                )
                
                # Add detailed competitor comparison
                results["competitor_comparison"] = self._create_detailed_comparison(
                    results["your_features"],
                    results["competitors"]
                )
            
            await cache_result(cache_key, results, ttl=86400)  # Cache for 24 hours
            
        except Exception as e:
            logger.error("Competitor analysis failed", domain=domain, error=str(e))
        
        return results
    
    async def _identify_competitors(
        self, 
        domain: str, 
        description: str,
        keywords: List[str],
        industry: Industry
    ) -> List[str]:
        """Identify actual competitors based on site content and industry"""
        competitors = []
        
        try:
            # Use AI to identify competitors based on the site's actual content
            if self.ai_provider and description:
                prompt = f"""Based on this website description: "{description}"
                And keywords: {', '.join(keywords[:10])}
                Industry: {industry.value}
                
                List 3-5 REAL, EXISTING competitor companies (just domains, no explanation).
                Only include actual companies that exist today and offer competing products.
                If this is a Kubernetes/container platform, competitors would be Rancher, OpenShift, etc.
                If this is a data integration/ETL platform, competitors would be Fivetran, Stitch, Matillion, etc.
                Format: domain1.com, domain2.com, domain3.com
                
                IMPORTANT: Only real companies, not open source projects or frameworks."""
                
                messages = [
                    {"role": "system", "content": "You are a market analyst identifying real competitors."},
                    {"role": "user", "content": prompt}
                ]
                
                comp_text = await self.ai_provider.generate_completion(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=100
                )
                # Extract domains from response
                domains = re.findall(r'[\w\-]+\.(?:com|io|co|net|org|ai)', comp_text)
                competitors.extend(domains)
            
            # Fallback: Use search to find competitors (would need search API)
            if not competitors:
                # More intelligent fallbacks based on actual content
                desc_lower = description.lower()
                keywords_lower = [k.lower() for k in keywords]
                
                if industry == Industry.SAAS:
                    # Better pattern matching for specific SaaS types
                    if any(term in desc_lower for term in ["data integration", "data pipeline", "etl", "elt", "data replication", "data sync"]):
                        competitors = ["fivetran.com", "stitchdata.com", "matillion.com"]
                    elif any(term in desc_lower for term in ["container", "kubernetes", "k8s", "orchestration", "docker"]):
                        competitors = ["rancher.com", "openshift.com", "portainer.io"]
                    elif any(term in desc_lower for term in ["cloud native", "platform", "paas"]):
                        competitors = ["platform9.com", "d2iq.com", "rafay.co"]
                    elif "crm" in desc_lower:
                        competitors = ["salesforce.com", "hubspot.com", "pipedrive.com"]
                    elif "analytics" in desc_lower and not "website" in desc_lower:
                        competitors = ["mixpanel.com", "amplitude.com", "segment.com"]
                    elif any(term in desc_lower for term in ["workflow", "automation", "orchestration"]) and "data" not in desc_lower:
                        competitors = ["zapier.com", "make.com", "workato.com"]
                    else:
                        # Don't provide wrong competitors - empty is better
                        competitors = []
                elif industry == Industry.ECOMMERCE:
                    competitors = ["shopify.com", "woocommerce.com", "bigcommerce.com"]
                elif industry == Industry.MARKETPLACE:
                    competitors = ["etsy.com", "ebay.com", "amazon.com"]
                else:
                    # For unknown industries, don't guess
                    competitors = []
            
        except Exception as e:
            logger.error(f"Failed to identify competitors for {domain}", error=str(e))
        
        return competitors[:5]  # Return top 5
    
    async def _analyze_your_site(self, domain: str) -> Dict:
        """Analyze the target site to understand what it does"""
        analysis = {
            "features": [],
            "description": "",
            "keywords": [],
            "value_props": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=10.0, follow_redirects=True)
                soup = BeautifulSoup(response.text, 'lxml')
                content = response.text.lower()
                
                # Extract description from meta or content
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    analysis["description"] = meta_desc.get('content', '')
                else:
                    # Get first paragraph or hero text
                    first_p = soup.find('p')
                    if first_p:
                        analysis["description"] = first_p.get_text(strip=True)[:200]
                
                # Extract keywords from headings
                headings = soup.find_all(['h1', 'h2', 'h3'])[:10]
                keywords = []
                for h in headings:
                    text = h.get_text(strip=True)
                    # Extract meaningful words
                    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
                    keywords.extend(words)
                analysis["keywords"] = list(set(keywords))[:20]
                
                # Detect features with more granular detection
                if "free trial" in content or "try free" in content or "start free" in content:
                    analysis["features"].append("free_trial")
                
                # Check for pricing page link
                pricing_link = soup.find('a', href=re.compile(r'/pricing|/plans|/price', re.I))
                if pricing_link and "contact" not in pricing_link.get_text(strip=True).lower():
                    analysis["features"].append("public_pricing")
                elif "pricing" in content and "contact us for pricing" not in content:
                    analysis["features"].append("public_pricing")
                
                if "book demo" in content or "request demo" in content or "schedule demo" in content:
                    analysis["features"].append("demo")
                
                if "api" in content and ("docs" in content or "documentation" in content):
                    analysis["features"].append("api_access")
                
                if "testimonial" in content or "case study" in content or "customer story" in content:
                    analysis["features"].append("social_proof")
                
                if "soc2" in content or "soc 2" in content or "iso 27001" in content or "gdpr" in content:
                    analysis["features"].append("enterprise_security")
                
                if "24/7" in content or "24x7" in content:
                    analysis["features"].append("24_7_support")
                elif "support" in content:
                    analysis["features"].append("customer_support")
                
                if "sign up" in content or "get started" in content:
                    analysis["features"].append("self_service")
                
                if "integration" in content or "integrate" in content:
                    analysis["features"].append("integrations")
                
                if "mobile app" in content or "ios" in content or "android" in content:
                    analysis["features"].append("mobile_app")
                
                # Extract value propositions
                value_props = []
                hero = soup.find(['section', 'div'], class_=re.compile(r'hero|banner'))
                if hero:
                    hero_text = hero.get_text(strip=True)
                    # Look for benefit statements
                    sentences = hero_text.split('.')
                    for sent in sentences[:3]:
                        if len(sent) > 20 and len(sent) < 150:
                            value_props.append(sent.strip())
                analysis["value_props"] = value_props
                
        except Exception as e:
            logger.error(f"Failed to analyze site {domain}", error=str(e))
        
        return analysis
    
    async def _analyze_competitor(self, domain: str, db: AsyncSession) -> Optional[Dict]:
        """Analyze a competitor's site"""
        try:
            # Check cache first
            result = await db.execute(
                select(CompetitorCache).where(CompetitorCache.domain == domain)
            )
            cached = result.scalar_one_or_none()
            
            if cached and cached.metrics:
                return {
                    "domain": domain,
                    "name": domain.split('.')[0].title(),
                    "features": cached.features or [],
                    "pricing_model": cached.pricing_model,
                    "traffic_estimate": cached.traffic_estimate,
                    **cached.metrics
                }
            
            # Analyze competitor site
            analysis = await self._analyze_your_site(domain)
            
            return {
                "domain": domain,
                "name": domain.split('.')[0].title(),
                "features": analysis.get("features", []),
                "description": analysis.get("description", ""),
                "value_props": analysis.get("value_props", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze competitor {domain}", error=str(e))
            return None
    
    def _analyze_gaps(
        self, 
        your_features: set, 
        competitor_features: set,
        competitors: List[Dict]
    ) -> List[Dict]:
        """Analyze competitive gaps with specific competitor names"""
        gaps = []
        
        feature_definitions = [
            ("free_trial", "Free Trial", "high", "14-day free trial with full feature access"),
            ("public_pricing", "Transparent Pricing", "high", "Public pricing page with clear tiers"),
            ("demo", "Product Demo", "high", "Interactive demo or video walkthrough"),
            ("api_access", "API Documentation", "medium", "Developer portal with API docs"),
            ("social_proof", "Customer Testimonials", "medium", "Case studies and success stories"),
            ("enterprise_security", "Security Compliance", "high", "SOC2, ISO 27001 certifications"),
            ("self_service", "Self-Service Signup", "high", "Instant account creation without sales"),
            ("integrations", "Third-party Integrations", "medium", "Pre-built connectors to popular tools"),
            ("24_7_support", "24/7 Support", "medium", "Round-the-clock customer support")
        ]
        
        for feature_key, feature_name, impact, description in feature_definitions:
            if feature_key in competitor_features and feature_key not in your_features:
                # Get specific competitor names who have this feature
                comps_with_feature = [
                    c.get("name", c.get("domain", "").split('.')[0].title())
                    for c in competitors 
                    if feature_key in c.get("features", [])
                ]
                
                if comps_with_feature:
                    # Create natural language description with competitor names
                    if len(comps_with_feature) == 1:
                        comp_text = f"{comps_with_feature[0]} offers this"
                    elif len(comps_with_feature) == 2:
                        comp_text = f"{comps_with_feature[0]} and {comps_with_feature[1]} offer this"
                    else:
                        comp_text = f"{', '.join(comps_with_feature[:2])} and {len(comps_with_feature)-2} others offer this"
                    
                    gaps.append({
                        "feature": feature_name,
                        "feature_key": feature_key,
                        "impact": impact,
                        "description": description,
                        "competitors_text": comp_text,
                        "competitors_with": comps_with_feature,
                        "recommendation": self._get_detailed_recommendation(feature_key),
                        "implementation_time": self._estimate_implementation_time(feature_key),
                        "business_impact": self._get_business_impact(feature_key)
                    })
        
        # Sort by impact (high first)
        gaps.sort(key=lambda x: 0 if x["impact"] == "high" else 1)
        return gaps
    
    def _create_detailed_comparison(self, your_features: List[str], competitors: List[Dict]) -> Dict:
        """Create a detailed feature comparison with specific competitor names"""
        comparison = {
            "summary": "",
            "feature_matrix": {},
            "competitor_strengths": {},
            "your_advantages": [],
            "key_takeaways": []
        }
        
        if not competitors:
            return comparison
        
        # Define all features to track
        all_features = {
            "free_trial": "Free Trial",
            "public_pricing": "Transparent Pricing",
            "demo": "Product Demo",
            "api_access": "API Access",
            "social_proof": "Case Studies",
            "enterprise_security": "Enterprise Security",
            "self_service": "Self-Serve Signup",
            "integrations": "Integrations",
            "mobile_app": "Mobile App",
            "24_7_support": "24/7 Support"
        }
        
        # Build feature matrix
        for feature_key, feature_name in all_features.items():
            comparison["feature_matrix"][feature_name] = {
                "you": feature_key in your_features
            }
            
            for comp in competitors:
                comp_name = comp.get("name", comp.get("domain", "").split('.')[0].title())
                has_feature = feature_key in comp.get("features", [])
                comparison["feature_matrix"][feature_name][comp_name] = has_feature
        
        # Analyze each competitor's strengths
        for comp in competitors:
            comp_name = comp.get("name", comp.get("domain", "").split('.')[0].title())
            comp_features = comp.get("features", [])
            unique_features = [all_features.get(f, f) for f in comp_features if f not in your_features]
            
            if unique_features:
                comparison["competitor_strengths"][comp_name] = {
                    "domain": comp.get("domain", ""),
                    "unique_features": unique_features[:5],
                    "feature_count": len(comp_features),
                    "description": comp.get("description", "")
                }
        
        # Identify your advantages
        all_comp_features = set()
        for comp in competitors:
            all_comp_features.update(comp.get("features", []))
        
        your_unique = [all_features.get(f, f) for f in your_features if f not in all_comp_features]
        if your_unique:
            comparison["your_advantages"] = your_unique
        
        # Create key takeaways
        total_gaps = sum(1 for f in all_comp_features if f not in your_features)
        
        if competitors:
            # Find the strongest competitor
            strongest_comp = max(competitors, key=lambda c: len(c.get("features", [])))
            strongest_name = strongest_comp.get("name", strongest_comp.get("domain", "").split('.')[0].title())
            
            comparison["key_takeaways"].append(
                f"{strongest_name} is your strongest competitor with {len(strongest_comp.get('features', []))} key features"
            )
        
        if total_gaps > 0:
            comparison["key_takeaways"].append(
                f"You're missing {total_gaps} features that competitors offer"
            )
        
        # Check for critical missing features
        critical_missing = []
        if "free_trial" not in your_features and "free_trial" in all_comp_features:
            critical_missing.append("free trial")
        if "public_pricing" not in your_features and "public_pricing" in all_comp_features:
            critical_missing.append("transparent pricing")
        
        if critical_missing:
            comparison["key_takeaways"].append(
                f"Critical gaps: {', '.join(critical_missing)}"
            )
        
        # Create summary
        comparison["summary"] = self._create_comparison_summary(your_features, competitors, total_gaps)
        
        return comparison
    
    def _create_comparison_summary(self, your_features: List[str], competitors: List[Dict], total_gaps: int) -> str:
        """Create a natural language summary of the competitive landscape"""
        if not competitors:
            return "No direct competitors identified."
        
        comp_names = [c.get("name", c.get("domain", "").split('.')[0].title()) for c in competitors[:3]]
        
        summary = f"Competing against {', '.join(comp_names[:2])}"
        if len(comp_names) > 2:
            summary += f" and {len(comp_names)-2} others"
        summary += ". "
        
        if total_gaps > 3:
            summary += f"You're behind with {total_gaps} missing features. "
        elif total_gaps > 0:
            summary += f"You have {total_gaps} feature gaps to close. "
        else:
            summary += "You're at feature parity. "
        
        # Highlight the most critical gap
        if "free_trial" not in your_features:
            trial_comps = [c.get("name", c.get("domain", "").split('.')[0].title()) 
                          for c in competitors if "free_trial" in c.get("features", [])]
            if trial_comps:
                summary += f"{trial_comps[0]} captures self-serve customers with free trials while you require sales contact."
        elif "public_pricing" not in your_features:
            pricing_comps = [c.get("name", c.get("domain", "").split('.')[0].title()) 
                            for c in competitors if "public_pricing" in c.get("features", [])]
            if pricing_comps:
                summary += f"{pricing_comps[0]} shows pricing transparently while you hide it."
        
        return summary
    
    def _get_detailed_recommendation(self, feature_key: str) -> str:
        """Get detailed implementation recommendation"""
        recommendations = {
            "free_trial": "Implement a 14-day free trial with automatic provisioning. No credit card required for signup.",
            "public_pricing": "Create a /pricing page with 3 tiers: Starter ($X/mo), Professional ($Y/mo), Enterprise (Contact Sales).",
            "demo": "Add an interactive product tour or recorded demo video on your homepage and product pages.",
            "api_access": "Build a developer portal at docs.yourdomain.com with API reference, SDKs, and code examples.",
            "social_proof": "Add customer logos, case studies, and testimonials throughout your site, especially on pricing page.",
            "enterprise_security": "Display security badges (SOC2, ISO 27001) in footer and create a dedicated security page.",
            "self_service": "Enable instant account creation without requiring sales contact. Add 'Start Free' CTAs.",
            "integrations": "Build native integrations with popular tools in your space. Display on an integrations page.",
            "24_7_support": "Implement 24/7 chat support or at minimum, guaranteed response times in your SLA."
        }
        return recommendations.get(feature_key, "Implement this feature to match competitor offerings.")
    
    def _estimate_implementation_time(self, feature_key: str) -> str:
        """Estimate time to implement a feature"""
        estimates = {
            "free_trial": "2-3 weeks",
            "public_pricing": "2-3 days",
            "demo": "1-2 weeks",
            "api_access": "4-6 weeks",
            "social_proof": "1 week",
            "enterprise_security": "2-3 months",
            "self_service": "3-4 weeks",
            "integrations": "2-4 weeks each",
            "24_7_support": "2-4 weeks"
        }
        return estimates.get(feature_key, "2-4 weeks")
    
    def _get_business_impact(self, feature_key: str) -> str:
        """Get the business impact of missing this feature"""
        impacts = {
            "free_trial": "Missing 40-60% of self-serve customers who won't talk to sales",
            "public_pricing": "67% of B2B buyers eliminate vendors without transparent pricing",
            "demo": "Losing visitors who want to see the product before talking to sales",
            "api_access": "Cannot capture developer-led growth or technical buyers",
            "social_proof": "Lower conversion rates due to lack of trust signals",
            "enterprise_security": "Automatically disqualified from enterprise RFPs",
            "self_service": "Forcing all prospects through slow sales process",
            "integrations": "Losing deals that require specific tool compatibility",
            "24_7_support": "Losing global customers who need support in their timezone"
        }
        return impacts.get(feature_key, "Competitive disadvantage in feature comparison")
    
    def _get_gap_recommendation(self, feature_key: str) -> str:
        """Legacy method for backward compatibility"""
        return self._get_detailed_recommendation(feature_key)