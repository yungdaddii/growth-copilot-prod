"""
SimilarWeb API Integration for real traffic and analytics data
Gets actual visitor data for both target site and competitors
"""

import httpx
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta
from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class SimilarWebAnalyzer:
    """
    Fetches real traffic and engagement data from SimilarWeb API
    Works for any domain - both yours and competitors
    """
    
    def __init__(self):
        self.api_key = settings.SIMILARWEB_API_KEY
        self.base_url = "https://api.similarweb.com/v1/website"
        self.headers = {"api-key": self.api_key} if self.api_key else {}
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Get comprehensive traffic analytics for a domain
        This works for ANY website, not just the user's
        """
        if not self.api_key:
            logger.warning("SimilarWeb API key not configured")
            return self._get_fallback_data()
        
        # Check cache first (API is expensive)
        cache_key = f"similarweb:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "has_data": False,
            "traffic_overview": {},
            "engagement_metrics": {},
            "traffic_sources": {},
            "top_keywords": [],
            "audience_interests": [],
            "geography": {},
            "competitor_traffic": {},
            "growth_trend": {},
            "estimated_revenue": None,
            "data_quality": "none"
        }
        
        try:
            # Fetch multiple data points in parallel
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                # Get date range for last 3 months
                end_date = datetime.now().strftime("%Y-%m")
                start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m")
                
                # 1. Traffic Overview
                traffic_response = await client.get(
                    f"{self.base_url}/{domain}/total-traffic-and-engagement/visits",
                    params={
                        "start_date": start_date,
                        "end_date": end_date,
                        "granularity": "monthly",
                        "main_domain_only": "false"
                    }
                )
                
                if traffic_response.status_code == 200:
                    traffic_data = traffic_response.json()
                    results["has_data"] = True
                    results["traffic_overview"] = self._process_traffic_data(traffic_data)
                
                # 2. Engagement Metrics (bounce rate, pages/visit, duration)
                engagement_response = await client.get(
                    f"{self.base_url}/{domain}/total-traffic-and-engagement/engagement",
                    params={
                        "start_date": start_date,
                        "end_date": end_date,
                        "granularity": "monthly"
                    }
                )
                
                if engagement_response.status_code == 200:
                    engagement_data = engagement_response.json()
                    results["engagement_metrics"] = self._process_engagement_data(engagement_data)
                
                # 3. Traffic Sources (organic, paid, direct, social, etc.)
                sources_response = await client.get(
                    f"{self.base_url}/{domain}/traffic-sources/overview",
                    params={"start_date": start_date, "end_date": end_date}
                )
                
                if sources_response.status_code == 200:
                    sources_data = sources_response.json()
                    results["traffic_sources"] = self._process_sources_data(sources_data)
                
                # 3a. Get more detailed channel breakdown
                # Organic vs Paid Search breakdown
                try:
                    search_response = await client.get(
                        f"{self.base_url}/{domain}/traffic-sources/search",
                        params={"start_date": start_date, "end_date": end_date}
                    )
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        results["search_breakdown"] = {
                            "organic": search_data.get("organic", 0) * 100,
                            "paid": search_data.get("paid", 0) * 100
                        }
                except:
                    pass
                
                # 3b. Top Referral Sources
                try:
                    referrals_response = await client.get(
                        f"{self.base_url}/{domain}/traffic-sources/referrals",
                        params={"start_date": start_date, "end_date": end_date, "limit": 10}
                    )
                    if referrals_response.status_code == 200:
                        referrals_data = referrals_response.json()
                        results["top_referrals"] = self._process_referrals_data(referrals_data)
                except:
                    pass
                
                # 3c. Social Networks breakdown
                try:
                    social_response = await client.get(
                        f"{self.base_url}/{domain}/traffic-sources/social",
                        params={"start_date": start_date, "end_date": end_date}
                    )
                    if social_response.status_code == 200:
                        social_data = social_response.json()
                        results["social_networks"] = self._process_social_data(social_data)
                except:
                    pass
                
                # 3d. Display Advertising (if they run display ads)
                try:
                    display_response = await client.get(
                        f"{self.base_url}/{domain}/traffic-sources/display",
                        params={"start_date": start_date, "end_date": end_date}
                    )
                    if display_response.status_code == 200:
                        display_data = display_response.json()
                        results["display_ads"] = {
                            "publishers": display_data.get("publishers", []),
                            "ad_networks": display_data.get("ad_networks", [])
                        }
                except:
                    pass
                
                # 4. Top Keywords (if available in plan)
                try:
                    keywords_response = await client.get(
                        f"{self.base_url}/{domain}/search/keywords",
                        params={"start_date": start_date, "end_date": end_date, "limit": 10}
                    )
                    
                    if keywords_response.status_code == 200:
                        keywords_data = keywords_response.json()
                        results["top_keywords"] = self._process_keywords_data(keywords_data)
                except:
                    pass  # Keywords might not be in API plan
                
                # 5. Geographic Distribution
                geo_response = await client.get(
                    f"{self.base_url}/{domain}/geo/traffic-by-country",
                    params={"start_date": start_date, "end_date": end_date}
                )
                
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    results["geography"] = self._process_geo_data(geo_data)
                
                # Calculate estimated revenue based on traffic
                if results["has_data"]:
                    results["estimated_revenue"] = self._estimate_revenue(
                        results["traffic_overview"],
                        results["engagement_metrics"],
                        domain
                    )
                    results["data_quality"] = self._assess_data_quality(results["traffic_overview"])
                
                # Cache for 24 hours
                await cache_result(cache_key, results, ttl=86400)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error("SimilarWeb API key invalid or quota exceeded")
            elif e.response.status_code == 404:
                logger.info(f"No SimilarWeb data available for {domain}")
            else:
                logger.error(f"SimilarWeb API error: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch SimilarWeb data for {domain}: {e}")
        
        return results
    
    async def compare_traffic(self, main_domain: str, competitor_domains: List[str]) -> Dict[str, Any]:
        """
        Compare traffic between main domain and competitors
        This is KEY for competitive analysis
        """
        comparison = {
            "main_domain": main_domain,
            "competitors": {},
            "market_share": {},
            "growth_comparison": {},
            "traffic_gaps": {},
            "winning_channels": {},
            "insights": []
        }
        
        # Get data for all domains
        all_domains = [main_domain] + competitor_domains
        domain_data = {}
        
        for domain in all_domains:
            data = await self.analyze(domain)
            if data.get("has_data"):
                domain_data[domain] = data
        
        if not domain_data:
            return comparison
        
        # Calculate market share
        total_traffic = sum(
            d.get("traffic_overview", {}).get("monthly_visits", 0) 
            for d in domain_data.values()
        )
        
        if total_traffic > 0:
            for domain, data in domain_data.items():
                visits = data.get("traffic_overview", {}).get("monthly_visits", 0)
                comparison["market_share"][domain] = {
                    "visits": visits,
                    "percentage": (visits / total_traffic) * 100
                }
        
        # Compare growth rates
        main_data = domain_data.get(main_domain, {})
        main_growth = main_data.get("traffic_overview", {}).get("growth_rate", 0)
        
        for comp_domain in competitor_domains:
            if comp_domain in domain_data:
                comp_growth = domain_data[comp_domain].get("traffic_overview", {}).get("growth_rate", 0)
                comparison["growth_comparison"][comp_domain] = {
                    "their_growth": comp_growth,
                    "your_growth": main_growth,
                    "difference": comp_growth - main_growth
                }
        
        # Find traffic source gaps
        main_sources = main_data.get("traffic_sources", {})
        for comp_domain in competitor_domains:
            if comp_domain in domain_data:
                comp_sources = domain_data[comp_domain].get("traffic_sources", {})
                gaps = []
                
                for source, percentage in comp_sources.items():
                    main_percentage = main_sources.get(source, 0)
                    if percentage > main_percentage * 1.5:  # They get 50% more from this source
                        gaps.append({
                            "source": source,
                            "their_share": percentage,
                            "your_share": main_percentage,
                            "gap": percentage - main_percentage
                        })
                
                if gaps:
                    comparison["traffic_gaps"][comp_domain] = gaps
        
        # Generate insights
        comparison["insights"] = self._generate_traffic_insights(
            main_domain, domain_data, comparison
        )
        
        return comparison
    
    def _process_traffic_data(self, data: Dict) -> Dict[str, Any]:
        """Process raw traffic data from API"""
        processed = {
            "monthly_visits": 0,
            "trend": [],
            "growth_rate": 0,
            "average_visits": 0
        }
        
        try:
            visits = data.get("visits", [])
            if visits:
                # Get most recent month
                recent_visits = [v.get("visits", 0) for v in visits[-3:]]
                processed["monthly_visits"] = recent_visits[-1] if recent_visits else 0
                processed["average_visits"] = sum(recent_visits) / len(recent_visits) if recent_visits else 0
                
                # Calculate growth
                if len(recent_visits) >= 2 and recent_visits[0] > 0:
                    processed["growth_rate"] = ((recent_visits[-1] - recent_visits[0]) / recent_visits[0]) * 100
                
                # Store trend
                processed["trend"] = recent_visits
        except Exception as e:
            logger.error(f"Error processing traffic data: {e}")
        
        return processed
    
    def _process_engagement_data(self, data: Dict) -> Dict[str, Any]:
        """Process engagement metrics"""
        processed = {
            "bounce_rate": 0,
            "pages_per_visit": 0,
            "avg_duration": 0  # in seconds
        }
        
        try:
            # Get most recent data
            if "bounce_rate" in data:
                bounce_data = data["bounce_rate"]
                if isinstance(bounce_data, list) and bounce_data:
                    processed["bounce_rate"] = bounce_data[-1].get("bounce_rate", 0) * 100
            
            if "pages_per_visit" in data:
                pages_data = data["pages_per_visit"]
                if isinstance(pages_data, list) and pages_data:
                    processed["pages_per_visit"] = pages_data[-1].get("pages_per_visit", 0)
            
            if "average_visit_duration" in data:
                duration_data = data["average_visit_duration"]
                if isinstance(duration_data, list) and duration_data:
                    processed["avg_duration"] = duration_data[-1].get("average_visit_duration", 0)
        except Exception as e:
            logger.error(f"Error processing engagement data: {e}")
        
        return processed
    
    def _process_sources_data(self, data: Dict) -> Dict[str, float]:
        """Process traffic sources breakdown"""
        sources = {}
        
        try:
            source_types = data.get("source_type", [])
            if source_types:
                recent = source_types[-1] if isinstance(source_types, list) else source_types
                
                sources = {
                    "direct": recent.get("direct", 0) * 100,
                    "search": recent.get("search", 0) * 100,
                    "social": recent.get("social", 0) * 100,
                    "referral": recent.get("referral", 0) * 100,
                    "paid": recent.get("paid", 0) * 100,
                    "email": recent.get("mail", 0) * 100
                }
        except Exception as e:
            logger.error(f"Error processing sources data: {e}")
        
        return sources
    
    def _process_keywords_data(self, data: Dict) -> List[Dict]:
        """Process top keywords data"""
        keywords = []
        
        try:
            search_data = data.get("search", [])
            for keyword_info in search_data[:10]:
                keywords.append({
                    "keyword": keyword_info.get("search_term", ""),
                    "visits": keyword_info.get("visits", 0),
                    "share": keyword_info.get("share", 0) * 100
                })
        except Exception as e:
            logger.error(f"Error processing keywords data: {e}")
        
        return keywords
    
    def _process_referrals_data(self, data: Dict) -> List[Dict]:
        """Process top referral sources"""
        referrals = []
        
        try:
            referral_list = data.get("referrals", [])
            for ref in referral_list[:10]:
                referrals.append({
                    "domain": ref.get("domain", ""),
                    "share": ref.get("share", 0) * 100,
                    "visits": ref.get("visits", 0)
                })
        except Exception as e:
            logger.error(f"Error processing referrals data: {e}")
        
        return referrals
    
    def _process_social_data(self, data: Dict) -> Dict[str, float]:
        """Process social networks breakdown"""
        social = {}
        
        try:
            social_data = data.get("social", {})
            
            # Map common social networks
            social = {
                "facebook": social_data.get("facebook", 0) * 100,
                "twitter": social_data.get("twitter", 0) * 100,
                "linkedin": social_data.get("linkedin", 0) * 100,
                "youtube": social_data.get("youtube", 0) * 100,
                "reddit": social_data.get("reddit", 0) * 100,
                "instagram": social_data.get("instagram", 0) * 100,
                "pinterest": social_data.get("pinterest", 0) * 100,
                "tiktok": social_data.get("tiktok", 0) * 100
            }
            
            # Remove zeros for cleaner data
            social = {k: v for k, v in social.items() if v > 0}
        except Exception as e:
            logger.error(f"Error processing social data: {e}")
        
        return social
    
    def _process_geo_data(self, data: Dict) -> Dict[str, Any]:
        """Process geographic distribution"""
        geo = {
            "top_countries": [],
            "distribution": {}
        }
        
        try:
            countries = data.get("records", [])
            for country_data in countries[:5]:
                country_name = country_data.get("country_name", "Unknown")
                share = country_data.get("share", 0) * 100
                
                geo["top_countries"].append({
                    "country": country_name,
                    "share": share
                })
                geo["distribution"][country_name] = share
        except Exception as e:
            logger.error(f"Error processing geo data: {e}")
        
        return geo
    
    def _estimate_revenue(self, traffic: Dict, engagement: Dict, domain: str) -> Dict[str, Any]:
        """
        Estimate potential revenue based on traffic and engagement
        This is an ESTIMATE but better than nothing
        """
        monthly_visits = traffic.get("monthly_visits", 0)
        bounce_rate = engagement.get("bounce_rate", 50) / 100
        pages_per_visit = engagement.get("pages_per_visit", 2)
        
        # Engaged visitors (didn't bounce)
        engaged_visitors = monthly_visits * (1 - bounce_rate)
        
        # Industry average conversion rates (can be customized)
        conversion_rates = {
            "saas": 0.03,      # 3% for SaaS
            "ecommerce": 0.025, # 2.5% for ecommerce
            "enterprise": 0.01, # 1% for enterprise
            "default": 0.02    # 2% default
        }
        
        # Determine industry (this could be passed from analyzer)
        industry = "default"
        domain_lower = domain.lower()
        if any(term in domain_lower for term in ["shop", "store", "buy"]):
            industry = "ecommerce"
        elif any(term in domain_lower for term in ["software", "app", "platform", "cloud"]):
            industry = "saas"
        
        conversion_rate = conversion_rates[industry]
        estimated_conversions = engaged_visitors * conversion_rate
        
        # Average deal sizes (these should come from user input ideally)
        avg_deal_sizes = {
            "saas": 100,       # $100/month
            "ecommerce": 75,   # $75 per order
            "enterprise": 5000, # $5000 per deal
            "default": 100
        }
        
        avg_deal_size = avg_deal_sizes[industry]
        estimated_monthly_revenue = estimated_conversions * avg_deal_size
        
        return {
            "estimated_monthly_revenue": estimated_monthly_revenue,
            "estimated_annual_revenue": estimated_monthly_revenue * 12,
            "engaged_visitors": engaged_visitors,
            "estimated_conversions": estimated_conversions,
            "conversion_rate_used": conversion_rate * 100,
            "avg_deal_size_used": avg_deal_size,
            "confidence": self._assess_data_quality(traffic),
            "note": "Based on industry benchmarks and traffic data"
        }
    
    def _assess_data_quality(self, traffic: Dict) -> str:
        """Assess the quality/confidence of the data"""
        monthly_visits = traffic.get("monthly_visits", 0)
        
        if monthly_visits >= 100000:
            return "high"
        elif monthly_visits >= 10000:
            return "medium"
        elif monthly_visits >= 1000:
            return "low"
        else:
            return "very_low"
    
    def _generate_traffic_insights(self, main_domain: str, domain_data: Dict, comparison: Dict) -> List[str]:
        """Generate actionable insights from traffic comparison"""
        insights = []
        
        # Market share insight
        if main_domain in comparison.get("market_share", {}):
            main_share = comparison["market_share"][main_domain]["percentage"]
            if main_share < 20:
                insights.append(f"You have {main_share:.1f}% market share - significant growth opportunity")
            elif main_share > 40:
                insights.append(f"You're the market leader with {main_share:.1f}% share")
        
        # Growth comparison
        for comp, growth_data in comparison.get("growth_comparison", {}).items():
            if growth_data["difference"] > 10:
                insights.append(f"{comp} is growing {growth_data['difference']:.1f}% faster - analyze their strategy")
        
        # Traffic source opportunities
        main_data = domain_data.get(main_domain, {})
        main_sources = main_data.get("traffic_sources", {})
        
        if main_sources.get("search", 0) < 30:
            insights.append("Low search traffic (< 30%) - invest in SEO")
        
        if main_sources.get("social", 0) < 5:
            insights.append("Minimal social traffic - opportunity for social media marketing")
        
        if main_sources.get("paid", 0) < 10:
            insights.append("Low paid traffic - consider PPC campaigns")
        
        # Engagement insights
        engagement = main_data.get("engagement_metrics", {})
        if engagement.get("bounce_rate", 0) > 60:
            insights.append(f"High bounce rate ({engagement['bounce_rate']:.1f}%) - improve landing pages")
        
        if engagement.get("pages_per_visit", 0) < 2:
            insights.append("Low pages per visit - improve internal linking and content discovery")
        
        return insights[:5]  # Top 5 insights
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return empty data structure when API is not available"""
        return {
            "has_data": False,
            "traffic_overview": {},
            "engagement_metrics": {},
            "traffic_sources": {},
            "top_keywords": [],
            "audience_interests": [],
            "geography": {},
            "competitor_traffic": {},
            "growth_trend": {},
            "estimated_revenue": None,
            "data_quality": "none",
            "note": "SimilarWeb API access limited - upgrade plan for full traffic data",
            "alternative_data": "Using browser analysis and estimates instead"
        }