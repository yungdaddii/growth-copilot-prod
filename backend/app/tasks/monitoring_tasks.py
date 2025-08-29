"""Celery tasks for monitoring websites and updating intelligence."""

from celery import shared_task
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.monitoring import MonitoringScheduler
import logging

logger = logging.getLogger(__name__)


# Create async engine for Celery tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task(name="monitor_websites")
def monitor_websites():
    """Monitor all tracked websites for changes."""
    
    async def run_monitoring():
        async with AsyncSessionLocal() as session:
            scheduler = MonitoringScheduler(session)
            await scheduler.check_monitored_sites()
            logger.info(f"Monitoring task completed at {datetime.utcnow()}")
    
    # Run async task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_monitoring())
    finally:
        loop.close()
    
    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}


@shared_task(name="update_competitor_intelligence")
def update_competitor_intelligence():
    """Update competitor intelligence data."""
    
    async def run_update():
        async with AsyncSessionLocal() as session:
            scheduler = MonitoringScheduler(session)
            await scheduler.update_competitor_intelligence()
            logger.info(f"Competitor intelligence updated at {datetime.utcnow()}")
    
    # Run async task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_update())
    finally:
        loop.close()
    
    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}


@shared_task(name="populate_benchmarks")
def populate_benchmarks():
    """Populate industry benchmarks from analyzed data."""
    
    async def run_populate():
        async with AsyncSessionLocal() as session:
            from app.models.context import GrowthBenchmark, SiteSnapshot
            from sqlalchemy import select, func
            
            # Calculate benchmarks from existing snapshots
            industries = ['saas', 'ecommerce', 'media', 'finance', 'general']
            metrics = [
                ('load_time', 'seconds'),
                ('testimonials_count', 'count'),
                ('form_fields_avg', 'count')
            ]
            
            for industry in industries:
                for metric_name, unit in metrics:
                    # Get all values for this metric
                    if metric_name == 'load_time':
                        result = await session.execute(
                            select(SiteSnapshot.load_time)
                            .where(SiteSnapshot.load_time.isnot(None))
                            .order_by(SiteSnapshot.load_time)
                        )
                        values = [r[0] for r in result if r[0] is not None]
                    elif metric_name == 'testimonials_count':
                        result = await session.execute(
                            select(SiteSnapshot.testimonials_count)
                            .where(SiteSnapshot.testimonials_count.isnot(None))
                            .order_by(SiteSnapshot.testimonials_count)
                        )
                        values = [r[0] for r in result if r[0] is not None]
                    else:
                        continue
                    
                    if len(values) >= 10:  # Need at least 10 data points
                        # Calculate percentiles
                        n = len(values)
                        benchmark = GrowthBenchmark(
                            industry=industry,
                            metric_name=metric_name,
                            p10_value=values[int(n * 0.1)],
                            p25_value=values[int(n * 0.25)],
                            median_value=values[int(n * 0.5)],
                            p75_value=values[int(n * 0.75)],
                            p90_value=values[int(n * 0.9)],
                            sample_size=n,
                            impact_on_conversion=0.1 if metric_name == 'load_time' else 0.05,
                            implementation_difficulty='medium'
                        )
                        
                        # Check if exists
                        existing = await session.execute(
                            select(GrowthBenchmark)
                            .where(
                                GrowthBenchmark.industry == industry,
                                GrowthBenchmark.metric_name == metric_name
                            )
                        )
                        if not existing.scalar_one_or_none():
                            session.add(benchmark)
            
            await session.commit()
            logger.info("Benchmarks populated successfully")
    
    # Run async task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_populate())
    finally:
        loop.close()
    
    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}