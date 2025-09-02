"""Context-aware chat service for personalized responses."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import json

from app.models.context import (
    UserContext, SiteSnapshot, CompetitorIntelligence, 
    GrowthBenchmark, GrowthExperiment
)
from app.services.monitoring import WebsiteMonitor
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ContextAwareChat:
    """Provides context-aware responses based on user history and monitoring data."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.monitor = WebsiteMonitor(session)
    
    async def get_or_create_context(self, session_id: str) -> UserContext:
        """Get or create user context."""
        result = await self.session.execute(
            select(UserContext).where(UserContext.session_id == session_id)
        )
        context = result.scalar_one_or_none()
        
        if not context:
            context = UserContext(session_id=session_id)
            self.session.add(context)
            await self.session.commit()
        
        return context
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process message with context awareness."""
        
        context = await self.get_or_create_context(session_id)
        
        # Detect intent
        intent = self._detect_intent(message)
        
        # Route to appropriate handler
        if intent == 'check_updates':
            return await self.check_competitor_updates(context)
        elif intent == 'show_progress':
            return await self.show_progress(context)
        elif intent == 'get_opportunities':
            return await self.get_growth_opportunities(context)
        elif intent == 'track_site':
            return await self.add_monitoring(message, context)
        elif intent == 'compare':
            return await self.compare_competitors(message, context)
        elif intent == 'predict_impact':
            return await self.predict_change_impact(message, context)
        else:
            # Regular analysis with context
            return await self.analyze_with_context(message, context)
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message."""
        message_lower = message.lower()
        logger.info(f"Detecting intent for message: {message[:100]}")
        
        # Check for specific intents
        if any(word in message_lower for word in ['update', 'new', 'change', 'what happened', "what's new", 'what changed']):
            logger.info("Intent: check_updates")
            return 'check_updates'
        elif any(word in message_lower for word in ['progress', 'improve', 'better', 'score']):
            return 'show_progress'
        elif any(word in message_lower for word in ['opportunity', 'should i', 'next', 'recommend']):
            return 'get_opportunities'
        elif any(word in message_lower for word in ['track', 'monitor', 'watch']):
            return 'track_site'
        elif any(word in message_lower for word in ['compare', 'versus', 'vs', 'competitor']):
            return 'compare'
        elif any(word in message_lower for word in ['if i', 'would', 'impact', 'predict']):
            return 'predict_impact'
        else:
            logger.info("Intent: analyze (default)")
            return 'analyze'
    
    async def check_competitor_updates(self, context: UserContext) -> Dict[str, Any]:
        """Check for competitor updates."""
        
        if not context.competitors:
            return {
                'type': 'info',
                'content': "I'm not tracking any competitors yet. Tell me which competitors you want to monitor, and I'll start tracking their changes daily."
            }
        
        updates = []
        for competitor in context.competitors[:3]:  # Top 3 competitors
            # Get recent changes
            result = await self.session.execute(
                select(SiteSnapshot)
                .where(
                    and_(
                        SiteSnapshot.domain == competitor,
                        SiteSnapshot.changes_detected.isnot(None),
                        SiteSnapshot.snapshot_date > datetime.utcnow() - timedelta(days=7)
                    )
                )
                .order_by(SiteSnapshot.snapshot_date.desc())
                .limit(1)
            )
            snapshot = result.scalar_one_or_none()
            
            if snapshot and snapshot.changes_detected:
                significant_changes = [c for c in snapshot.changes_detected 
                                      if c.get('impact') in ['high', 'medium']]
                if significant_changes:
                    updates.append({
                        'competitor': competitor,
                        'date': snapshot.snapshot_date,
                        'changes': significant_changes[:3]  # Top 3 changes
                    })
        
        if updates:
            response = "## 🔍 Competitor Updates (Last 7 Days)\n\n"
            for update in updates:
                response += f"### {update['competitor']}\n"
                response += f"*Updated {self._format_time_ago(update['date'])}*\n\n"
                
                for change in update['changes']:
                    if change['type'] == 'cta_buttons':
                        if change.get('added'):
                            response += f"✨ **New CTAs:** {', '.join(change['added'])}\n"
                        if change.get('removed'):
                            response += f"❌ **Removed CTAs:** {', '.join(change['removed'])}\n"
                    elif change['type'] == 'performance':
                        old_time = change.get('old', 0)
                        new_time = change.get('new', 0)
                        if change.get('improvement'):
                            response += f"⚡ **Faster load time:** {old_time:.1f}s → {new_time:.1f}s\n"
                        else:
                            response += f"🐌 **Slower load time:** {old_time:.1f}s → {new_time:.1f}s\n"
                    elif change['type'] == 'title':
                        response += f"📝 **New title:** \"{change.get('new', '')}\"\n"
                    elif change['type'] == 'social_proof':
                        response += f"💬 **Testimonials:** {change.get('old_count', 0)} → {change.get('new_count', 0)}\n"
                
                response += "\n"
            
            response += "💡 **What this means:** Your competitors are actively optimizing. "
            response += "Would you like me to suggest similar improvements for your site?"
        else:
            response = "No significant competitor changes in the last 7 days. Your competitors are stable, which gives you an opportunity to get ahead."
        
        return {
            'type': 'competitor_update',
            'content': response,
            'has_updates': len(updates) > 0
        }
    
    async def show_progress(self, context: UserContext) -> Dict[str, Any]:
        """Show user's progress over time."""
        
        if not context.primary_domain:
            return {
                'type': 'info',
                'content': "I haven't analyzed your site yet. Share your domain and I'll start tracking your progress!"
            }
        
        # Get snapshots over time
        result = await self.session.execute(
            select(SiteSnapshot)
            .where(SiteSnapshot.domain == context.primary_domain)
            .order_by(SiteSnapshot.snapshot_date.desc())
            .limit(5)
        )
        snapshots = result.scalars().all()
        
        if len(snapshots) < 2:
            return {
                'type': 'info',
                'content': "I need more data points to show progress. Check back tomorrow for trending data!"
            }
        
        # Compare oldest to newest
        oldest = snapshots[-1]
        newest = snapshots[0]
        
        improvements = []
        regressions = []
        
        # Performance comparison
        if oldest.load_time and newest.load_time:
            diff = oldest.load_time - newest.load_time
            if diff > 0.1:
                improvements.append(f"⚡ Page speed improved by {diff:.1f}s")
            elif diff < -0.1:
                regressions.append(f"🐌 Page speed decreased by {abs(diff):.1f}s")
        
        # Testimonials comparison
        if oldest.testimonials_count != newest.testimonials_count:
            diff = newest.testimonials_count - oldest.testimonials_count
            if diff > 0:
                improvements.append(f"💬 Added {diff} testimonials")
            else:
                regressions.append(f"❌ Removed {abs(diff)} testimonials")
        
        # Build response
        response = f"## 📊 Progress Report for {context.primary_domain}\n\n"
        response += f"*Tracking since {oldest.snapshot_date.strftime('%B %d, %Y')}*\n\n"
        
        if improvements:
            response += "### ✅ Improvements\n"
            for imp in improvements:
                response += f"- {imp}\n"
            response += "\n"
        
        if regressions:
            response += "### ⚠️ Areas Needing Attention\n"
            for reg in regressions:
                response += f"- {reg}\n"
            response += "\n"
        
        if not improvements and not regressions:
            response += "No significant changes detected. Time to make some improvements!\n\n"
        
        # Add growth score
        score = self._calculate_growth_score(oldest, newest)
        response += f"### 🎯 Growth Score: {score}/100\n"
        
        if score < 50:
            response += "You have significant room for improvement. Let me suggest some quick wins!\n"
        elif score < 75:
            response += "Good progress! A few optimizations could push you to the next level.\n"
        else:
            response += "Excellent work! You're outpacing most competitors.\n"
        
        return {
            'type': 'progress_report',
            'content': response,
            'score': score
        }
    
    async def get_growth_opportunities(self, context: UserContext) -> Dict[str, Any]:
        """Get personalized growth opportunities."""
        
        if not context.primary_domain:
            return {
                'type': 'info',
                'content': "Share your domain first, and I'll analyze growth opportunities specifically for your site."
            }
        
        # Get opportunities from monitor
        opportunities = await self.monitor.generate_growth_opportunities(
            context.primary_domain, context
        )
        
        if not opportunities:
            # Generate generic opportunities based on industry
            opportunities = self._get_generic_opportunities(context.industry)
        
        # Format response
        response = "## 🚀 Growth Opportunities\n\n"
        response += "*Based on real data from your site and successful competitors*\n\n"
        
        for i, opp in enumerate(opportunities[:5], 1):
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(opp.get('priority', 'medium'))
            
            response += f"### {i}. {opp['title']} {priority_emoji}\n"
            response += f"**Impact:** {opp.get('predicted_impact', 'Moderate improvement')}\n"
            response += f"**Effort:** {opp.get('effort', 'Medium')}\n"
            response += f"**Why:** {opp.get('description', '')}\n"
            
            if opp.get('implementation'):
                response += f"**How:** {opp['implementation']}\n"
            
            if opp.get('based_on'):
                response += f"*Based on: {opp['based_on']}*\n"
            
            response += "\n"
        
        response += "💡 **Next Step:** Pick the highest priority item and I can help you implement it step-by-step."
        
        return {
            'type': 'opportunities',
            'content': response,
            'opportunities': opportunities
        }
    
    async def add_monitoring(self, message: str, context: UserContext) -> Dict[str, Any]:
        """Add a site to monitoring list."""
        
        # Extract domain from message
        import re
        domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        match = re.search(domain_pattern, message)
        
        if not match:
            return {
                'type': 'error',
                'content': "Please provide a valid domain to track (e.g., 'track example.com')"
            }
        
        domain = match.group(1)
        
        # Add to monitoring list
        if not context.monitoring_sites:
            context.monitoring_sites = []
        
        if domain not in context.monitoring_sites:
            context.monitoring_sites.append(domain)
            await self.session.commit()
            
            # Capture initial snapshot
            await self.monitor.capture_snapshot(domain)
            
            response = f"✅ Now monitoring **{domain}** daily!\n\n"
            response += "I'll track:\n"
            response += "- Content changes (headlines, CTAs, copy)\n"
            response += "- Performance improvements\n"
            response += "- New features and A/B tests\n"
            response += "- Conversion elements (forms, testimonials)\n\n"
            response += "Ask me 'what's new?' anytime to see updates."
        else:
            response = f"Already monitoring {domain}. Ask 'what's new with {domain}?' to see recent changes."
        
        return {
            'type': 'monitoring_added',
            'content': response,
            'domain': domain
        }
    
    async def compare_competitors(self, message: str, context: UserContext) -> Dict[str, Any]:
        """Compare sites mentioned in the message."""
        
        # Extract domains
        import re
        domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        domains = re.findall(domain_pattern, message)
        
        if len(domains) < 2:
            return {
                'type': 'error',
                'content': "Please provide at least 2 domains to compare (e.g., 'compare stripe.com vs square.com')"
            }
        
        # Get latest snapshots or analyze fresh
        snapshots = {}
        analyses = {}
        
        # Try to use the full analyzer for better data
        try:
            from app.core.analyzer import DomainAnalyzer
            analyzer = DomainAnalyzer()
            
            for domain in domains[:3]:  # Max 3 domains
                # Check if we have recent data (less than 1 hour old)
                result = await self.session.execute(
                    select(SiteSnapshot)
                    .where(SiteSnapshot.domain == domain)
                    .where(SiteSnapshot.snapshot_date > datetime.utcnow() - timedelta(hours=1))
                    .order_by(SiteSnapshot.snapshot_date.desc())
                    .limit(1)
                )
                snapshot = result.scalar_one_or_none()
                
                if not snapshot:
                    # Do a full analysis for better data
                    try:
                        analysis_result = await analyzer.analyze(domain)
                        analyses[domain] = analysis_result
                        # Also capture snapshot for storage
                        snapshot = await self.monitor.capture_snapshot(domain)
                    except Exception as e:
                        logger.warning(f"Full analysis failed for {domain}, using basic capture: {e}")
                        snapshot = await self.monitor.capture_snapshot(domain)
                
                snapshots[domain] = snapshot
        except Exception as e:
            logger.error(f"Error in comparison analysis: {e}")
            # Fallback to basic snapshots
            for domain in domains[:3]:
                result = await self.session.execute(
                    select(SiteSnapshot)
                    .where(SiteSnapshot.domain == domain)
                    .order_by(SiteSnapshot.snapshot_date.desc())
                    .limit(1)
                )
                snapshot = result.scalar_one_or_none()
                
                if not snapshot:
                    snapshot = await self.monitor.capture_snapshot(domain)
                
                snapshots[domain] = snapshot
        
        # Compare metrics
        response = f"## ⚔️ Comparison: {' vs '.join(domains[:3])}\n\n"
        
        # Performance comparison
        response += "### ⚡ Performance\n"
        for domain, snap in snapshots.items():
            load_time = snap.load_time if snap.load_time else "Unknown"
            response += f"- **{domain}:** {load_time:.1f}s load time\n" if isinstance(load_time, float) else f"- **{domain}:** {load_time}\n"
        
        # Find winner
        fastest = min(snapshots.items(), key=lambda x: x[1].load_time if x[1].load_time else 999)
        response += f"*Winner: {fastest[0]} (fastest)*\n\n"
        
        # Conversion elements
        response += "### 💬 Social Proof\n"
        for domain, snap in snapshots.items():
            response += f"- **{domain}:** {snap.testimonials_count} testimonials\n"
        
        most_testimonials = max(snapshots.items(), key=lambda x: x[1].testimonials_count or 0)
        response += f"*Winner: {most_testimonials[0]} (most social proof)*\n\n"
        
        # CTAs
        response += "### 🎯 Call-to-Actions\n"
        for domain, snap in snapshots.items():
            ctas = snap.cta_buttons[:3] if snap.cta_buttons else ["None found"]
            response += f"- **{domain}:** {', '.join(ctas)}\n"
        response += "\n"
        
        # Forms
        response += "### 📝 Form Optimization\n"
        for domain, snap in snapshots.items():
            if snap.form_fields:
                avg_fields = sum(len(f.get('field_types', [])) for f in snap.form_fields) / len(snap.form_fields)
                response += f"- **{domain}:** ~{avg_fields:.0f} fields per form\n"
            else:
                response += f"- **{domain}:** No forms detected\n"
        response += "\n"
        
        # Overall recommendation
        response += "### 💡 Key Takeaways\n"
        response += self._generate_comparison_insights(snapshots)
        
        # Update context with competitors
        if not context.competitors:
            context.competitors = []
        
        for domain in domains:
            if domain != context.primary_domain and domain not in context.competitors:
                context.competitors.append(domain)
        
        await self.session.commit()
        
        return {
            'type': 'comparison',
            'content': response,
            'domains': domains
        }
    
    async def predict_change_impact(self, message: str, context: UserContext) -> Dict[str, Any]:
        """Predict impact of a proposed change."""
        
        # Parse the proposed change
        change_type = self._detect_change_type(message)
        
        if not change_type:
            return {
                'type': 'info',
                'content': "I can predict the impact of changes like:\n- Adding testimonials\n- Improving page speed\n- Simplifying forms\n- Changing CTA copy\n\nTry asking: 'What if I add 5 testimonials?'"
            }
        
        # Get benchmarks for prediction
        result = await self.session.execute(
            select(GrowthBenchmark)
            .where(
                and_(
                    GrowthBenchmark.industry == (context.industry or 'general'),
                    GrowthBenchmark.metric_name == change_type['metric']
                )
            )
        )
        benchmark = result.scalar_one_or_none()
        
        # Calculate predicted impact
        if benchmark:
            current_percentile = self._calculate_percentile(change_type['current'], benchmark)
            target_percentile = self._calculate_percentile(change_type['target'], benchmark)
            
            # Estimate conversion impact
            conversion_lift = (target_percentile - current_percentile) * benchmark.impact_on_conversion
            
            response = f"## 🔮 Impact Prediction\n\n"
            response += f"**Proposed Change:** {change_type['description']}\n\n"
            response += f"### Expected Impact\n"
            response += f"- **Conversion Rate:** +{conversion_lift:.1f}%\n"
            
            # Calculate revenue impact
            if context.primary_domain:
                response += f"- **Monthly Revenue:** +${conversion_lift * 1000:.0f} (estimated)\n"
            
            response += f"- **Industry Percentile:** {current_percentile}th → {target_percentile}th\n\n"
            
            response += f"### Implementation\n"
            response += f"- **Difficulty:** {benchmark.implementation_difficulty}\n"
            response += f"- **Time to Impact:** 2-4 weeks\n\n"
            
            response += f"### Similar Success Stories\n"
            response += f"Based on {benchmark.sample_size} similar sites that made this change:\n"
            response += f"- Top 25% saw +{conversion_lift * 1.5:.1f}% improvement\n"
            response += f"- Median saw +{conversion_lift:.1f}% improvement\n"
            response += f"- Bottom 25% saw +{conversion_lift * 0.5:.1f}% improvement\n"
            
        else:
            # Provide generic prediction
            response = self._generate_generic_prediction(change_type)
        
        # Create experiment record
        experiment = GrowthExperiment(
            session_id=context.session_id,
            domain=context.primary_domain or 'unknown',
            experiment_type=change_type['type'],
            title=change_type['description'],
            hypothesis=f"This change will improve conversion by {conversion_lift:.1f}%" if benchmark else "Expected positive impact",
            predicted_impact=conversion_lift if benchmark else 5.0,
            confidence_level=75.0 if benchmark else 50.0,
            impact_metric='conversion_rate',
            implementation_difficulty=benchmark.implementation_difficulty if benchmark else 'medium',
            status='suggested'
        )
        self.session.add(experiment)
        await self.session.commit()
        
        return {
            'type': 'prediction',
            'content': response,
            'experiment_id': str(experiment.id)
        }
    
    async def analyze_with_context(self, message: str, context: UserContext) -> Dict[str, Any]:
        """Regular analysis with context awareness."""
        
        # Extract domain from message
        import re
        domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        match = re.search(domain_pattern, message)
        
        if match:
            domain = match.group(1)
            
            # Update context if this is their primary domain
            if not context.primary_domain:
                context.primary_domain = domain
                await self.session.commit()
            
            # Add to monitoring
            if not context.monitoring_sites:
                context.monitoring_sites = []
            if domain not in context.monitoring_sites:
                context.monitoring_sites.append(domain)
                await self.session.commit()
        
        # Return normal analysis (will be handled by existing analyzer)
        return {
            'type': 'analyze',
            'message': message,
            'context': {
                'primary_domain': context.primary_domain,
                'competitors': context.competitors,
                'industry': context.industry
            }
        }
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as time ago."""
        now = datetime.utcnow()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    def _calculate_growth_score(self, old: SiteSnapshot, new: SiteSnapshot) -> int:
        """Calculate growth score from 0-100."""
        score = 50  # Base score
        
        # Performance improvement
        if old.load_time and new.load_time:
            if new.load_time < old.load_time:
                score += min(20, int((old.load_time - new.load_time) * 10))
        
        # More testimonials
        if new.testimonials_count > old.testimonials_count:
            score += min(15, (new.testimonials_count - old.testimonials_count) * 3)
        
        # More CTAs
        if len(new.cta_buttons or []) > len(old.cta_buttons or []):
            score += 10
        
        # Better forms
        if new.form_fields and old.form_fields:
            new_avg = sum(len(f.get('field_types', [])) for f in new.form_fields) / len(new.form_fields)
            old_avg = sum(len(f.get('field_types', [])) for f in old.form_fields) / len(old.form_fields)
            if new_avg < old_avg:
                score += 15
        
        return min(100, max(0, score))
    
    def _get_generic_opportunities(self, industry: Optional[str]) -> List[Dict]:
        """Get generic opportunities based on industry."""
        opportunities = [
            {
                'title': 'Add Social Proof',
                'description': 'Most sites see 18% conversion lift from testimonials',
                'predicted_impact': '+18% conversion',
                'priority': 'high',
                'effort': 'low',
                'implementation': 'Add 5-7 customer testimonials with names and photos'
            },
            {
                'title': 'Optimize Page Speed',
                'description': 'Sites loading under 2s convert 30% better',
                'predicted_impact': '+15-30% conversion',
                'priority': 'high',
                'effort': 'medium',
                'implementation': 'Compress images, enable caching, use CDN'
            },
            {
                'title': 'Simplify Forms',
                'description': '3-field forms convert 25% better than 5+ fields',
                'predicted_impact': '+25% form completion',
                'priority': 'medium',
                'effort': 'low',
                'implementation': 'Remove optional fields, use progressive disclosure'
            }
        ]
        
        return opportunities
    
    def _detect_change_type(self, message: str) -> Optional[Dict]:
        """Detect what type of change is being proposed."""
        message_lower = message.lower()
        
        if 'testimonial' in message_lower or 'social proof' in message_lower:
            return {
                'type': 'social_proof',
                'metric': 'testimonials',
                'description': 'Adding customer testimonials',
                'current': 0,
                'target': 5
            }
        elif 'speed' in message_lower or 'performance' in message_lower or 'load' in message_lower:
            return {
                'type': 'performance',
                'metric': 'load_time',
                'description': 'Improving page load speed',
                'current': 4.0,
                'target': 2.0
            }
        elif 'form' in message_lower or 'field' in message_lower:
            return {
                'type': 'forms',
                'metric': 'form_fields',
                'description': 'Simplifying forms',
                'current': 7,
                'target': 3
            }
        elif 'cta' in message_lower or 'button' in message_lower:
            return {
                'type': 'cta',
                'metric': 'cta_copy',
                'description': 'Optimizing CTA copy',
                'current': 50,
                'target': 75
            }
        
        return None
    
    def _calculate_percentile(self, value: float, benchmark: GrowthBenchmark) -> int:
        """Calculate percentile position based on benchmark."""
        if value <= benchmark.p10_value:
            return 10
        elif value <= benchmark.p25_value:
            return 25
        elif value <= benchmark.median_value:
            return 50
        elif value <= benchmark.p75_value:
            return 75
        elif value <= benchmark.p90_value:
            return 90
        else:
            return 95
    
    def _generate_comparison_insights(self, snapshots: Dict[str, SiteSnapshot]) -> str:
        """Generate insights from comparison."""
        insights = []
        
        # Find best practices
        all_have = []
        none_have = []
        
        # Check testimonials
        testimonial_counts = [s.testimonials_count for s in snapshots.values()]
        if all(c > 0 for c in testimonial_counts):
            all_have.append("social proof")
        elif all(c == 0 for c in testimonial_counts):
            none_have.append("testimonials")
        
        # Build insights
        if all_have:
            insights.append(f"✅ All sites use {', '.join(all_have)} (industry standard)")
        
        if none_have:
            insights.append(f"🚀 None use {', '.join(none_have)} (opportunity to differentiate)")
        
        # Performance insight
        load_times = [(d, s.load_time) for d, s in snapshots.items() if s.load_time]
        if load_times:
            fastest = min(load_times, key=lambda x: x[1])
            slowest = max(load_times, key=lambda x: x[1])
            if fastest[1] < 2 and slowest[1] > 3:
                insights.append(f"⚡ {fastest[0]} has a significant speed advantage")
        
        return '\n'.join(insights) if insights else "Each site has unique strengths. Consider combining the best elements from each."
    
    def _generate_generic_prediction(self, change_type: Dict) -> str:
        """Generate generic prediction when no benchmark data available."""
        
        response = f"## 🔮 Impact Prediction\n\n"
        response += f"**Proposed Change:** {change_type['description']}\n\n"
        response += "### Expected Impact (Industry Averages)\n"
        
        if change_type['type'] == 'social_proof':
            response += "- **Conversion Rate:** +10-20%\n"
            response += "- **Trust Score:** +30%\n"
            response += "- **Time on Site:** +15%\n"
        elif change_type['type'] == 'performance':
            response += "- **Conversion Rate:** +7% per second improved\n"
            response += "- **Bounce Rate:** -10-20%\n"
            response += "- **Page Views:** +10-15%\n"
        elif change_type['type'] == 'forms':
            response += "- **Form Completion:** +25-50%\n"
            response += "- **Lead Quality:** Maintained or improved\n"
            response += "- **Conversion Rate:** +10-15%\n"
        else:
            response += "- **Conversion Rate:** +5-15%\n"
            response += "- **Engagement:** +10-20%\n"
        
        response += "\n*Note: These are industry averages. Actual impact depends on your specific audience and implementation.*"
        
        return response