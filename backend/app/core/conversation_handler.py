from typing import Dict, Any, Optional, List
import re
import structlog
from app.models.analysis import Analysis
from app.models.conversation import Conversation

logger = structlog.get_logger()


class ConversationHandler:
    """
    Handles conversational follow-ups and deep dives after initial analysis.
    Makes the Growth Co-pilot truly interactive and intelligent.
    """
    
    # Define conversation patterns and intents
    CONVERSATION_PATTERNS = {
        "deep_dive": {
            "patterns": [
                r"tell me more about (.*)",
                r"explain (.*) in detail",
                r"dive deeper into (.*)",
                r"more details on (.*)",
                r"what about (.*)",
                r"elaborate on (.*)"
            ],
            "handler": "handle_deep_dive"
        },
        "forms": {
            "patterns": [
                r".*forms?.*",
                r".*sign ?up.*",
                r".*demo request.*",
                r".*field.*",
                r".*conversion.*form.*"
            ],
            "handler": "handle_forms_query"
        },
        "pricing": {
            "patterns": [
                r".*pricing.*",
                r".*price.*",
                r".*cost.*",
                r".*plans.*",
                r".*tiers.*"
            ],
            "handler": "handle_pricing_query"
        },
        "content": {
            "patterns": [
                r".*content.*",
                r".*blog.*",
                r".*articles.*",
                r".*topics.*",
                r".*seo.*content.*"
            ],
            "handler": "handle_content_query"
        },
        "ai_search": {
            "patterns": [
                r".*ai.*search.*",
                r".*chatgpt.*",
                r".*claude.*",
                r".*llms.*",
                r".*ai.*visibility.*"
            ],
            "handler": "handle_ai_search_query"
        },
        "competitors": {
            "patterns": [
                r".*competitor.*",
                r".*vs.*",
                r".*compare.*",
                r".*alternative.*",
                r".*competition.*"
            ],
            "handler": "handle_competitor_query"
        },
        "quick_wins": {
            "patterns": [
                r".*quick.*win.*",
                r".*easy.*fix.*",
                r".*low.*hanging.*",
                r".*fast.*improvement.*",
                r".*quick.*fix.*"
            ],
            "handler": "handle_quick_wins_query"
        },
        "specific_page": {
            "patterns": [
                r".*(homepage|home page).*",
                r".*landing.*page.*",
                r".*about.*page.*",
                r".*features.*page.*",
                r".*demo.*page.*"
            ],
            "handler": "handle_page_query"
        },
        "mobile": {
            "patterns": [
                r".*mobile.*",
                r".*responsive.*",
                r".*phone.*",
                r".*tablet.*"
            ],
            "handler": "handle_mobile_query"
        },
        "performance": {
            "patterns": [
                r".*performance.*",
                r".*speed.*",
                r".*load.*time.*",
                r".*core.*web.*vital.*"
            ],
            "handler": "handle_performance_query"
        },
        "show_all": {
            "patterns": [
                r".*show.*all.*",
                r".*full.*report.*",
                r".*everything.*",
                r".*complete.*analysis.*"
            ],
            "handler": "handle_show_all"
        },
        "fix_instructions": {
            "patterns": [
                r"how.*fix.*",
                r"how.*implement.*",
                r".*step.*step.*",
                r".*instructions.*",
                r".*tutorial.*"
            ],
            "handler": "handle_fix_instructions"
        }
    }
    
    def __init__(self):
        self.last_analysis = None
        
    async def handle_follow_up(
        self, 
        message: str, 
        analysis: Analysis,
        conversation: Optional[Conversation] = None
    ) -> Dict[str, Any]:
        """Main entry point for handling follow-up questions"""
        
        logger.info(f"Handling follow-up message: {message[:50]}...")
        
        if not analysis or not analysis.results:
            logger.warning("No analysis data available for follow-up")
            return {
                "content": "I need to analyze a website first before I can answer questions about it. Please provide a domain to analyze.",
                "metadata": {"type": "error"}
            }
        
        self.last_analysis = analysis
        message_lower = message.lower()
        
        # Detect intent
        intent = self._detect_intent(message_lower)
        logger.info(f"Detected conversational intent: {intent}")
        
        # Route to appropriate handler
        if intent:
            handler_name = self.CONVERSATION_PATTERNS[intent]["handler"]
            handler = getattr(self, handler_name)
            logger.info(f"Routing to handler: {handler_name}")
            return await handler(message, analysis)
        
        # Default response with suggestions
        logger.info("No specific intent detected, showing suggestions")
        return self._generate_suggestions_response(analysis)
    
    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect the intent of the user's message"""
        for intent, config in self.CONVERSATION_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, message):
                    return intent
        return None
    
    async def handle_deep_dive(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle requests for more detail on a specific topic"""
        # Extract what they want to dive into
        topics = re.findall(r"(?:about|into|on)\s+(.+?)(?:\?|$|\.)", message)
        topic = topics[0] if topics else "the analysis"
        
        # Map topic to analysis section
        if "form" in topic:
            return await self.handle_forms_query(message, analysis)
        elif "price" in topic or "pricing" in topic:
            return await self.handle_pricing_query(message, analysis)
        elif "content" in topic:
            return await self.handle_content_query(message, analysis)
        elif "ai" in topic:
            return await self.handle_ai_search_query(message, analysis)
        else:
            return self._generate_overview_response(analysis)
    
    async def handle_forms_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about forms"""
        form_data = analysis.results.get("form_intelligence", {})
        
        if not form_data or form_data.get("forms_found", 0) == 0:
            return {
                "content": "📝 **No forms detected** on the analyzed pages.\n\nThis could mean:\n• Forms are behind login/authentication\n• Using third-party tools (Calendly, TypeForm)\n• JavaScript-rendered forms not detected\n\nWould you like me to analyze the demo/contact pages specifically?",
                "metadata": {"type": "forms_analysis"}
            }
        
        response = f"📝 **Form Analysis Results**\n\n"
        response += f"Found **{form_data['forms_found']} forms** across the site.\n"
        response += f"Best Practices Score: **{form_data.get('best_practices_score', 0)}/100**\n"
        response += f"Potential Conversion Lift: **{form_data.get('estimated_conversion_lift', 0)}%**\n\n"
        
        # Form-specific recommendations
        form_opps = form_data.get("optimization_opportunities", [])
        if form_opps:
            response += "**🎯 Form Optimization Opportunities:**\n\n"
            for i, opp in enumerate(form_opps[:5], 1):
                response += f"{i}. **{opp.get('issue', '')}**\n"
                response += f"   → Fix: {opp.get('fix', '')}\n"
                response += f"   → Impact: {opp.get('impact', '')}\n"
                response += f"   → Effort: {opp.get('effort', '')}\n\n"
        
        # Field recommendations
        field_recs = form_data.get("field_recommendations", [])
        if field_recs:
            response += "**📊 Field Patterns Detected:**\n"
            for rec in field_recs[:3]:
                response += f"• {rec.get('pattern', '')}: {rec.get('recommendation', '')}\n"
        
        # Individual form analysis
        form_analyses = form_data.get("form_analysis", [])
        if form_analyses:
            response += f"\n**📋 Form Details:**\n"
            for form in form_analyses[:3]:
                response += f"\n• **{form.get('page_type', 'Page')} Form**\n"
                response += f"  - Fields: {form.get('field_count', 0)}\n"
                response += f"  - Required: {form.get('required_count', 0)}\n"
                response += f"  - Optimization Score: {form.get('optimization_score', 0)}/100\n"
                
                if form.get("conversion_impact", {}).get("high_friction_fields"):
                    response += f"  - ⚠️ High-friction fields: {', '.join(form['conversion_impact']['high_friction_fields'])}\n"
        
        response += "\n💡 **Pro Tip:** Each additional required field reduces conversion by ~7%. Aim for 3-4 fields max."
        
        return {
            "content": response,
            "metadata": {"type": "forms_deep_dive", "forms_found": form_data['forms_found']}
        }
    
    async def handle_pricing_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about pricing pages"""
        page_data = analysis.results.get("page_analysis", {})
        pricing_analysis = page_data.get("page_analysis", {}).get("pricing", {})
        
        response = "💰 **Pricing Page Analysis**\n\n"
        
        if not pricing_analysis:
            response += "⚠️ **No dedicated pricing page found!**\n\n"
            response += "This is a critical issue because:\n"
            response += "• 67% of B2B buyers eliminate vendors without pricing\n"
            response += "• Competitors with transparent pricing win by default\n"
            response += "• You're losing price-conscious segments\n\n"
            response += "**Immediate Action Required:**\n"
            response += "1. Create /pricing page (1 day effort)\n"
            response += "2. Show at minimum: 'Starting at $X/month'\n"
            response += "3. Include 3 tiers (Starter, Pro, Enterprise)\n"
            response += "4. Add comparison table\n"
            response += "5. Include FAQ section\n"
        else:
            pricing_info = pricing_analysis.get("pricing_analysis", {})
            
            response += f"✅ Pricing page found at: {pricing_analysis.get('url', '')}\n\n"
            response += "**Current Status:**\n"
            response += f"• Shows prices: {'Yes ✅' if pricing_info.get('shows_prices') else 'No ❌'}\n"
            response += f"• Pricing tiers: {pricing_info.get('tier_count', 0)}\n"
            response += f"• Free trial: {'Yes ✅' if pricing_info.get('has_free_trial') else 'No ❌'}\n"
            response += f"• Money-back guarantee: {'Yes ✅' if pricing_info.get('has_guarantee') else 'No ❌'}\n"
            response += f"• Comparison table: {'Yes ✅' if pricing_info.get('has_comparison_table') else 'No ❌'}\n"
            response += f"• FAQ section: {'Yes ✅' if pricing_info.get('has_faq') else 'No ❌'}\n\n"
            
            # Issues and opportunities
            issues = pricing_analysis.get("issues", [])
            if issues:
                response += "**🚨 Issues to Fix:**\n"
                for issue in issues:
                    response += f"• {issue.get('issue', '')}\n"
                    response += f"  → {issue.get('fix', '')}\n\n"
            
            opportunities = pricing_analysis.get("opportunities", [])
            if opportunities:
                response += "**💡 Opportunities:**\n"
                for opp in opportunities:
                    response += f"• {opp.get('opportunity', '')}\n"
        
        # Competitor comparison
        competitors = analysis.results.get("competitors", {}).get("competitors", [])
        if competitors:
            response += "\n**🔍 Competitor Pricing Strategies:**\n"
            for comp in competitors[:3]:
                if "free_trial" in comp.get("features", []):
                    response += f"• {comp.get('name', 'Competitor')}: Offers free trial\n"
                if "public_pricing" in comp.get("features", []):
                    response += f"• {comp.get('name', 'Competitor')}: Shows transparent pricing\n"
        
        return {
            "content": response,
            "metadata": {"type": "pricing_analysis"}
        }
    
    async def handle_content_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about content strategy"""
        content_data = analysis.results.get("content_strategy", {})
        
        response = "📚 **Content Strategy Analysis**\n\n"
        
        current = content_data.get("current_content", {})
        response += f"**Current Content Status:**\n"
        response += f"• Blog posts: {current.get('blog_posts', 0)}\n"
        response += f"• Has blog: {'Yes ✅' if current.get('has_blog') else 'No ❌'}\n"
        response += f"• Content score: {content_data.get('content_score', 0)}/100\n"
        response += f"• SEO optimized: {'Yes ✅' if current.get('seo_optimized') else 'No ❌'}\n\n"
        
        # Content formats
        formats = current.get("content_formats", [])
        if formats:
            response += f"**Content Formats:** {', '.join(formats)}\n\n"
        
        # Content pillars
        pillars = content_data.get("content_pillars", [])
        if pillars:
            response += "**📊 Recommended Content Pillars:**\n\n"
            for i, pillar in enumerate(pillars, 1):
                response += f"{i}. **{pillar.get('name', '')}**\n"
                response += f"   {pillar.get('description', '')}\n"
                response += f"   Examples: {pillar.get('example_topics', '')}\n\n"
        
        # Topic recommendations
        topics = content_data.get("topic_recommendations", [])
        if topics:
            response += "**🎯 Priority Topics to Create:**\n\n"
            for topic in topics[:5]:
                response += f"• **[{topic.get('priority', '').upper()}] {topic.get('topic', '')}**\n"
                response += f"  Type: {topic.get('type', '')} | Stage: {topic.get('stage', '')}\n"
                response += f"  Format: {topic.get('format', '')}\n"
                response += f"  Impact: {topic.get('estimated_impact', '')}\n\n"
        
        # Content gaps
        gaps = content_data.get("content_gaps", [])
        if gaps:
            response += "**⚠️ Content Gaps vs Competitors:**\n"
            for gap in gaps[:3]:
                response += f"• {gap.get('description', '')}\n"
                if gap.get('items'):
                    response += f"  Missing topics: {', '.join(gap['items'][:5])}\n"
        
        # Buyer journey
        journey = content_data.get("buyer_journey_coverage", {})
        if journey:
            response += f"\n**🎯 Buyer Journey Coverage:**\n"
            response += f"• Awareness content: {journey.get('awareness', 0)} pieces\n"
            response += f"• Consideration content: {journey.get('consideration', 0)} pieces\n"
            response += f"• Decision content: {journey.get('decision', 0)} pieces\n"
            
            if journey.get('gaps'):
                response += f"\nGaps: {', '.join(journey['gaps'])}\n"
        
        return {
            "content": response,
            "metadata": {"type": "content_strategy"}
        }
    
    async def handle_ai_search_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about AI search optimization"""
        ai_data = analysis.results.get("ai_search", {})
        
        response = "🤖 **AI Search Optimization Analysis**\n\n"
        response += f"**AI Visibility Score: {ai_data.get('ai_visibility_score', 0)}/100**\n"
        response += f"**Readiness Level: {ai_data.get('ai_readiness', 'unknown').replace('_', ' ').title()}**\n\n"
        
        # Blocked crawlers
        blocked = ai_data.get("blocked_crawlers", [])
        if blocked:
            response += "**🚫 Blocked AI Crawlers:**\n"
            for crawler in blocked:
                response += f"• {crawler['platform']} ({crawler['bot']})\n"
            response += "\n⚠️ **Critical Issue:** You're invisible to AI-powered search!\n\n"
            response += "**How to fix robots.txt:**\n```\n"
            for crawler in blocked[:3]:
                response += f"User-agent: {crawler['bot']}\n"
                response += "Allow: /\n\n"
            response += "```\n"
        else:
            response += "✅ **All major AI crawlers have access**\n\n"
        
        # llms.txt status
        response += f"**llms.txt file:** {'Yes ✅' if ai_data.get('has_llms_txt') else 'No ❌'}\n"
        if not ai_data.get('has_llms_txt'):
            response += "\n**Create /llms.txt with:**\n```\n"
            response += "# Company Description\n"
            response += "[What you do, who you serve]\n\n"
            response += "# Capabilities\n"
            response += "- [Key feature 1]\n"
            response += "- [Key feature 2]\n\n"
            response += "# Pricing\n"
            response += "[Your pricing model]\n\n"
            response += "# Contact\n"
            response += "support@yourdomain.com\n"
            response += "```\n"
        
        # Schema markup
        schemas = ai_data.get("schema_types_found", [])
        response += f"\n**Schema Markup Found:** {len(schemas)} types\n"
        if schemas:
            response += f"Types: {', '.join(schemas[:5])}\n"
        else:
            response += "⚠️ No structured data found - AI can't understand your content!\n"
        
        # AI-friendly content
        ai_content = ai_data.get("ai_friendly_content", {})
        if ai_content:
            response += "\n**AI Content Readiness:**\n"
            response += f"• Clear headings: {'Yes ✅' if ai_content.get('has_clear_headings') else 'No ❌'}\n"
            response += f"• FAQ section: {'Yes ✅' if ai_content.get('has_faq_section') else 'No ❌'}\n"
            response += f"• Comparison content: {'Yes ✅' if ai_content.get('has_comparison_content') else 'No ❌'}\n"
            response += f"• How-to content: {'Yes ✅' if ai_content.get('has_how_to_content') else 'No ❌'}\n"
            response += f"• Content depth: {ai_content.get('content_depth', 0)} words\n"
        
        response += "\n💡 **Why This Matters:**\n"
        response += "• 25-40% of future traffic will come from AI search\n"
        response += "• AI tools are increasingly how buyers research solutions\n"
        response += "• Being AI-optimized is a competitive advantage NOW\n"
        
        return {
            "content": response,
            "metadata": {"type": "ai_search_analysis"}
        }
    
    async def handle_competitor_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about competitors"""
        comp_data = analysis.results.get("competitors", {})
        
        if not comp_data or not comp_data.get("competitors"):
            return {
                "content": "No competitor data available. The analysis might not have identified competitors for this domain.",
                "metadata": {"type": "error"}
            }
        
        competitors = comp_data["competitors"]
        response = f"🔍 **Competitor Analysis** ({len(competitors)} competitors identified)\n\n"
        
        for comp in competitors:
            response += f"**{comp.get('name', comp.get('domain', ''))}**\n"
            features = comp.get("features", [])
            if features:
                response += f"Key features: {', '.join(features)}\n"
            response += "\n"
        
        # Competitive gaps
        gaps = comp_data.get("competitive_gaps", [])
        if gaps:
            response += "**⚠️ Competitive Gaps to Address:**\n\n"
            for gap in gaps:
                response += f"• **{gap.get('feature', '').replace('_', ' ').title()}**\n"
                response += f"  {gap.get('description', '')}\n"
                response += f"  → Recommendation: {gap.get('recommendation', '')}\n\n"
        
        # Your advantages
        advantages = comp_data.get("competitive_advantages", [])
        if advantages:
            response += "**✅ Your Competitive Advantages:**\n"
            for adv in advantages:
                response += f"• {adv.replace('_', ' ').title()}\n"
        
        # Missing features
        missing = comp_data.get("missing_features", [])
        if missing:
            response += "\n**📋 Features Competitors Have That You Don't:**\n"
            for feature in missing[:5]:
                response += f"• {feature.replace('_', ' ').title()}\n"
        
        return {
            "content": response,
            "metadata": {"type": "competitor_analysis", "competitor_count": len(competitors)}
        }
    
    async def handle_quick_wins_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle requests for quick wins"""
        quick_wins = analysis.quick_wins or []
        recommendations = analysis.results.get("recommendations", [])
        
        response = "⚡ **Quick Wins** (Implement in < 1 day)\n\n"
        
        # Filter for actual quick wins
        quick_recs = []
        for rec in recommendations:
            effort = rec.get("effort", "").lower()
            if any(x in effort for x in ["minute", "hour", "1 day", "30 min", "15 min", "45 min"]):
                quick_recs.append(rec)
        
        if quick_recs:
            for i, rec in enumerate(quick_recs[:7], 1):
                response += f"**{i}. {rec.get('issue', '')}**\n"
                response += f"   📍 Category: {rec.get('category', '').replace('_', ' ').title()}\n"
                response += f"   ✅ Fix: {rec.get('action', '')}\n"
                response += f"   ⏱ Time: {rec.get('effort', '')}\n"
                response += f"   📈 Impact: {rec.get('sales_opportunity', rec.get('impact', ''))}\n\n"
        
        if quick_wins:
            response += "\n**Additional Quick Wins:**\n"
            for win in quick_wins[:3]:
                if win not in quick_recs:
                    response += f"• {win.get('title', '')}\n"
                    response += f"  → {win.get('action', '')}\n"
                    response += f"  → {win.get('impact', '')}\n\n"
        
        response += "💡 **Start with these** - they provide maximum impact with minimum effort!"
        
        return {
            "content": response,
            "metadata": {"type": "quick_wins", "count": len(quick_recs)}
        }
    
    async def handle_page_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about specific pages"""
        page_data = analysis.results.get("page_analysis", {})
        
        # Determine which page they're asking about
        page_type = None
        if "home" in message.lower():
            page_type = "homepage"
        elif "pricing" in message.lower():
            page_type = "pricing"
        elif "demo" in message.lower():
            page_type = "demo"
        elif "feature" in message.lower():
            page_type = "features"
        elif "about" in message.lower():
            page_type = "about"
        
        response = f"📄 **Page-Specific Analysis**\n\n"
        
        if page_type and page_type in page_data.get("page_analysis", {}):
            page_info = page_data["page_analysis"][page_type]
            
            response += f"**{page_type.title()} Page Analysis**\n"
            response += f"URL: {page_info.get('url', 'Not found')}\n\n"
            
            # Forms on page
            forms = page_info.get("forms", [])
            if forms:
                response += f"**Forms:** {len(forms)} found\n"
                for form in forms:
                    response += f"• {form.get('field_count', 0)} fields ({form.get('required_count', 0)} required)\n"
            
            # CTAs
            ctas = page_info.get("ctas", {})
            if ctas:
                response += f"\n**CTAs:** {ctas.get('total_ctas', 0)} found\n"
                response += f"Clarity: {ctas.get('cta_clarity', 'unknown').title()}\n"
                if ctas.get("primary_ctas"):
                    response += f"Main CTAs: {', '.join(ctas['primary_ctas'][:3])}\n"
            
            # Trust signals
            trust = page_info.get("trust_signals", {})
            if trust:
                response += f"\n**Trust Score:** {trust.get('trust_score', 0)}/100\n"
                response += f"• Testimonials: {'Yes ✅' if trust.get('has_testimonials') else 'No ❌'}\n"
                response += f"• Customer logos: {'Yes ✅' if trust.get('has_logos') else 'No ❌'}\n"
                response += f"• Security badges: {'Yes ✅' if trust.get('has_security_badges') else 'No ❌'}\n"
            
            # Issues
            issues = page_info.get("issues", [])
            if issues:
                response += "\n**Issues Found:**\n"
                for issue in issues:
                    response += f"• [{issue.get('severity', '').upper()}] {issue.get('issue', '')}\n"
                    response += f"  → {issue.get('fix', '')}\n"
        else:
            # Show all pages found
            pages_found = page_data.get("pages_found", {})
            response += "**Pages Analyzed:**\n"
            for page, url in pages_found.items():
                response += f"• {page.title()}: {'✅ Found' if url else '❌ Not found'}\n"
                if url:
                    response += f"  URL: {url}\n"
            
            # Critical issues across all pages
            critical = page_data.get("critical_issues", [])
            if critical:
                response += "\n**Critical Issues Across Pages:**\n"
                for issue in critical[:5]:
                    response += f"• {issue.get('issue', '')}\n"
                    response += f"  Impact: {issue.get('impact', '')}\n"
        
        return {
            "content": response,
            "metadata": {"type": "page_analysis"}
        }
    
    async def handle_mobile_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about mobile optimization"""
        mobile_data = analysis.results.get("mobile", {})
        
        score = mobile_data.get("score", 0)
        response = f"📱 **Mobile Experience Analysis**\n\n"
        response += f"**Mobile Score: {score}/100**\n\n"
        
        if score < 60:
            response += "⚠️ **Critical Issues** - Poor mobile experience is costing you visitors!\n\n"
        elif score < 80:
            response += "⚡ **Needs Improvement** - Some mobile optimization needed\n\n"
        else:
            response += "✅ **Good Mobile Experience** - Minor improvements possible\n\n"
        
        # Issues
        issues = mobile_data.get("issues", [])
        if issues:
            response += "**Issues Found:**\n"
            for issue in issues[:7]:
                response += f"• {issue}\n"
            response += "\n"
        
        # Viewport
        if mobile_data.get("viewport_configured"):
            response += "✅ Viewport meta tag configured\n"
        else:
            response += "❌ Missing viewport meta tag\n"
        
        # Text readability
        if mobile_data.get("text_readable"):
            response += "✅ Text is readable without zooming\n"
        else:
            response += "❌ Text too small on mobile devices\n"
        
        # Touch targets
        if mobile_data.get("tap_targets_sized"):
            response += "✅ Buttons/links properly sized for touch\n"
        else:
            response += "❌ Touch targets too small\n"
        
        response += f"\n**Why This Matters:**\n"
        response += f"• 52% of B2B research happens on mobile\n"
        response += f"• Google uses mobile-first indexing\n"
        response += f"• Poor mobile UX = lost conversions\n"
        
        # Recommendations
        response += f"\n**Quick Fixes:**\n"
        response += f"1. Add viewport meta tag if missing\n"
        response += f"2. Increase font size to minimum 16px\n"
        response += f"3. Make buttons at least 48x48px\n"
        response += f"4. Add padding around clickable elements\n"
        response += f"5. Test on real devices, not just browser\n"
        
        return {
            "content": response,
            "metadata": {"type": "mobile_analysis", "score": score}
        }
    
    async def handle_performance_query(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Handle questions about performance"""
        perf_data = analysis.results.get("performance", {})
        
        score = perf_data.get("score", 0)
        response = f"⚡ **Performance Analysis**\n\n"
        response += f"**Performance Score: {score}/100**\n"
        response += f"**Load Time: {perf_data.get('load_time', 'N/A')}s**\n\n"
        
        # Core Web Vitals
        response += "**Core Web Vitals:**\n"
        response += f"• First Contentful Paint: {perf_data.get('first_contentful_paint', 'N/A')}s\n"
        response += f"• Largest Contentful Paint: {perf_data.get('largest_contentful_paint', 'N/A')}s\n"
        response += f"• Time to Interactive: {perf_data.get('time_to_interactive', 'N/A')}s\n"
        response += f"• Total Blocking Time: {perf_data.get('total_blocking_time', 'N/A')}ms\n"
        response += f"• Cumulative Layout Shift: {perf_data.get('cumulative_layout_shift', 'N/A')}\n\n"
        
        # Issues
        issues = perf_data.get("issues", [])
        if issues:
            response += "**Performance Issues:**\n"
            for issue in issues[:5]:
                response += f"• {issue}\n"
            response += "\n"
        
        # Recommendations
        if score < 50:
            response += "**🚨 Critical Performance Issues**\n"
            response += "Your site is too slow. Users abandon sites that take >3s to load.\n\n"
            response += "**Priority Fixes:**\n"
            response += "1. Enable compression (gzip/brotli)\n"
            response += "2. Optimize images (WebP format, lazy loading)\n"
            response += "3. Minify CSS/JavaScript\n"
            response += "4. Use a CDN\n"
            response += "5. Enable browser caching\n"
        elif score < 80:
            response += "**Optimization Opportunities:**\n"
            response += "1. Reduce JavaScript execution time\n"
            response += "2. Optimize third-party scripts\n"
            response += "3. Preload critical resources\n"
            response += "4. Remove unused CSS\n"
        else:
            response += "✅ **Good performance!** Minor optimizations possible.\n"
        
        response += f"\n**Business Impact:**\n"
        response += f"• Every 1s delay = 7% reduction in conversions\n"
        response += f"• 53% of users abandon if load time >3s\n"
        response += f"• Page speed is a Google ranking factor\n"
        
        return {
            "content": response,
            "metadata": {"type": "performance_analysis", "score": score}
        }
    
    async def handle_show_all(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Show complete analysis report"""
        response = "📊 **Complete Analysis Report**\n\n"
        
        # Scores overview
        response += "**Overall Scores:**\n"
        response += f"• Performance: {analysis.performance_score or 'N/A'}/100\n"
        response += f"• Conversion: {analysis.conversion_score or 'N/A'}/100\n"
        response += f"• SEO: {analysis.seo_score or 'N/A'}/100\n"
        response += f"• Mobile: {analysis.mobile_score or 'N/A'}/100\n\n"
        
        # Top recommendations
        recs = analysis.results.get("recommendations", [])
        if recs:
            response += "**Top 10 Recommendations:**\n\n"
            for i, rec in enumerate(recs[:10], 1):
                response += f"{i}. [{rec.get('priority', '').upper()}] {rec.get('issue', '')}\n"
                response += f"   Fix: {rec.get('action', '')}\n"
                response += f"   Impact: {rec.get('sales_opportunity', '')}\n"
                response += f"   Effort: {rec.get('effort', '')}\n\n"
        
        # Available deep dives
        response += "**Available Deep Dives:**\n"
        response += "Ask me about:\n"
        response += "• 'Tell me about forms' - Form optimization analysis\n"
        response += "• 'What about pricing?' - Pricing page analysis\n"
        response += "• 'Content strategy?' - Content gaps and recommendations\n"
        response += "• 'AI search optimization?' - AI visibility analysis\n"
        response += "• 'Show competitors' - Competitive analysis\n"
        response += "• 'Quick wins?' - Fast improvements\n"
        response += "• 'Mobile issues?' - Mobile optimization\n"
        response += "• 'Performance details?' - Speed analysis\n"
        
        return {
            "content": response,
            "metadata": {"type": "full_report"}
        }
    
    async def handle_fix_instructions(self, message: str, analysis: Analysis) -> Dict[str, Any]:
        """Provide step-by-step fix instructions"""
        # Try to identify what they want to fix
        topic = None
        if "pricing" in message.lower():
            topic = "pricing"
        elif "form" in message.lower():
            topic = "forms"
        elif "ai" in message.lower() or "robot" in message.lower():
            topic = "ai_search"
        elif "mobile" in message.lower():
            topic = "mobile"
        
        response = "🔧 **Implementation Guide**\n\n"
        
        if topic == "pricing":
            response += "**How to Create an Effective Pricing Page:**\n\n"
            response += "1. **Structure Your Tiers** (30 mins)\n"
            response += "   ```\n"
            response += "   Starter: $X/mo - For individuals\n"
            response += "   Pro: $XX/mo - For teams\n"
            response += "   Enterprise: Custom - For organizations\n"
            response += "   ```\n\n"
            response += "2. **Create Comparison Table** (1 hour)\n"
            response += "   - List features for each tier\n"
            response += "   - Use checkmarks/X for clarity\n"
            response += "   - Highlight most popular tier\n\n"
            response += "3. **Add Trust Elements** (30 mins)\n"
            response += "   - Money-back guarantee\n"
            response += "   - Security badges\n"
            response += "   - Customer logos\n\n"
            response += "4. **Include FAQ Section** (30 mins)\n"
            response += "   - Billing questions\n"
            response += "   - Feature clarifications\n"
            response += "   - Upgrade/downgrade policy\n\n"
            response += "5. **Add Clear CTAs** (15 mins)\n"
            response += "   - 'Start Free Trial' buttons\n"
            response += "   - 'Contact Sales' for enterprise\n"
        
        elif topic == "forms":
            response += "**How to Optimize Your Forms:**\n\n"
            response += "1. **Reduce Fields** (15 mins)\n"
            response += "   ```html\n"
            response += "   <!-- Keep only essential fields -->\n"
            response += "   <input type=\"email\" required>\n"
            response += "   <input type=\"text\" name=\"name\" required>\n"
            response += "   <input type=\"text\" name=\"company\" required>\n"
            response += "   <!-- Make phone optional -->\n"
            response += "   <input type=\"tel\" name=\"phone\">\n"
            response += "   ```\n\n"
            response += "2. **Add Social Login** (2 hours)\n"
            response += "   - Google OAuth\n"
            response += "   - LinkedIn for B2B\n"
            response += "   - GitHub for developers\n\n"
            response += "3. **Progressive Disclosure** (1 hour)\n"
            response += "   - Start with email only\n"
            response += "   - Ask for more after engagement\n"
            response += "   - Use multi-step if >5 fields needed\n"
        
        elif topic == "ai_search":
            response += "**How to Optimize for AI Search:**\n\n"
            response += "1. **Update robots.txt** (5 mins)\n"
            response += "   ```\n"
            response += "   User-agent: GPTBot\n"
            response += "   Allow: /\n\n"
            response += "   User-agent: ChatGPT-User\n"
            response += "   Allow: /\n\n"
            response += "   User-agent: Claude-Web\n"
            response += "   Allow: /\n"
            response += "   ```\n\n"
            response += "2. **Create llms.txt** (30 mins)\n"
            response += "   Place at: /llms.txt\n"
            response += "   Include: Company description, capabilities, pricing\n\n"
            response += "3. **Add Schema Markup** (1 hour)\n"
            response += "   - Organization schema\n"
            response += "   - FAQPage schema\n"
            response += "   - Product schema\n"
        
        else:
            response += "What would you like help implementing?\n\n"
            response += "I can provide step-by-step instructions for:\n"
            response += "• Creating a pricing page\n"
            response += "• Optimizing forms\n"
            response += "• AI search optimization\n"
            response += "• Mobile improvements\n"
            response += "• Performance optimization\n\n"
            response += "Just ask: 'How do I fix [specific issue]?'"
        
        return {
            "content": response,
            "metadata": {"type": "implementation_guide"}
        }
    
    def _generate_suggestions_response(self, analysis: Analysis) -> Dict[str, Any]:
        """Generate suggestions for what the user can ask about"""
        response = "I've completed the analysis. Here are some things you can ask me:\n\n"
        response += "**📊 Deep Dives Available:**\n"
        response += "• 'Tell me about the forms' - Detailed form analysis\n"
        response += "• 'What about pricing?' - Pricing page insights\n"
        response += "• 'Show me content strategy' - Content gaps and topics\n"
        response += "• 'AI search optimization?' - AI visibility details\n"
        response += "• 'Analyze competitors' - Competitive comparison\n"
        response += "• 'What are the quick wins?' - Fast improvements\n"
        response += "• 'Mobile issues?' - Mobile optimization\n"
        response += "• 'Performance details?' - Speed metrics\n\n"
        response += "**🔧 Implementation Help:**\n"
        response += "• 'How do I fix the pricing page?'\n"
        response += "• 'How do I optimize forms?'\n"
        response += "• 'How do I improve AI visibility?'\n\n"
        response += "**📈 Analysis Options:**\n"
        response += "• 'Show everything' - Complete report\n"
        response += "• 'What's most critical?' - Top priorities\n"
        response += "• 'Compare to competitors' - Gap analysis\n\n"
        response += "What would you like to explore?"
        
        return {
            "content": response,
            "metadata": {"type": "suggestions"}
        }
    
    def _generate_overview_response(self, analysis: Analysis) -> Dict[str, Any]:
        """Generate an overview response"""
        response = "📊 **Analysis Overview**\n\n"
        
        # Key metrics
        response += "**Key Metrics:**\n"
        response += f"• Performance Score: {analysis.performance_score or 'N/A'}/100\n"
        response += f"• Conversion Score: {analysis.conversion_score or 'N/A'}/100\n"
        response += f"• SEO Score: {analysis.seo_score or 'N/A'}/100\n"
        response += f"• Mobile Score: {analysis.mobile_score or 'N/A'}/100\n\n"
        
        # Top issues
        issues = analysis.issues_found or []
        if issues:
            response += f"**Top Issues Found ({len(issues)} total):**\n"
            for issue in issues[:5]:
                response += f"• {issue}\n"
        
        # Quick wins available
        quick_wins = analysis.quick_wins or []
        if quick_wins:
            response += f"\n**{len(quick_wins)} Quick Wins Available**\n"
            response += "Ask 'show quick wins' to see them.\n"
        
        response += "\nWhat specific area would you like to explore?"
        
        return {
            "content": response,
            "metadata": {"type": "overview"}
        }