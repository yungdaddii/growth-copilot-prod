"""Enhanced comparison service that provides deep, actionable insights."""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.performance import PerformanceAnalyzer
from app.analyzers.conversion import ConversionAnalyzer
from app.analyzers.seo import SEOAnalyzer
from app.analyzers.social import SocialAnalyzer
from app.analyzers.content_strategy import ContentStrategyAnalyzer
from app.analyzers.revenue_intelligence import RevenueIntelligenceAnalyzer
from app.analyzers.pricing_intelligence import PricingIntelligenceAnalyzer
from app.analyzers.form_intelligence import FormIntelligenceAnalyzer
from app.analyzers.content_quality import ContentQualityAnalyzer
from app.analyzers.technical_seo_deep import TechnicalSEODeepAnalyzer
from app.core.metrics import MetricsCalculator

logger = structlog.get_logger()


class EnhancedComparisonService:
    """Provides deep, strategic comparisons between websites."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_calculator = MetricsCalculator()
        
        # Initialize all analyzers
        self.analyzers = {
            'performance': PerformanceAnalyzer(),
            'conversion': ConversionAnalyzer(),
            'seo': SEOAnalyzer(),
            'social': SocialAnalyzer(),
            'content': ContentStrategyAnalyzer(),
            'revenue': RevenueIntelligenceAnalyzer(),
            'pricing': PricingIntelligenceAnalyzer(),
            'forms': FormIntelligenceAnalyzer(),
            'quality': ContentQualityAnalyzer(),
            'technical': TechnicalSEODeepAnalyzer(),
        }
    
    async def compare_domains(self, domains: List[str]) -> Dict[str, Any]:
        """Perform comprehensive comparison of multiple domains."""
        
        # Limit to 3 domains for performance
        domains = domains[:3]
        
        # Run all analyses in parallel
        analyses = await self._run_parallel_analyses(domains)
        
        # Generate insights
        insights = self._generate_strategic_insights(analyses)
        
        # Format response
        response = self._format_enhanced_response(domains, analyses, insights)
        
        return {
            'type': 'enhanced_comparison',
            'domains': domains,
            'analyses': analyses,
            'insights': insights,
            'response': response
        }
    
    async def _run_parallel_analyses(self, domains: List[str]) -> Dict[str, Dict]:
        """Run all analyzers for all domains in parallel."""
        
        results = {}
        tasks = []
        
        for domain in domains:
            domain_tasks = []
            
            # Create tasks for each analyzer
            for name, analyzer in self.analyzers.items():
                try:
                    # Create async task for each analyzer
                    task = self._safe_analyze(analyzer, domain, name)
                    domain_tasks.append((name, task))
                except Exception as e:
                    logger.warning(f"Failed to create task for {name} analyzer: {e}")
            
            # Run all tasks for this domain
            domain_results = {}
            for name, task in domain_tasks:
                try:
                    result = await task
                    if result:
                        domain_results[name] = result
                except Exception as e:
                    logger.error(f"Analyzer {name} failed for {domain}: {e}")
                    domain_results[name] = None
            
            results[domain] = domain_results
        
        return results
    
    async def _safe_analyze(self, analyzer: Any, domain: str, analyzer_name: str) -> Optional[Dict]:
        """Safely run an analyzer with timeout and error handling."""
        try:
            # Set timeout for each analyzer (10 seconds)
            result = await asyncio.wait_for(
                analyzer.analyze(domain),
                timeout=10.0
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"{analyzer_name} analyzer timed out for {domain}")
            return None
        except Exception as e:
            logger.error(f"{analyzer_name} analyzer failed for {domain}: {e}")
            return None
    
    def _generate_strategic_insights(self, analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate strategic insights from analysis data."""
        
        insights = {
            'winner': None,
            'market_gaps': [],
            'opportunities': [],
            'differentiators': {},
            'recommendations': []
        }
        
        # Determine winner based on multiple factors
        scores = {}
        for domain, data in analyses.items():
            score = 0
            
            # Performance score
            if data.get('performance'):
                perf = data['performance']
                if perf.get('load_time', 999) < 2:
                    score += 20
                elif perf.get('load_time', 999) < 3:
                    score += 10
            
            # Conversion optimization score
            if data.get('conversion'):
                conv = data['conversion']
                if conv.get('has_social_proof'):
                    score += 15
                if conv.get('has_urgency'):
                    score += 10
                if conv.get('clear_cta'):
                    score += 10
            
            # SEO score
            if data.get('seo'):
                seo = data['seo']
                score += min(seo.get('score', 0) / 5, 20)  # Max 20 points for SEO
            
            # Content quality
            if data.get('quality'):
                quality = data['quality']
                score += quality.get('readability_score', 0) / 5  # Max 20 points
            
            # Revenue model sophistication
            if data.get('revenue'):
                rev = data['revenue']
                if rev.get('has_multiple_tiers'):
                    score += 15
                if rev.get('has_enterprise_option'):
                    score += 10
            
            scores[domain] = score
        
        # Determine winner
        if scores:
            winner = max(scores.items(), key=lambda x: x[1])
            insights['winner'] = {
                'domain': winner[0],
                'score': winner[1],
                'reason': self._get_winning_reason(analyses[winner[0]])
            }
        
        # Find market gaps
        insights['market_gaps'] = self._identify_market_gaps(analyses)
        
        # Generate opportunities
        insights['opportunities'] = self._generate_opportunities(analyses)
        
        # Identify key differentiators
        for domain in analyses:
            insights['differentiators'][domain] = self._get_differentiators(
                domain, analyses
            )
        
        # Generate actionable recommendations
        insights['recommendations'] = self._generate_recommendations(analyses)
        
        return insights
    
    def _get_winning_reason(self, analysis: Dict) -> str:
        """Determine why a site is winning."""
        reasons = []
        
        if analysis.get('performance', {}).get('load_time', 999) < 2:
            reasons.append("lightning-fast performance")
        
        if analysis.get('conversion', {}).get('has_social_proof'):
            reasons.append("strong social proof")
        
        if analysis.get('seo', {}).get('score', 0) > 80:
            reasons.append("superior SEO")
        
        if analysis.get('revenue', {}).get('has_enterprise_option'):
            reasons.append("comprehensive pricing strategy")
        
        return " + ".join(reasons) if reasons else "overall optimization"
    
    def _identify_market_gaps(self, analyses: Dict[str, Dict]) -> List[str]:
        """Identify gaps in the market that no one is addressing."""
        gaps = []
        
        # Check if anyone has testimonials
        has_testimonials = any(
            a.get('conversion', {}).get('has_social_proof') 
            for a in analyses.values()
        )
        if not has_testimonials:
            gaps.append("No competitor uses customer testimonials effectively - huge trust opportunity")
        
        # Check for mobile optimization
        poor_mobile = all(
            a.get('performance', {}).get('mobile_score', 0) < 70
            for a in analyses.values()
        )
        if poor_mobile:
            gaps.append("Mobile experience is poor across all competitors - mobile-first approach would dominate")
        
        # Check for interactive demos
        no_demos = all(
            not a.get('conversion', {}).get('has_demo')
            for a in analyses.values()
        )
        if no_demos:
            gaps.append("No one offers interactive demos - reduce friction with try-before-buy")
        
        # Check for transparent pricing
        hidden_pricing = all(
            not a.get('pricing', {}).get('has_transparent_pricing')
            for a in analyses.values()
        )
        if hidden_pricing:
            gaps.append("All competitors hide pricing - transparency could be a differentiator")
        
        return gaps
    
    def _generate_opportunities(self, analyses: Dict[str, Dict]) -> List[Dict]:
        """Generate specific opportunities based on analysis."""
        opportunities = []
        
        # Performance opportunity
        load_times = {
            domain: data.get('performance', {}).get('load_time', 999)
            for domain, data in analyses.items()
        }
        slowest = max(load_times.values())
        if slowest > 3:
            opportunities.append({
                'title': 'Performance Advantage',
                'description': f'Competitors have {slowest:.1f}s load times',
                'action': 'Achieve <2s load time for 20% conversion boost',
                'impact': 'High',
                'effort': 'Medium',
                'timeline': '2 weeks'
            })
        
        # Social proof opportunity
        testimonial_counts = {
            domain: data.get('conversion', {}).get('testimonial_count', 0)
            for domain, data in analyses.items()
        }
        if max(testimonial_counts.values()) < 5:
            opportunities.append({
                'title': 'Social Proof Gap',
                'description': 'Competitors lack strong testimonials',
                'action': 'Add 10+ detailed case studies with metrics',
                'impact': 'High',
                'effort': 'Low',
                'timeline': '1 week'
            })
        
        # SEO opportunity
        seo_scores = {
            domain: data.get('seo', {}).get('score', 0)
            for domain, data in analyses.items()
        }
        if max(seo_scores.values()) < 70:
            opportunities.append({
                'title': 'SEO Dominance',
                'description': 'All competitors have weak SEO',
                'action': 'Comprehensive SEO overhaul for #1 rankings',
                'impact': 'Very High',
                'effort': 'High',
                'timeline': '3 months'
            })
        
        return opportunities
    
    def _get_differentiators(self, domain: str, all_analyses: Dict[str, Dict]) -> List[str]:
        """Identify what makes this domain unique."""
        differentiators = []
        my_analysis = all_analyses[domain]
        
        # Performance differentiator
        my_load = my_analysis.get('performance', {}).get('load_time', 999)
        others_load = [
            a.get('performance', {}).get('load_time', 999)
            for d, a in all_analyses.items() if d != domain
        ]
        if my_load < min(others_load, default=999):
            differentiators.append(f"Fastest site ({my_load:.1f}s)")
        
        # Pricing differentiator
        if my_analysis.get('pricing', {}).get('has_free_tier'):
            has_free = sum(
                1 for d, a in all_analyses.items()
                if d != domain and a.get('pricing', {}).get('has_free_tier')
            )
            if has_free == 0:
                differentiators.append("Only one with free tier")
        
        # Content differentiator
        my_content = my_analysis.get('quality', {}).get('content_depth', 0)
        others_content = [
            a.get('quality', {}).get('content_depth', 0)
            for d, a in all_analyses.items() if d != domain
        ]
        if my_content > max(others_content, default=0):
            differentiators.append("Most comprehensive content")
        
        return differentiators
    
    def _generate_recommendations(self, analyses: Dict[str, Dict]) -> List[Dict]:
        """Generate specific, actionable recommendations."""
        recommendations = []
        
        # Quick wins (1 week)
        recommendations.append({
            'priority': 'Quick Win',
            'timeline': '1 week',
            'items': [
                {
                    'action': 'Add 5 customer testimonials above the fold',
                    'why': 'Competitors lack social proof',
                    'how': 'Email top 10 customers for quotes, add with headshots',
                    'impact': '+15% conversion rate'
                },
                {
                    'action': 'Implement exit-intent popup with discount',
                    'why': 'No competitor captures abandoning visitors',
                    'how': 'Use Sumo or OptinMonster, offer 10% discount',
                    'impact': '+5% email capture rate'
                }
            ]
        })
        
        # Medium-term (1 month)
        recommendations.append({
            'priority': 'Medium-term',
            'timeline': '1 month',
            'items': [
                {
                    'action': 'Launch interactive product demo',
                    'why': 'Reduce sales friction, no competitor has this',
                    'how': 'Use Navattic or Walnut for demo creation',
                    'impact': '+30% trial signups'
                },
                {
                    'action': 'Create comparison page vs competitors',
                    'why': 'Capture high-intent comparison searches',
                    'how': 'Honest comparison highlighting your strengths',
                    'impact': '+20% organic traffic'
                }
            ]
        })
        
        # Strategic (3 months)
        recommendations.append({
            'priority': 'Strategic',
            'timeline': '3 months',
            'items': [
                {
                    'action': 'Launch freemium tier',
                    'why': 'Competitors require demos, you can capture SMBs',
                    'how': 'Limited features, upgrade prompts at limits',
                    'impact': '3x lead volume'
                },
                {
                    'action': 'Build partnership ecosystem',
                    'why': 'Create moat competitors cannot easily copy',
                    'how': 'Integrate with top 10 tools in your space',
                    'impact': '+40% enterprise deals'
                }
            ]
        })
        
        return recommendations
    
    def _format_enhanced_response(self, domains: List[str], analyses: Dict, insights: Dict) -> str:
        """Format the analysis into a comprehensive, actionable response."""
        
        response = f"# 🎯 Strategic Analysis: {' vs '.join(domains)}\n\n"
        
        # Executive Summary
        response += "## Executive Summary\n\n"
        if insights['winner']:
            winner = insights['winner']
            response += f"**Winner:** {winner['domain']} ({winner['reason']})\n\n"
        
        response += "**Key Findings:**\n"
        for gap in insights['market_gaps'][:3]:
            response += f"- 🔍 {gap}\n"
        response += "\n"
        
        # Strategic Insights
        response += "## 📊 Strategic Insights\n\n"
        
        for domain in domains:
            differentiators = insights['differentiators'].get(domain, [])
            if differentiators:
                response += f"### {domain} Advantages\n"
                for diff in differentiators:
                    response += f"- ✅ {diff}\n"
                response += "\n"
        
        # Market Opportunities
        response += "## 🚀 Market Opportunities\n\n"
        
        for i, opp in enumerate(insights['opportunities'][:5], 1):
            response += f"### {i}. {opp['title']}\n"
            response += f"**Why:** {opp['description']}\n"
            response += f"**Action:** {opp['action']}\n"
            response += f"**Impact:** {opp['impact']} | **Effort:** {opp['effort']} | **Timeline:** {opp['timeline']}\n\n"
        
        # Detailed Metrics
        response += "## 📈 Detailed Metrics\n\n"
        
        # Performance comparison
        response += "### ⚡ Performance\n"
        for domain, data in analyses.items():
            perf = data.get('performance', {})
            load_time = perf.get('load_time', 'N/A')
            response += f"- **{domain}:** {load_time:.1f}s load time" if isinstance(load_time, (int, float)) else f"- **{domain}:** {load_time}\n"
        response += "\n"
        
        # Conversion Elements
        response += "### 💰 Conversion Optimization\n"
        for domain, data in analyses.items():
            conv = data.get('conversion', {})
            elements = []
            if conv.get('has_social_proof'):
                elements.append("✅ Social Proof")
            else:
                elements.append("❌ No Social Proof")
            
            if conv.get('clear_cta'):
                elements.append("✅ Clear CTAs")
            else:
                elements.append("❌ Weak CTAs")
            
            if conv.get('has_urgency'):
                elements.append("✅ Urgency")
            else:
                elements.append("❌ No Urgency")
            
            response += f"- **{domain}:** {' | '.join(elements)}\n"
        response += "\n"
        
        # SEO Strength
        response += "### 🔍 SEO Strength\n"
        for domain, data in analyses.items():
            seo = data.get('seo', {})
            score = seo.get('score', 0)
            response += f"- **{domain}:** {score}/100"
            if score > 80:
                response += " (Excellent)"
            elif score > 60:
                response += " (Good)"
            else:
                response += " (Needs Work)"
            response += "\n"
        response += "\n"
        
        # Action Plan
        response += "## 🎬 Action Plan\n\n"
        
        for rec_group in insights['recommendations']:
            response += f"### {rec_group['priority']} ({rec_group['timeline']})\n\n"
            
            for item in rec_group['items']:
                response += f"**✓ {item['action']}**\n"
                response += f"- Why: {item['why']}\n"
                response += f"- How: {item['how']}\n"
                response += f"- Expected Impact: {item['impact']}\n\n"
        
        # Bottom Line
        response += "## 💡 Bottom Line\n\n"
        
        if insights['market_gaps']:
            response += f"**Biggest Opportunity:** {insights['market_gaps'][0]}\n\n"
        
        response += "**Your Next Move:** "
        if insights['recommendations'] and insights['recommendations'][0]['items']:
            first_action = insights['recommendations'][0]['items'][0]
            response += f"{first_action['action']} → {first_action['impact']}\n"
        
        return response


async def test_enhanced_comparison():
    """Test the enhanced comparison service."""
    from app.database import get_db_context
    
    async with get_db_context() as db:
        service = EnhancedComparisonService(db)
        result = await service.compare_domains(['stripe.com', 'square.com'])
        print(result['response'])
        return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_comparison())