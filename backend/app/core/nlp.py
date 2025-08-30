from openai import AsyncOpenAI
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from app.config import settings
from app.models.analysis import Analysis
from app.models.conversation import Conversation

logger = structlog.get_logger()

# Configure OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class NLPProcessor:
    def __init__(self):
        self.client = client
        self.model = settings.OPENAI_MODEL
        # Updated system prompt to be more data-driven and professional
        self.system_prompt = """You are Growth Co-pilot, an AI that helps growth marketers fix specific problems to capture more sales opportunities.

CRITICAL RULES:
- Use the TOP 3 recommendations from the data
- NEVER make up competitors or data
- Be specific with numbers and actions
- NO EMOJIS in your response
- Professional but conversational tone

Your response structure:
1. Lead with impact: "Analysis reveals [biggest opportunity/problem]"
2. Present top 3 fixes in this format:
   • Issue: [specific problem]
   • Fix: [exact action to take]
   • Impact: [sales opportunity]
   • Time: [effort required]
3. End with: "Want to see all X quick wins?" or if competitors exist: "Should I analyze how [competitor] handles this?"

Focus on:
- Conversion optimization first
- Traffic/growth opportunities second  
- Technical issues last

NEVER mention generic SEO advice or made-up competitors.
"""
    
    async def detect_intent(self, text: str) -> Dict[str, Any]:
        # Clean up text - remove protocol if present
        cleaned_text = text.lower().strip()
        cleaned_text = re.sub(r'^https?://', '', cleaned_text)
        cleaned_text = re.sub(r'^www\.', '', cleaned_text)
        
        # First check for direct domain input (e.g., "stripe.com" or "https://www.stripe.com")
        direct_domain_pattern = r'^([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.)+[a-zA-Z]{2,}(?:/.*)?$'
        direct_match = re.match(direct_domain_pattern, cleaned_text)
        
        if direct_match:
            domain = direct_match.group().split('/')[0]  # Remove any path
            return {
                "type": "analyze_domain",
                "domain": domain,
                "context": text
            }
        
        # Then check for domain with action words (e.g., "analyze stripe.com")
        domain_pattern = r'(?:analyze|check|audit|review|look at)\s+([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.)+[a-zA-Z]{2,}'
        domain_match = re.search(domain_pattern, text.lower())
        
        if domain_match:
            domain = domain_match.group().split()[-1]
            return {
                "type": "analyze_domain",
                "domain": domain,
                "context": text
            }
        
        # Check for unsupported tracking/attribution questions first
        unsupported_patterns = [
            "attribution", "tracking", "utm", "ga4", "google analytics", 
            "gtm", "tag manager", "pixel", "conversion tracking",
            "cross-domain", "multi-touch", "analytics setup",
            "mixpanel", "amplitude", "segment", "crm", "hubspot",
            "marketing automation", "email tracking"
        ]
        
        if any(pattern in text.lower() for pattern in unsupported_patterns):
            return {
                "type": "unsupported_topic",
                "topic": "tracking_attribution",
                "context": text
            }
        
        # Check for follow-up patterns (expanded for better conversation)
        follow_up_patterns = {
            "competitors": ["competitor", "compare", "versus", "vs", "competition"],
            "mobile": ["mobile", "responsive", "phone", "tablet"],
            "quick_wins": ["quick", "easy", "fast", "simple", "low-hanging"],
            "more": ["more", "else", "other", "continue", "next", "detail", "deeper", "explain"],
            "fix": ["fix", "solve", "implement", "how to", "tutorial"],
            "forms": ["form", "field", "signup", "demo", "conversion"],
            "pricing": ["pricing", "price", "cost", "plans", "tiers"],
            "content": ["content", "blog", "articles", "topics", "seo"],
            "ai_search": ["ai", "chatgpt", "claude", "llms", "robots"],
            "performance": ["performance", "speed", "load", "slow", "fast"],
            "pages": ["page", "homepage", "landing", "about", "features"]
        }
        
        for subtype, patterns in follow_up_patterns.items():
            if any(pattern in text.lower() for pattern in patterns):
                return {
                    "type": "follow_up",
                    "subtype": subtype,
                    "context": text
                }
        
        return {
            "type": "general",
            "context": text
        }
    
    async def generate_analysis_response(
        self,
        domain: str,
        analysis: Analysis,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate we have real data
        if not analysis.results:
            return {
                "content": f"Analysis failed for {domain}. I wasn't able to collect sufficient data. This might be due to the site being inaccessible or blocking automated analysis. Please check if the domain is correct and accessible.",
                "metadata": {"error": True}
            }
        
        # Extract real data from analysis
        performance_data = analysis.results.get("performance", {})
        conversion_data = analysis.results.get("conversion", {})
        seo_data = analysis.results.get("seo", {})
        competitor_data = analysis.results.get("competitors", {})
        traffic_data = analysis.results.get("traffic", {})
        similarweb_data = analysis.results.get("similarweb", {})  # REAL TRAFFIC DATA
        traffic_comparison = analysis.results.get("traffic_comparison", {})  # Competitive traffic data
        social_data = analysis.results.get("social", {})
        ads_data = analysis.results.get("ads", {})
        ai_search_data = analysis.results.get("ai_search", {})
        page_analysis_data = analysis.results.get("page_analysis", {})
        form_intelligence_data = analysis.results.get("form_intelligence", {})
        content_strategy_data = analysis.results.get("content_strategy", {})
        
        # Build data-driven insights
        insights = []
        
        # Performance insights (real data)
        if performance_data:
            score = performance_data.get("score", 0)
            load_time = performance_data.get("load_time", 0)
            fcp = performance_data.get("first_contentful_paint", 0)
            
            if score < 50:
                insights.append({
                    "type": "performance",
                    "severity": "critical",
                    "data": f"Performance score is {score}/100 with {load_time:.1f}s load time",
                    "impact": "Users abandon sites that take >3s to load"
                })
        
        # Conversion insights (real data)
        if conversion_data:
            has_trial = conversion_data.get("has_free_trial", False)
            has_pricing = conversion_data.get("has_pricing", False)
            form_fields = conversion_data.get("form_fields", 0)
            cta_clarity = conversion_data.get("cta_clarity", "unknown")
            
            if not has_trial and competitor_data.get("competitors"):
                comp_with_trial = [c for c in competitor_data["competitors"] if "free_trial" in c.get("features", [])]
                if comp_with_trial:
                    insights.append({
                        "type": "conversion",
                        "severity": "high",
                        "data": f"No free trial while {len(comp_with_trial)} competitors offer one",
                        "impact": "Missing self-serve revenue channel"
                    })
            
            if form_fields > 6:
                insights.append({
                    "type": "conversion",
                    "severity": "medium",
                    "data": f"Form has {form_fields} fields (optimal is 3-4)",
                    "impact": "Each extra field reduces conversion by ~7%"
                })
        
        # AI Search insights (critical for 2025+)
        if ai_search_data:
            blocked_crawlers = ai_search_data.get("blocked_crawlers", [])
            has_llms_txt = ai_search_data.get("has_llms_txt", False)
            ai_score = ai_search_data.get("ai_visibility_score", 0)
            
            if blocked_crawlers:
                crawler_names = [c["platform"] for c in blocked_crawlers[:2]]
                insights.append({
                    "type": "ai_search",
                    "severity": "critical",
                    "data": f"Blocking AI crawlers: {', '.join(crawler_names)}",
                    "impact": "Invisible to AI-powered search (25-40% of future traffic)"
                })
            
            if ai_score < 40:
                insights.append({
                    "type": "ai_search",
                    "severity": "high",
                    "data": f"AI visibility score: {ai_score}/100",
                    "impact": "AI can't understand or recommend your product"
                })
        
        # SEO insights (real data)
        if seo_data:
            blocks_ai = seo_data.get("blocks_ai_crawlers", False)
            has_schema = seo_data.get("has_schema", False)
            seo_score = seo_data.get("score", 100)
            
            if blocks_ai and not ai_search_data:  # Only if AI search analyzer didn't run
                insights.append({
                    "type": "seo",
                    "severity": "critical",
                    "data": "Blocking AI crawlers (ChatGPT, Claude, etc.)",
                    "impact": "Invisible to AI-powered search and recommendations"
                })
        
        # SimilarWeb Traffic insights (REAL DATA - highest priority)
        if similarweb_data and similarweb_data.get("has_data"):
            traffic_overview = similarweb_data.get("traffic_overview", {})
            engagement = similarweb_data.get("engagement_metrics", {})
            sources = similarweb_data.get("traffic_sources", {})
            
            monthly_visits = traffic_overview.get("monthly_visits", 0)
            growth_rate = traffic_overview.get("growth_rate", 0)
            bounce_rate = engagement.get("bounce_rate", 0)
            
            # Traffic growth insights
            if growth_rate < -10:
                insights.append({
                    "type": "traffic",
                    "severity": "critical",
                    "data": f"Traffic declining {abs(growth_rate):.1f}% month-over-month ({monthly_visits:,} visits)",
                    "impact": "Losing market share to competitors"
                })
            elif monthly_visits < 10000:
                insights.append({
                    "type": "traffic",
                    "severity": "high",
                    "data": f"Only {monthly_visits:,} monthly visits",
                    "impact": "Limited market reach - need growth strategy"
                })
            
            # Bounce rate insights
            if bounce_rate > 60:
                insights.append({
                    "type": "engagement",
                    "severity": "high",
                    "data": f"{bounce_rate:.1f}% bounce rate (industry avg: 40-50%)",
                    "impact": f"Losing {int((bounce_rate - 50) * monthly_visits / 100):,} potential customers/month"
                })
            
            # Traffic source insights
            if sources:
                organic_traffic = sources.get("search", 0) + sources.get("direct", 0)
                if organic_traffic < 40:
                    insights.append({
                        "type": "acquisition",
                        "severity": "high",
                        "data": f"Only {organic_traffic:.1f}% organic traffic",
                        "impact": "Over-reliance on paid channels - not sustainable"
                    })
                
                if sources.get("social", 0) < 5 and monthly_visits > 10000:
                    insights.append({
                        "type": "social",
                        "severity": "medium",
                        "data": f"Social traffic only {sources.get('social', 0):.1f}%",
                        "impact": "Missing free traffic from social channels"
                    })
            
            # Competitive traffic comparison
            if traffic_comparison and traffic_comparison.get("market_share"):
                market_share = traffic_comparison["market_share"].get(domain, {})
                if market_share.get("percentage", 0) < 20:
                    top_competitor = max(traffic_comparison["market_share"].items(), 
                                       key=lambda x: x[1].get("visits", 0))
                    if top_competitor[0] != domain:
                        insights.append({
                            "type": "competitive",
                            "severity": "high",
                            "data": f"{top_competitor[0]} gets {top_competitor[1].get('visits', 0):,} visits vs your {monthly_visits:,}",
                            "impact": f"Competitor has {int(top_competitor[1].get('visits', 0) / max(monthly_visits, 1))}x more traffic"
                        })
        
        # Fallback to estimated traffic if no SimilarWeb data
        elif traffic_data:
            domain_authority = traffic_data.get("domain_authority", 0)
            monthly_visits = traffic_data.get("estimated_monthly_visits", 0)
            
            if domain_authority < 30:
                insights.append({
                    "type": "traffic",
                    "severity": "high",
                    "data": f"Domain authority is {domain_authority}/100",
                    "impact": "Low search visibility and organic traffic potential"
                })
        
        # Social insights (real data)
        if social_data:
            engagement_score = social_data.get("engagement_score", 0)
            total_followers = social_data.get("total_followers", 0)
            
            if engagement_score < 30 and ads_data.get("ad_platforms_detected"):
                insights.append({
                    "type": "social",
                    "severity": "medium",
                    "data": f"Low social engagement ({engagement_score}/100) despite paid ads",
                    "impact": "Missing organic amplification of paid campaigns"
                })
        
        # Page-specific insights (critical pages)
        if page_analysis_data:
            critical_issues = page_analysis_data.get("critical_issues", [])
            if critical_issues:
                for issue in critical_issues[:1]:  # Top critical issue
                    insights.append({
                        "type": "page_specific",
                        "severity": issue.get("severity", "high"),
                        "data": issue.get("issue", ""),
                        "impact": issue.get("impact", "")
                    })
        
        # Form intelligence insights
        if form_intelligence_data:
            conversion_lift = form_intelligence_data.get("estimated_conversion_lift", 0)
            if conversion_lift > 20:
                insights.append({
                    "type": "form_optimization",
                    "severity": "critical",
                    "data": f"Forms can be optimized for {conversion_lift}% conversion lift",
                    "impact": "Quick wins available in form optimization"
                })
        
        # Ads insights (real data)
        if ads_data:
            platforms = ads_data.get("ad_platforms_detected", [])
            retargeting = ads_data.get("retargeting_enabled", False)
            
            if platforms and not retargeting:
                insights.append({
                    "type": "ads",
                    "severity": "high",
                    "data": "Running ads without retargeting pixels",
                    "impact": "Missing 30-50% conversion opportunity from warm audiences"
                })
        
        # Find the biggest issue from real data
        if insights:
            biggest_issue = max(insights, key=lambda x: 
                3 if x["severity"] == "critical" else 2 if x["severity"] == "high" else 1)
        else:
            biggest_issue = None
        
        # Get recommendations
        recommendations = analysis.results.get("recommendations", [])
        quick_wins = analysis.results.get("quick_wins_detailed", [])
        
        # Generate response based on real data
        if not self.client:
            # Fallback without OpenAI
            return self._generate_fallback_response(domain, analysis, insights, biggest_issue, recommendations)
        
        # Build prompt with actual data
        prompt = f"""Domain analyzed: {domain}
Industry: {analysis.industry}

REAL DATA COLLECTED:
Performance & Technical:
- Performance score: {performance_data.get('score', 'N/A')}/100
- Load time: {performance_data.get('load_time', 'N/A')}s
- SEO score: {analysis.seo_score or 'N/A'}/100
- Mobile score: {analysis.mobile_score or 'N/A'}/100

Conversion & Growth:
- Conversion score: {analysis.conversion_score or 'N/A'}/100
- Has free trial: {conversion_data.get('has_free_trial', False)}
- Form fields: {conversion_data.get('form_fields', 'N/A')}
- CTA clarity: {conversion_data.get('cta_clarity', 'N/A')}

Traffic & Authority:
- Domain authority: {traffic_data.get('domain_authority', 'N/A')}/100
- Est. monthly visits: {traffic_data.get('estimated_monthly_visits', 'N/A')}
- Content velocity: {traffic_data.get('content_velocity', 'N/A')}

Marketing Presence:
- Social engagement: {social_data.get('engagement_score', 'N/A')}/100
- Total followers: {social_data.get('total_followers', 'N/A')}
- Ad platforms: {', '.join(ads_data.get('ad_platforms_detected', [])) or 'None detected'}
- Retargeting enabled: {ads_data.get('retargeting_enabled', False)}
- Est. ad spend: {ads_data.get('estimated_ad_spend', 'Unknown')}

AI Search Optimization:
- AI visibility score: {ai_search_data.get('ai_visibility_score', 'N/A')}/100
- Blocked AI crawlers: {len(ai_search_data.get('blocked_crawlers', []))}
- Has llms.txt: {ai_search_data.get('has_llms_txt', False)}
- Schema types: {len(ai_search_data.get('schema_types_found', []))}

Page Analysis:
- Critical pages found: {len(page_analysis_data.get('pages_found', {}))}
- Critical issues: {len(page_analysis_data.get('critical_issues', []))}
- Page recommendations: {len(page_analysis_data.get('page_recommendations', []))}

Form Intelligence:
- Forms analyzed: {form_intelligence_data.get('forms_found', 0)}
- Best practices score: {form_intelligence_data.get('best_practices_score', 'N/A')}/100
- Conversion lift potential: {form_intelligence_data.get('estimated_conversion_lift', 0)}%

Content Strategy:
- Blog posts: {content_strategy_data.get('current_content', {}).get('blog_posts', 0)}
- Content score: {content_strategy_data.get('content_score', 'N/A')}/100
- Content gaps: {len(content_strategy_data.get('content_gaps', []))}

ACTUAL COMPETITORS FOUND:
{json.dumps([c.get('name', c.get('domain')) for c in competitor_data.get('competitors', [])[:3]])}

TOP RECOMMENDATIONS (prioritized):
{json.dumps(recommendations[:3]) if recommendations else "No specific recommendations"}

QUICK WINS AVAILABLE:
{json.dumps(quick_wins[:2]) if quick_wins else "No quick wins identified"}

Generate a comprehensive but focused response (250-300 words):

1. Start with: "Analysis reveals [most impactful finding based on priority]"
2. List the TOP 3 recommendations using this exact format:
   • [Category]: [Issue from recommendation]
     Fix: [Action from recommendation]
     Impact: [Sales opportunity from recommendation]
     Effort: [Time from recommendation]

3. If quick wins exist, mention how many
4. End with appropriate follow-up based on available data

Use ONLY the recommendations provided. Focus on specifics, not generic advice.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2  # Low temperature for consistent, factual responses
                # max_tokens removed - let model complete naturally
            )
            
            content = response.choices[0].message.content
            
            # Add metadata for UI cards
            metadata = self._build_metadata(analysis, insights, competitor_data)
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error("Failed to generate analysis response", error=str(e))
            return self._generate_fallback_response(domain, analysis, insights, biggest_issue, recommendations)
    
    def _generate_fallback_response(
        self, 
        domain: str, 
        analysis: Analysis, 
        insights: List[Dict],
        biggest_issue: Optional[Dict],
        recommendations: List[Dict]
    ) -> Dict[str, Any]:
        """Generate response without AI when OpenAI fails"""
        if not insights:
            return {
                "content": f"✓ Analysis complete for {domain}. Your site is performing well with no critical issues found. Performance score: {analysis.performance_score or 'N/A'}/100.",
                "metadata": {}
            }
        
        # Build response from real data
        response_parts = [f"✓ Analysis complete for {domain}."]
        
        if biggest_issue:
            response_parts.append(f"\n\nBiggest finding: {biggest_issue['data']}")
            response_parts.append(f"Impact: {biggest_issue['impact']}")
        
        # Add scores if available
        scores = []
        if analysis.performance_score is not None:
            scores.append(f"Performance: {analysis.performance_score}/100")
        if analysis.conversion_score is not None:
            scores.append(f"Conversion: {analysis.conversion_score}/100")
        if analysis.seo_score is not None:
            scores.append(f"SEO: {analysis.seo_score}/100")
        
        if scores:
            response_parts.append(f"\n\nScores: {' | '.join(scores)}")
        
        # Add issue count
        response_parts.append(f"\n\nFound {len(insights)} issues to address.")
        
        return {
            "content": " ".join(response_parts),
            "metadata": self._build_metadata(analysis, insights, {})
        }
    
    def _build_metadata(
        self, 
        analysis: Analysis, 
        insights: List[Dict],
        competitor_data: Dict
    ) -> Dict[str, Any]:
        """Build metadata for UI cards from real data"""
        metadata = {}
        
        # Add issues card if we have real issues
        if insights:
            metadata["issues_card"] = {
                "total_issues": len(insights),
                "critical_issues": len([i for i in insights if i.get("severity") == "critical"]),
                "high_issues": len([i for i in insights if i.get("severity") == "high"])
            }
        
        # Add quick actions based on available data
        actions = []
        if analysis.quick_wins:
            actions.append({
                "label": "Show quick wins",
                "action": "show_quick_wins"
            })
        
        if competitor_data.get("competitors"):
            actions.append({
                "label": f"Compare to {len(competitor_data['competitors'])} competitors",
                "action": "show_competitors"
            })
        
        if actions:
            metadata["quick_actions"] = actions
        
        # Add performance metrics if available
        if analysis.results.get("performance"):
            perf = analysis.results["performance"]
            metadata["performance_metrics"] = {
                "score": perf.get("score"),
                "load_time": perf.get("load_time"),
                "fcp": perf.get("first_contentful_paint")
            }
        
        return metadata
    
    async def generate_follow_up_response(
        self,
        question: str,
        conversation: Conversation,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Get the last analysis from conversation
        last_analysis = None
        if conversation.analyses:
            last_analysis = conversation.analyses[-1]
        
        if not last_analysis or not last_analysis.results:
            return {
                "content": "I don't have analysis data to answer that question. Please analyze a website first.",
                "metadata": {"error": True}
            }
        
        subtype = context.get("subtype", "more")
        
        if subtype == "competitors":
            return await self._generate_competitor_response(last_analysis)
        elif subtype == "mobile":
            return await self._generate_mobile_response(last_analysis)
        elif subtype == "quick_wins":
            return await self._generate_quick_wins_response(last_analysis)
        else:
            return await self.generate_response(question)
    
    async def _generate_competitor_response(self, analysis: Analysis) -> Dict[str, Any]:
        competitor_data = analysis.results.get("competitors", {})
        
        if not competitor_data or not competitor_data.get("competitors"):
            return {
                "content": "I wasn't able to identify competitors for this analysis. This might be because the site's industry wasn't clear or competitor data wasn't available.",
                "metadata": {"error": True}
            }
        
        # Build response from real competitor data
        competitors = competitor_data["competitors"]
        gaps = competitor_data.get("competitive_gaps", [])
        
        response_parts = [f"🔍 I analyzed {len(competitors)} competitors:"]
        
        for comp in competitors:
            name = comp.get("name", comp.get("domain", "Unknown"))
            features = comp.get("features", [])
            response_parts.append(f"\n\n**{name}**")
            if features:
                response_parts.append(f"Key features: {', '.join(features)}")
        
        if gaps:
            response_parts.append("\n\n⚠️ **Competitive gaps to address:**")
            for gap in gaps[:3]:
                response_parts.append(f"\n• {gap['description']}")
                if gap.get("recommendation"):
                    response_parts.append(f"  → {gap['recommendation']}")
        
        return {
            "content": "\n".join(response_parts),
            "metadata": {"type": "competitor_analysis", "competitor_count": len(competitors)}
        }
    
    async def _generate_mobile_response(self, analysis: Analysis) -> Dict[str, Any]:
        mobile_data = analysis.results.get("mobile", {})
        
        if not mobile_data:
            return {
                "content": "Mobile analysis data is not available for this site. The mobile check may have failed or the site might be blocking automated testing.",
                "metadata": {"error": True}
            }
        
        score = mobile_data.get("score", 0)
        issues = mobile_data.get("issues", [])
        
        response_parts = [f"📱 Mobile Experience Score: {score}/100"]
        
        if issues:
            response_parts.append("\n\n**Issues found:**")
            for issue in issues[:5]:
                response_parts.append(f"\n• {issue}")
        
        return {
            "content": "\n".join(response_parts),
            "metadata": {"type": "mobile_analysis", "score": score}
        }
    
    async def _generate_quick_wins_response(self, analysis: Analysis) -> Dict[str, Any]:
        quick_wins = analysis.quick_wins or []
        
        if not quick_wins:
            return {
                "content": "No quick wins identified in this analysis. The site may already be well-optimized or require more complex improvements.",
                "metadata": {"error": False}
            }
        
        response_parts = ["🚀 **Quick Wins** (can be implemented quickly):"]
        
        for i, win in enumerate(quick_wins[:5], 1):
            response_parts.append(f"\n\n{i}. **{win.get('title', 'Improvement')}**")
            response_parts.append(f"   {win.get('description', '')}")
            if win.get('implementation_time'):
                response_parts.append(f"   ⏱ Time: {win['implementation_time']}")
            if win.get('impact'):
                response_parts.append(f"   📈 Impact: {win['impact']}")
        
        return {
            "content": "\n".join(response_parts),
            "metadata": {"type": "quick_wins", "count": len(quick_wins)}
        }
    
    async def generate_response(self, text: str) -> Dict[str, Any]:
        """General response generation"""
        if not self.client:
            return {
                "content": "I can help you analyze websites to find revenue opportunities. Enter a domain name to get started.",
                "metadata": {}
            }
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful website analysis assistant. Keep responses brief and factual."},
                    {"role": "user", "content": text}
                ],
                temperature=0.5
                # No max_tokens limit - let response complete naturally
            )
            
            return {
                "content": response.choices[0].message.content,
                "metadata": {}
            }
        except Exception as e:
            logger.error("Failed to generate response", error=str(e))
            return {
                "content": "I can help you analyze websites. Enter a domain name to get started.",
                "metadata": {}
            }