import asyncio
import httpx
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime, timezone
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.analysis import Analysis, AnalysisStatus, Industry, CompetitorCache
from app.models.benchmarks import IndustryBenchmark
from app.analyzers import (
    PerformanceAnalyzer,
    ConversionAnalyzer,
    CompetitorAnalyzer,
    SEOAnalyzer,
    MobileAnalyzer
)
from app.analyzers.revenue_intelligence import RevenueIntelligenceAnalyzer
from app.analyzers.growth_opportunities import GrowthOpportunitiesAnalyzer
from app.analyzers.browser_analyzer import BrowserAnalyzer
from app.analyzers.traffic import TrafficAnalyzer
from app.analyzers.similarweb import SimilarWebAnalyzer
from app.analyzers.social import SocialAnalyzer
from app.analyzers.ads import AdsAnalyzer
from app.analyzers.ai_search import AISearchAnalyzer
from app.analyzers.page_analyzer import PageAnalyzer
from app.analyzers.form_intelligence import FormIntelligenceAnalyzer
from app.analyzers.content_strategy import ContentStrategyAnalyzer

# New real-time analyzers for deeper insights
from app.analyzers.realtime_browser import RealtimeBrowserAnalyzer
from app.analyzers.form_conversion_killer import FormConversionKillerAnalyzer
from app.analyzers.content_quality import ContentQualityAnalyzer
from app.analyzers.technical_seo_deep import TechnicalSEODeepAnalyzer
from app.analyzers.pricing_intelligence import PricingIntelligenceAnalyzer
from app.core.metrics import MetricsCalculator
from app.core.recommendations import RecommendationEngine
from app.utils.cache import cache_result, get_cached_result
from app.utils.analytics import Analytics

logger = structlog.get_logger()


