from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import structlog

from app.models.analysis import Industry

logger = structlog.get_logger()


@dataclass
class Issue:
    category: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    current_state: str
    recommended_state: str
    impact_score: int  # 0-100
    fix_difficulty: str  # easy, medium, hard
    fix_time: str  # "2 hours", "1 day", etc.
    competitor_advantage: str  # How competitors handle this


@dataclass
class QuickWin:
    title: str
    current_state: str
    recommended_state: str
    improvement_potential: str  # "40% better conversion"
    implementation_time: str
    implementation_steps: List[str]
    impact_score: int  # 0-100


class MetricsCalculator:
    def __init__(self):
        # Industry benchmarks (in production, load from DB)
        self.benchmarks = {
            Industry.SAAS: {
                "form_fields": {"good": 4, "acceptable": 6, "poor": 8},
                "page_speed": {"good": 2.5, "acceptable": 4.0, "poor": 6.0},
                "mobile_score": {"good": 90, "acceptable": 70, "poor": 50},
                "conversion_rate": {"good": 4.0, "acceptable": 2.5, "poor": 1.0},
                "trial_to_paid": {"good": 20, "acceptable": 15, "poor": 10},
            },
            Industry.ECOMMERCE: {
                "form_fields": {"good": 5, "acceptable": 7, "poor": 10},
                "page_speed": {"good": 2.0, "acceptable": 3.0, "poor": 5.0},
                "mobile_score": {"good": 95, "acceptable": 80, "poor": 60},
                "cart_abandonment": {"good": 60, "acceptable": 70, "poor": 80},
                "checkout_steps": {"good": 3, "acceptable": 4, "poor": 5},
            }
        }
    
    async def calculate(
        self,
        domain: str,
        results: Dict[str, Any],
        industry: Industry,
        benchmarks: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        issues = []
        quick_wins = []
        
        # Get industry benchmarks
        industry_bench = self.benchmarks.get(industry, self.benchmarks[Industry.SAAS])
        
        # Analyze performance issues
        if "performance" in results:
            perf_issues, perf_wins = self._analyze_performance(
                results["performance"], industry_bench
            )
            issues.extend(perf_issues)
            quick_wins.extend(perf_wins)
        
        # Analyze conversion issues
        if "conversion" in results:
            conv_issues, conv_wins = self._analyze_conversion(
                results["conversion"], industry_bench
            )
            issues.extend(conv_issues)
            quick_wins.extend(conv_wins)
        
        # Analyze competitor gaps
        if "competitors" in results:
            comp_issues = self._analyze_competitors(
                results["competitors"], domain
            )
            issues.extend(comp_issues)
        
        # Analyze mobile issues
        if "mobile" in results:
            mobile_issues, mobile_wins = self._analyze_mobile(
                results["mobile"], industry_bench
            )
            issues.extend(mobile_issues)
            quick_wins.extend(mobile_wins)
        
        # Analyze SEO issues
        if "seo" in results:
            seo_issues, seo_wins = self._analyze_seo(
                results["seo"]
            )
            issues.extend(seo_issues)
            quick_wins.extend(seo_wins)
        
        # Sort by impact score
        issues.sort(key=lambda x: x.impact_score if hasattr(x, 'impact_score') else 0, reverse=True)
        quick_wins.sort(key=lambda x: x.impact_score if hasattr(x, 'impact_score') else 0, reverse=True)
        
        # Convert to dicts
        issues_dict = [self._issue_to_dict(i) for i in issues[:10]]  # Top 10
        wins_dict = [self._win_to_dict(w) for w in quick_wins[:5]]  # Top 5
        
        return issues_dict, wins_dict
    
    def _analyze_performance(
        self, perf_data: Dict, benchmarks: Dict
    ) -> Tuple[List[Issue], List[QuickWin]]:
        issues = []
        quick_wins = []
        
        # Page speed analysis
        if "load_time" in perf_data:
            load_time = perf_data.get("load_time")
            bench = benchmarks.get("page_speed", {})
            
            if load_time and load_time > bench.get("poor", 6.0):
                issues.append(Issue(
                    category="performance",
                    severity="critical",
                    title="Critical page speed issues",
                    description=f"Your site takes {load_time:.1f}s to load",
                    current_state=f"{load_time:.1f} seconds load time",
                    recommended_state=f"Under {bench.get('good', 2.5)} seconds",
                    impact_score=90,
                    fix_difficulty="medium",
                    fix_time="1-2 days",
                    competitor_advantage="Competitors load 3x faster"
                ))
                
                # Image optimization quick win
                if perf_data.get("unoptimized_images", 0) > 5:
                    quick_wins.append(QuickWin(
                        title="Compress images",
                        current_state=f"{perf_data['unoptimized_images']} unoptimized images",
                        recommended_state="All images optimized",
                        improvement_potential="50% faster page load",
                        implementation_time="2 hours",
                        implementation_steps=[
                            "Run images through compression tool",
                            "Convert to WebP format",
                            "Implement lazy loading"
                        ],
                        impact_score=75
                    ))
        
        return issues, quick_wins
    
    def _analyze_conversion(
        self, conv_data: Dict, benchmarks: Dict
    ) -> Tuple[List[Issue], List[QuickWin]]:
        issues = []
        quick_wins = []
        
        # Form field analysis
        if "form_fields" in conv_data:
            field_count = conv_data["form_fields"]
            bench = benchmarks.get("form_fields", {})
            
            if field_count > bench.get("poor", 8):
                abandonment_rate = min(67, field_count * 5)  # Estimate
                issues.append(Issue(
                    category="conversion",
                    severity="critical",
                    title="Excessive form fields killing conversion",
                    description=f"You have {field_count} fields vs industry standard of {bench.get('good', 4)}",
                    current_state=f"{field_count} required fields",
                    recommended_state=f"{bench.get('good', 4)} fields maximum",
                    impact_score=95,
                    fix_difficulty="easy",
                    fix_time="2 hours",
                    competitor_advantage=f"Competitors see {abandonment_rate}% less abandonment"
                ))
                
                quick_wins.append(QuickWin(
                    title="Reduce form to essential fields",
                    current_state=f"{field_count} fields causing {abandonment_rate}% abandonment",
                    recommended_state="Name, Email, Company, Phone only",
                    improvement_potential="40% better conversion",
                    implementation_time="2 hours",
                    implementation_steps=[
                        "Remove non-essential fields",
                        "Move qualifying questions to sales call",
                        "Add progressive profiling post-signup"
                    ],
                    impact_score=90
                ))
        
        # CTA analysis
        if conv_data.get("weak_cta", False):
            issues.append(Issue(
                category="conversion",
                severity="high",
                title="Weak call-to-action buttons",
                description="Your CTAs don't stand out or communicate value",
                current_state=conv_data.get("cta_text", "Generic CTA"),
                recommended_state="Action-oriented, value-focused CTA",
                impact_score=70,
                fix_difficulty="easy",
                fix_time="1 hour",
                competitor_advantage="Competitors have 2x higher click rates"
            ))
        
        return issues, quick_wins
    
    def _analyze_competitors(
        self, comp_data: Dict, domain: str
    ) -> List[Issue]:
        issues = []
        
        for competitor in comp_data.get("competitors", []):
            # Free trial advantage
            if competitor.get("has_free_trial") and not comp_data.get("your_free_trial"):
                issues.append(Issue(
                    category="competitive",
                    severity="critical",
                    title=f"Missing free trial while {competitor['name']} offers one",
                    description=f"{competitor['name']} captures developer-led growth with free trial",
                    current_state="Demo-only approach",
                    recommended_state="Free trial + demo option",
                    impact_score=85,
                    fix_difficulty="hard",
                    fix_time="2-4 weeks",
                    competitor_advantage=f"{competitor['name']} gets 2,400+ trials/month"
                ))
            
            # Pricing transparency
            if competitor.get("public_pricing") and not comp_data.get("your_pricing_visible"):
                issues.append(Issue(
                    category="competitive",
                    severity="high",
                    title="Hidden pricing losing trust",
                    description="Competitors show pricing, building trust immediately",
                    current_state="Contact us for pricing",
                    recommended_state="Transparent pricing tiers",
                    impact_score=75,
                    fix_difficulty="medium",
                    fix_time="1 week",
                    competitor_advantage="Competitors pre-qualify leads better"
                ))
        
        return issues
    
    def _analyze_mobile(
        self, mobile_data: Dict, benchmarks: Dict
    ) -> Tuple[List[Issue], List[QuickWin]]:
        issues = []
        quick_wins = []
        
        mobile_score = mobile_data.get("score", 0)
        bench = benchmarks.get("mobile_score", {})
        
        if mobile_score < bench.get("poor", 50):
            issues.append(Issue(
                category="mobile",
                severity="critical",
                title="Mobile experience is broken",
                description=f"Mobile score of {mobile_score}/100",
                current_state=f"{mobile_score}/100 mobile score",
                recommended_state=f"Above {bench.get('good', 90)}/100",
                impact_score=85,
                fix_difficulty="medium",
                fix_time="3-5 days",
                competitor_advantage="34% of your traffic is mobile"
            ))
        
        # Mobile-specific quick wins
        if mobile_data.get("missing_viewport"):
            quick_wins.append(QuickWin(
                title="Add mobile viewport meta tag",
                current_state="No viewport set",
                recommended_state="Responsive viewport",
                improvement_potential="Instant mobile fix",
                implementation_time="10 minutes",
                implementation_steps=[
                    "Add viewport meta tag to HTML head",
                    "Test on multiple devices"
                ],
                impact_score=80
            ))
        
        return issues, quick_wins
    
    def _analyze_seo(self, seo_data: Dict) -> Tuple[List[Issue], List[QuickWin]]:
        issues = []
        quick_wins = []
        
        # AI visibility
        if seo_data.get("blocks_ai_crawlers"):
            issues.append(Issue(
                category="seo",
                severity="critical",
                title="Invisible to AI search (ChatGPT, Perplexity)",
                description="You're blocking AI crawlers in robots.txt",
                current_state="Blocking GPTBot, CCBot",
                recommended_state="Allow AI crawlers",
                impact_score=80,
                fix_difficulty="easy",
                fix_time="5 minutes",
                competitor_advantage="Competitors get recommended by AI"
            ))
            
            quick_wins.append(QuickWin(
                title="Unblock AI crawlers immediately",
                current_state="Invisible to ChatGPT searches",
                recommended_state="Indexed by AI search",
                improvement_potential="Capture AI-driven traffic",
                implementation_time="5 minutes",
                implementation_steps=[
                    "Remove AI bot blocks from robots.txt",
                    "Add structured data markup",
                    "Submit sitemap"
                ],
                impact_score=85
            ))
        
        return issues, quick_wins
    
    def _issue_to_dict(self, issue: Issue) -> Dict:
        return {
            "category": issue.category,
            "severity": issue.severity,
            "title": issue.title,
            "description": issue.description,
            "current_state": issue.current_state,
            "recommended_state": issue.recommended_state,
            "impact_score": issue.impact_score,
            "fix_difficulty": issue.fix_difficulty,
            "fix_time": issue.fix_time,
            "competitor_advantage": issue.competitor_advantage
        }
    
    def _win_to_dict(self, win: QuickWin) -> Dict:
        return {
            "title": win.title,
            "current_state": win.current_state,
            "recommended_state": win.recommended_state,
            "improvement_potential": win.improvement_potential,
            "implementation_time": win.implementation_time,
            "implementation_steps": win.implementation_steps,
            "impact_score": win.impact_score
        }