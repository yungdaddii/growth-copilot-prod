"""Enhanced formatter for single domain analysis with actionable insights."""

from typing import Dict, Any, List, Optional
import json


class EnhancedAnalysisFormatter:
    """Formats analysis results into rich, actionable insights."""
    
    @staticmethod
    def format_analysis(domain: str, analysis_data: Dict[str, Any]) -> str:
        """Format a single domain analysis into comprehensive insights."""
        
        response = f"# 🎯 Deep Analysis: {domain}\n\n"
        
        # Executive Summary
        response += "## Executive Summary\n\n"
        response += EnhancedAnalysisFormatter._generate_executive_summary(analysis_data)
        response += "\n\n"
        
        # Critical Issues
        critical_issues = EnhancedAnalysisFormatter._identify_critical_issues(analysis_data)
        if critical_issues:
            response += "## 🚨 Critical Issues to Fix\n\n"
            for i, issue in enumerate(critical_issues[:5], 1):
                response += f"### {i}. {issue['title']}\n"
                response += f"**Problem:** {issue['problem']}\n"
                response += f"**Impact:** {issue['impact']}\n"
                response += f"**Solution:** {issue['solution']}\n"
                response += f"**Timeline:** {issue['timeline']}\n\n"
        
        # Growth Opportunities
        response += "## 🚀 Growth Opportunities\n\n"
        opportunities = EnhancedAnalysisFormatter._generate_opportunities(analysis_data)
        for i, opp in enumerate(opportunities[:5], 1):
            response += f"### {i}. {opp['title']}\n"
            response += f"**Opportunity:** {opp['description']}\n"
            response += f"**Implementation:** {opp['implementation']}\n"
            response += f"**Expected ROI:** {opp['roi']}\n\n"
        
        # Performance Metrics
        response += "## 📊 Performance Metrics\n\n"
        response += EnhancedAnalysisFormatter._format_performance_metrics(analysis_data)
        response += "\n"
        
        # Conversion Analysis
        response += "## 💰 Conversion Optimization\n\n"
        response += EnhancedAnalysisFormatter._format_conversion_analysis(analysis_data)
        response += "\n"
        
        # SEO & Visibility
        response += "## 🔍 SEO & Visibility\n\n"
        response += EnhancedAnalysisFormatter._format_seo_analysis(analysis_data)
        response += "\n"
        
        # Competitive Intelligence
        response += "## 🎯 Competitive Intelligence\n\n"
        response += EnhancedAnalysisFormatter._format_competitive_insights(analysis_data)
        response += "\n"
        
        # Action Plan
        response += "## 📋 30-Day Action Plan\n\n"
        response += EnhancedAnalysisFormatter._generate_action_plan(analysis_data)
        
        return response
    
    @staticmethod
    def _generate_executive_summary(data: Dict) -> str:
        """Generate executive summary from analysis data."""
        
        summary_points = []
        
        # Performance insight
        if data.get('performance'):
            load_time = data['performance'].get('load_time', 999)
            if load_time < 2:
                summary_points.append("✅ **Excellent Performance** - Site loads in under 2 seconds")
            elif load_time < 3:
                summary_points.append("⚠️ **Good Performance** - Site loads in 2-3 seconds (room for improvement)")
            else:
                summary_points.append(f"🚨 **Poor Performance** - {load_time:.1f}s load time costs you ~{int((load_time-2)*7)}% in conversions")
        
        # Conversion optimization
        if data.get('conversion'):
            conv = data['conversion']
            conversion_score = 0
            if conv.get('has_social_proof'):
                conversion_score += 30
            if conv.get('clear_cta'):
                conversion_score += 30
            if conv.get('has_urgency'):
                conversion_score += 20
            if conv.get('trust_signals'):
                conversion_score += 20
            
            if conversion_score > 70:
                summary_points.append(f"✅ **Strong Conversion Elements** - {conversion_score}% optimization score")
            elif conversion_score > 40:
                summary_points.append(f"⚠️ **Moderate Conversion Optimization** - {conversion_score}% score, significant room for improvement")
            else:
                summary_points.append(f"🚨 **Weak Conversion Elements** - Only {conversion_score}% optimized, losing 30-50% of potential customers")
        
        # SEO health
        if data.get('seo'):
            seo_score = data['seo'].get('score', 0)
            if seo_score > 80:
                summary_points.append(f"✅ **Excellent SEO** - {seo_score}/100 score positions you well")
            elif seo_score > 60:
                summary_points.append(f"⚠️ **Good SEO** - {seo_score}/100 score with optimization opportunities")
            else:
                summary_points.append(f"🚨 **Poor SEO** - {seo_score}/100 score limits organic growth")
        
        # Revenue model
        if data.get('revenue_intelligence'):
            rev = data['revenue_intelligence']
            if rev.get('pricing_model'):
                summary_points.append(f"💰 **Revenue Model:** {rev['pricing_model']} with {rev.get('tiers', 'unknown')} pricing tiers")
        
        # Traffic insights
        if data.get('traffic'):
            monthly_visits = data['traffic'].get('monthly_visits', 0)
            if monthly_visits > 0:
                summary_points.append(f"📈 **Traffic:** ~{monthly_visits:,} monthly visits")
        
        return "\n".join(summary_points) if summary_points else "Analysis data limited - recommend full scan"
    
    @staticmethod
    def _identify_critical_issues(data: Dict) -> List[Dict]:
        """Identify critical issues that need immediate attention."""
        
        issues = []
        
        # Performance issues
        if data.get('performance'):
            load_time = data['performance'].get('load_time', 0)
            if load_time > 3:
                issues.append({
                    'title': 'Slow Page Load Speed',
                    'problem': f'Your {load_time:.1f}s load time is losing you visitors',
                    'impact': f'Estimated {int((load_time-2)*7)}% conversion loss',
                    'solution': 'Optimize images, enable caching, use CDN, minimize JavaScript',
                    'timeline': '1 week'
                })
        
        # Mobile issues
        if data.get('mobile'):
            mobile_score = data['mobile'].get('score', 100)
            if mobile_score < 70:
                issues.append({
                    'title': 'Poor Mobile Experience',
                    'problem': f'Mobile score of {mobile_score}/100 frustrates {data["mobile"].get("mobile_traffic_percent", 60)}% of visitors',
                    'impact': 'Losing 40-60% of mobile conversions',
                    'solution': 'Responsive redesign, touch-friendly buttons, optimize mobile speed',
                    'timeline': '2 weeks'
                })
        
        # Conversion issues
        if data.get('conversion'):
            if not data['conversion'].get('has_social_proof'):
                issues.append({
                    'title': 'Missing Social Proof',
                    'problem': 'No testimonials or reviews visible',
                    'impact': '15-30% lower conversion rate',
                    'solution': 'Add 5-10 customer testimonials, display trust badges, show user count',
                    'timeline': '3 days'
                })
            
            if not data['conversion'].get('clear_cta'):
                issues.append({
                    'title': 'Weak Call-to-Actions',
                    'problem': 'CTAs are not clear or compelling',
                    'impact': '20-35% of visitors don\'t know next step',
                    'solution': 'Use action verbs, create contrast, add urgency, A/B test copy',
                    'timeline': '2 days'
                })
        
        # SEO issues
        if data.get('seo'):
            if not data['seo'].get('has_meta_description'):
                issues.append({
                    'title': 'Missing Meta Descriptions',
                    'problem': 'Pages lack meta descriptions for search results',
                    'impact': '5-10% lower click-through rate from search',
                    'solution': 'Write compelling 155-character descriptions for all pages',
                    'timeline': '1 day'
                })
        
        # Form issues
        if data.get('forms'):
            avg_fields = data['forms'].get('average_fields', 0)
            if avg_fields > 7:
                issues.append({
                    'title': 'Form Abandonment Risk',
                    'problem': f'Forms have {avg_fields} fields on average',
                    'impact': 'Each field beyond 5 reduces completion by 5-10%',
                    'solution': 'Reduce to 3-5 fields, use progressive disclosure, add autofill',
                    'timeline': '1 week'
                })
        
        return sorted(issues, key=lambda x: self._get_issue_priority(x), reverse=True)
    
    @staticmethod
    def _get_issue_priority(issue: Dict) -> int:
        """Calculate priority score for an issue."""
        priority = 0
        
        # Check impact severity
        if '30%' in issue['impact'] or '40%' in issue['impact'] or '50%' in issue['impact']:
            priority += 30
        elif '20%' in issue['impact'] or '25%' in issue['impact']:
            priority += 20
        elif '10%' in issue['impact'] or '15%' in issue['impact']:
            priority += 10
        
        # Check timeline urgency
        if 'day' in issue['timeline']:
            priority += 20
        elif 'week' in issue['timeline']:
            priority += 10
        
        return priority
    
    @staticmethod
    def _generate_opportunities(data: Dict) -> List[Dict]:
        """Generate growth opportunities from analysis."""
        
        opportunities = []
        
        # Performance opportunity
        if data.get('performance', {}).get('load_time', 0) > 2:
            current_time = data['performance']['load_time']
            opportunities.append({
                'title': 'Speed Optimization',
                'description': f'Reduce load time from {current_time:.1f}s to <2s',
                'implementation': 'Image optimization, lazy loading, CDN setup, code minification',
                'roi': f'+{int((current_time-2)*7)}% conversion rate'
            })
        
        # Conversion opportunities
        if data.get('conversion'):
            if not data['conversion'].get('has_exit_intent'):
                opportunities.append({
                    'title': 'Exit Intent Capture',
                    'description': 'Capture abandoning visitors with targeted offers',
                    'implementation': 'Add exit-intent popup with discount or content upgrade',
                    'roi': '+10-15% email capture, +5% conversions'
                })
            
            if not data['conversion'].get('has_live_chat'):
                opportunities.append({
                    'title': 'Live Chat Implementation',
                    'description': 'Reduce friction with instant support',
                    'implementation': 'Add Intercom/Drift, staff during business hours',
                    'roi': '+20% conversions, -30% support tickets'
                })
        
        # Content opportunities
        if data.get('content'):
            if data['content'].get('blog_posts', 0) < 20:
                opportunities.append({
                    'title': 'Content Marketing Expansion',
                    'description': 'Build authority with comprehensive content',
                    'implementation': 'Publish 2 articles/week, target long-tail keywords',
                    'roi': '+150% organic traffic in 6 months'
                })
        
        # Social proof opportunities
        if data.get('social', {}).get('reviews_count', 0) < 50:
            opportunities.append({
                'title': 'Review Collection Campaign',
                'description': 'Build trust with customer reviews',
                'implementation': 'Email campaign to past customers, incentivize reviews',
                'roi': '+25% trust score, +15% conversions'
            })
        
        # Pricing opportunities
        if data.get('pricing_intelligence'):
            if not data['pricing_intelligence'].get('has_free_trial'):
                opportunities.append({
                    'title': 'Free Trial Introduction',
                    'description': 'Reduce purchase friction with try-before-buy',
                    'implementation': '14-day free trial, no credit card required',
                    'roi': '+200% trial signups, +40% paid conversions'
                })
        
        return opportunities
    
    @staticmethod
    def _format_performance_metrics(data: Dict) -> str:
        """Format performance metrics section."""
        
        metrics = []
        
        if data.get('performance'):
            perf = data['performance']
            
            # Load time
            load_time = perf.get('load_time', 0)
            if load_time:
                status = "✅" if load_time < 2 else "⚠️" if load_time < 3 else "🚨"
                metrics.append(f"{status} **Load Time:** {load_time:.1f}s")
                if load_time > 2:
                    metrics.append(f"   → Recommendation: Target <2s for optimal conversions")
            
            # Page size
            page_size = perf.get('page_size_mb', 0)
            if page_size:
                status = "✅" if page_size < 2 else "⚠️" if page_size < 4 else "🚨"
                metrics.append(f"{status} **Page Size:** {page_size:.1f}MB")
                if page_size > 2:
                    metrics.append(f"   → Recommendation: Compress images, remove unused CSS/JS")
            
            # Requests
            requests = perf.get('requests', 0)
            if requests:
                status = "✅" if requests < 50 else "⚠️" if requests < 100 else "🚨"
                metrics.append(f"{status} **HTTP Requests:** {requests}")
                if requests > 50:
                    metrics.append(f"   → Recommendation: Combine files, use sprites, lazy load")
        
        # Mobile performance
        if data.get('mobile'):
            mobile_score = data['mobile'].get('score', 0)
            if mobile_score:
                status = "✅" if mobile_score > 80 else "⚠️" if mobile_score > 60 else "🚨"
                metrics.append(f"{status} **Mobile Score:** {mobile_score}/100")
        
        return "\n".join(metrics) if metrics else "Performance data not available"
    
    @staticmethod
    def _format_conversion_analysis(data: Dict) -> str:
        """Format conversion optimization analysis."""
        
        elements = []
        
        if data.get('conversion'):
            conv = data['conversion']
            
            # Social proof
            if conv.get('has_social_proof'):
                elements.append("✅ **Social Proof:** Present")
                if conv.get('testimonial_count'):
                    elements.append(f"   • {conv['testimonial_count']} testimonials found")
            else:
                elements.append("🚨 **Social Proof:** Missing")
                elements.append("   → Add testimonials, reviews, client logos")
            
            # CTAs
            if conv.get('clear_cta'):
                elements.append("✅ **Call-to-Actions:** Clear and compelling")
            else:
                elements.append("⚠️ **Call-to-Actions:** Could be stronger")
                elements.append("   → Use action verbs, create urgency, increase contrast")
            
            # Trust signals
            if conv.get('trust_signals'):
                elements.append("✅ **Trust Signals:** Present")
                trust_types = conv.get('trust_types', [])
                if trust_types:
                    elements.append(f"   • Found: {', '.join(trust_types)}")
            else:
                elements.append("🚨 **Trust Signals:** Weak or missing")
                elements.append("   → Add security badges, certifications, guarantees")
            
            # Forms
            if conv.get('form_optimization'):
                form_score = conv['form_optimization'].get('score', 0)
                if form_score > 70:
                    elements.append(f"✅ **Forms:** Well optimized ({form_score}/100)")
                else:
                    elements.append(f"⚠️ **Forms:** Need optimization ({form_score}/100)")
                    elements.append("   → Reduce fields, add progress bars, improve labels")
        
        return "\n".join(elements) if elements else "Conversion data not available"
    
    @staticmethod
    def _format_seo_analysis(data: Dict) -> str:
        """Format SEO analysis section."""
        
        seo_insights = []
        
        if data.get('seo'):
            seo = data['seo']
            
            # Overall score
            score = seo.get('score', 0)
            status = "✅" if score > 80 else "⚠️" if score > 60 else "🚨"
            seo_insights.append(f"{status} **SEO Score:** {score}/100")
            
            # Title tags
            if seo.get('has_title_tags'):
                seo_insights.append("✅ **Title Tags:** Properly configured")
            else:
                seo_insights.append("🚨 **Title Tags:** Missing or duplicate")
            
            # Meta descriptions
            if seo.get('has_meta_descriptions'):
                seo_insights.append("✅ **Meta Descriptions:** Present")
            else:
                seo_insights.append("🚨 **Meta Descriptions:** Missing")
            
            # Schema markup
            if seo.get('has_schema'):
                seo_insights.append("✅ **Schema Markup:** Implemented")
            else:
                seo_insights.append("⚠️ **Schema Markup:** Not found")
                seo_insights.append("   → Add structured data for rich snippets")
            
            # Sitemap
            if seo.get('has_sitemap'):
                seo_insights.append("✅ **XML Sitemap:** Found")
            else:
                seo_insights.append("🚨 **XML Sitemap:** Not found")
        
        # Traffic data
        if data.get('traffic'):
            traffic = data['traffic']
            if traffic.get('organic_percent'):
                seo_insights.append(f"📊 **Organic Traffic:** {traffic['organic_percent']}%")
            if traffic.get('top_keywords'):
                seo_insights.append(f"🔍 **Top Keywords:** {', '.join(traffic['top_keywords'][:3])}")
        
        return "\n".join(seo_insights) if seo_insights else "SEO data not available"
    
    @staticmethod
    def _format_competitive_insights(data: Dict) -> str:
        """Format competitive intelligence section."""
        
        insights = []
        
        # Market position
        if data.get('competitive_analysis'):
            comp = data['competitive_analysis']
            
            if comp.get('market_position'):
                insights.append(f"**Market Position:** {comp['market_position']}")
            
            if comp.get('unique_features'):
                insights.append(f"**Unique Features:**")
                for feature in comp['unique_features'][:5]:
                    insights.append(f"   • {feature}")
            
            if comp.get('weaknesses'):
                insights.append(f"**Competitive Weaknesses:**")
                for weakness in comp['weaknesses'][:3]:
                    insights.append(f"   • {weakness}")
        
        # Pricing intelligence
        if data.get('pricing_intelligence'):
            pricing = data['pricing_intelligence']
            
            if pricing.get('pricing_model'):
                insights.append(f"**Pricing Model:** {pricing['pricing_model']}")
            
            if pricing.get('price_range'):
                insights.append(f"**Price Range:** {pricing['price_range']}")
            
            if pricing.get('competitive_advantage'):
                insights.append(f"**Pricing Advantage:** {pricing['competitive_advantage']}")
        
        return "\n".join(insights) if insights else "Competitive data not available"
    
    @staticmethod
    def _generate_action_plan(data: Dict) -> str:
        """Generate a prioritized 30-day action plan."""
        
        plan = []
        
        plan.append("### Week 1: Quick Wins")
        plan.append("1. **Add Social Proof** (2 days)")
        plan.append("   - Add 5 testimonials above fold")
        plan.append("   - Display customer logos")
        plan.append("   - Add trust badges")
        plan.append("")
        plan.append("2. **Optimize CTAs** (1 day)")
        plan.append("   - Increase button contrast")
        plan.append("   - Add urgency copy")
        plan.append("   - A/B test button text")
        plan.append("")
        plan.append("3. **Fix Critical SEO** (2 days)")
        plan.append("   - Write meta descriptions")
        plan.append("   - Fix broken links")
        plan.append("   - Submit sitemap")
        plan.append("")
        
        plan.append("### Week 2-3: Performance")
        plan.append("4. **Speed Optimization** (1 week)")
        plan.append("   - Compress all images")
        plan.append("   - Implement lazy loading")
        plan.append("   - Set up CDN")
        plan.append("   - Minify CSS/JS")
        plan.append("")
        plan.append("5. **Mobile Experience** (3 days)")
        plan.append("   - Fix responsive issues")
        plan.append("   - Optimize touch targets")
        plan.append("   - Test on real devices")
        plan.append("")
        
        plan.append("### Week 4: Growth")
        plan.append("6. **Conversion Optimization** (1 week)")
        plan.append("   - Add exit-intent popup")
        plan.append("   - Implement live chat")
        plan.append("   - Create urgency with limited offers")
        plan.append("")
        plan.append("7. **Content & SEO** (ongoing)")
        plan.append("   - Publish 2 blog posts")
        plan.append("   - Build 10 quality backlinks")
        plan.append("   - Optimize for featured snippets")
        plan.append("")
        
        plan.append("### Expected Results")
        plan.append("- **Week 1:** +10-15% conversion rate")
        plan.append("- **Week 2-3:** +20% site speed, +25% mobile conversions")
        plan.append("- **Week 4:** +30% overall conversions")
        plan.append("- **Month 2+:** +50% organic traffic")
        
        return "\n".join(plan)