class DomainAnalyzer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.performance_analyzer = PerformanceAnalyzer()
        self.conversion_analyzer = ConversionAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        self.mobile_analyzer = MobileAnalyzer()
        self.traffic_analyzer = TrafficAnalyzer()
        self.social_analyzer = SocialAnalyzer()
        self.ads_analyzer = AdsAnalyzer()
        self.ai_search_analyzer = AISearchAnalyzer()
        self.page_analyzer = PageAnalyzer()
        self.form_intelligence_analyzer = FormIntelligenceAnalyzer()
        self.content_strategy_analyzer = ContentStrategyAnalyzer()
        self.revenue_intelligence_analyzer = RevenueIntelligenceAnalyzer()
        self.growth_opportunities_analyzer = GrowthOpportunitiesAnalyzer()
        self.browser_analyzer = BrowserAnalyzer()
        self.similarweb_analyzer = SimilarWebAnalyzer()
        
        # New real-time deep analyzers
        self.realtime_browser_analyzer = RealtimeBrowserAnalyzer()
        self.form_conversion_killer_analyzer = FormConversionKillerAnalyzer()
        self.content_quality_analyzer = ContentQualityAnalyzer()
        self.technical_seo_deep_analyzer = TechnicalSEODeepAnalyzer()
        self.pricing_intelligence_analyzer = PricingIntelligenceAnalyzer()
        
        self.metrics_calculator = MetricsCalculator()
        self.recommendation_engine = RecommendationEngine()
    
    async def analyze(
        self,
        domain: str,
        conversation_id: UUID,
        update_callback: Optional[Callable] = None,
        user_id: Optional[UUID] = None
    ) -> Analysis:
        # Clean and validate domain
        domain = self._clean_domain(domain)
        
        # Create analysis record
        analysis = Analysis(
            conversation_id=conversation_id,
            domain=domain,
            status=AnalysisStatus.ANALYZING,
            user_id=user_id
        )
        self.db.add(analysis)
        await self.db.commit()
        
        try:
            # Stream update: Starting
            if update_callback:
                await update_callback(
                    "starting",
                    "🔍 Scanning homepage and key pages...",
                    10
                )
            
            # Detect industry
            industry = await self._detect_industry(domain)
            analysis.industry = industry
            
            # Get benchmarks for this industry
            benchmarks = await self._get_industry_benchmarks(industry)
            
            # Stream update: Performance
            if update_callback:
                await update_callback(
                    "performance",
                    "⚡ Checking site performance...",
                    25
                )
            
            # Run analyzers in parallel with timeout
            async def run_with_updates():
                # Create tasks for progress updates that happen during analysis
                async def send_progress_updates():
                    if update_callback:
                        await asyncio.sleep(2.0)  # Wait for analyzers to start
                        await update_callback("conversion", "📊 Analyzing conversion paths...", 40)
                        await asyncio.sleep(2.0)
                        await update_callback("competitors", "🎯 Comparing to competitors...", 55)
                        await asyncio.sleep(2.0)
                        await update_callback("mobile", "📱 Checking mobile experience...", 70)
                
                # Run analyzers and progress updates in parallel
                analyzer_task = asyncio.create_task(
                    self._run_analyzers_parallel(domain, industry, benchmarks, update_callback)
                )
                progress_task = asyncio.create_task(send_progress_updates())
                
                # Wait for analyzers to complete
                result = await analyzer_task
                
                # Cancel progress updates if still running
                progress_task.cancel()
                try:
                    await progress_task
                except asyncio.CancelledError:
                    pass
                
                return result
            
            results = await asyncio.wait_for(
                run_with_updates(),
                timeout=90.0  # Increased timeout for comprehensive analysis
            )
            
            # Stream update: Calculating impact
            if update_callback:
                await update_callback(
                    "calculating",
                    "💡 Calculating improvement opportunities...",
                    85
                )
            
            # Calculate metrics and issues
            logger.info(f"Calculating metrics for {domain}")
            issues, quick_wins = await self.metrics_calculator.calculate(
                domain, results, industry, benchmarks
            )
            logger.info(f"Found {len(issues)} issues and {len(quick_wins)} quick wins")
            
            # Generate actionable recommendations
            recommendations = self.recommendation_engine.generate_recommendations(results)
            quick_wins_detailed = self.recommendation_engine.generate_quick_wins(results)
            
            # Update analysis with results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.now(timezone.utc)
            analysis.duration_seconds = (
                analysis.completed_at - analysis.started_at
            ).total_seconds()
            
            analysis.results = results
            analysis.issues_found = issues
            analysis.quick_wins = quick_wins_detailed if quick_wins_detailed else quick_wins
            
            # Store recommendations in results for NLP to use
            results["recommendations"] = recommendations
            results["quick_wins_detailed"] = quick_wins_detailed
            
            # Set scores
            analysis.performance_score = results.get("performance", {}).get("score", 0)
            analysis.conversion_score = results.get("conversion", {}).get("score", 0)
            analysis.mobile_score = results.get("mobile", {}).get("score", 0)
            analysis.seo_score = results.get("seo", {}).get("score", 0)
            
            await self.db.commit()
            await self.db.refresh(analysis)
            
            # Stream update: Complete
            if update_callback:
                await update_callback(
                    "complete",
                    "✅ Analysis complete!",
                    100
                )
            
            logger.info(
                "Analysis completed",
                domain=domain,
                duration=analysis.duration_seconds,
                issues_count=len(issues)
            )
            
            return analysis
            
        except asyncio.TimeoutError:
            analysis.status = AnalysisStatus.PARTIAL
            await self.db.commit()
            logger.warning("Analysis timeout", domain=domain)
            raise
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            await self.db.commit()
            logger.error("Analysis failed", domain=domain, error=str(e))
            raise
    
    async def _run_analyzers_parallel(
        self,
        domain: str,
        industry: Industry,
        benchmarks: Dict,
        update_callback: Optional[Callable]
    ) -> Dict[str, Any]:
        tasks = []
        analyzer_names = []
        
        # Performance analysis
        tasks.append(self.performance_analyzer.analyze(domain))
        analyzer_names.append("performance")
        
        # Conversion analysis  
        tasks.append(self.conversion_analyzer.analyze(domain, industry))
        analyzer_names.append("conversion")
        
        # Competitor analysis
        tasks.append(self.competitor_analyzer.analyze(domain, industry, self.db))
        analyzer_names.append("competitors")
        
        # Mobile analysis
        tasks.append(self.mobile_analyzer.analyze(domain))
        analyzer_names.append("mobile")
        
        # SEO analysis
        tasks.append(self.seo_analyzer.analyze(domain))
        analyzer_names.append("seo")
        
        # Traffic analysis
        tasks.append(self.traffic_analyzer.analyze(domain))
        analyzer_names.append("traffic")
        
        # SimilarWeb traffic data (REAL TRAFFIC DATA)
        tasks.append(self.similarweb_analyzer.analyze(domain))
        analyzer_names.append("similarweb")
        
        # Social media analysis
        tasks.append(self.social_analyzer.analyze(domain))
        analyzer_names.append("social")
        
        # Ads analysis
        tasks.append(self.ads_analyzer.analyze(domain))
        analyzer_names.append("ads")
        
        # AI Search analysis
        tasks.append(self.ai_search_analyzer.analyze(domain))
        analyzer_names.append("ai_search")
        
        # Page-specific analysis
        tasks.append(self.page_analyzer.analyze(domain))
        analyzer_names.append("page_analysis")
        
        # Form intelligence analysis
        tasks.append(self.form_intelligence_analyzer.analyze(domain))
        analyzer_names.append("form_intelligence")
        
        # Revenue Intelligence and Growth Opportunities
        tasks.append(self.revenue_intelligence_analyzer.analyze(domain, industry))
        analyzer_names.append("revenue_intelligence")
        tasks.append(self.growth_opportunities_analyzer.analyze(domain, None))  # Will get competitors from results later
        analyzer_names.append("growth_opportunities")
        
        # Browser-based validation (most accurate but slower)
        tasks.append(self.browser_analyzer.analyze(domain))
        analyzer_names.append("browser_validation")
        
        # NEW: Real-time browser analysis for JavaScript errors and dynamic issues
        tasks.append(self.realtime_browser_analyzer.analyze(domain))
        analyzer_names.append("realtime_browser")
        
        # NEW: Deep form conversion killer analysis
        tasks.append(self.form_conversion_killer_analyzer.analyze(domain))
        analyzer_names.append("form_conversion_killers")
        
        # NEW: Content quality analysis (not just existence)
        tasks.append(self.content_quality_analyzer.analyze(domain))
        analyzer_names.append("content_quality")
        
        # NEW: Technical SEO deep dive
        tasks.append(self.technical_seo_deep_analyzer.analyze(domain))
        analyzer_names.append("technical_seo_deep")
        
        # NEW: Pricing intelligence extraction
        tasks.append(self.pricing_intelligence_analyzer.analyze(domain))
        analyzer_names.append("pricing_intelligence")
        
        # Content strategy analysis (pass competitors if found)
        # Will be handled after initial results
        
        # Track analyzer execution with timing
        import time
        analyzer_timings = {}
        
        # Run all analyzers and track timing
        start_times = [time.time() for _ in tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Track each analyzer's performance
        for i, (result, name) in enumerate(zip(results, analyzer_names)):
            duration = time.time() - start_times[0]  # Approximate since they run in parallel
            success = not isinstance(result, Exception)
            error = str(result) if isinstance(result, Exception) else None
            
            Analytics.track_analyzer_performance(
                analyzer_name=name,
                domain=domain,
                duration=duration,
                success=success,
                error=error
            )
        
        # Combine results
        combined = {}
        for i, key in enumerate(analyzer_names):
            if i < len(results) and not isinstance(results[i], Exception):
                combined[key] = results[i]
            else:
                if i < len(results):
                    logger.error(f"{key} analysis failed", error=str(results[i]))
                    combined[key] = {"error": str(results[i])}
                else:
                    combined[key] = {}
        
        # Run content strategy analysis with competitor data
        if combined.get("competitors", {}).get("competitors"):
            competitor_domains = [c.get("domain") for c in combined["competitors"]["competitors"] if c.get("domain")]
            try:
                content_strategy = await self.content_strategy_analyzer.analyze(domain, competitor_domains)
                combined["content_strategy"] = content_strategy
            except Exception as e:
                logger.error(f"Content strategy analysis failed", error=str(e))
                combined["content_strategy"] = {}
            
            # Re-run growth opportunities with competitor data
            try:
                growth_opps_enhanced = await self.growth_opportunities_analyzer.analyze(domain, competitor_domains)
                # Merge with initial results
                if combined.get("growth_opportunities"):
                    for key in growth_opps_enhanced:
                        if key not in combined["growth_opportunities"] or not combined["growth_opportunities"][key]:
                            combined["growth_opportunities"][key] = growth_opps_enhanced[key]
                else:
                    combined["growth_opportunities"] = growth_opps_enhanced
            except Exception as e:
                logger.error(f"Enhanced growth opportunities analysis failed", error=str(e))
            
            # Get competitive traffic comparison from SimilarWeb
            if combined.get("similarweb", {}).get("has_data"):
                try:
                    traffic_comparison = await self.similarweb_analyzer.compare_traffic(domain, competitor_domains)
                    combined["traffic_comparison"] = traffic_comparison
                    
                    # Add traffic data to each competitor
                    for comp in combined["competitors"]["competitors"]:
                        comp_domain = comp.get("domain")
                        if comp_domain:
                            comp_traffic = await self.similarweb_analyzer.analyze(comp_domain)
                            if comp_traffic.get("has_data"):
                                comp["traffic_data"] = {
                                    "monthly_visits": comp_traffic.get("traffic_overview", {}).get("monthly_visits", 0),
                                    "bounce_rate": comp_traffic.get("engagement_metrics", {}).get("bounce_rate", 0),
                                    "growth_rate": comp_traffic.get("traffic_overview", {}).get("growth_rate", 0)
                                }
                except Exception as e:
                    logger.error(f"Traffic comparison failed", error=str(e))
        
        return combined
    
    async def _run_with_update(
        self,
        coro,
        name: str,
        update_callback: Optional[Callable],
        message: str,
        progress: int
    ):
        result = await coro
        if update_callback:
            await update_callback(name, message, progress)
        return result
    
    async def _detect_industry(self, domain: str) -> Industry:
        # Check cache first
        cached = await get_cached_result(f"industry:{domain}")
        if cached:
            return Industry(cached)
        
        # Simple industry detection based on keywords and patterns
        # In production, use more sophisticated ML model or API
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"https://{domain}", timeout=10)
                content = response.text.lower()
                
                if any(word in content for word in ["saas", "software", "api", "dashboard", "trial"]):
                    industry = Industry.SAAS
                elif any(word in content for word in ["shop", "cart", "buy", "product", "checkout"]):
                    industry = Industry.ECOMMERCE
                elif any(word in content for word in ["enterprise", "solutions", "consulting"]):
                    industry = Industry.ENTERPRISE
                elif any(word in content for word in ["marketplace", "vendors", "sellers"]):
                    industry = Industry.MARKETPLACE
                else:
                    industry = Industry.OTHER
                
                await cache_result(f"industry:{domain}", industry.value, ttl=86400)
                return industry
                
            except Exception as e:
                logger.error("Industry detection failed", domain=domain, error=str(e))
                return Industry.OTHER
    
    async def _get_industry_benchmarks(self, industry: Industry) -> Dict[str, Any]:
        result = await self.db.execute(
            select(IndustryBenchmark).where(IndustryBenchmark.industry == industry)
        )
        benchmarks = result.scalars().all()
        
        return {
            b.metric_type.value: {
                "p25": b.p25_value,
                "p50": b.p50_value,
                "p75": b.p75_value,
                "p90": b.p90_value
            }
            for b in benchmarks
        }
    
    def _clean_domain(self, domain: str) -> str:
        domain = domain.lower().strip()
        domain = domain.replace("http://", "").replace("https://", "")
        domain = domain.replace("www.", "")
        if "/" in domain:
            domain = domain.split("/")[0]
        return domain