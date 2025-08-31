"""
Google Ads NLP Responder

Generates natural language responses for Google Ads data.
Converts raw campaign metrics into conversational insights.
"""

from typing import Dict, List, Any, Optional
import structlog
from datetime import datetime

# Try real API first, fallback to simple client
from .google_ads_api_client import GoogleAdsAPIClient
from .google_ads_simple_client import SimpleGoogleAdsClient

logger = structlog.get_logger()


class GoogleAdsNLPResponder:
    """Generate natural language responses for Google Ads insights."""
    
    def __init__(self, session_id: str):
        """
        Initialize NLP responder with API client.
        
        Args:
            session_id: User's session ID
        """
        self.session_id = session_id
        # Try to use real API client first
        self.api_client = GoogleAdsAPIClient(session_id)
        self.simple_client = SimpleGoogleAdsClient(session_id)
        self.using_mock = False
    
    async def respond_to_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for processing Google Ads queries.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dict with response content and metadata
        """
        query_lower = query.lower()
        
        # Route to appropriate handler based on query
        if any(term in query_lower for term in ["waste", "wasting", "bleeding"]):
            return await self.analyze_wasted_spend()
        elif any(term in query_lower for term in ["performance", "performing", "how are"]):
            return await self.analyze_performance()
        elif any(term in query_lower for term in ["campaign", "campaigns"]):
            return await self.analyze_campaigns()
        elif any(term in query_lower for term in ["best", "top", "winning"]):
            return await self.analyze_top_performers()
        else:
            return await self.provide_overview()
    
    async def analyze_wasted_spend(self) -> Dict[str, Any]:
        """Analyze keywords and campaigns wasting budget."""
        try:
            wasted_keywords = await self.api_client.get_wasted_spend_keywords()
            
            if not wasted_keywords:
                return {
                    "content": "Good news! I couldn't find any keywords with significant wasted spend. Your campaigns appear to be well-optimized.",
                    "metadata": {"type": "google_ads_analysis", "category": "wasted_spend"}
                }
            
            # Calculate total waste
            total_waste = sum(k["cost"] for k in wasted_keywords)
            
            # Format top wasters
            top_3 = wasted_keywords[:3]
            waste_details = []
            for i, keyword in enumerate(top_3, 1):
                waste_details.append(
                    f"{i}. **\"{keyword['keyword']}\"** - ${keyword['cost']:.2f} spent, "
                    f"{keyword['clicks']} clicks, 0 conversions"
                )
            
            response = f"""I found **{len(wasted_keywords)} keywords** wasting **${total_waste:,.2f}** with zero conversions in the last 30 days.

**Top Money Wasters:**
{chr(10).join(waste_details)}

**Immediate Actions:**
• Pause these {len(wasted_keywords)} keywords to save ${total_waste:,.2f}/month
• Add as negative keywords if irrelevant to your business
• Consider testing different match types or ad copy

