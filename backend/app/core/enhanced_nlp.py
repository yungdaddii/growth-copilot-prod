"""
Enhanced NLP Processor with Context Awareness
Generates personalized, specific responses based on conversation context
"""

from typing import Dict, Any, Optional, List
import structlog
from app.core.nlp import NLPProcessor
from app.core.conversation_context import ConversationContext
from app.models.analysis import Analysis

logger = structlog.get_logger()


class EnhancedNLPProcessor(NLPProcessor):
    """Enhanced NLP with context awareness and specific recommendations"""
    
    def __init__(self, context: Optional[ConversationContext] = None):
        super().__init__()
        self.context = context
    
    def _build_dynamic_prompt(self, personalization: Dict[str, Any]) -> str:
        """Build a dynamic system prompt based on user context"""
        
        # Base prompt components
        base = "You are Growth Co-pilot, an AI that helps businesses improve their online presence and revenue."
        
        # Adjust tone based on technical level
        technical_level = personalization.get("technical_level", "medium")
        if technical_level == "high":
            tone = "Be technical and specific. Include implementation details, code snippets when relevant, and technical metrics."
        elif technical_level == "low":
            tone = "Use simple, non-technical language. Explain concepts clearly. Focus on business impact rather than technical details."
        else:
            tone = "Balance technical accuracy with clarity. Provide actionable steps without overwhelming details."
        
        # Adjust style based on preference
        style = personalization.get("response_style", "balanced")
        if style == "concise":
            style_guide = "Be extremely concise. Use bullet points. Maximum 150 words."
        elif style == "detailed":
            style_guide = "Provide comprehensive analysis. Include context, examples, and step-by-step guidance."
        else:
            style_guide = "Be clear and thorough but respect the user's time. 200-250 words ideal."
        
        # Focus areas
        focus_areas = personalization.get("focus_areas", [])
        if focus_areas:
            focus = f"Prioritize these areas: {', '.join(focus_areas)}."
        else:
            focus = "Focus on conversion optimization first, then growth, then technical issues."
        
        # Message count awareness
        message_count = personalization.get("message_count", 0)
        if message_count > 5:
            continuity = "Build on our previous discussion. Reference earlier points when relevant. Avoid repeating recommendations already given."
        elif message_count > 0:
            continuity = "Acknowledge this is a continuing conversation."
        else:
            continuity = "This is the start of our conversation."
        
        # Industry awareness
        industry = personalization.get("industry")
        if industry:
            industry_context = f"Use {industry} industry terminology and benchmarks."
        else:
            industry_context = ""
        
        # Build complete prompt
        prompt = f"""{base}

{tone}
{style_guide}
{focus}
{continuity}
{industry_context}

CRITICAL RULES:
- Use ACTUAL data from the analysis, never make up numbers
- Be specific: mention exact field names, page names, competitor names
- If user wants code examples: {personalization.get('wants_code', False)}
- Reference competitor names: {personalization.get('wants_competitor_names', True)}
- NO EMOJIS unless user uses them first
- End with a natural follow-up question or suggestion

Current conversation context:
- Messages exchanged: {message_count}
- Topics discussed: {', '.join(personalization.get('topics_discussed', [])[-3:]) or 'none yet'}
- User's technical level: {technical_level}
- User's focus: {', '.join(focus_areas) if focus_areas else 'general improvement'}"""
        
        return prompt
    
    async def generate_analysis_response(
        self,
        domain: str,
        analysis: Analysis,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate context-aware analysis response"""
        
        # Get personalization parameters if context exists
        if self.context:
            personalization = self.context.get_personalization_params()
            self.system_prompt = self._build_dynamic_prompt(personalization)
            
            # Store analysis in context
            self.context.set_current_analysis(domain, analysis.results)
        else:
            personalization = {}
        
        # Extract more specific data
        specific_insights = self._extract_specific_insights(analysis.results)
        
        # Build enhanced response
        response = await super().generate_analysis_response(domain, analysis, context)
        
        # Enhance with specific data
        response = self._enhance_with_specifics(response, specific_insights, personalization)
        
        # Track what we've discussed
        if self.context and response.get("content"):
            # Track recommendations given
            for rec in analysis.results.get("recommendations", [])[:3]:
                self.context.add_recommendation_given(rec)
        
        return response
    
    def _extract_specific_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract very specific, actionable insights from analysis"""
        specific = {}
        
        # Form field specifics
        if "conversion" in results:
            conv = results["conversion"]
            if "required_fields" in conv and conv["required_fields"]:
                specific["form_fields_to_remove"] = [
                    field for field in conv["required_fields"]
                    if field in ["company", "phone", "job_title", "company_size"]
                ]
            
            if "cta_text" in conv:
                specific["current_cta"] = conv["cta_text"]
                specific["better_cta"] = self._generate_better_cta(conv["cta_text"])
        
        # Competitor specifics
        if "competitors" in results:
            comps = results["competitors"].get("competitors", [])
            if comps:
                specific["competitor_names"] = [
                    c.get("name", c.get("domain", "")) for c in comps[:3]
                ]
                specific["competitor_features"] = {}
                for comp in comps[:2]:
                    name = comp.get("name", comp.get("domain"))
                    specific["competitor_features"][name] = comp.get("features", [])[:3]
        
        # Performance specifics
        if "performance" in results:
            perf = results["performance"]
            # Check if large_images is a list before slicing
            large_images = perf.get("large_images", [])
            if isinstance(large_images, list):
                specific["largest_images"] = large_images[:3]
            
            # Check if render_blocking is a list before slicing
            render_blocking = perf.get("render_blocking", [])
            if isinstance(render_blocking, list):
                specific["render_blocking_resources"] = render_blocking[:3]
            
            # Specific performance numbers
            if "load_time" in perf:
                specific["load_time_impact"] = f"{max(0, perf['load_time'] - 3):.1f}s too slow"
        
        # Page-specific issues
        if "page_analysis" in results:
            pages = results["page_analysis"].get("pages_found", {})
            specific["critical_pages"] = {}
            for page_type, page_data in pages.items():
                if page_data.get("issues"):
                    specific["critical_pages"][page_type] = page_data["issues"][:2]
        
        # Traffic specifics
        if "similarweb" in results and results["similarweb"].get("has_data"):
            traffic = results["similarweb"]["traffic_overview"]
            specific["exact_monthly_visits"] = traffic.get("monthly_visits", 0)
            specific["traffic_growth"] = traffic.get("growth_rate", 0)
            
            sources = results["similarweb"].get("traffic_sources", {})
            if sources:
                specific["traffic_breakdown"] = {
                    "organic": sources.get("search", 0) + sources.get("direct", 0),
                    "paid": sources.get("paid", 0),
                    "social": sources.get("social", 0),
                    "referral": sources.get("referral", 0)
                }
        
        # Enhanced SEO specifics
        if "seo" in results:
            seo = results["seo"]
            
            # Extract keyword opportunities
            if seo.get("keyword_opportunities"):
                top_keywords = seo["keyword_opportunities"][:5]
                specific["keyword_opportunities"] = [
                    {
                        "keyword": kw.get("keyword"),
                        "traffic": kw.get("estimated_traffic"),
                        "content_type": kw.get("content_type"),
                        "title": kw.get("title_suggestion")
                    }
                    for kw in top_keywords
                ]
            
            # Extract content recommendations
            if seo.get("content_recommendations"):
                top_content = seo["content_recommendations"][:3]
                specific["content_to_create"] = [
                    {
                        "title": rec.get("title"),
                        "type": rec.get("type"),
                        "traffic_potential": rec.get("estimated_monthly_traffic"),
                        "word_count": rec.get("word_count")
                    }
                    for rec in top_content
                ]
            
            # Extract content gaps
            if seo.get("content_gaps"):
                critical_gaps = [gap for gap in seo["content_gaps"] if gap.get("priority") == "critical"]
                specific["missing_pages"] = [
                    {
                        "page_type": gap.get("page_type"),
                        "impact": gap.get("impact"),
                        "traffic": gap.get("estimated_traffic")
                    }
                    for gap in critical_gaps[:3]
                ]
        
        # AI/SEO specifics
        if "ai_search" in results:
            ai = results["ai_search"]
            blocked = ai.get("blocked_crawlers", [])
            if blocked:
                specific["blocked_ai_bots"] = [
                    f"{c['platform']} ({c['bot']})" for c in blocked[:3]
                ]
        
        return specific
    
    def _generate_better_cta(self, current_cta: str) -> str:
        """Generate a better CTA based on the current one"""
        weak_to_strong = {
            "submit": "Get Your Free Analysis",
            "send": "Start Growing Today",
            "next": "See My Opportunities",
            "continue": "Unlock Growth Insights",
            "learn more": "Show Me How",
            "contact": "Get Expert Help",
            "sign up": "Start Free Trial",
            "register": "Claim Your Account",
            "download": "Get Instant Access",
            "subscribe": "Join 10,000+ Users"
        }
        
        current_lower = current_cta.lower().strip()
        for weak, strong in weak_to_strong.items():
            if weak in current_lower:
                return strong
        
        # Default improvements
        if len(current_cta) < 10:
            return f"Get Started with {current_cta}"
        return current_cta
    
    def _enhance_with_specifics(
        self, 
        response: Dict[str, Any], 
        specifics: Dict[str, Any],
        personalization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance response with specific actionable data"""
        
        # Add specific data to metadata
        if "metadata" not in response:
            response["metadata"] = {}
        
        response["metadata"]["specifics"] = specifics
        
        # Add code examples if requested
        if personalization.get("wants_code") and specifics:
            response["metadata"]["code_examples"] = self._generate_code_examples(specifics)
        
        # Add progressive disclosure options
        response["metadata"]["follow_up_suggestions"] = self._generate_follow_ups(
            specifics, 
            personalization.get("topics_discussed", [])
        )
        
        return response
    
    def _generate_code_examples(self, specifics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate code examples for fixes"""
        examples = []
        
        if "better_cta" in specifics:
            examples.append({
                "title": "Better CTA Button",
                "language": "html",
                "code": f"""<button class="cta-primary">
  <span class="cta-text">{specifics['better_cta']}</span>
  <svg class="cta-arrow">...</svg>
</button>

<style>
.cta-primary {{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px 32px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: transform 0.2s;
}}
.cta-primary:hover {{
  transform: translateY(-2px);
}}
</style>"""
            })
        
        if "blocked_ai_bots" in specifics:
            examples.append({
                "title": "Fix robots.txt for AI",
                "language": "txt",
                "code": """# Allow AI crawlers
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Bingbot
Allow: /

# Block bad bots
User-agent: SemrushBot
Disallow: /"""
            })
        
        return examples
    
    def _generate_follow_ups(
        self, 
        specifics: Dict[str, Any], 
        topics_discussed: List[str]
    ) -> List[str]:
        """Generate relevant follow-up questions"""
        follow_ups = []
        
        # Based on specifics found
        if "competitor_names" in specifics and "competitors" not in topics_discussed:
            follow_ups.append(f"How do you compare to {specifics['competitor_names'][0]}?")
        
        if "form_fields_to_remove" in specifics and "forms" not in topics_discussed:
            follow_ups.append("Should we optimize your forms for higher conversion?")
        
        if "traffic_breakdown" in specifics and "traffic" not in topics_discussed:
            follow_ups.append("Want to see your traffic acquisition breakdown?")
        
        if "critical_pages" in specifics and "pages" not in topics_discussed:
            follow_ups.append("Should I analyze your critical pages in detail?")
        
        # Always have a fallback
        if not follow_ups:
            if "quick_wins" not in topics_discussed:
                follow_ups.append("Want to see quick wins you can implement today?")
            else:
                follow_ups.append("What specific area should we dive deeper into?")
        
        return follow_ups[:3]  # Max 3 suggestions
    
    async def generate_follow_up_response(
        self,
        question: str,
        conversation: Any,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate context-aware follow-up response"""
        
        # Update context if available
        if self.context:
            # Track the topic
            subtype = context.get("subtype", "general")
            self.context.add_topic_discussed(subtype)
            
            # Check if we should vary response
            if self.context.should_vary_response():
                # Get undiscussed issues
                undiscussed = self.context.get_undiscussed_issues()
                if undiscussed:
                    # Pivot to undiscussed issue
                    context["pivot_to"] = undiscussed[0]
        
        response = await super().generate_follow_up_response(question, conversation, context)
        
        # Enhance with context
        if self.context:
            personalization = self.context.get_personalization_params()
            response = self._enhance_with_specifics(response, {}, personalization)
        
        return response