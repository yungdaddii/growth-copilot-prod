"""Monitoring service for tracking website changes and competitor intelligence."""

import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from bs4 import BeautifulSoup
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.context import SiteSnapshot, CompetitorIntelligence, UserContext
from app.analyzers.performance import PerformanceAnalyzer
from app.analyzers.seo import SEOAnalyzer
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class WebsiteMonitor:
    """Monitors websites for changes and updates intelligence."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.performance_analyzer = PerformanceAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
    
    async def capture_snapshot(self, domain: str, url: Optional[str] = None) -> SiteSnapshot:
        """Capture current state of a website."""
        
        if not url:
            url = f"https://{domain}"
        
        logger.info(f"Capturing snapshot for {domain}")
        
        # Fetch the page
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            content = response.text
            
        # Parse content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract metrics
        snapshot = SiteSnapshot(
            domain=domain,
            url=url,
            snapshot_date=datetime.utcnow(),
            
            # Content metrics
            page_title=soup.find('title').text if soup.find('title') else '',
            meta_description=self._get_meta_description(soup),
            headlines=self._extract_headlines(soup),
            cta_buttons=self._extract_ctas(soup),
            form_fields=self._extract_forms(soup),
            images_count=len(soup.find_all('img')),
            testimonials_count=self._count_testimonials(soup),
            
            # SEO metrics
            word_count=len(soup.get_text().split()),
            internal_links=len([a for a in soup.find_all('a', href=True) 
                               if domain in a['href'] or a['href'].startswith('/')]),
            external_links=len([a for a in soup.find_all('a', href=True) 
                               if domain not in a['href'] and a['href'].startswith('http')]),
            
            # Content hash for change detection
            content_hash=hashlib.md5(content.encode()).hexdigest(),
            full_content=soup.get_text()[:50000]  # Store first 50k chars
        )
        
        # Get performance metrics
        try:
            perf_data = await self.performance_analyzer.analyze(domain)
            if perf_data:
                snapshot.load_time = perf_data.get('load_time', 0)
                snapshot.page_size = perf_data.get('page_size_mb', 0)
                snapshot.requests_count = perf_data.get('requests', 0)
        except Exception as e:
            logger.warning(f"Could not get performance metrics for {domain}: {e}")
        
        # Detect changes from previous snapshot
        previous = await self._get_previous_snapshot(domain)
        if previous:
            changes = self._detect_changes(previous, snapshot)
            snapshot.changes_detected = changes
            snapshot.change_score = self._calculate_change_significance(changes)
        
        # Save snapshot
        self.session.add(snapshot)
        await self.session.commit()
        
        return snapshot
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        return ''
    
    def _extract_headlines(self, soup: BeautifulSoup) -> Dict:
        """Extract all headlines."""
        headlines = {}
        for i in range(1, 4):  # H1, H2, H3
            tags = soup.find_all(f'h{i}')
            headlines[f'h{i}'] = [tag.get_text().strip() for tag in tags[:5]]  # First 5
        return headlines
    
    def _extract_ctas(self, soup: BeautifulSoup) -> List[str]:
        """Extract CTA button texts."""
        cta_keywords = ['start', 'try', 'get', 'sign', 'join', 'buy', 'download', 'demo', 'free']
        buttons = []
        
        for button in soup.find_all(['button', 'a']):
            text = button.get_text().strip().lower()
            if any(keyword in text for keyword in cta_keywords):
                buttons.append(button.get_text().strip())
        
        return list(set(buttons))[:10]  # Unique, max 10
    
    def _extract_forms(self, soup: BeautifulSoup) -> Dict:
        """Extract form information."""
        forms = soup.find_all('form')
        form_data = []
        
        for form in forms[:3]:  # Analyze first 3 forms
            inputs = form.find_all(['input', 'textarea', 'select'])
            form_data.append({
                'field_count': len(inputs),
                'field_types': [inp.get('type', 'text') for inp in inputs]
            })
        
        return form_data
    
    def _count_testimonials(self, soup: BeautifulSoup) -> int:
        """Count testimonial elements."""
        testimonial_keywords = ['testimonial', 'review', 'customer-story', 'quote', 'feedback']
        count = 0
        
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class', []))
            if any(keyword in classes.lower() for keyword in testimonial_keywords):
                count += 1
        
        # Also check for quote patterns
        blockquotes = len(soup.find_all('blockquote'))
        
        return min(count + blockquotes, 50)  # Cap at 50
    
    async def _get_previous_snapshot(self, domain: str) -> Optional[SiteSnapshot]:
        """Get the most recent snapshot for a domain."""
        result = await self.session.execute(
            select(SiteSnapshot)
            .where(SiteSnapshot.domain == domain)
            .order_by(SiteSnapshot.snapshot_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    def _detect_changes(self, previous: SiteSnapshot, current: SiteSnapshot) -> List[Dict]:
        """Detect changes between snapshots."""
        changes = []
        
        # Content changes
        if previous.page_title != current.page_title:
            changes.append({
                'type': 'title',
                'old': previous.page_title,
                'new': current.page_title,
                'impact': 'high'
            })
        
        if previous.meta_description != current.meta_description:
            changes.append({
                'type': 'meta_description',
                'old': previous.meta_description,
                'new': current.meta_description,
                'impact': 'medium'
            })
        
        # CTA changes
        old_ctas = set(previous.cta_buttons or [])
        new_ctas = set(current.cta_buttons or [])
        if old_ctas != new_ctas:
            changes.append({
                'type': 'cta_buttons',
                'added': list(new_ctas - old_ctas),
                'removed': list(old_ctas - new_ctas),
                'impact': 'high'
            })
        
        # Form changes
        if len(previous.form_fields or []) != len(current.form_fields or []):
            changes.append({
                'type': 'forms',
                'old_count': len(previous.form_fields or []),
                'new_count': len(current.form_fields or []),
                'impact': 'high'
            })
        
        # Performance changes
        if previous.load_time and current.load_time:
            time_diff = current.load_time - previous.load_time
            if abs(time_diff) > 0.5:  # 0.5 second change
                changes.append({
                    'type': 'performance',
                    'metric': 'load_time',
                    'old': previous.load_time,
                    'new': current.load_time,
                    'improvement': time_diff < 0,
                    'impact': 'high' if abs(time_diff) > 1 else 'medium'
                })
        
        # Testimonial changes
        if abs((previous.testimonials_count or 0) - (current.testimonials_count or 0)) > 2:
            changes.append({
                'type': 'social_proof',
                'old_count': previous.testimonials_count,
                'new_count': current.testimonials_count,
                'impact': 'medium'
            })
        
        return changes
    
    def _calculate_change_significance(self, changes: List[Dict]) -> float:
        """Calculate a significance score for changes (0-100)."""
        if not changes:
            return 0.0
        
        impact_scores = {'high': 30, 'medium': 15, 'low': 5}
        total_score = 0
        
        for change in changes:
            impact = change.get('impact', 'low')
            total_score += impact_scores.get(impact, 5)
        
        return min(total_score, 100)  # Cap at 100
    
    async def analyze_competitor_changes(self, domain: str, competitors: List[str]) -> Dict:
        """Analyze what competitors are doing differently."""
        
        # Get latest snapshots for all competitors
        snapshots = {}
        for competitor in competitors[:5]:  # Max 5 competitors
            snapshot = await self._get_previous_snapshot(competitor)
            if snapshot:
                snapshots[competitor] = snapshot
        
        if not snapshots:
            return {}
        
        # Find patterns and best practices
        analysis = {
            'common_updates': [],
            'unique_features': [],
            'performance_leaders': [],
            'conversion_elements': {}
        }
        
        # Analyze common elements
        all_ctas = []
        load_times = []
        testimonial_counts = []
        
        for comp, snap in snapshots.items():
            all_ctas.extend(snap.cta_buttons or [])
            if snap.load_time:
                load_times.append((comp, snap.load_time))
            testimonial_counts.append((comp, snap.testimonials_count or 0))
        
        # Find most common CTAs
        from collections import Counter
        cta_counter = Counter(all_ctas)
        analysis['common_ctas'] = cta_counter.most_common(5)
        
        # Performance leaders
        if load_times:
            load_times.sort(key=lambda x: x[1])
            analysis['performance_leaders'] = load_times[:3]
        
        # Social proof leaders
        testimonial_counts.sort(key=lambda x: x[1], reverse=True)
        analysis['social_proof_leaders'] = testimonial_counts[:3]
        
        return analysis
    
    async def generate_growth_opportunities(self, domain: str, context: UserContext) -> List[Dict]:
        """Generate specific growth opportunities based on data."""
        
        opportunities = []
        
        # Get user's latest snapshot
        snapshot = await self._get_previous_snapshot(domain)
        if not snapshot:
            return []
        
        # Get competitor analysis
        if context.competitors:
            competitor_analysis = await self.analyze_competitor_changes(
                domain, context.competitors
            )
        else:
            competitor_analysis = {}
        
        # Check performance opportunities
        if snapshot.load_time and snapshot.load_time > 3:
            opportunities.append({
                'title': 'Improve Page Load Speed',
                'description': f'Your site loads in {snapshot.load_time:.1f}s. Best practice is under 2s.',
                'predicted_impact': '+15-30% conversion rate',
                'priority': 'high',
                'implementation': 'Optimize images, enable caching, use CDN',
                'effort': 'medium',
                'based_on': 'Google data shows 53% of users abandon sites that take >3s to load'
            })
        
        # Check social proof
        if snapshot.testimonials_count < 3:
            comp_testimonials = competitor_analysis.get('social_proof_leaders', [])
            if comp_testimonials and comp_testimonials[0][1] > 5:
                opportunities.append({
                    'title': 'Add Customer Testimonials',
                    'description': f'You have {snapshot.testimonials_count} testimonials. Top competitors have {comp_testimonials[0][1]}.',
                    'predicted_impact': '+18% conversion rate',
                    'priority': 'high',
                    'implementation': 'Add 5-7 customer testimonials with names and photos',
                    'effort': 'low',
                    'based_on': f'{comp_testimonials[0][0]} has {comp_testimonials[0][1]} testimonials'
                })
        
        # Check CTAs
        if snapshot.cta_buttons:
            common_ctas = competitor_analysis.get('common_ctas', [])
            if common_ctas:
                missing_ctas = [cta for cta, _ in common_ctas[:3] 
                               if cta not in snapshot.cta_buttons]
                if missing_ctas:
                    opportunities.append({
                        'title': 'Test New CTA Copy',
                        'description': f"Competitors use: {', '.join(missing_ctas[:2])}",
                        'predicted_impact': '+8-12% click-through rate',
                        'priority': 'medium',
                        'implementation': f'A/B test your CTA against "{missing_ctas[0]}"',
                        'effort': 'low',
                        'based_on': 'Used by 3+ successful competitors'
                    })
        
        # Check forms
        if snapshot.form_fields:
            avg_fields = sum(len(f.get('field_types', [])) for f in snapshot.form_fields) / len(snapshot.form_fields)
            if avg_fields > 5:
                opportunities.append({
                    'title': 'Simplify Forms',
                    'description': f'Your forms average {avg_fields:.0f} fields. Best practice is 3-4.',
                    'predicted_impact': '+25% form completion',
                    'priority': 'high',
                    'implementation': 'Remove optional fields, use progressive disclosure',
                    'effort': 'low',
                    'based_on': 'HubSpot data: 3-field forms convert 25% better than 5+ fields'
                })
        
        return opportunities


class MonitoringScheduler:
    """Schedules and manages monitoring tasks."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.monitor = WebsiteMonitor(session)
    
    async def check_monitored_sites(self):
        """Check all sites being monitored for changes."""
        
        # Get all unique monitored sites
        result = await self.session.execute(
            select(UserContext.monitoring_sites).where(
                UserContext.monitoring_sites.isnot(None)
            )
        )
        
        all_sites = set()
        for row in result:
            if row[0]:
                all_sites.update(row[0])
        
        logger.info(f"Checking {len(all_sites)} monitored sites")
        
        # Capture snapshots for each
        for site in all_sites:
            try:
                await self.monitor.capture_snapshot(site)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error monitoring {site}: {e}")
    
    async def update_competitor_intelligence(self):
        """Update competitor intelligence data."""
        
        # Get all competitors being tracked
        result = await self.session.execute(
            select(UserContext.competitors).where(
                UserContext.competitors.isnot(None)
            )
        )
        
        all_competitors = set()
        for row in result:
            if row[0]:
                all_competitors.update(row[0])
        
        for competitor in all_competitors:
            try:
                # Get recent snapshots
                snapshots = await self.session.execute(
                    select(SiteSnapshot)
                    .where(
                        and_(
                            SiteSnapshot.domain == competitor,
                            SiteSnapshot.snapshot_date > datetime.utcnow() - timedelta(days=30)
                        )
                    )
                    .order_by(SiteSnapshot.snapshot_date.desc())
                )
                
                recent_snapshots = snapshots.scalars().all()
                if recent_snapshots:
                    # Update or create intelligence record
                    intel = await self._get_or_create_intelligence(competitor)
                    intel.recent_updates = self._summarize_changes(recent_snapshots)
                    intel.updated_at = datetime.utcnow()
                    
                    await self.session.commit()
                    
            except Exception as e:
                logger.error(f"Error updating intelligence for {competitor}: {e}")
    
    async def _get_or_create_intelligence(self, domain: str) -> CompetitorIntelligence:
        """Get or create competitor intelligence record."""
        result = await self.session.execute(
            select(CompetitorIntelligence).where(
                CompetitorIntelligence.domain == domain
            )
        )
        intel = result.scalar_one_or_none()
        
        if not intel:
            intel = CompetitorIntelligence(domain=domain)
            self.session.add(intel)
        
        return intel
    
    def _summarize_changes(self, snapshots: List[SiteSnapshot]) -> List[Dict]:
        """Summarize changes from snapshots."""
        changes = []
        
        for snapshot in snapshots[:10]:  # Last 10 snapshots
            if snapshot.changes_detected and snapshot.change_score > 10:
                changes.append({
                    'date': snapshot.snapshot_date.isoformat(),
                    'score': snapshot.change_score,
                    'changes': snapshot.changes_detected[:3]  # Top 3 changes
                })
        
        return changes