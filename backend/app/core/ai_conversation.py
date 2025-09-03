from typing import Dict, Any, Optional, List
import re
import json
import structlog
from app.models.analysis import Analysis
from app.models.conversation import Conversation
from app.config import settings
from app.core.ai_providers import AIProviderFactory

logger = structlog.get_logger()


class AIConversationEngine:
    """
    AI-powered conversational engine that understands natural language
    and provides dynamic, contextual responses about growth marketing.
    """
    
    def __init__(self):
        # Use the new AI provider factory
        self.provider = AIProviderFactory.create_provider()
        
        # Log which model we're using
        if self.provider:
            logger.info(f"AI Conversation Engine initialized with: {self.provider.get_model_name()}")
        else:
            logger.warning("No AI provider available - using fallback responses")
        
        self.system_prompt = """You are Growth Co-pilot, an expert growth marketing AI that analyzes websites and finds revenue opportunities.

CRITICAL INSTRUCTION: You MUST use ONLY the actual data provided in the context. Never make up numbers or metrics.

🔍 REAL DATA WE PROVIDE IN CONTEXT:
- Performance scores and load times (from PageSpeed API)
- SEO scores and issues (from SEO analyzer)
- Form field counts and conversion lift potential (from form analyzer)
- Competitor names and feature gaps (from competitor analyzer)
- AI search visibility and blocked crawlers (from robots.txt analysis)
- Mobile scores and issues (from mobile analyzer)
- Missing pages like pricing/demo (from page analyzer)
- Content gaps and recommendations (from content analyzer)

STRICT RESPONSE RULES:
1. ONLY use numbers from the context provided - NEVER invent metrics
2. If a metric isn't in context, say "Based on our analysis..." without inventing numbers
3. Always reference specific data: "Your performance score is X" (from context.scores.performance)
4. For competitors, use actual names from context.competitors.names
5. For issues, use actual issues from context (performance.issues, forms.issues, etc.)

CONTEXT-AWARE RESPONSES:
- When asked about "SEO": Focus on context.scores.seo, context.pages.missing_pages, context.content
- When asked about "competitors": Use context.competitors.names, gaps, and strengths
- When asked about "performance": Use context.performance.score, load_time, issues
- When asked about "forms": Use context.forms.conversion_lift_potential, field_count, issues
- When asked about "AI search": Use context.ai_search.blocked_crawlers, score

FORMATTING RULES:
1. Use visual indicators: ✅ for good, ⚠️ for warning, ❌ for issues
2. Structure with clear sections and bullet points
3. Lead with the most impactful finding from the data
4. Provide specific, actionable fixes based on the actual issues found

When discussing specific topics:
- SEO: "Your SEO score is [context.scores.seo]/100. Key issues: [context.pages.missing_pages]"
- Competitors: "[context.competitors.names] offer features you're missing: [context.competitors.gaps]"
- Performance: "Load time: [context.performance.load_time]s, Score: [context.performance.score]/100"
- Forms: "Potential [context.forms.conversion_lift_potential]% conversion increase by optimizing forms"

NEVER say things like:
- "Your site loads in 1.2 seconds" (unless context.performance.load_time = 1.2)
- "You have 85/100 SEO score" (unless context.scores.seo = 85)
- "You get 10,000 visits/month" (unless this exact number is in context)

If data is missing from context, say:
"I don't have specific data on [topic] from this analysis. Would you like me to run a deeper analysis on [topic]?"""
    
    async def generate_response(
        self,
        user_message: str,
        analysis: Optional[Analysis] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate a natural, contextual response to any user input"""
        
        if not self.provider:
            return self._generate_fallback_response(user_message, analysis)
        
        try:
            # Build context from analysis
            context = self._build_context(analysis) if analysis else {}
            
            # Build conversation history for context
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Build the user prompt with context
            user_prompt = self._build_user_prompt(user_message, context)
            messages.append({"role": "user", "content": user_prompt})
            
            # Generate response using the provider
            content = await self.provider.generate_completion(
                messages=messages,
                temperature=0.7
                # No max_tokens limit for complete responses
            )
            
            # Extract any specific data requests from the response
            metadata = self._extract_metadata(content, analysis)
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"AI conversation failed: {str(e)}")
            return self._generate_fallback_response(user_message, analysis)
    
    def _build_context(self, analysis: Analysis) -> Dict[str, Any]:
        """Build context from analysis data"""
        if not analysis or not analysis.results:
            return {}
        
        context = {
            "domain": analysis.domain,
            "scores": {
                "performance": analysis.performance_score,
                "conversion": analysis.conversion_score,
                "seo": analysis.seo_score,
                "mobile": analysis.mobile_score
            }
        }
        
        # Extract key insights
        results = analysis.results
        
        # Performance insights
        perf = results.get("performance", {})
        context["performance"] = {
            "score": perf.get("score", 0),
            "load_time": perf.get("load_time", 0),
            "issues": perf.get("issues", [])[:3]
        }
        
        # Form intelligence
        forms = results.get("form_intelligence", {})
        context["forms"] = {
            "count": forms.get("forms_found", 0),
            "conversion_lift_potential": forms.get("estimated_conversion_lift", 0),
            "best_practices_score": forms.get("best_practices_score", 0),
            "issues": []
        }
        
        # Extract form issues
        for form_analysis in forms.get("form_analysis", [])[:2]:
            if form_analysis.get("field_count", 0) > 5:
                context["forms"]["issues"].append({
                    "page": form_analysis.get("page_type"),
                    "field_count": form_analysis.get("field_count"),
                    "high_friction_fields": form_analysis.get("conversion_impact", {}).get("high_friction_fields", [])
                })
        
        # Competitors with enhanced details
        comp_data = results.get("competitors", {})
        competitors = comp_data.get("competitors", [])
        comparison = comp_data.get("competitor_comparison", {})
        
        context["competitors"] = {
            "count": len(competitors),
            "names": [c.get("name", c.get("domain", "")) for c in competitors[:3]],
            "gaps": [],
            "summary": comparison.get("summary", ""),
            "key_takeaways": comparison.get("key_takeaways", []),
            "competitor_strengths": comparison.get("competitor_strengths", {})
        }
        
        # Enhanced competitive gaps with specific competitor names
        for gap in comp_data.get("competitive_gaps", [])[:5]:
            context["competitors"]["gaps"].append({
                "feature": gap.get("feature"),
                "impact": gap.get("impact"),
                "competitors_text": gap.get("competitors_text", ""),
                "business_impact": gap.get("business_impact", ""),
                "recommendation": gap.get("recommendation", ""),
                "implementation_time": gap.get("implementation_time", "")
            })
        
        # AI Search
        ai_search = results.get("ai_search", {})
        context["ai_search"] = {
            "score": ai_search.get("ai_visibility_score", 0),
            "blocked_crawlers": [c["platform"] for c in ai_search.get("blocked_crawlers", [])[:3]],
            "has_llms_txt": ai_search.get("has_llms_txt", False),
            "readiness": ai_search.get("ai_readiness", "unknown")
        }
        
        # Page-specific issues
        page_analysis = results.get("page_analysis", {})
        context["pages"] = {
            "found": list(page_analysis.get("pages_found", {}).keys()),
            "critical_issues": page_analysis.get("critical_issues", [])[:3],
            "missing_pages": []
        }
        
        # Check for missing critical pages
        pages_found = page_analysis.get("pages_found", {})
        if not pages_found.get("pricing"):
            context["pages"]["missing_pages"].append("pricing")
        if not pages_found.get("demo"):
            context["pages"]["missing_pages"].append("demo")
        
        # Content strategy
        content = results.get("content_strategy", {})
        context["content"] = {
            "blog_posts": content.get("current_content", {}).get("blog_posts", 0),
            "content_score": content.get("content_score", 0),
            "gaps": [g.get("description", "") for g in content.get("content_gaps", [])[:2]],
            "recommendations": [t.get("topic", "") for t in content.get("topic_recommendations", [])[:3]]
        }
        
        # Traffic
        traffic = results.get("traffic", {})
        context["traffic"] = {
            "estimated_visits": traffic.get("estimated_monthly_visits", 0),
            "domain_authority": traffic.get("domain_authority", 0)
        }
        
        # Quick wins
        context["quick_wins"] = []
        recommendations = results.get("recommendations", [])
        for rec in recommendations[:5]:
            effort = rec.get("effort", "").lower()
            if any(x in effort for x in ["minute", "hour", "1 day"]):
                context["quick_wins"].append({
                    "issue": rec.get("issue"),
                    "fix": rec.get("action"),
                    "impact": rec.get("sales_opportunity"),
                    "time": rec.get("effort")
                })
        
        # Revenue Intelligence data
        revenue_intel = results.get("revenue_intelligence", {})
        if revenue_intel:
            context["revenue_leaks"] = revenue_intel.get("revenue_leaks", [])[:3]
            context["conversion_blockers"] = revenue_intel.get("conversion_blockers", [])[:3]
            context["pricing_opportunities"] = revenue_intel.get("pricing_opportunities", [])[:3]
            context["total_revenue_impact"] = revenue_intel.get("total_revenue_impact", 0)
            context["metrics_request"] = revenue_intel.get("metrics_request", {})
        
        # Growth Opportunities data
        growth_opps = results.get("growth_opportunities", {})
        if growth_opps:
            context["untapped_channels"] = growth_opps.get("untapped_channels", [])[:3]
            context["viral_opportunities"] = growth_opps.get("viral_opportunities", [])[:2]
            context["referral_opportunities"] = growth_opps.get("referral_opportunities", [])[:2]
            context["total_user_potential"] = growth_opps.get("total_user_potential", 0)
        
        return context
    
    def _build_user_prompt(self, user_message: str, context: Dict) -> str:
        """Build the prompt with user message and context"""
        
        if not context:
            return user_message
        
        # Determine what the user is asking about
        message_lower = user_message.lower()
        is_seo_question = 'seo' in message_lower or 'search' in message_lower
        is_competitor_question = 'competitor' in message_lower or 'vs' in message_lower or 'compare' in message_lower
        is_performance_question = 'performance' in message_lower or 'speed' in message_lower or 'load' in message_lower
        
        prompt = f"""User question: {user_message}

ACTUAL ANALYSIS DATA for {context.get('domain', 'the website')}:

REAL SCORES FROM OUR ANALYSIS:
- Performance: {context['scores']['performance']}/100
- Conversion: {context['scores']['conversion']}/100
- SEO: {context['scores']['seo']}/100
- Mobile: {context['scores']['mobile']}/100

SPECIFIC DATA POINTS:
"""
        
        # Add form insights
        if context.get("forms", {}).get("conversion_lift_potential", 0) > 10:
            prompt += f"\n- Forms can be optimized for {context['forms']['conversion_lift_potential']}% conversion lift"
            if context['forms'].get('issues'):
                for issue in context['forms']['issues']:
                    prompt += f"\n  • {issue['page']} form has {issue['field_count']} fields"
        
        # Add detailed competitor insights
        if context.get("competitors", {}).get("gaps"):
            prompt += f"\n\nCOMPETITOR ANALYSIS:"
            prompt += f"\n- Competitors: {', '.join(context['competitors'].get('names', [])) if context['competitors'].get('names') else 'Unknown'}"
            prompt += f"\n- You're missing {len(context['competitors']['gaps'])} features that competitors offer"
            for gap in context['competitors']['gaps'][:3]:
                prompt += f"\n  • {gap['feature']}: {gap.get('competitors_text', 'Competitors offer this')}"
                prompt += f"\n    Impact: {gap.get('business_impact', 'Competitive disadvantage')}"
        
        # Add AI search insights
        if context.get("ai_search", {}).get("blocked_crawlers"):
            prompt += f"\n- Blocking AI crawlers: {', '.join(context['ai_search']['blocked_crawlers'])}"
        
        # Add missing pages
        if context.get("pages", {}).get("missing_pages"):
            prompt += f"\n- Missing critical pages: {', '.join(context['pages']['missing_pages'])}"
        
        # Add traffic data
        if context.get("traffic", {}).get("estimated_visits"):
            prompt += f"\n- Estimated traffic: {context['traffic']['estimated_visits']:,} visits/month"
            prompt += f"\n- Domain authority: {context['traffic']['domain_authority']}/100"
        
        # Add actual performance data
        if context.get("performance", {}).get("load_time"):
            prompt += f"\n- Actual load time: {context['performance']['load_time']} seconds"
        if context.get("performance", {}).get("issues"):
            prompt += f"\n- Performance issues found: {', '.join(context['performance']['issues'][:3])}"
        
        # Add quick wins
        if context.get("quick_wins"):
            prompt += f"\n- {len(context['quick_wins'])} quick wins available"
        
        # Add Revenue Intelligence insights
        if context.get("total_revenue_impact"):
            prompt += f"\n\nREVENUE INTELLIGENCE:"
            prompt += f"\n- Total monthly revenue impact identified: ${context['total_revenue_impact']:,.0f}"
            
            if context.get("conversion_blockers"):
                prompt += f"\n- {len(context['conversion_blockers'])} conversion blockers found"
                for blocker in context['conversion_blockers'][:2]:
                    prompt += f"\n  • {blocker.get('issue', '')}: ${blocker.get('monthly_impact', 0):,.0f}/month"
            
            if context.get("pricing_opportunities"):
                prompt += f"\n- {len(context['pricing_opportunities'])} pricing opportunities"
                for opp in context['pricing_opportunities'][:2]:
                    prompt += f"\n  • {opp.get('issue', '')}"
        
        # Add Growth Opportunities
        if context.get("total_user_potential"):
            prompt += f"\n\nGROWTH OPPORTUNITIES:"
            prompt += f"\n- Potential new users/month: {context['total_user_potential']:,}"
            
            if context.get("untapped_channels"):
                prompt += f"\n- {len(context['untapped_channels'])} untapped acquisition channels"
                for channel in context['untapped_channels'][:2]:
                    prompt += f"\n  • {channel.get('channel', '')}: {channel.get('expected_users', '')}"
        
        prompt += "\n\nIMPORTANT: Provide a response using ONLY the specific data points above. Do not invent any numbers or metrics not shown here. Focus on what's relevant to the user's question."
        
        # Add context-specific instructions
        if is_seo_question:
            prompt += f"\n\nFocus on: SEO score ({context['scores']['seo']}/100), missing pages ({context.get('pages', {}).get('missing_pages', [])}), content gaps."
        elif is_competitor_question:
            prompt += f"\n\nFocus on: Competitors ({', '.join(context.get('competitors', {}).get('names', []))}), competitive gaps, specific features they offer."
        elif is_performance_question:
            prompt += f"\n\nFocus on: Performance score ({context['scores']['performance']}/100), load time ({context.get('performance', {}).get('load_time', 'not measured')}), specific issues."
        
        return prompt
    
    def _extract_metadata(self, content: str, analysis: Optional[Analysis]) -> Dict[str, Any]:
        """Extract metadata from the AI response"""
        metadata = {
            "type": "ai_conversation"
        }
        
        # Check if response mentions specific areas
        content_lower = content.lower()
        if "competitor" in content_lower:
            metadata["topic"] = "competitors"
        elif "form" in content_lower:
            metadata["topic"] = "forms"
        elif "pricing" in content_lower:
            metadata["topic"] = "pricing"
        elif "mobile" in content_lower:
            metadata["topic"] = "mobile"
        elif "ai" in content_lower and "search" in content_lower:
            metadata["topic"] = "ai_search"
        elif "quick win" in content_lower:
            metadata["topic"] = "quick_wins"
        
        # Add suggested actions if mentioned
        if "ask me about" in content_lower or "try asking" in content_lower:
            metadata["has_suggestions"] = True
        
        return metadata
    
    def _generate_fallback_response(self, user_message: str, analysis: Optional[Analysis]) -> Dict[str, Any]:
        """Generate a fallback response without AI"""
        
        if not analysis:
            return {
                "content": "I need to analyze a website first. Please provide a domain name like 'example.com' and I'll analyze it for growth opportunities.",
                "metadata": {"type": "prompt"}
            }
        
        # Simple pattern matching for common questions
        message_lower = user_message.lower()
        
        # Check for AI search questions first (most specific)
        if ("ai" in message_lower and "search" in message_lower) or "chatgpt" in message_lower or "claude" in message_lower or "gpt" in message_lower:
            ai_data = analysis.results.get("ai_search", {})
            score = ai_data.get("ai_visibility_score", 0)
            blocked = ai_data.get("blocked_crawlers", [])
            has_llms = ai_data.get("has_llms_txt", False)
            
            if blocked:
                blocked_names = [c.get("platform", "") for c in blocked[:3]]
                return {
                    "content": f"⚠️ You're blocking AI crawlers ({', '.join(blocked_names)})! This means ChatGPT and Claude can't recommend your product. Your AI visibility score is only {score}/100. Fix your robots.txt to allow GPTBot, ChatGPT-User, and Claude-Web. Want the full AI optimization checklist?",
                    "metadata": {"type": "ai_search"}
                }
            else:
                content = f"Your AI search visibility score is {score}/100. "
                if not has_llms:
                    content += "You're missing an llms.txt file to guide AI responses about your product. "
                content += "Want specific recommendations to improve your AI search ranking?"
                return {
                    "content": content,
                    "metadata": {"type": "ai_search"}
                }
        
        elif "competitor" in message_lower:
            comp_data = analysis.results.get("competitors", {})
            competitors = comp_data.get("competitors", [])
            comparison = comp_data.get("competitor_comparison", {})
            gaps = comp_data.get("competitive_gaps", [])
            
            if competitors:
                names = [c.get("name", c.get("domain", "").split('.')[0].title()) for c in competitors[:3]]
                response_text = f"**Your main competitors:** {', '.join(names)}\n\n"
                
                # Be specific about what each competitor does better
                if gaps:
                    response_text += "**What they're doing better:**\n\n"
                    
                    # Group by competitor
                    for comp in competitors[:3]:
                        comp_name = comp.get("name", comp.get("domain", "").split('.')[0].title())
                        comp_features = comp.get("features", [])
                        
                        # Find what this specific competitor has that you don't
                        your_features = comp_data.get("your_features", [])
                        missing = [f for f in comp_features if f not in your_features]
                        
                        if missing:
                            response_text += f"**{comp_name}:**\n"
                            feature_map = {
                                "free_trial": "14-day free trial with instant access",
                                "public_pricing": "Transparent pricing starting at $120/month",
                                "self_service": "Self-serve signup without sales contact",
                                "demo": "Interactive product demo on homepage",
                                "api_access": "Public API documentation for developers",
                                "integrations": "150+ pre-built connectors",
                                "enterprise_security": "SOC2 Type II certified"
                            }
                            
                            for feature in missing[:3]:
                                feature_desc = feature_map.get(feature, feature.replace('_', ' ').title())
                                response_text += f"  • {feature_desc}\n"
                            response_text += "\n"
                    
                    # Add business impact
                    response_text += "**Business Impact:**\n"
                    for gap in gaps[:2]:
                        response_text += f"• {gap.get('business_impact', '')}\n"
                    
                    response_text += "\n**Quick Fix:** Start with a pricing page and free trial - these take 2-3 weeks combined.\n"
                    response_text += "\nWant the full implementation roadmap?"
                
                return {
                    "content": response_text,
                    "metadata": {"type": "competitors"}
                }
        
        elif "form" in message_lower:
            forms = analysis.results.get("form_intelligence", {})
            lift = forms.get("estimated_conversion_lift", 0)
            if lift > 0:
                return {
                    "content": f"Your forms can be optimized for {lift}% more conversions. The main issues are too many required fields and missing social login options. Want the field-by-field breakdown?",
                    "metadata": {"type": "forms"}
                }
        
        elif "quick" in message_lower or "easy" in message_lower:
            quick_wins = analysis.quick_wins or []
            if quick_wins:
                return {
                    "content": f"I found {len(quick_wins)} quick wins you can implement today. The fastest one takes just 5 minutes. Want to see them all?",
                    "metadata": {"type": "quick_wins"}
                }
        
        # Default response
        return {
            "content": f"I've analyzed {analysis.domain}. The biggest opportunities are in conversion optimization and AI search visibility. What specific area would you like to explore?",
            "metadata": {"type": "overview"}
        }
    
    async def generate_streaming_update(self, status: str, progress: int) -> str:
        """Generate natural language streaming updates during analysis"""
        
        updates = {
            "starting": [
                "🔍 Starting comprehensive analysis...",
                "🔍 Scanning your website for opportunities...",
                "🔍 Beginning growth analysis..."
            ],
            "performance": [
                "⚡ Checking site speed and Core Web Vitals...",
                "⚡ Analyzing page performance...",
                "⚡ Measuring load times..."
            ],
            "conversion": [
                "📊 Analyzing conversion paths and forms...",
                "📊 Checking your conversion funnel...",
                "📊 Evaluating signup flows..."
            ],
            "competitors": [
                "🎯 Comparing to your competitors...",
                "🎯 Analyzing competitive landscape...",
                "🎯 Finding competitive gaps..."
            ],
            "ai_search": [
                "🤖 Checking AI search visibility...",
                "🤖 Analyzing ChatGPT/Claude accessibility...",
                "🤖 Evaluating AI optimization..."
            ],
            "content": [
                "📚 Analyzing content strategy...",
                "📚 Evaluating your content gaps...",
                "📚 Checking blog and resources..."
            ],
            "calculating": [
                "💡 Calculating improvement opportunities...",
                "💡 Prioritizing recommendations...",
                "💡 Computing potential impact..."
            ],
            "complete": [
                "✅ Analysis complete! Processing insights...",
                "✅ Done! Preparing recommendations...",
                "✅ Finished! Here's what I found..."
            ]
        }
        
        import random
        return random.choice(updates.get(status, ["Analyzing..."]))
    
    async def format_initial_response(self, domain: str, analysis: Analysis) -> str:
        """Format the initial analysis response in a conversational way"""
        
        # Extract the most impactful finding
        biggest_issue = self._find_biggest_issue(analysis)
        
        # Build conversational response
        response = f"I've analyzed {domain} using public website data. Here's what I found:\n\n"
        response += "📊 **Data Sources:** Performance metrics (PageSpeed), SEO analysis, visual inspection, competitor comparison\n\n"
        
        if biggest_issue:
            response += f"**Biggest Finding (from website analysis):** {biggest_issue['headline']}\n\n"
            response += f"What the data shows:\n"
            for point in biggest_issue['points']:
                response += f"• {point}\n"
            response += f"\n**Recommended fix:** {biggest_issue['fix']}\n"
        
        # Add conversation starters with clear scope
        response += "\n**What else I can analyze (based on public data):**\n"
        response += "• 'competitors' - Feature comparison with similar sites\n"
        response += "• 'performance' - Load times and Core Web Vitals\n"
        response += "• 'forms' - Form field optimization\n"
        response += "• 'mobile' - Mobile responsiveness issues\n"
        response += "• 'seo' - Meta tags, schema, content gaps\n"
        response += "\n*Note: I analyze public website elements, not internal analytics or tracking setups.*"
        
        return response
    
    def _find_biggest_issue(self, analysis: Analysis) -> Optional[Dict]:
        """Find the most impactful issue from the analysis"""
        
        results = analysis.results
        issues = []
        
        # Check pricing page quality (not just existence)
        pages = results.get("page_analysis", {})
        page_data = results.get("page_analysis", {})
        pricing_analysis = page_data.get("pricing", {})
        
        # Check if pricing exists but has issues
        if pages.get("pages_found", {}).get("pricing"):
            # Pricing exists, check for transparency issues
            if pricing_analysis.get("has_prices") == False:
                issues.append({
                    "impact": 90,
                    "headline": "Your pricing page exists but doesn't show actual prices",
                    "points": [
                        "67% of B2B buyers eliminate vendors without transparent pricing",
                        "Competitors like Fivetran show clear pricing tiers",
                        "'Contact Sales' only approach loses self-serve customers"
                    ],
                    "fix": "Add actual pricing tiers or at minimum 'Starting at $X/month'"
                })
        else:
            # No pricing page at all
            issues.append({
                "impact": 100,
                "headline": "You're losing price-conscious buyers without a pricing page",
                "points": [
                    "67% of B2B buyers eliminate vendors without transparent pricing",
                    "Your competitors all show pricing publicly",
                    "You're forcing unnecessary sales conversations"
                ],
                "fix": "Create a pricing page with at least 'Starting at $X' and three tiers"
            })
        
        # Check for form issues
        forms = results.get("form_intelligence", {})
        lift = forms.get("estimated_conversion_lift", 0)
        if lift > 30:
            form_issues = []
            for form in forms.get("form_analysis", []):
                if form.get("field_count", 0) > 7:
                    form_issues.append(f"{form.get('page_type', 'Demo')} form has {form.get('field_count')} fields (should be 3-4)")
            
            if form_issues:
                issues.append({
                    "impact": lift,
                    "headline": f"Your forms are costing you {lift}% of potential leads",
                    "points": form_issues + [
                        "Each extra field reduces conversion by ~7%",
                        "No social login options available"
                    ],
                    "fix": f"Reduce to Name, Email, Company. Make everything else optional."
                })
        
        # Check for AI search blocking
        ai_search = results.get("ai_search", {})
        if ai_search.get("blocked_crawlers"):
            blocked = [c["platform"] for c in ai_search["blocked_crawlers"][:3]]
            issues.append({
                "impact": 80,
                "headline": f"You're invisible to AI search (blocking {', '.join(blocked)})",
                "points": [
                    "25-40% of future traffic will come from AI search",
                    "Competitors are getting recommended by ChatGPT/Claude",
                    "You're missing AI-driven lead generation"
                ],
                "fix": "Update robots.txt to allow GPTBot, ChatGPT-User, Claude-Web"
            })
        
        # Check for competitor gaps
        comp_data = results.get("competitors", {})
        gaps = comp_data.get("competitive_gaps", [])
        if gaps:
            critical_gaps = [g for g in gaps if g.get("impact") == "high"]
            if critical_gaps:
                gap_points = [g.get("description", "") for g in critical_gaps[:3]]
                issues.append({
                    "impact": 70,
                    "headline": "Your competitors have significant advantages",
                    "points": gap_points,
                    "fix": critical_gaps[0].get("recommendation", "Match competitor features")
                })
        
        # Return the highest impact issue
        if issues:
            return max(issues, key=lambda x: x["impact"])
        
        # Fallback
        return {
            "headline": f"Your site has a {analysis.conversion_score}/100 conversion score",
            "points": [
                f"Performance score: {analysis.performance_score}/100",
                f"Mobile score: {analysis.mobile_score}/100",
                f"SEO score: {analysis.seo_score}/100"
            ],
            "fix": "Focus on the top recommendations I've identified"
        }