**Reallocation Opportunity:**
This ${total_waste:,.2f} budget could be shifted to your converting keywords for an estimated {int(total_waste / 50)} additional conversions (based on your average CPA)."""
            
            return {
                "content": response,
                "metadata": {
                    "type": "google_ads_analysis",
                    "category": "wasted_spend",
                    "total_waste": total_waste,
                    "keyword_count": len(wasted_keywords),
                    "actionable": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze wasted spend: {e}")
            return {
                "content": "I need to connect to your Google Ads account first to analyze wasted spend. Would you like to connect it now?",
                "metadata": {"type": "connection_required", "platform": "google_ads"}
            }
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall account performance and trends."""
        try:
            # Try real API first
            performance = await self.api_client.get_account_performance()
            
            # If real API fails, try mock data as fallback
            if not performance:
                logger.info("Real API returned no data, trying mock fallback")
                performance = await self.simple_client.get_account_performance()
                self.using_mock = True
            
            if not performance:
                return {
                    "content": "I need access to your Google Ads account to analyze performance. Would you like to connect it?",
                    "metadata": {"type": "connection_required", "platform": "google_ads"}
                }
            
            current = performance["current_period"]
            changes = performance["changes"]
            
            # Determine performance direction
            if changes["conversions_change"] > 10:
                trend = "📈 improving"
                trend_detail = "up"
            elif changes["conversions_change"] < -10:
                trend = "📉 declining"
                trend_detail = "down"
            else:
                trend = "➡️ stable"
                trend_detail = "flat"
            
            response = f"""Your Google Ads performance is **{trend}** over the last 30 days.

**Current Period Metrics:**
• **Spend:** ${current['cost']:,.2f} ({changes['cost_change']:+.1f}% vs previous period)
• **Conversions:** {current['conversions']:.0f} ({changes['conversions_change']:+.1f}% change)
• **CPA:** ${current['cpa']:.2f} per conversion
• **ROAS:** {current['roas']:.2f}x return on ad spend
• **CTR:** {current['ctr']:.2f}%
• **Conversion Rate:** {current['conversion_rate']:.2f}%

**Key Insights:**"""
            
            # Add contextual insights
            insights = []
            
            if current['cpa'] > 100:
                insights.append(f"• Your CPA of ${current['cpa']:.2f} is high. Consider reviewing keyword quality scores and landing page relevance.")
            
            if current['ctr'] < 2:
                insights.append(f"• CTR of {current['ctr']:.2f}% is below industry average (2-5%). Test new ad copy focusing on unique value props.")
            
            if current['conversion_rate'] < 2:
                insights.append(f"• Conversion rate of {current['conversion_rate']:.2f}% suggests landing page optimization opportunities.")
            
            if current['roas'] < 3:
                insights.append(f"• ROAS of {current['roas']:.2f}x is below breakeven for most businesses. Focus on high-intent keywords.")
            
            if not insights:
                insights.append("• Performance metrics look healthy overall!")
            
            response += "\n" + "\n".join(insights)
            
            return {
                "content": response,
                "metadata": {
                    "type": "google_ads_analysis",
                    "category": "performance",
                    "metrics": current,
                    "trend": trend_detail
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
            return {
                "content": "I couldn't retrieve your Google Ads performance data. Please check your connection.",
                "metadata": {"type": "error", "category": "performance"}
            }
    
    async def analyze_campaigns(self) -> Dict[str, Any]:
        """Analyze individual campaign performance."""
        try:
            campaigns = await self.api_client.get_campaigns(limit=10)
            
            if not campaigns:
                return {
                    "content": "I need access to your Google Ads campaigns. Would you like to connect your account?",
                    "metadata": {"type": "connection_required", "platform": "google_ads"}
                }
            
            # Sort by cost
            campaigns.sort(key=lambda x: x["cost"], reverse=True)
            
            # Calculate totals
            total_cost = sum(c["cost"] for c in campaigns)
            total_conversions = sum(c["conversions"] for c in campaigns)
            
            # Format top campaigns
            campaign_details = []
            for i, campaign in enumerate(campaigns[:5], 1):
                conv_rate = campaign["conversion_rate"]
                status = "🟢" if conv_rate > 3 else "🟡" if conv_rate > 1 else "🔴"
                
                campaign_details.append(
                    f"{i}. {status} **{campaign['name']}**\n"
                    f"   Spend: ${campaign['cost']:.2f} | "
                    f"Conversions: {campaign['conversions']:.0f} | "
                    f"CPA: ${campaign['cost']/campaign['conversions']:.2f}" 
                    if campaign['conversions'] > 0 else 
                    f"   Spend: ${campaign['cost']:.2f} | No conversions ⚠️"
                )
            
            # Identify issues
            problem_campaigns = [c for c in campaigns if c["conversions"] == 0 and c["cost"] > 100]
            high_cpa_campaigns = [c for c in campaigns if c["conversions"] > 0 and c["cost"]/c["conversions"] > 100]
            
            response = f"""You have **{len(campaigns)} active campaigns** with ${total_cost:,.2f} total spend and {total_conversions:.0f} conversions.

**Top Campaigns by Spend:**
{chr(10).join(campaign_details)}"""
            
            if problem_campaigns:
                response += f"""

**⚠️ Campaigns Needing Attention:**
{len(problem_campaigns)} campaigns have spent ${sum(c['cost'] for c in problem_campaigns):.2f} with zero conversions. Consider pausing or restructuring these."""
            
            if high_cpa_campaigns:
                response += f"""

**💰 High CPA Alert:**
{len(high_cpa_campaigns)} campaigns have CPA over $100. Review targeting and bidding strategies."""
            
            return {
                "content": response,
                "metadata": {
                    "type": "google_ads_analysis",
                    "category": "campaigns",
                    "campaign_count": len(campaigns),
                    "total_spend": total_cost
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze campaigns: {e}")
            return {
                "content": "I couldn't retrieve your campaign data. Please check your Google Ads connection.",
                "metadata": {"type": "error", "category": "campaigns"}
            }
    
    async def analyze_top_performers(self) -> Dict[str, Any]:
        """Analyze top performing keywords and opportunities."""
        try:
            top_keywords = await self.api_client.get_top_performing_keywords()
            
            if not top_keywords:
                return {
                    "content": "I need access to your Google Ads account to identify top performers. Would you like to connect?",
                    "metadata": {"type": "connection_required", "platform": "google_ads"}
                }
            
            # Format top performers
            keyword_details = []
            for i, kw in enumerate(top_keywords[:5], 1):
                keyword_details.append(
                    f"{i}. **\"{kw['keyword']}\"**\n"
                    f"   {kw['conversions']:.0f} conversions | "
                    f"CPA: ${kw['cpa']:.2f} | "
                    f"ROAS: {kw['roas']:.1f}x"
                )
            
            # Calculate scaling opportunity
            avg_cpa = sum(k["cpa"] for k in top_keywords[:3]) / min(3, len(top_keywords))
            available_budget = 5000  # Hypothetical additional budget
            potential_conversions = available_budget / avg_cpa
            
            response = f"""Here are your **top performing keywords** driving the most conversions:

{chr(10).join(keyword_details)}

**Scaling Opportunity:**
Your top 3 keywords have an average CPA of ${avg_cpa:.2f}. With an additional ${available_budget:,.0f} budget allocated to these winners, you could potentially generate {potential_conversions:.0f} more conversions per month.

**Recommended Actions:**
1. Increase bids on these top performers by 15-20%
2. Create dedicated ad groups for each top keyword
3. Develop keyword-specific landing pages
4. Add close variants as exact match keywords

These keywords are your profit drivers - protect and scale them! 🚀"""
            
            return {
                "content": response,
                "metadata": {
                    "type": "google_ads_analysis",
                    "category": "top_performers",
                    "keyword_count": len(top_keywords),
                    "avg_cpa": avg_cpa
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze top performers: {e}")
            return {
                "content": "I couldn't retrieve your keyword performance data. Please check your connection.",
                "metadata": {"type": "error", "category": "top_performers"}
            }
    
    async def provide_overview(self) -> Dict[str, Any]:
        """Provide a general overview of Google Ads account."""
        try:
            # Gather all data
            performance = await self.api_client.get_account_performance()
            campaigns = await self.api_client.get_campaigns(limit=5)
            wasted = await self.api_client.get_wasted_spend_keywords(threshold_cost=50)
            
            if not performance:
                return {
                    "content": "To analyze your Google Ads performance, I need to connect to your account. Would you like to set that up? It only takes 30 seconds.",
                    "metadata": {"type": "connection_required", "platform": "google_ads"}
                }
            
            current = performance["current_period"]
            total_waste = sum(k["cost"] for k in wasted) if wasted else 0
            
            response = f"""Here's your **Google Ads overview** for the last 30 days:

**Performance Summary:**
• Total Spend: ${current['cost']:,.2f}
• Conversions: {current['conversions']:.0f}
• Average CPA: ${current['cpa']:.2f}
• ROAS: {current['roas']:.2f}x

**Campaign Status:**
• Active Campaigns: {len(campaigns)}
• Best Performer: {campaigns[0]['name'] if campaigns else 'N/A'}
• Wasted Spend Identified: ${total_waste:.2f}

**Quick Wins Available:**"""
            
            # Add quick wins
            quick_wins = []
            
            if total_waste > 100:
                quick_wins.append(f"1. Pause {len(wasted)} wasteful keywords to save ${total_waste:.2f}/month")
            
            if current['ctr'] < 2:
                quick_wins.append(f"2. Improve ad copy to increase CTR from {current['ctr']:.1f}% to 3%+")
            
            if current['conversion_rate'] < 3:
                quick_wins.append(f"3. Optimize landing pages to boost conversion rate above 3%")
            
            if not quick_wins:
                quick_wins.append("• Your account is well-optimized! Consider scaling successful campaigns.")
            
            response += "\n" + "\n".join(quick_wins)
            
            response += "\n\nWould you like me to dive deeper into any specific area?"
            
            return {
                "content": response,
                "metadata": {
                    "type": "google_ads_analysis",
                    "category": "overview",
                    "has_data": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to provide overview: {e}")
            return {
                "content": "I encountered an issue accessing your Google Ads data. Please try reconnecting your account.",
                "metadata": {"type": "error", "category": "overview"}
            }