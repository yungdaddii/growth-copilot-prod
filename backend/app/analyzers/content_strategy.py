import httpx
import re
from typing import Dict, Any, List, Optional, Set
from bs4 import BeautifulSoup
import structlog
from collections import Counter
from urllib.parse import urljoin, urlparse

from app.config import settings
from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class ContentStrategyAnalyzer:
    """
    AI-powered content strategy generator that identifies content gaps,
    suggests content pillars, and provides specific topic recommendations.
    """
    
    # Content types to identify
    CONTENT_TYPES = {
        "educational": ["how to", "guide", "tutorial", "learn", "understand"],
        "comparison": ["vs", "versus", "compare", "alternative", "better than"],
        "listicle": ["best", "top", "list", "tools", "tips", "ways"],
        "case_study": ["case study", "success story", "customer story", "example"],
        "thought_leadership": ["future", "trends", "insights", "opinion", "why"],
        "product": ["features", "pricing", "demo", "tour", "product"],
        "faq": ["faq", "questions", "answers", "q&a", "asked"]
    }
    
    # Buyer journey stages
    BUYER_STAGES = {
        "awareness": ["what is", "how to", "guide", "tutorial", "learn"],
        "consideration": ["vs", "compare", "best", "review", "alternative"],
        "decision": ["pricing", "demo", "trial", "implementation", "roi"]
    }
    
    def __init__(self):
        self.client = None
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze(self, domain: str, competitor_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """Comprehensive content strategy analysis"""
        cache_key = f"content_strategy:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "current_content": {},
            "content_gaps": [],
            "content_pillars": [],
            "topic_recommendations": [],
            "competitor_content": {},
            "content_score": 0,
            "buyer_journey_coverage": {},
            "content_opportunities": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                self.client = client
                
                # Analyze current content
                current_content = await self._analyze_current_content(domain)
                results["current_content"] = current_content
                
                # Analyze competitor content if provided
                if competitor_domains:
                    competitor_content = await self._analyze_competitor_content(competitor_domains[:3])
                    results["competitor_content"] = competitor_content
                    
                    # Identify content gaps
                    results["content_gaps"] = self._identify_content_gaps(
                        current_content,
                        competitor_content
                    )
                
                # Generate content pillars based on business focus
                results["content_pillars"] = await self._generate_content_pillars(
                    domain,
                    current_content
                )
                
                # Generate specific topic recommendations
                results["topic_recommendations"] = await self._generate_topic_recommendations(
                    domain,
                    current_content,
                    results["content_gaps"]
                )
                
                # Analyze buyer journey coverage
                results["buyer_journey_coverage"] = self._analyze_buyer_journey(current_content)
                
                # Calculate content score
                results["content_score"] = self._calculate_content_score(current_content, results)
                
                # Generate opportunities
                results["content_opportunities"] = self._generate_opportunities(results)
                
            await cache_result(cache_key, results, ttl=86400)
            
        except Exception as e:
            logger.error(f"Content strategy analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _analyze_current_content(self, domain: str) -> Dict[str, Any]:
        """Analyze existing content on the website"""
        content_analysis = {
            "total_pages": 0,
            "blog_posts": 0,
            "content_types": {},
            "topics_covered": [],
            "content_depth": 0,
            "update_frequency": "unknown",
            "seo_optimized": False,
            "has_blog": False,
            "has_resources": False,
            "content_formats": []
        }
        
        try:
            # Check for blog/resources section
            blog_urls = [
                f"https://{domain}/blog",
                f"https://{domain}/resources",
                f"https://{domain}/articles",
                f"https://{domain}/insights"
            ]
            
            blog_found = False
            all_posts = []
            
            for blog_url in blog_urls:
                try:
                    response = await self.client.get(blog_url)
                    if response.status_code == 200:
                        blog_found = True
                        content_analysis["has_blog"] = True
                        
                        soup = BeautifulSoup(response.text, 'lxml')
                        
                        # Find blog posts
                        posts = self._extract_blog_posts(soup)
                        all_posts.extend(posts)
                        
                        # Analyze content types
                        for post in posts:
                            content_type = self._identify_content_type(post["title"])
                            if content_type:
                                content_analysis["content_types"][content_type] = \
                                    content_analysis["content_types"].get(content_type, 0) + 1
                        
                        break
                except:
                    continue
            
            content_analysis["blog_posts"] = len(all_posts)
            
            # Extract topics from post titles
            if all_posts:
                topics = self._extract_topics(all_posts)
                content_analysis["topics_covered"] = topics[:20]  # Top 20 topics
            
            # Check homepage for content depth
            homepage_response = await self.client.get(f"https://{domain}")
            homepage_soup = BeautifulSoup(homepage_response.text, 'lxml')
            
            # Calculate content depth
            text_content = homepage_soup.get_text()
            word_count = len(text_content.split())
            content_analysis["content_depth"] = word_count
            
            # Check for different content formats
            if homepage_soup.find(['video', 'iframe']):
                content_analysis["content_formats"].append("video")
            if homepage_soup.find('img', alt=re.compile(r'infographic|chart|graph', re.I)):
                content_analysis["content_formats"].append("infographic")
            if 'podcast' in homepage_response.text.lower():
                content_analysis["content_formats"].append("podcast")
            if 'webinar' in homepage_response.text.lower():
                content_analysis["content_formats"].append("webinar")
            if 'ebook' in homepage_response.text.lower() or 'whitepaper' in homepage_response.text.lower():
                content_analysis["content_formats"].append("ebook")
            
            # Check for resources section
            if 'resources' in homepage_response.text.lower() or 'library' in homepage_response.text.lower():
                content_analysis["has_resources"] = True
            
            # SEO optimization check
            meta_description = homepage_soup.find('meta', attrs={'name': 'description'})
            title_tag = homepage_soup.find('title')
            h1_tags = homepage_soup.find_all('h1')
            
            if meta_description and title_tag and h1_tags:
                content_analysis["seo_optimized"] = True
            
        except Exception as e:
            logger.error(f"Failed to analyze current content for {domain}", error=str(e))
        
        return content_analysis
    
    def _extract_blog_posts(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract blog post information from a blog page"""
        posts = []
        
        # Common patterns for blog post containers
        article_selectors = [
            'article',
            '.post',
            '.blog-post',
            '.article',
            '[class*="post"]',
            '[class*="article"]'
        ]
        
        for selector in article_selectors:
            articles = soup.select(selector)
            if articles:
                for article in articles[:20]:  # Limit to 20 posts
                    post = {}
                    
                    # Find title
                    title = article.find(['h2', 'h3', 'h4', 'a'])
                    if title:
                        post["title"] = title.get_text(strip=True)
                    
                    # Find link
                    link = article.find('a', href=True)
                    if link:
                        post["url"] = link['href']
                    
                    # Find date
                    date = article.find(['time', '.date', '.published'])
                    if date:
                        post["date"] = date.get_text(strip=True)
                    
                    if post.get("title"):
                        posts.append(post)
                
                break
        
        return posts
    
    def _identify_content_type(self, title: str) -> Optional[str]:
        """Identify the content type from title"""
        title_lower = title.lower()
        
        for content_type, keywords in self.CONTENT_TYPES.items():
            if any(keyword in title_lower for keyword in keywords):
                return content_type
        
        return None
    
    def _extract_topics(self, posts: List[Dict]) -> List[str]:
        """Extract main topics from blog posts"""
        # Extract significant words from titles
        all_words = []
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been'}
        
        for post in posts:
            title = post.get("title", "").lower()
            words = re.findall(r'\b[a-z]{4,}\b', title)
            words = [w for w in words if w not in stop_words]
            all_words.extend(words)
        
        # Count frequency
        word_counts = Counter(all_words)
        
        # Return most common topics
        return [word for word, count in word_counts.most_common(20)]
    
    async def _analyze_competitor_content(self, competitor_domains: List[str]) -> Dict[str, Any]:
        """Analyze competitor content strategies"""
        competitor_content = {}
        
        for domain in competitor_domains:
            try:
                content = await self._analyze_current_content(domain)
                competitor_content[domain] = content
            except:
                continue
        
        return competitor_content
    
    def _identify_content_gaps(self, current: Dict, competitors: Dict) -> List[Dict[str, Any]]:
        """Identify content gaps compared to competitors"""
        gaps = []
        
        # Aggregate competitor topics
        competitor_topics = set()
        competitor_content_types = Counter()
        
        for domain, content in competitors.items():
            competitor_topics.update(content.get("topics_covered", []))
            for content_type, count in content.get("content_types", {}).items():
                competitor_content_types[content_type] += count
        
        # Current topics
        current_topics = set(current.get("topics_covered", []))
        current_types = current.get("content_types", {})
        
        # Topic gaps
        missing_topics = competitor_topics - current_topics
        if missing_topics:
            gaps.append({
                "type": "topic_gap",
                "description": "Topics competitors cover that you don't",
                "items": list(missing_topics)[:10],
                "priority": "high",
                "impact": "Capture organic traffic for these keywords"
            })
        
        # Content type gaps
        for content_type, count in competitor_content_types.items():
            if current_types.get(content_type, 0) < count / len(competitors):
                gaps.append({
                    "type": "content_type_gap",
                    "description": f"Less {content_type} content than competitors",
                    "recommendation": f"Create more {content_type} content",
                    "priority": "medium",
                    "impact": "Match competitor content diversity"
                })
        
        # Volume gap
        avg_competitor_posts = sum(c.get("blog_posts", 0) for c in competitors.values()) / max(len(competitors), 1)
        if current.get("blog_posts", 0) < avg_competitor_posts * 0.5:
            gaps.append({
                "type": "volume_gap",
                "description": f"You have {current.get('blog_posts', 0)} posts vs competitor avg of {avg_competitor_posts:.0f}",
                "recommendation": "Increase content production frequency",
                "priority": "high",
                "impact": "Build domain authority through consistent publishing"
            })
        
        # Format gaps
        if "video" not in current.get("content_formats", []) and \
           any("video" in c.get("content_formats", []) for c in competitors.values()):
            gaps.append({
                "type": "format_gap",
                "description": "No video content (competitors have videos)",
                "recommendation": "Create product demo videos and tutorials",
                "priority": "medium",
                "impact": "88% longer time on site with video"
            })
        
        return gaps
    
    async def _generate_content_pillars(self, domain: str, current_content: Dict) -> List[Dict[str, Any]]:
        """Generate content pillar recommendations using AI"""
        pillars = []
        
        if self.openai_client:
            try:
                # Get homepage content for context
                response = await self.client.get(f"https://{domain}")
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Extract key information
                title = soup.find('title').get_text() if soup.find('title') else ""
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content') if meta_desc else ""
                h1 = soup.find('h1').get_text() if soup.find('h1') else ""
                
                prompt = f"""Based on this company:
                Domain: {domain}
                Title: {title}
                Description: {description}
                Headline: {h1}
                Current topics: {', '.join(current_content.get('topics_covered', [])[:10])}
                
                Generate 4 content pillars (main topic categories) for their content strategy.
                Each pillar should:
                1. Align with their business goals
                2. Appeal to their target audience
                3. Support SEO and thought leadership
                
                Format each as:
                Pillar Name | Description | Example Topics (3) | Target Audience | Business Goal
                """
                
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=400
                )
                
                # Parse AI response
                lines = response.choices[0].message.content.split('\n')
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            pillars.append({
                                "name": parts[0].strip(),
                                "description": parts[1].strip(),
                                "example_topics": parts[2].strip(),
                                "target_audience": parts[3].strip(),
                                "business_goal": parts[4].strip()
                            })
                
            except Exception as e:
                logger.error(f"Failed to generate content pillars using AI", error=str(e))
        
        # Fallback pillars if AI fails
        if not pillars:
            pillars = [
                {
                    "name": "Product Education",
                    "description": "How-to guides and tutorials",
                    "example_topics": "Getting started, Best practices, Advanced features",
                    "target_audience": "Current and potential users",
                    "business_goal": "Reduce support tickets, improve onboarding"
                },
                {
                    "name": "Industry Insights",
                    "description": "Trends and thought leadership",
                    "example_topics": "Market trends, Future predictions, Industry analysis",
                    "target_audience": "Decision makers",
                    "business_goal": "Build authority and trust"
                },
                {
                    "name": "Customer Success",
                    "description": "Case studies and success stories",
                    "example_topics": "Customer stories, ROI examples, Implementation guides",
                    "target_audience": "Evaluating buyers",
                    "business_goal": "Social proof and conversion"
                },
                {
                    "name": "Comparison Content",
                    "description": "Alternatives and comparisons",
                    "example_topics": "Vs competitors, Build vs buy, Feature comparisons",
                    "target_audience": "Consideration stage buyers",
                    "business_goal": "Win competitive deals"
                }
            ]
        
        return pillars[:4]  # Return top 4 pillars
    
    async def _generate_topic_recommendations(self, domain: str, current_content: Dict, gaps: List[Dict]) -> List[Dict[str, Any]]:
        """Generate specific topic recommendations"""
        recommendations = []
        
        # High-intent topics (decision stage)
        recommendations.append({
            "topic": f"{domain.split('.')[0]} vs [competitor]",
            "type": "comparison",
            "stage": "decision",
            "priority": "critical",
            "estimated_impact": "Capture buyers comparing solutions",
            "format": "Detailed comparison page with matrix"
        })
        
        recommendations.append({
            "topic": f"{domain.split('.')[0]} pricing guide",
            "type": "educational",
            "stage": "decision",
            "priority": "high",
            "estimated_impact": "Address pricing questions upfront",
            "format": "Interactive pricing calculator"
        })
        
        # Middle funnel topics (consideration)
        recommendations.append({
            "topic": f"Complete guide to [your solution category]",
            "type": "educational",
            "stage": "consideration",
            "priority": "high",
            "estimated_impact": "Rank for category terms",
            "format": "10,000+ word ultimate guide"
        })
        
        recommendations.append({
            "topic": "ROI calculator for [your solution]",
            "type": "tool",
            "stage": "consideration",
            "priority": "high",
            "estimated_impact": "Help justify purchase decision",
            "format": "Interactive calculator tool"
        })
        
        # Top funnel topics (awareness)
        recommendations.append({
            "topic": "What is [problem you solve]?",
            "type": "educational",
            "stage": "awareness",
            "priority": "medium",
            "estimated_impact": "Capture problem-aware searchers",
            "format": "SEO-optimized blog post"
        })
        
        # Gap-based recommendations
        if gaps:
            for gap in gaps[:2]:
                if gap["type"] == "topic_gap" and gap.get("items"):
                    recommendations.append({
                        "topic": gap["items"][0],
                        "type": "gap_fill",
                        "stage": "various",
                        "priority": "high",
                        "estimated_impact": "Match competitor coverage",
                        "format": "Blog post or guide"
                    })
        
        # AI/Future-focused content
        recommendations.append({
            "topic": f"How AI is changing [your industry]",
            "type": "thought_leadership",
            "stage": "awareness",
            "priority": "medium",
            "estimated_impact": "Position as innovative leader",
            "format": "Research report with data"
        })
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _analyze_buyer_journey(self, current_content: Dict) -> Dict[str, Any]:
        """Analyze content coverage across buyer journey stages"""
        journey_coverage = {
            "awareness": 0,
            "consideration": 0,
            "decision": 0,
            "gaps": []
        }
        
        content_types = current_content.get("content_types", {})
        
        # Map content types to journey stages
        journey_coverage["awareness"] = content_types.get("educational", 0) + content_types.get("thought_leadership", 0)
        journey_coverage["consideration"] = content_types.get("comparison", 0) + content_types.get("listicle", 0)
        journey_coverage["decision"] = content_types.get("case_study", 0) + content_types.get("product", 0)
        
        # Identify gaps
        total = sum([journey_coverage["awareness"], journey_coverage["consideration"], journey_coverage["decision"]])
        
        if total > 0:
            if journey_coverage["awareness"] / total < 0.4:
                journey_coverage["gaps"].append("Need more top-funnel awareness content")
            if journey_coverage["consideration"] / total < 0.3:
                journey_coverage["gaps"].append("Need more comparison and evaluation content")
            if journey_coverage["decision"] / total < 0.2:
                journey_coverage["gaps"].append("Need more case studies and ROI content")
        else:
            journey_coverage["gaps"].append("No content found across buyer journey")
        
        return journey_coverage
    
    def _calculate_content_score(self, current_content: Dict, results: Dict) -> int:
        """Calculate overall content strategy score"""
        score = 0
        
        # Has blog (20 points)
        if current_content.get("has_blog"):
            score += 20
        
        # Content volume (20 points)
        posts = current_content.get("blog_posts", 0)
        if posts >= 50:
            score += 20
        elif posts >= 20:
            score += 15
        elif posts >= 10:
            score += 10
        elif posts > 0:
            score += 5
        
        # Content diversity (20 points)
        content_types = len(current_content.get("content_types", {}))
        if content_types >= 4:
            score += 20
        elif content_types >= 2:
            score += 10
        
        # Content formats (15 points)
        formats = len(current_content.get("content_formats", []))
        score += min(formats * 5, 15)
        
        # SEO optimization (10 points)
        if current_content.get("seo_optimized"):
            score += 10
        
        # Buyer journey coverage (15 points)
        journey = results.get("buyer_journey_coverage", {})
        if not journey.get("gaps"):
            score += 15
        elif len(journey.get("gaps", [])) == 1:
            score += 10
        elif len(journey.get("gaps", [])) == 2:
            score += 5
        
        return min(score, 100)
    
    def _generate_opportunities(self, results: Dict) -> List[Dict[str, Any]]:
        """Generate content opportunities based on analysis"""
        opportunities = []
        
        # Blog opportunity
        if not results["current_content"].get("has_blog"):
            opportunities.append({
                "type": "foundation",
                "opportunity": "Launch company blog",
                "impact": "Build organic traffic and thought leadership",
                "effort": "Medium",
                "priority": "critical",
                "next_steps": "Start with 10 cornerstone pieces"
            })
        
        # Volume opportunity
        if results["current_content"].get("blog_posts", 0) < 20:
            opportunities.append({
                "type": "consistency",
                "opportunity": "Increase publishing frequency",
                "impact": "Build domain authority faster",
                "effort": "Medium",
                "priority": "high",
                "next_steps": "Publish 2-4 posts per month minimum"
            })
        
        # Format opportunities
        if "video" not in results["current_content"].get("content_formats", []):
            opportunities.append({
                "type": "format",
                "opportunity": "Add video content",
                "impact": "88% longer time on site",
                "effort": "Medium",
                "priority": "medium",
                "next_steps": "Start with product demo video"
            })
        
        # Gap opportunities
        for gap in results.get("content_gaps", [])[:2]:
            opportunities.append({
                "type": "competitive",
                "opportunity": gap.get("description"),
                "impact": gap.get("impact"),
                "effort": "Low-Medium",
                "priority": gap.get("priority"),
                "next_steps": gap.get("recommendation")
            })
        
        return opportunities