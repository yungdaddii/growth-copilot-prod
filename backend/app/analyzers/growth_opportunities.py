import httpx
import asyncio
from typing import Dict, Any, List, Optional
import re
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urlparse, urljoin
import json

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class GrowthOpportunitiesAnalyzer:
    """
    Discovers untapped acquisition channels and growth opportunities.
    Identifies specific, actionable strategies without requiring integrations.
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
    async def analyze(self, domain: str, competitors: List[str] = None) -> Dict[str, Any]:
        """
        Analyze website for growth opportunities and untapped channels.
        Returns specific, actionable growth strategies.
        """
        # Check cache first
        cache_key = f"growth_opportunities:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "untapped_channels": [],
            "content_opportunities": [],
            "keyword_gaps": [],
            "viral_opportunities": [],
            "partnership_opportunities": [],
            "retention_improvements": [],
            "referral_opportunities": [],
            "community_building": [],
            "total_user_potential": 0,
            "acquisition_cost_reduction": [],
            "channel_recommendations": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Run all analyses in parallel
                tasks = [
                    self._analyze_social_presence(domain, client),
                    self._analyze_content_strategy(domain, client),
                    self._analyze_seo_opportunities(domain, client),
                    self._analyze_referral_potential(domain, client),
                    self._analyze_community_opportunities(domain, client),
                    self._analyze_partnership_signals(domain, client),
                    self._analyze_viral_mechanics(domain, client),
                    self._analyze_acquisition_channels(domain, client),
                    self._analyze_retention_signals(domain, client),
                    self._analyze_competitor_channels(domain, competitors, client) if competitors else self._analyze_industry_channels(domain, client)
                ]
                
                analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(analysis_results):
                    if isinstance(result, Exception):
                        logger.error(f"Growth analysis task {i} failed", error=str(result))
                    elif result:
                        # Merge results based on task index
                        if i == 0:  # Social presence
                            results["untapped_channels"].extend(result.get("channels", []))
                        elif i == 1:  # Content strategy
                            results["content_opportunities"] = result.get("opportunities", [])
                        elif i == 2:  # SEO
                            results["keyword_gaps"] = result.get("gaps", [])
                        elif i == 3:  # Referral
                            results["referral_opportunities"] = result.get("opportunities", [])
                        elif i == 4:  # Community
                            results["community_building"] = result.get("opportunities", [])
                        elif i == 5:  # Partnerships
                            results["partnership_opportunities"] = result.get("opportunities", [])
                        elif i == 6:  # Viral
                            results["viral_opportunities"] = result.get("opportunities", [])
                        elif i == 7:  # Acquisition channels
                            results["channel_recommendations"] = result.get("recommendations", [])
                        elif i == 8:  # Retention
                            results["retention_improvements"] = result.get("improvements", [])
                        elif i == 9:  # Competitor/Industry channels
                            results["untapped_channels"].extend(result.get("channels", []))
                
                # Calculate total user potential
                results["total_user_potential"] = self._calculate_user_potential(results)
                
                # Prioritize opportunities by impact
                results = self._prioritize_opportunities(results)
                
            # Cache for 24 hours
            await cache_result(cache_key, results, ttl=86400)
            return results
            
        except Exception as e:
            logger.error(f"Growth opportunities analysis failed for {domain}", error=str(e))
            return results
    
    async def _analyze_social_presence(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze social media presence and identify gaps"""
        channels = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = response.text.lower()
                
                # Check for social media links
                social_platforms = {
                    'twitter': {'found': False, 'url_pattern': 'twitter.com|x.com'},
                    'linkedin': {'found': False, 'url_pattern': 'linkedin.com'},
                    'facebook': {'found': False, 'url_pattern': 'facebook.com'},
                    'instagram': {'found': False, 'url_pattern': 'instagram.com'},
                    'youtube': {'found': False, 'url_pattern': 'youtube.com'},
                    'tiktok': {'found': False, 'url_pattern': 'tiktok.com'},
                    'reddit': {'found': False, 'url_pattern': 'reddit.com'},
                    'discord': {'found': False, 'url_pattern': 'discord.com|discord.gg'},
                    'slack': {'found': False, 'url_pattern': 'slack.com'},
                    'github': {'found': False, 'url_pattern': 'github.com'},
                    'producthunt': {'found': False, 'url_pattern': 'producthunt.com'}
                }
                
                # Find all links
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href'].lower()
                    for platform, info in social_platforms.items():
                        if re.search(info['url_pattern'], href):
                            info['found'] = True
                
                # Reddit opportunity (high-value for B2B)
                if not social_platforms['reddit']['found']:
                    channels.append({
                        "channel": "Reddit",
                        "opportunity": "No Reddit presence detected",
                        "strategy": "Join relevant subreddits and answer questions weekly",
                        "specific_actions": [
                            "Find 3-5 relevant subreddits in your niche",
                            "Answer 2-3 questions per week with helpful content",
                            "Share case studies on Thursdays (highest engagement)",
                            "Create comparison posts: 'YourTool vs Competitor'"
                        ],
                        "expected_users": "800-1500/month",
                        "effort": "2 hours/week",
                        "user_acquisition_potential": 1200
                    })
                
                # LinkedIn opportunity (B2B essential)
                if not social_platforms['linkedin']['found']:
                    channels.append({
                        "channel": "LinkedIn",
                        "opportunity": "Missing LinkedIn company page",
                        "strategy": "Build thought leadership on LinkedIn",
                        "specific_actions": [
                            "Create company page with weekly updates",
                            "CEO/Founder should post 2-3x per week",
                            "Share customer success stories",
                            "Comment on industry posts daily"
                        ],
                        "expected_users": "500-1000/month",
                        "effort": "3 hours/week",
                        "user_acquisition_potential": 750
                    })
                
                # YouTube opportunity (education/demo)
                if not social_platforms['youtube']['found']:
                    channels.append({
                        "channel": "YouTube",
                        "opportunity": "No YouTube channel for demos/tutorials",
                        "strategy": "Create educational content and product demos",
                        "specific_actions": [
                            "Create 5-minute product demo video",
                            "Weekly 'how-to' videos for common use cases",
                            "Comparison videos with competitors",
                            "Customer success story videos"
                        ],
                        "expected_users": "1000-2000/month",
                        "effort": "1 video/week",
                        "user_acquisition_potential": 1500
                    })
                
                # Discord/Slack community
                if not social_platforms['discord']['found'] and not social_platforms['slack']['found']:
                    channels.append({
                        "channel": "Community Platform",
                        "opportunity": "No community platform (Discord/Slack)",
                        "strategy": "Build a community for users and prospects",
                        "specific_actions": [
                            "Launch Discord/Slack community",
                            "Host weekly office hours",
                            "Create channels for support, feedback, announcements",
                            "Incentivize early members with perks"
                        ],
                        "expected_users": "300-500 engaged users",
                        "effort": "5 hours/week initially",
                        "user_acquisition_potential": 400
                    })
                
                # Product Hunt
                if not social_platforms['producthunt']['found']:
                    channels.append({
                        "channel": "Product Hunt",
                        "opportunity": "Haven't launched on Product Hunt",
                        "strategy": "Plan a Product Hunt launch",
                        "specific_actions": [
                            "Build pre-launch email list (500+ hunters)",
                            "Create compelling tagline and description",
                            "Prepare launch day assets (GIFs, videos)",
                            "Coordinate team for launch day support"
                        ],
                        "expected_users": "2000-5000 one-time spike",
                        "effort": "2 weeks preparation",
                        "user_acquisition_potential": 3000
                    })
                
                # GitHub (for developer tools)
                if not social_platforms['github']['found'] and ('api' in content or 'developer' in content or 'sdk' in content):
                    channels.append({
                        "channel": "GitHub",
                        "opportunity": "No GitHub presence for developer audience",
                        "strategy": "Open source parts of your product",
                        "specific_actions": [
                            "Open source SDKs or helper libraries",
                            "Create example projects and templates",
                            "Maintain active README with clear docs",
                            "Engage with developer community"
                        ],
                        "expected_users": "500-1000 developers/month",
                        "effort": "Ongoing maintenance",
                        "user_acquisition_potential": 750
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing social presence", error=str(e))
        
        return {"channels": channels}
    
    async def _analyze_content_strategy(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze content marketing opportunities"""
        opportunities = []
        
        try:
            # Check for blog
            blog_urls = [
                f"https://{domain}/blog",
                f"https://blog.{domain}",
                f"https://{domain}/resources",
                f"https://{domain}/articles"
            ]
            
            has_blog = False
            blog_content = None
            
            for url in blog_urls:
                try:
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        has_blog = True
                        blog_content = response.text
                        break
                except:
                    continue
            
            if not has_blog:
                opportunities.append({
                    "type": "no_blog",
                    "opportunity": "No blog or content hub found",
                    "strategy": "Launch SEO-focused content marketing",
                    "specific_actions": [
                        "Create blog with 10 cornerstone articles",
                        "Target 'how to [solve problem]' keywords",
                        "Write comparison posts for '[competitor] alternative'",
                        "Create ultimate guides for main use cases"
                    ],
                    "expected_traffic": "5000-10000 organic visits/month after 6 months",
                    "effort": "2 articles/week",
                    "user_acquisition_potential": 2000
                })
            else:
                # Analyze blog content
                soup = BeautifulSoup(blog_content, 'html.parser')
                
                # Check for content types
                has_comparisons = 'vs' in blog_content.lower() or 'versus' in blog_content.lower() or 'alternative' in blog_content.lower()
                has_guides = 'guide' in blog_content.lower() or 'how to' in blog_content.lower() or 'tutorial' in blog_content.lower()
                has_case_studies = 'case study' in blog_content.lower() or 'success story' in blog_content.lower()
                
                if not has_comparisons:
                    opportunities.append({
                        "type": "no_comparison_content",
                        "opportunity": "No comparison/alternative content",
                        "strategy": "Create competitor comparison content",
                        "specific_actions": [
                            "Write '[Competitor] vs [YourProduct]' articles",
                            "'Best [Competitor] Alternatives' listicles",
                            "Feature comparison tables",
                            "Migration guides from competitors"
                        ],
                        "expected_traffic": "2000-4000 high-intent visits/month",
                        "effort": "1 comparison article/week",
                        "user_acquisition_potential": 800
                    })
                
                if not has_case_studies:
                    opportunities.append({
                        "type": "no_case_studies",
                        "opportunity": "No customer success stories",
                        "strategy": "Publish customer case studies",
                        "specific_actions": [
                            "Interview 5 successful customers",
                            "Create detailed case studies with metrics",
                            "Include industry, challenge, solution, results",
                            "Add video testimonials"
                        ],
                        "expected_impact": "20-30% improvement in conversion",
                        "effort": "1 case study/month",
                        "user_acquisition_potential": 500
                    })
            
            # Check for resources/tools
            resources_urls = [
                f"https://{domain}/tools",
                f"https://{domain}/resources",
                f"https://{domain}/templates",
                f"https://{domain}/calculators"
            ]
            
            has_tools = False
            for url in resources_urls:
                try:
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        has_tools = True
                        break
                except:
                    continue
            
            if not has_tools:
                opportunities.append({
                    "type": "no_free_tools",
                    "opportunity": "No free tools or calculators",
                    "strategy": "Create free tools for lead generation",
                    "specific_actions": [
                        "Build ROI calculator for your solution",
                        "Create free tier of your product",
                        "Offer templates and checklists",
                        "Build Chrome extension or simple tool"
                    ],
                    "expected_users": "3000-5000 email signups/month",
                    "effort": "1-2 week development",
                    "user_acquisition_potential": 1500
                })
        
        except Exception as e:
            logger.debug(f"Error analyzing content strategy", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_seo_opportunities(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze SEO and keyword opportunities"""
        gaps = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check title and meta description
                title = soup.find('title')
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                
                if title:
                    title_text = title.get_text().lower()
                    
                    # Check for category keywords
                    category_keywords = ['best', 'top', 'review', 'compare', 'alternative', 'vs']
                    has_category = any(keyword in title_text for keyword in category_keywords)
                    
                    if not has_category:
                        gaps.append({
                            "type": "missing_category_keywords",
                            "opportunity": "Not targeting category keywords",
                            "strategy": "Target 'best [category]' keywords",
                            "specific_keywords": [
                                f"best {domain.split('.')[0]} alternative",
                                f"top {domain.split('.')[0]} tools",
                                f"{domain.split('.')[0]} reviews",
                                f"{domain.split('.')[0]} pricing"
                            ],
                            "expected_traffic": "1000-3000 visits/month",
                            "effort": "Create targeted landing pages",
                            "user_acquisition_potential": 600
                        })
                
                # Check for long-tail opportunities
                content = response.text.lower()
                if 'how to' not in content and 'guide' not in content:
                    gaps.append({
                        "type": "missing_how_to_content",
                        "opportunity": "Not targeting 'how to' keywords",
                        "strategy": "Create how-to content",
                        "specific_keywords": [
                            "how to [solve main problem]",
                            "how to choose [product category]",
                            "how to implement [solution]",
                            "[industry] guide to [problem]"
                        ],
                        "expected_traffic": "2000-5000 visits/month",
                        "effort": "10 comprehensive guides",
                        "user_acquisition_potential": 1000
                    })
                
                # Check for local SEO (if applicable)
                if 'enterprise' in content or 'business' in content:
                    if not any(city in content for city in ['new york', 'san francisco', 'london', 'toronto']):
                        gaps.append({
                            "type": "no_local_seo",
                            "opportunity": "Missing local/regional targeting",
                            "strategy": "Create location-specific pages",
                            "specific_actions": [
                                "Create pages for major business hubs",
                                "Target '[solution] for [city] businesses'",
                                "Include local case studies",
                                "Get listed in local directories"
                            ],
                            "expected_traffic": "500-1000 local visits/month",
                            "effort": "5 location pages",
                            "user_acquisition_potential": 300
                        })
        
        except Exception as e:
            logger.debug(f"Error analyzing SEO opportunities", error=str(e))
        
        return {"gaps": gaps}
    
    async def _analyze_referral_potential(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze referral program opportunities"""
        opportunities = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for existing referral program
                referral_indicators = ['referral', 'refer a friend', 'refer and earn', 'invitation', 'invite']
                has_referral = any(indicator in content for indicator in referral_indicators)
                
                if not has_referral:
                    opportunities.append({
                        "type": "no_referral_program",
                        "opportunity": "No referral program found",
                        "strategy": "Launch customer referral program",
                        "implementation": {
                            "advocate_incentive": "1 month free for each referral",
                            "friend_incentive": "20% off first 3 months",
                            "tracking": "Use ReferralCandy or build simple tracking",
                            "promotion": "Email to existing customers + in-app banner"
                        },
                        "expected_growth": "15-25% of new customers from referrals",
                        "effort": "1 week setup + ongoing management",
                        "user_acquisition_potential": 800
                    })
                
                # Check for affiliate program
                affiliate_indicators = ['affiliate', 'partner program', 'reseller', 'commission']
                has_affiliate = any(indicator in content for indicator in affiliate_indicators)
                
                if not has_affiliate:
                    opportunities.append({
                        "type": "no_affiliate_program",
                        "opportunity": "No affiliate/partner program",
                        "strategy": "Launch affiliate program",
                        "implementation": {
                            "commission": "20-30% recurring commission",
                            "targets": "Industry influencers, consultants, agencies",
                            "tools": "Post Affiliate Pro or Rewardful",
                            "recruitment": "Reach out to 50 potential affiliates"
                        },
                        "expected_growth": "10-20% of revenue from affiliates",
                        "effort": "2 weeks setup + recruitment",
                        "user_acquisition_potential": 600
                    })
                
                # Check for social sharing
                share_indicators = ['share', 'tweet', 'linkedin', 'facebook']
                has_sharing = any(indicator in content for indicator in share_indicators)
                
                if not has_sharing:
                    opportunities.append({
                        "type": "no_social_sharing",
                        "opportunity": "No social sharing features",
                        "strategy": "Add viral sharing mechanics",
                        "implementation": {
                            "share_buttons": "Add to key pages and blog posts",
                            "incentivized_sharing": "Unlock features by sharing",
                            "social_proof": "Show '1,234 people shared this'",
                            "click_to_tweet": "Pre-written tweets for key stats"
                        },
                        "expected_growth": "5-10% traffic increase",
                        "effort": "1 day implementation",
                        "user_acquisition_potential": 300
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing referral potential", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_community_opportunities(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze community building opportunities"""
        opportunities = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for community indicators
                community_indicators = ['community', 'forum', 'discord', 'slack', 'discussion']
                has_community = any(indicator in content for indicator in community_indicators)
                
                if not has_community:
                    opportunities.append({
                        "type": "no_community",
                        "opportunity": "No user community detected",
                        "strategy": "Build engaged user community",
                        "implementation": {
                            "platform": "Discord or Slack (based on audience)",
                            "structure": {
                                "channels": ["general", "support", "feature-requests", "showcase"],
                                "events": "Weekly office hours, monthly demos",
                                "incentives": "Community-only features, early access",
                                "moderation": "Hire community manager or use power users"
                            },
                            "launch_strategy": [
                                "Invite top 100 customers first",
                                "Offer exclusive perks for early members",
                                "Host launch event with product team",
                                "Create community guidelines and culture"
                            ]
                        },
                        "expected_impact": "30% reduction in support tickets, 20% increase in retention",
                        "effort": "2 weeks setup + ongoing management",
                        "user_acquisition_potential": 500
                    })
                
                # Check for user-generated content
                ugc_indicators = ['showcase', 'gallery', 'examples', 'templates', 'made with']
                has_ugc = any(indicator in content for indicator in ugc_indicators)
                
                if not has_ugc:
                    opportunities.append({
                        "type": "no_user_generated_content",
                        "opportunity": "No user showcase or examples",
                        "strategy": "Enable user-generated content",
                        "implementation": {
                            "showcase_page": "Create 'Made with [Product]' gallery",
                            "template_library": "User-submitted templates",
                            "case_studies": "User success stories",
                            "incentives": "Feature users, give credits/rewards"
                        },
                        "expected_impact": "Increased social proof and organic reach",
                        "effort": "1 week development",
                        "user_acquisition_potential": 400
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing community opportunities", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_partnership_signals(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Identify partnership and integration opportunities"""
        opportunities = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for integrations
                integration_indicators = ['integrate', 'integration', 'connect', 'sync', 'api', 'webhook', 'zapier']
                has_integrations = any(indicator in content for indicator in integration_indicators)
                
                if not has_integrations:
                    opportunities.append({
                        "type": "no_integrations",
                        "opportunity": "Limited integration ecosystem",
                        "strategy": "Build strategic integrations",
                        "implementation": {
                            "priority_integrations": [
                                "Zapier (opens 5000+ integrations)",
                                "Slack (if B2B)",
                                "Google Workspace",
                                "Microsoft 365"
                            ],
                            "partnership_approach": [
                                "Apply for integration partner programs",
                                "Co-marketing with integration partners",
                                "Joint webinars and content",
                                "Featured in partner marketplaces"
                            ]
                        },
                        "expected_impact": "20-30% increase in enterprise adoption",
                        "effort": "2-4 weeks per integration",
                        "user_acquisition_potential": 1000
                    })
                
                # Check for technology partners
                if 'partners' not in content or 'partnership' not in content:
                    opportunities.append({
                        "type": "no_partner_ecosystem",
                        "opportunity": "No visible partner ecosystem",
                        "strategy": "Build technology partner network",
                        "implementation": {
                            "partner_types": [
                                "Technology partners (complementary tools)",
                                "Service partners (agencies, consultants)",
                                "Reseller partners (VARs)",
                                "OEM partners (white-label)"
                            ],
                            "partner_benefits": {
                                "revenue_share": "20-30% of referred revenue",
                                "co_marketing": "Joint campaigns and content",
                                "training": "Partner certification program",
                                "support": "Dedicated partner success manager"
                            }
                        },
                        "expected_impact": "30-40% of revenue from partners within 12 months",
                        "effort": "3 months to build program",
                        "user_acquisition_potential": 1500
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing partnership signals", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_viral_mechanics(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze potential for viral growth mechanics"""
        opportunities = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for viral loops
                viral_indicators = ['invite', 'share', 'collaborate', 'team', 'workspace']
                has_viral_loop = any(indicator in content for indicator in viral_indicators)
                
                if not has_viral_loop:
                    opportunities.append({
                        "type": "no_viral_loop",
                        "opportunity": "No built-in viral mechanics",
                        "strategy": "Add collaborative features for viral growth",
                        "implementation": {
                            "collaboration_features": [
                                "Shared workspaces/projects",
                                "Guest access for clients",
                                "Team invitations",
                                "Public sharing links"
                            ],
                            "viral_triggers": [
                                "'Powered by' branding on shared content",
                                "Limit features unless users invite others",
                                "Network effects (better with more users)",
                                "Social proof notifications"
                            ]
                        },
                        "expected_k_factor": "1.2-1.5 (20-50% viral growth)",
                        "effort": "4-6 weeks development",
                        "user_acquisition_potential": 2000
                    })
                
                # Check for freemium
                freemium_indicators = ['free plan', 'free tier', 'free forever', 'start free']
                has_freemium = any(indicator in content for indicator in freemium_indicators)
                
                if not has_freemium:
                    opportunities.append({
                        "type": "no_freemium",
                        "opportunity": "No freemium offering",
                        "strategy": "Launch strategic freemium tier",
                        "implementation": {
                            "freemium_limits": [
                                "Limited usage (e.g., 100 actions/month)",
                                "Limited features (core only)",
                                "Limited users (1-2 users)",
                                "'Powered by' branding"
                            ],
                            "conversion_strategy": [
                                "In-app upgrade prompts at limits",
                                "Email nurture campaigns",
                                "Feature teasers",
                                "Time-limited premium trials"
                            ]
                        },
                        "expected_conversion": "2-5% freemium to paid",
                        "effort": "2-4 weeks to implement",
                        "user_acquisition_potential": 3000
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing viral mechanics", error=str(e))
        
        return {"opportunities": opportunities}
    
    async def _analyze_acquisition_channels(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze and recommend acquisition channels"""
        recommendations = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Determine product type and recommend channels
                is_b2b = any(term in content for term in ['enterprise', 'business', 'team', 'organization', 'company'])
                is_developer = any(term in content for term in ['api', 'developer', 'sdk', 'documentation', 'github'])
                is_saas = any(term in content for term in ['subscription', 'monthly', 'trial', 'pricing'])
                
                if is_b2b:
                    recommendations.append({
                        "channel": "LinkedIn Outbound",
                        "strategy": "Targeted LinkedIn outreach",
                        "tactics": [
                            "Sales Navigator for prospect identification",
                            "Personalized connection requests",
                            "Value-first messaging (share relevant content)",
                            "Book 15-minute discovery calls"
                        ],
                        "expected_results": "10-15% response rate, 2-3% conversion",
                        "budget": "$99/month for Sales Navigator",
                        "user_acquisition_potential": 200
                    })
                    
                    recommendations.append({
                        "channel": "Cold Email",
                        "strategy": "Targeted cold email campaigns",
                        "tactics": [
                            "Use Apollo.io or Hunter.io for emails",
                            "Segment by industry and company size",
                            "A/B test subject lines",
                            "Follow up 3-4 times"
                        ],
                        "expected_results": "1-3% response rate, 0.5-1% conversion",
                        "budget": "$49-199/month for tools",
                        "user_acquisition_potential": 150
                    })
                
                if is_developer:
                    recommendations.append({
                        "channel": "Developer Communities",
                        "strategy": "Engage in developer forums",
                        "tactics": [
                            "Answer questions on Stack Overflow",
                            "Contribute to GitHub discussions",
                            "Write technical tutorials on Dev.to",
                            "Sponsor developer newsletters"
                        ],
                        "expected_results": "500-1000 developer eyes/month",
                        "budget": "$0-500/month for sponsorships",
                        "user_acquisition_potential": 300
                    })
                
                if is_saas:
                    recommendations.append({
                        "channel": "AppSumo/LTD Sites",
                        "strategy": "Lifetime deal launch",
                        "tactics": [
                            "Apply to AppSumo with compelling offer",
                            "Prepare for high-volume support",
                            "Use LTD buyers for testimonials",
                            "Upsell to recurring plans later"
                        ],
                        "expected_results": "1000-5000 customers",
                        "budget": "30-40% revenue share",
                        "user_acquisition_potential": 2000
                    })
                
                # Universal recommendations
                recommendations.append({
                    "channel": "Podcast Guesting",
                    "strategy": "Appear on industry podcasts",
                    "tactics": [
                        "Use PodcastGuests.com to find opportunities",
                        "Pitch unique angle or story",
                        "Prepare 3-5 key talking points",
                        "Offer exclusive discount for listeners"
                    ],
                    "expected_results": "100-500 qualified leads per appearance",
                    "budget": "$0 (time investment only)",
                    "user_acquisition_potential": 400
                })
        
        except Exception as e:
            logger.debug(f"Error analyzing acquisition channels", error=str(e))
        
        return {"recommendations": recommendations}
    
    async def _analyze_retention_signals(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze retention and engagement improvement opportunities"""
        improvements = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for onboarding
                onboarding_indicators = ['onboarding', 'getting started', 'setup', 'welcome', 'tour']
                has_onboarding = any(indicator in content for indicator in onboarding_indicators)
                
                if not has_onboarding:
                    improvements.append({
                        "type": "no_onboarding",
                        "opportunity": "No visible onboarding process",
                        "strategy": "Build guided onboarding flow",
                        "implementation": {
                            "onboarding_elements": [
                                "Welcome email series (5 emails over 14 days)",
                                "In-app product tour",
                                "Progress checklist",
                                "Quick win in first 5 minutes"
                            ],
                            "activation_metrics": [
                                "Define key activation event",
                                "Track time to first value",
                                "Monitor 7-day and 30-day retention",
                                "A/B test onboarding variations"
                            ]
                        },
                        "expected_impact": "40-60% improvement in activation rate",
                        "effort": "2 weeks implementation",
                        "retention_impact": 35
                    })
                
                # Check for education
                education_indicators = ['academy', 'university', 'certification', 'course', 'training']
                has_education = any(indicator in content for indicator in education_indicators)
                
                if not has_education:
                    improvements.append({
                        "type": "no_education_program",
                        "opportunity": "No user education program",
                        "strategy": "Create customer education content",
                        "implementation": {
                            "education_content": [
                                "Video tutorial library",
                                "Best practices guide",
                                "Certification program",
                                "Monthly webinars"
                            ],
                            "benefits": [
                                "Reduced support tickets",
                                "Increased feature adoption",
                                "Higher customer lifetime value",
                                "Community building"
                            ]
                        },
                        "expected_impact": "25% reduction in churn",
                        "effort": "Ongoing content creation",
                        "retention_impact": 25
                    })
                
                # Check for customer success
                cs_indicators = ['customer success', 'account manager', 'dedicated support']
                has_cs = any(indicator in content for indicator in cs_indicators)
                
                if not has_cs:
                    improvements.append({
                        "type": "no_customer_success",
                        "opportunity": "No proactive customer success",
                        "strategy": "Implement customer success program",
                        "implementation": {
                            "cs_activities": [
                                "Quarterly business reviews",
                                "Usage monitoring and alerts",
                                "Proactive check-ins",
                                "Success planning"
                            ],
                            "automation": [
                                "Health score tracking",
                                "Automated re-engagement campaigns",
                                "Usage-based tips and suggestions",
                                "Milestone celebrations"
                            ]
                        },
                        "expected_impact": "30% reduction in churn for key accounts",
                        "effort": "Hire CS manager or automate",
                        "retention_impact": 30
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing retention signals", error=str(e))
        
        return {"improvements": improvements}
    
    async def _analyze_competitor_channels(self, domain: str, competitors: List[str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze competitor acquisition channels"""
        channels = []
        
        if not competitors:
            return {"channels": channels}
        
        try:
            # Analyze each competitor
            for competitor_domain in competitors[:3]:  # Limit to top 3
                try:
                    response = await client.get(f"https://{competitor_domain}", follow_redirects=True)
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # Check what channels they're using
                        if 'product hunt' in content:
                            channels.append({
                                "channel": "Product Hunt",
                                "competitor_using": competitor_domain,
                                "opportunity": f"{competitor_domain} launched on Product Hunt",
                                "strategy": "Plan your own Product Hunt launch",
                                "user_acquisition_potential": 2000
                            })
                        
                        if 'app store' in content or 'google play' in content:
                            channels.append({
                                "channel": "Mobile App Stores",
                                "competitor_using": competitor_domain,
                                "opportunity": f"{competitor_domain} has mobile apps",
                                "strategy": "Consider mobile app development",
                                "user_acquisition_potential": 1500
                            })
                        
                        if 'chrome extension' in content or 'browser extension' in content:
                            channels.append({
                                "channel": "Browser Extension",
                                "competitor_using": competitor_domain,
                                "opportunity": f"{competitor_domain} has browser extension",
                                "strategy": "Build complementary browser extension",
                                "user_acquisition_potential": 1000
                            })
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Error analyzing competitor channels", error=str(e))
        
        return {"channels": channels}
    
    async def _analyze_industry_channels(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Analyze industry-specific growth channels"""
        channels = []
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Industry-specific recommendations
                if 'ecommerce' in content or 'shopify' in content or 'store' in content:
                    channels.append({
                        "channel": "Shopify App Store",
                        "opportunity": "List in Shopify App Store",
                        "strategy": "Build Shopify app integration",
                        "expected_users": "500-2000/month from app store",
                        "user_acquisition_potential": 1000
                    })
                
                if 'marketing' in content or 'analytics' in content:
                    channels.append({
                        "channel": "Marketing Communities",
                        "opportunity": "Engage in marketing communities",
                        "strategy": "Be active in GrowthHackers, Indiehackers",
                        "expected_users": "200-500/month",
                        "user_acquisition_potential": 350
                    })
                
                if 'sales' in content or 'crm' in content:
                    channels.append({
                        "channel": "Sales Communities",
                        "opportunity": "Target sales professionals",
                        "strategy": "Engage in Sales Hacker, RevGenius communities",
                        "expected_users": "300-600/month",
                        "user_acquisition_potential": 450
                    })
        
        except Exception as e:
            logger.debug(f"Error analyzing industry channels", error=str(e))
        
        return {"channels": channels}
    
    def _calculate_user_potential(self, results: Dict[str, Any]) -> int:
        """Calculate total user acquisition potential"""
        total = 0
        
        # Sum up all user acquisition potentials
        for category in results.values():
            if isinstance(category, list):
                for item in category:
                    if isinstance(item, dict):
                        total += item.get('user_acquisition_potential', 0)
        
        return total
    
    def _prioritize_opportunities(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize opportunities by impact and effort"""
        
        # Collect all opportunities with their effort scores
        all_opportunities = []
        
        for key, value in results.items():
            if isinstance(value, list) and key != "acquisition_cost_reduction":
                for item in value:
                    if isinstance(item, dict):
                        # Calculate effort score (lower is better)
                        effort = item.get('effort', '')
                        if 'day' in str(effort) or 'hour' in str(effort):
                            effort_score = 1
                        elif 'week' in str(effort):
                            effort_score = 2
                        elif 'month' in str(effort):
                            effort_score = 3
                        else:
                            effort_score = 4
                        
                        # Calculate impact score
                        impact = item.get('user_acquisition_potential', 0)
                        
                        # Priority score (high impact, low effort = high priority)
                        priority = impact / effort_score
                        
                        item['priority_score'] = priority
                        all_opportunities.append({
                            'category': key,
                            'item': item
                        })
        
        # Sort by priority
        all_opportunities.sort(key=lambda x: x['item'].get('priority_score', 0), reverse=True)
        
        # Add top 5 to quick wins
        results['quick_wins'] = [opp['item'] for opp in all_opportunities[:5]]
        
        return results