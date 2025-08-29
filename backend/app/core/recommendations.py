from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()


class RecommendationEngine:
    """Generate specific, actionable recommendations from analysis data"""
    
    def generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized, actionable recommendations"""
        recommendations = []
        
        # Extract data
        perf = analysis_results.get("performance", {})
        conv = analysis_results.get("conversion", {})
        seo = analysis_results.get("seo", {})
        traffic = analysis_results.get("traffic", {})
        social = analysis_results.get("social", {})
        ads = analysis_results.get("ads", {})
        competitors = analysis_results.get("competitors", {})
        ai_search = analysis_results.get("ai_search", {})
        page_analysis = analysis_results.get("page_analysis", {})
        form_intelligence = analysis_results.get("form_intelligence", {})
        content_strategy = analysis_results.get("content_strategy", {})
        
        # CONVERSION RECOMMENDATIONS
        if conv:
            # Form optimization
            form_fields = conv.get("form_fields", 0)
            if form_fields > 6:
                recommendations.append({
                    "priority": "critical",
                    "category": "conversion",
                    "issue": f"Your form has {form_fields} fields (industry best practice is 3-4)",
                    "impact": f"Reducing to 4 fields could increase conversions by {(form_fields - 4) * 7}%",
                    "action": "Remove these fields: company size, phone (make optional), use case description",
                    "effort": "30 minutes",
                    "sales_opportunity": f"Capture {(form_fields - 4) * 7}% more leads from existing traffic"
                })
            
            # CTA optimization
            if conv.get("cta_clarity") == "weak":
                recommendations.append({
                    "priority": "high",
                    "category": "conversion",
                    "issue": f"Weak CTA: '{conv.get('cta_text', 'Submit')}'",
                    "impact": "Strong CTAs increase clicks by 21%",
                    "action": "Change to action-oriented: 'Get Your Free Demo' or 'Start Free Trial'",
                    "effort": "15 minutes",
                    "sales_opportunity": "21% more demo requests from same traffic"
                })
            
            # Free trial vs demo
            if not conv.get("has_free_trial") and competitors.get("competitors"):
                comp_with_trial = [c for c in competitors["competitors"] if "free_trial" in c.get("features", [])]
                if comp_with_trial:
                    recommendations.append({
                        "priority": "critical",
                        "category": "conversion",
                        "issue": f"No free trial while {len(comp_with_trial)} competitors offer one",
                        "impact": "Free trials convert 2.5x better than demo-only",
                        "action": "Add 14-day free trial with credit card optional",
                        "effort": "2-4 weeks",
                        "sales_opportunity": "Capture self-serve buyers who won't book demos"
                    })
            
            # Pricing transparency
            if not conv.get("has_pricing") and traffic.get("estimated_monthly_visits", 0) > 5000:
                recommendations.append({
                    "priority": "high",
                    "category": "conversion",
                    "issue": "No public pricing information",
                    "impact": "67% of B2B buyers eliminate vendors without transparent pricing",
                    "action": "Add pricing page with tiers, or at minimum 'Starting at $X'",
                    "effort": "1 day",
                    "sales_opportunity": "Stop losing price-conscious buyers to transparent competitors"
                })
        
        # PAGE-SPECIFIC RECOMMENDATIONS
        if page_analysis:
            # Add page-specific recommendations
            page_recs = page_analysis.get("page_recommendations", [])
            for rec in page_recs[:3]:  # Top 3 page recommendations
                recommendations.append({
                    "priority": rec.get("priority", "medium"),
                    "category": "page_optimization",
                    "issue": f"{rec.get('page', 'Page')}: {rec.get('issue', '')}",
                    "impact": rec.get("impact", ""),
                    "action": rec.get("fix", ""),
                    "effort": rec.get("effort", ""),
                    "sales_opportunity": rec.get("impact", "")
                })
        
        # FORM INTELLIGENCE RECOMMENDATIONS
        if form_intelligence:
            # Add form optimization opportunities
            form_opps = form_intelligence.get("optimization_opportunities", [])
            for opp in form_opps[:2]:  # Top 2 form recommendations
                recommendations.append({
                    "priority": opp.get("priority", "high"),
                    "category": "form_optimization",
                    "issue": opp.get("issue", ""),
                    "impact": opp.get("impact", ""),
                    "action": opp.get("fix", ""),
                    "effort": opp.get("effort", ""),
                    "sales_opportunity": opp.get("impact", "")
                })
        
        # AI SEARCH OPTIMIZATION (Critical for 2025+)
        if ai_search:
            # Check if blocking AI crawlers
            blocked_crawlers = ai_search.get("blocked_crawlers", [])
            if blocked_crawlers:
                crawler_names = [c["platform"] for c in blocked_crawlers[:3]]
                recommendations.append({
                    "priority": "critical",
                    "category": "ai_search",
                    "issue": f"Blocking AI crawlers: {', '.join(crawler_names)}",
                    "impact": "Missing 25-40% of future traffic from AI search",
                    "action": f"Update robots.txt to allow: {', '.join([c['bot'] for c in blocked_crawlers[:3]])}",
                    "effort": "5 minutes",
                    "sales_opportunity": "Get discovered when buyers ask AI for recommendations"
                })
            
            # Check for llms.txt
            if not ai_search.get("has_llms_txt"):
                recommendations.append({
                    "priority": "high",
                    "category": "ai_search",
                    "issue": "No llms.txt file for AI context",
                    "impact": "AI lacks understanding of your business",
                    "action": "Create /llms.txt with company description, capabilities, and pricing",
                    "effort": "30 minutes",
                    "sales_opportunity": "Ensure AI accurately represents your solution"
                })
            
            # Check schema markup
            if not ai_search.get("schema_types_found"):
                recommendations.append({
                    "priority": "high",
                    "category": "ai_search",
                    "issue": "No structured data for AI comprehension",
                    "impact": "AI can't extract key information about your product",
                    "action": "Add Organization and FAQPage schema markup",
                    "effort": "1 hour",
                    "sales_opportunity": "Appear in AI-generated comparisons and recommendations"
                })
        
        # TRAFFIC & SEO RECOMMENDATIONS
        if seo:
            # AI visibility
            if seo.get("blocks_ai_crawlers"):
                recommendations.append({
                    "priority": "critical",
                    "category": "seo",
                    "issue": "Blocking AI crawlers (ChatGPT, Claude)",
                    "impact": "Missing 15-25% of future traffic from AI search",
                    "action": "Update robots.txt: Remove blocks for GPTBot, ChatGPT-User, Claude-Web",
                    "effort": "5 minutes",
                    "sales_opportunity": "Get recommended by AI tools when buyers ask for solutions"
                })
            
            # SEO opportunities (lower priority than conversion/growth)
            for opp in seo.get("opportunities", [])[:2]:  # Only top 2
                if opp.get("impact") == "high":
                    recommendations.append({
                        "priority": "medium",  # Downgrade from high to medium
                        "category": "seo",
                        "issue": opp["message"],
                        "impact": "Could improve organic traffic by 10-15%",
                        "action": self._get_seo_action(opp),
                        "effort": "1-2 hours",
                        "sales_opportunity": "10-15% more organic leads without paid spend"
                    })
        
        # PAID ADVERTISING RECOMMENDATIONS
        if ads:
            # Retargeting missing
            if ads.get("ad_platforms_detected") and not ads.get("retargeting_enabled"):
                recommendations.append({
                    "priority": "critical",
                    "category": "advertising",
                    "issue": "Running ads without retargeting",
                    "impact": "Retargeting visitors convert 70% better",
                    "action": "Install Facebook Pixel + Google Remarketing Tag",
                    "effort": "1 hour",
                    "sales_opportunity": "Re-engage 30% of visitors who didn't convert"
                })
            
            # No ads but competitors have them
            if not ads.get("ad_platforms_detected") and traffic.get("estimated_monthly_visits", 0) < 10000:
                recommendations.append({
                    "priority": "high",
                    "category": "advertising",
                    "issue": "No paid advertising detected",
                    "impact": "Competitors are capturing your keywords",
                    "action": "Start with Google Ads on bottom-funnel keywords",
                    "effort": "1 week to set up",
                    "sales_opportunity": "Capture high-intent buyers searching for your solution"
                })
        
        # MOBILE RECOMMENDATIONS
        mobile = analysis_results.get("mobile", {})
        if mobile and mobile.get("score", 100) < 60:
            recommendations.append({
                "priority": "high",
                "category": "mobile",
                "issue": f"Poor mobile experience (score: {mobile.get('score')}/100)",
                "impact": "52% of B2B research happens on mobile",
                "action": "Fix viewport issues, increase tap target sizes, optimize images",
                "effort": "1-2 days",
                "sales_opportunity": "Stop losing mobile visitors who can't navigate your site"
            })
        
        # SOCIAL PROOF RECOMMENDATIONS
        if social:
            if social.get("engagement_score", 0) < 30:
                recommendations.append({
                    "priority": "medium",
                    "category": "social",
                    "issue": "Weak social proof and engagement",
                    "impact": "Social proof increases conversions by 15%",
                    "action": "Add customer logos, testimonials, and case studies above fold",
                    "effort": "2-3 hours",
                    "sales_opportunity": "Build trust to convert skeptical visitors"
                })
        
        # CONTENT STRATEGY RECOMMENDATIONS
        if content_strategy:
            # Content gap recommendations
            content_gaps = content_strategy.get("content_gaps", [])
            for gap in content_gaps[:1]:  # Top content gap
                if gap.get("type") == "volume_gap":
                    recommendations.append({
                        "priority": "medium",
                        "category": "content",
                        "issue": gap.get("description", ""),
                        "impact": gap.get("impact", ""),
                        "action": gap.get("recommendation", ""),
                        "effort": "Ongoing",
                        "sales_opportunity": "Build authority and organic traffic"
                    })
            
            # Content opportunities
            content_opps = content_strategy.get("content_opportunities", [])
            for opp in content_opps[:1]:  # Top opportunity
                if opp.get("type") == "foundation":
                    recommendations.append({
                        "priority": "high",
                        "category": "content",
                        "issue": opp.get("opportunity", ""),
                        "impact": opp.get("impact", ""),
                        "action": opp.get("next_steps", ""),
                        "effort": opp.get("effort", ""),
                        "sales_opportunity": opp.get("impact", "")
                    })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return recommendations[:10]  # Top 10 recommendations
    
    def generate_quick_wins(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate quick wins (< 1 day effort, high impact)"""
        all_recs = self.generate_recommendations(analysis_results)
        
        quick_wins = []
        for rec in all_recs:
            effort = rec.get("effort", "")
            if any(x in effort.lower() for x in ["minute", "hour", "1 day"]):
                quick_wins.append({
                    "title": rec["issue"],
                    "action": rec["action"],
                    "time": rec["effort"],
                    "impact": rec.get("sales_opportunity", rec["impact"]),
                    "category": rec["category"]
                })
        
        return quick_wins[:5]
    
    def _get_seo_action(self, opportunity: Dict) -> str:
        """Get specific action for SEO opportunity"""
        opp_type = opportunity.get("type", "")
        
        if opp_type == "rich_snippets":
            return "Add FAQ schema markup using Google's Structured Data Helper"
        elif opp_type == "accessibility":
            return "Add descriptive alt text to all images (use product names + context)"
        elif opp_type == "internal_linking":
            return "Add 3-5 contextual links per page to related content"
        elif opp_type == "technical":
            return "Add canonical tags to all pages (prevents duplicate content penalties)"
        else:
            return "Implement SEO best practice"