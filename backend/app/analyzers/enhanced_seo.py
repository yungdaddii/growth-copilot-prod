"""
Enhanced SEO Analyzer with Advanced Intelligence
Provides deep, actionable SEO insights with keyword analysis, 
content optimization, and competitive intelligence.
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import structlog
from bs4 import BeautifulSoup
import re
from collections import Counter
import json
from urllib.parse import urlparse, urljoin
import hashlib

from app.utils.cache import cache_result, get_cached_result
from app.config import settings

logger = structlog.get_logger()


class EnhancedSEOAnalyzer:
    def __init__(self):
        self.ai_crawlers = [
            'GPTBot', 'ChatGPT-User', 'CCBot', 'Claude-Web', 
            'PerplexityBot', 'Bingbot', 'Googlebot', 'FacebookBot'
        ]
        
        # Industry-specific keyword modifiers
        self.industry_keywords = {
            'saas': ['software', 'platform', 'solution', 'tool', 'app', 'cloud', 'api', 'integration'],
            'ecommerce': ['shop', 'buy', 'store', 'cart', 'checkout', 'products', 'shipping'],
            'finance': ['payment', 'banking', 'investment', 'trading', 'crypto', 'finance', 'money'],
            'health': ['health', 'medical', 'wellness', 'care', 'treatment', 'therapy', 'doctor'],
            'education': ['learn', 'course', 'training', 'education', 'tutorial', 'certification']
        }
        
        # SEO scoring weights
        self.scoring_weights = {
            'technical': 0.25,
            'content': 0.30,
            'keywords': 0.20,
            'user_experience': 0.15,
            'authority': 0.10
        }
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis with advanced insights"""
        cache_key = f"enhanced_seo:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "score": 0,
            "technical_seo": {},
            "content_analysis": {},
            "keyword_intelligence": {},
            "serp_features": {},
            "competitive_gaps": {},
            "ai_search_optimization": {},
            "recommendations": [],
            "critical_issues": [],
            "quick_wins": [],
            "long_term_opportunities": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Parallel fetching of multiple pages for comprehensive analysis
                tasks = [
                    self._analyze_homepage(client, domain),
                    self._analyze_robots_txt(client, domain),
                    self._analyze_sitemap(client, domain),
                    self._check_ssl_and_security(client, domain),
                    self._analyze_page_speed_impact(client, domain)
                ]
                
                homepage_data, robots_data, sitemap_data, security_data, speed_data = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process homepage analysis
                if not isinstance(homepage_data, Exception):
                    results.update(homepage_data)
                
                # Technical SEO compilation
                results["technical_seo"] = {
                    "robots_txt": robots_data if not isinstance(robots_data, Exception) else {"error": str(robots_data)},
                    "sitemap": sitemap_data if not isinstance(sitemap_data, Exception) else {"error": str(sitemap_data)},
                    "security": security_data if not isinstance(security_data, Exception) else {"error": str(security_data)},
                    "page_speed_seo_impact": speed_data if not isinstance(speed_data, Exception) else {"error": str(speed_data)}
                }
                
                # Calculate comprehensive SEO score
                results["score"] = self._calculate_seo_score(results)
                
                # Generate actionable recommendations
                results["recommendations"] = self._generate_recommendations(results)
                
                # Identify quick wins vs long-term opportunities
                self._categorize_opportunities(results)
                
                await cache_result(cache_key, results, ttl=3600)
                
        except Exception as e:
            logger.error(f"Enhanced SEO analysis failed for {domain}", error=str(e))
            results["error"] = str(e)
        
        return results
    
    async def _analyze_homepage(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Deep homepage analysis including content, keywords, and structure"""
        try:
            response = await client.get(f"https://{domain}")
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract all text content for analysis
            text_content = soup.get_text(separator=' ', strip=True)
            
            results = {
                "meta_analysis": self._analyze_meta_tags(soup),
                "content_quality": self._analyze_content_quality(soup, text_content),
                "keyword_density": self._analyze_keyword_density(text_content),
                "heading_structure": self._analyze_heading_structure(soup),
                "internal_linking": self._analyze_internal_links(soup, domain),
                "schema_markup": self._analyze_schema_markup(soup),
                "images_seo": self._analyze_images(soup),
                "serp_optimization": self._analyze_serp_features(soup),
                "ai_optimization": self._check_ai_optimization(soup, response.text)
            }
            
            # Detect industry and provide specific insights
            results["industry_detection"] = self._detect_industry(text_content)
            
            return results
            
        except Exception as e:
            logger.error(f"Homepage analysis failed for {domain}", error=str(e))
            return {"error": str(e)}
    
    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Comprehensive meta tag analysis with recommendations"""
        meta_analysis = {
            "title": {"value": "", "length": 0, "issues": [], "score": 0},
            "description": {"value": "", "length": 0, "issues": [], "score": 0},
            "keywords": {"found": False, "value": ""},
            "open_graph": {"complete": False, "missing": []},
            "twitter_cards": {"complete": False, "missing": []},
            "other_meta": {}
        }
        
        # Title analysis
        title = soup.find('title')
        if title:
            title_text = title.text.strip()
            meta_analysis["title"]["value"] = title_text
            meta_analysis["title"]["length"] = len(title_text)
            
            if len(title_text) < 30:
                meta_analysis["title"]["issues"].append("Too short - aim for 30-60 characters")
                meta_analysis["title"]["score"] = 60
            elif len(title_text) > 60:
                meta_analysis["title"]["issues"].append("Too long - Google truncates at ~60 characters")
                meta_analysis["title"]["score"] = 70
            else:
                meta_analysis["title"]["score"] = 95
                
            # Check for keyword stuffing
            words = title_text.lower().split()
            word_freq = Counter(words)
            if any(count > 2 for word, count in word_freq.items() if len(word) > 3):
                meta_analysis["title"]["issues"].append("Potential keyword stuffing detected")
                meta_analysis["title"]["score"] -= 15
        else:
            meta_analysis["title"]["issues"].append("Missing title tag - CRITICAL SEO issue")
            
        # Description analysis
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            desc_text = desc.get('content', '')
            meta_analysis["description"]["value"] = desc_text
            meta_analysis["description"]["length"] = len(desc_text)
            
            if len(desc_text) < 120:
                meta_analysis["description"]["issues"].append("Too short - aim for 120-160 characters")
                meta_analysis["description"]["score"] = 70
            elif len(desc_text) > 160:
                meta_analysis["description"]["issues"].append("Too long - Google truncates at ~160 characters")
                meta_analysis["description"]["score"] = 80
            else:
                meta_analysis["description"]["score"] = 95
                
            # Check for call-to-action
            cta_keywords = ['learn', 'discover', 'get', 'start', 'try', 'free', 'now']
            if not any(word in desc_text.lower() for word in cta_keywords):
                meta_analysis["description"]["issues"].append("No call-to-action detected - consider adding one")
                meta_analysis["description"]["score"] -= 10
        else:
            meta_analysis["description"]["issues"].append("Missing meta description - important for CTR")
            
        # Open Graph analysis
        og_required = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
        og_found = []
        for tag in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = tag.get('property')
            if prop:
                og_found.append(prop)
                
        meta_analysis["open_graph"]["missing"] = [tag for tag in og_required if tag not in og_found]
        meta_analysis["open_graph"]["complete"] = len(meta_analysis["open_graph"]["missing"]) == 0
        
        # Twitter Cards
        twitter_required = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
        twitter_found = []
        for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = tag.get('name')
            if name:
                twitter_found.append(name)
                
        meta_analysis["twitter_cards"]["missing"] = [tag for tag in twitter_required if tag not in twitter_found]
        meta_analysis["twitter_cards"]["complete"] = len(meta_analysis["twitter_cards"]["missing"]) == 0
        
        return meta_analysis
    
    def _analyze_content_quality(self, soup: BeautifulSoup, text_content: str) -> Dict[str, Any]:
        """Analyze content quality, readability, and depth"""
        words = text_content.split()
        sentences = re.split(r'[.!?]+', text_content)
        
        content_analysis = {
            "word_count": len(words),
            "average_sentence_length": len(words) / max(len(sentences), 1),
            "readability_score": 0,
            "content_depth_score": 0,
            "unique_words": len(set(words)),
            "lexical_diversity": len(set(words)) / max(len(words), 1),
            "issues": [],
            "opportunities": []
        }
        
        # Content depth scoring
        if content_analysis["word_count"] < 300:
            content_analysis["issues"].append("Thin content - less than 300 words")
            content_analysis["content_depth_score"] = 30
        elif content_analysis["word_count"] < 800:
            content_analysis["opportunities"].append("Consider expanding content to 800+ words for better rankings")
            content_analysis["content_depth_score"] = 60
        elif content_analysis["word_count"] < 1500:
            content_analysis["content_depth_score"] = 80
        else:
            content_analysis["content_depth_score"] = 95
            
        # Readability scoring (simplified Flesch Reading Ease)
        if content_analysis["average_sentence_length"] > 25:
            content_analysis["issues"].append("Sentences too long - aim for 15-20 words average")
            content_analysis["readability_score"] = 60
        elif content_analysis["average_sentence_length"] < 10:
            content_analysis["issues"].append("Sentences too short - may appear choppy")
            content_analysis["readability_score"] = 70
        else:
            content_analysis["readability_score"] = 90
            
        # Check for content freshness indicators
        current_year = "2024"
        if current_year in text_content:
            content_analysis["freshness_signals"] = True
            content_analysis["opportunities"].append("Content appears current - good freshness signals")
        else:
            content_analysis["freshness_signals"] = False
            content_analysis["opportunities"].append("Add current year/dates for freshness signals")
            
        return content_analysis
    
    def _analyze_keyword_density(self, text_content: str) -> Dict[str, Any]:
        """Advanced keyword analysis with semantic understanding"""
        # Clean and tokenize
        words = re.findall(r'\b[a-z]+\b', text_content.lower())
        
        # Remove common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'could', 'of', 'in', 'to', 'for', 'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Calculate keyword frequency
        word_freq = Counter(filtered_words)
        total_words = len(filtered_words)
        
        # Extract top keywords with density
        top_keywords = []
        for word, count in word_freq.most_common(20):
            density = (count / total_words) * 100
            top_keywords.append({
                "keyword": word,
                "count": count,
                "density": round(density, 2),
                "optimal": 1.0 <= density <= 3.0
            })
        
        # Identify 2-word and 3-word phrases
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        bigram_freq = Counter(bigrams)
        trigram_freq = Counter(trigrams)
        
        keyword_analysis = {
            "top_keywords": top_keywords[:10],
            "top_phrases": [
                {"phrase": phrase, "count": count} 
                for phrase, count in bigram_freq.most_common(5)
            ],
            "long_tail_keywords": [
                {"phrase": phrase, "count": count} 
                for phrase, count in trigram_freq.most_common(5)
            ],
            "keyword_stuffing_risk": any(kw["density"] > 5.0 for kw in top_keywords),
            "recommendations": []
        }
        
        # Add recommendations
        if keyword_analysis["keyword_stuffing_risk"]:
            keyword_analysis["recommendations"].append("Reduce keyword density to avoid over-optimization penalty")
            
        # Check for LSI keywords
        lsi_opportunities = self._identify_lsi_opportunities(top_keywords, text_content)
        keyword_analysis["lsi_opportunities"] = lsi_opportunities
        
        return keyword_analysis
    
    def _identify_lsi_opportunities(self, top_keywords: List[Dict], text_content: str) -> List[str]:
        """Identify LSI (Latent Semantic Indexing) keyword opportunities"""
        lsi_suggestions = []
        
        # Common LSI patterns based on top keywords
        lsi_patterns = {
            'software': ['platform', 'solution', 'tool', 'application', 'system'],
            'service': ['support', 'help', 'assistance', 'consultation', 'professional'],
            'product': ['features', 'benefits', 'pricing', 'reviews', 'comparison'],
            'business': ['company', 'enterprise', 'organization', 'corporate', 'commercial'],
            'online': ['digital', 'internet', 'web', 'virtual', 'cloud']
        }
        
        text_lower = text_content.lower()
        for kw_data in top_keywords[:5]:
            keyword = kw_data["keyword"]
            if keyword in lsi_patterns:
                for lsi in lsi_patterns[keyword]:
                    if lsi not in text_lower:
                        lsi_suggestions.append(f"Add '{lsi}' as LSI keyword for '{keyword}'")
                        
        return lsi_suggestions[:5]  # Return top 5 suggestions
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading hierarchy and optimization"""
        headings = {
            "h1": [],
            "h2": [],
            "h3": [],
            "h4": [],
            "h5": [],
            "h6": []
        }
        
        for level in headings.keys():
            tags = soup.find_all(level)
            headings[level] = [tag.get_text(strip=True) for tag in tags]
        
        structure_analysis = {
            "h1_count": len(headings["h1"]),
            "h1_text": headings["h1"],
            "h2_count": len(headings["h2"]),
            "total_headings": sum(len(h) for h in headings.values()),
            "hierarchy_score": 0,
            "issues": [],
            "keyword_optimization": []
        }
        
        # H1 analysis
        if structure_analysis["h1_count"] == 0:
            structure_analysis["issues"].append("Missing H1 tag - critical for SEO")
            structure_analysis["hierarchy_score"] = 0
        elif structure_analysis["h1_count"] == 1:
            structure_analysis["hierarchy_score"] = 90
            # Check H1 optimization
            h1_text = headings["h1"][0].lower()
            if len(h1_text) < 20:
                structure_analysis["issues"].append("H1 too short - not descriptive enough")
                structure_analysis["hierarchy_score"] -= 10
            elif len(h1_text) > 70:
                structure_analysis["issues"].append("H1 too long - keep under 70 characters")
                structure_analysis["hierarchy_score"] -= 10
        else:
            structure_analysis["issues"].append(f"Multiple H1 tags ({structure_analysis['h1_count']}) - use only one")
            structure_analysis["hierarchy_score"] = 50
            
        # Check logical hierarchy
        if len(headings["h2"]) == 0 and len(headings["h3"]) > 0:
            structure_analysis["issues"].append("H3 tags without H2 - break hierarchy")
            structure_analysis["hierarchy_score"] -= 20
            
        # Check for keyword optimization in headings
        important_headings = headings["h1"] + headings["h2"]
        if important_headings:
            structure_analysis["keyword_optimization"].append(
                f"Headings should include target keywords. Current H1-H2: {', '.join(important_headings[:3])}"
            )
            
        return structure_analysis
    
    def _analyze_internal_links(self, soup: BeautifulSoup, domain: str) -> Dict[str, Any]:
        """Analyze internal linking structure and opportunities"""
        all_links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []
        
        for link in all_links:
            href = link['href']
            if href.startswith('http'):
                if domain in href:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(href)
                
        link_analysis = {
            "internal_count": len(internal_links),
            "external_count": len(external_links),
            "ratio": len(internal_links) / max(len(external_links), 1),
            "anchor_text_diversity": self._analyze_anchor_text(all_links),
            "issues": [],
            "opportunities": []
        }
        
        # Analyze link depth
        if link_analysis["internal_count"] < 10:
            link_analysis["issues"].append("Weak internal linking - add more contextual links")
        elif link_analysis["internal_count"] > 100:
            link_analysis["opportunities"].append("Many internal links - ensure they're relevant and not spammy")
            
        # Check for nofollow on internal links (usually bad)
        internal_nofollow = sum(1 for link in all_links 
                              if 'nofollow' in link.get('rel', '') 
                              and (link['href'].startswith('/') or domain in link['href']))
        
        if internal_nofollow > 0:
            link_analysis["issues"].append(f"{internal_nofollow} internal links have nofollow - remove for better PageRank flow")
            
        return link_analysis
    
    def _analyze_anchor_text(self, links: List) -> Dict[str, Any]:
        """Analyze anchor text distribution"""
        anchor_texts = []
        for link in links:
            text = link.get_text(strip=True)
            if text:
                anchor_texts.append(text.lower())
                
        anchor_freq = Counter(anchor_texts)
        
        # Check for over-optimization
        generic_anchors = ['click here', 'read more', 'learn more', 'here', 'link']
        generic_count = sum(anchor_freq.get(g, 0) for g in generic_anchors)
        
        return {
            "total_unique": len(set(anchor_texts)),
            "most_common": [{"text": text, "count": count} for text, count in anchor_freq.most_common(5)],
            "generic_percentage": (generic_count / max(len(anchor_texts), 1)) * 100,
            "diverse": len(set(anchor_texts)) > len(anchor_texts) * 0.5
        }
    
    def _analyze_schema_markup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze structured data implementation"""
        schema_scripts = soup.find_all('script', type='application/ld+json')
        
        schema_analysis = {
            "found": len(schema_scripts) > 0,
            "types": [],
            "opportunities": [],
            "score": 0
        }
        
        if schema_scripts:
            for script in schema_scripts:
                try:
                    data = json.loads(script.string)
                    if '@type' in data:
                        schema_analysis["types"].append(data['@type'])
                except:
                    pass
                    
            schema_analysis["score"] = min(90, 30 + len(schema_analysis["types"]) * 20)
        else:
            schema_analysis["opportunities"].append("No Schema.org markup found - missing rich snippets opportunity")
            
        # Recommend schemas based on content
        recommended_schemas = [
            "Organization", "WebSite", "BreadcrumbList", "FAQPage", 
            "Product", "Review", "HowTo", "Article"
        ]
        
        for schema in recommended_schemas:
            if schema not in schema_analysis["types"]:
                schema_analysis["opportunities"].append(f"Consider adding {schema} schema")
                
        return schema_analysis
    
    def _analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze image SEO optimization"""
        images = soup.find_all('img')
        
        image_analysis = {
            "total_images": len(images),
            "missing_alt": 0,
            "missing_title": 0,
            "lazy_loading": 0,
            "next_gen_formats": 0,
            "large_images": [],
            "issues": [],
            "score": 100
        }
        
        for img in images:
            # Check alt text
            if not img.get('alt'):
                image_analysis["missing_alt"] += 1
                
            # Check title
            if not img.get('title'):
                image_analysis["missing_title"] += 1
                
            # Check lazy loading
            if img.get('loading') == 'lazy':
                image_analysis["lazy_loading"] += 1
                
            # Check for next-gen formats
            src = img.get('src', '')
            if any(ext in src.lower() for ext in ['.webp', '.avif']):
                image_analysis["next_gen_formats"] += 1
                
            # Identify potentially large images
            if 'background' in src.lower() or 'hero' in src.lower() or 'banner' in src.lower():
                image_analysis["large_images"].append(src)
                
        # Calculate issues and score
        if image_analysis["missing_alt"] > 0:
            image_analysis["issues"].append(f"{image_analysis['missing_alt']} images missing alt text - hurts SEO and accessibility")
            image_analysis["score"] -= image_analysis["missing_alt"] * 5
            
        if image_analysis["lazy_loading"] < image_analysis["total_images"] * 0.5:
            image_analysis["issues"].append("Most images not using lazy loading - impacts page speed")
            image_analysis["score"] -= 10
            
        if image_analysis["next_gen_formats"] == 0:
            image_analysis["issues"].append("No next-gen image formats (WebP/AVIF) detected")
            image_analysis["score"] -= 15
            
        image_analysis["score"] = max(0, image_analysis["score"])
        
        return image_analysis
    
    def _analyze_serp_features(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze optimization for SERP features"""
        serp_optimization = {
            "featured_snippet_ready": False,
            "people_also_ask_ready": False,
            "knowledge_panel_signals": False,
            "rich_snippets_potential": [],
            "opportunities": []
        }
        
        # Check for featured snippet optimization (lists, tables, definitions)
        lists = soup.find_all(['ul', 'ol'])
        tables = soup.find_all('table')
        
        if lists or tables:
            serp_optimization["featured_snippet_ready"] = True
            serp_optimization["opportunities"].append("Content structure supports featured snippets")
            
        # Check for Q&A content (People Also Ask)
        text = soup.get_text().lower()
        question_patterns = ['what is', 'how to', 'why do', 'when should', 'where can']
        
        if any(pattern in text for pattern in question_patterns):
            serp_optimization["people_also_ask_ready"] = True
            serp_optimization["opportunities"].append("Q&A content detected - good for People Also Ask")
            
        # Check for entity signals (Knowledge Panel)
        if soup.find('script', type='application/ld+json'):
            serp_optimization["knowledge_panel_signals"] = True
            
        return serp_optimization
    
    def _check_ai_optimization(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """Check optimization for AI search engines"""
        ai_optimization = {
            "ai_friendly_score": 100,
            "llm_readable": True,
            "structured_content": False,
            "natural_language": False,
            "issues": [],
            "opportunities": []
        }
        
        # Check for structured content that LLMs prefer
        if soup.find_all(['section', 'article', 'aside', 'nav']):
            ai_optimization["structured_content"] = True
        else:
            ai_optimization["issues"].append("Limited semantic HTML5 elements - use section/article tags")
            ai_optimization["ai_friendly_score"] -= 20
            
        # Check for natural language patterns
        text = soup.get_text()
        sentences = re.split(r'[.!?]+', text)
        
        # Check for conversational tone
        conversational_patterns = ['you', 'your', 'we', 'our', 'let\'s', 'here\'s']
        conversational_count = sum(1 for pattern in conversational_patterns if pattern in text.lower())
        
        if conversational_count > 5:
            ai_optimization["natural_language"] = True
            ai_optimization["opportunities"].append("Good conversational tone for AI interpretation")
        else:
            ai_optimization["opportunities"].append("Add more conversational language for better AI understanding")
            ai_optimization["ai_friendly_score"] -= 10
            
        # Check for clear information hierarchy
        if not soup.find('nav'):
            ai_optimization["issues"].append("No navigation element - harder for AI to understand site structure")
            ai_optimization["ai_friendly_score"] -= 15
            
        return ai_optimization
    
    def _detect_industry(self, text_content: str) -> Dict[str, Any]:
        """Detect industry and provide specific recommendations"""
        text_lower = text_content.lower()
        detected_industries = []
        
        for industry, keywords in self.industry_keywords.items():
            match_count = sum(1 for keyword in keywords if keyword in text_lower)
            if match_count >= 3:
                detected_industries.append({
                    "industry": industry,
                    "confidence": min(95, match_count * 15),
                    "matched_keywords": [kw for kw in keywords if kw in text_lower][:5]
                })
                
        # Sort by confidence
        detected_industries.sort(key=lambda x: x["confidence"], reverse=True)
        
        industry_result = {
            "primary_industry": detected_industries[0] if detected_industries else None,
            "secondary_industries": detected_industries[1:3] if len(detected_industries) > 1 else [],
            "recommendations": []
        }
        
        # Industry-specific recommendations
        if industry_result["primary_industry"]:
            industry = industry_result["primary_industry"]["industry"]
            
            if industry == "saas":
                industry_result["recommendations"].extend([
                    "Add software comparison pages for '[Your Product] vs [Competitor]'",
                    "Create feature pages targeting 'best [feature] software' keywords",
                    "Implement free trial CTAs prominently"
                ])
            elif industry == "ecommerce":
                industry_result["recommendations"].extend([
                    "Optimize product pages with schema markup",
                    "Create category pages targeting commercial intent keywords",
                    "Add customer reviews and ratings for trust signals"
                ])
            elif industry == "finance":
                industry_result["recommendations"].extend([
                    "Add trust badges and security certifications prominently",
                    "Create educational content for YMYL (Your Money Your Life) authority",
                    "Implement FAQ schema for common financial questions"
                ])
                
        return industry_result
    
    async def _analyze_robots_txt(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze robots.txt for SEO issues and AI crawler access"""
        try:
            response = await client.get(f"https://{domain}/robots.txt")
            
            if response.status_code != 200:
                return {
                    "exists": False,
                    "issues": ["No robots.txt file found - create one for better crawl control"]
                }
                
            content = response.text.lower()
            lines = content.split('\n')
            
            robots_analysis = {
                "exists": True,
                "ai_crawlers_blocked": [],
                "important_paths_blocked": [],
                "sitemap_declared": False,
                "crawl_delay": None,
                "issues": [],
                "opportunities": []
            }
            
            # Check for AI crawler blocking
            for crawler in self.ai_crawlers:
                if f"user-agent: {crawler.lower()}" in content:
                    # Check if it's being blocked
                    for i, line in enumerate(lines):
                        if crawler.lower() in line:
                            # Look for disallow in next few lines
                            for j in range(i+1, min(i+5, len(lines))):
                                if 'disallow:' in lines[j] and lines[j].strip() != 'disallow:':
                                    robots_analysis["ai_crawlers_blocked"].append(crawler)
                                    break
                                elif 'user-agent:' in lines[j]:
                                    break
                                    
            # Check for sitemap declaration
            if 'sitemap:' in content:
                robots_analysis["sitemap_declared"] = True
            else:
                robots_analysis["opportunities"].append("Add sitemap URL to robots.txt")
                
            # Check for crawl delay
            crawl_delay_match = re.search(r'crawl-delay:\s*(\d+)', content)
            if crawl_delay_match:
                robots_analysis["crawl_delay"] = int(crawl_delay_match.group(1))
                if robots_analysis["crawl_delay"] > 10:
                    robots_analysis["issues"].append(f"High crawl delay ({robots_analysis['crawl_delay']}s) may hurt indexing")
                    
            # Check for important paths being blocked
            important_paths = ['/wp-admin', '/admin', '/*.js', '/*.css']
            for path in important_paths:
                if f"disallow: {path}" in content:
                    if path in ['/*.js', '/*.css']:
                        robots_analysis["issues"].append(f"Blocking {path} prevents Google from rendering pages properly")
                        
            # AI crawler recommendations
            if robots_analysis["ai_crawlers_blocked"]:
                robots_analysis["issues"].append(
                    f"Blocking AI crawlers ({', '.join(robots_analysis['ai_crawlers_blocked'])}) - missing AI search visibility"
                )
                
            return robots_analysis
            
        except Exception as e:
            return {"error": str(e), "exists": False}
    
    async def _analyze_sitemap(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Analyze XML sitemap for completeness and issues"""
        sitemap_urls = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemap",
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = await client.get(sitemap_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    
                    urls = soup.find_all('url')
                    
                    sitemap_analysis = {
                        "exists": True,
                        "url": sitemap_url,
                        "url_count": len(urls),
                        "has_images": len(soup.find_all('image:image')) > 0,
                        "has_video": len(soup.find_all('video:video')) > 0,
                        "issues": [],
                        "opportunities": []
                    }
                    
                    # Check for lastmod dates
                    lastmod_count = len(soup.find_all('lastmod'))
                    if lastmod_count < len(urls):
                        sitemap_analysis["issues"].append("Missing lastmod dates - add for better crawl prioritization")
                        
                    # Check for priority tags
                    priority_count = len(soup.find_all('priority'))
                    if priority_count < len(urls):
                        sitemap_analysis["opportunities"].append("Add priority tags to indicate page importance")
                        
                    # Check URL count
                    if sitemap_analysis["url_count"] > 50000:
                        sitemap_analysis["issues"].append("Sitemap has >50k URLs - split into multiple sitemaps")
                    elif sitemap_analysis["url_count"] < 10:
                        sitemap_analysis["issues"].append("Very few URLs in sitemap - ensure all important pages are included")
                        
                    return sitemap_analysis
                    
            except Exception as e:
                continue
                
        return {
            "exists": False,
            "issues": ["No XML sitemap found - create one for better indexation"],
            "opportunities": ["Create and submit sitemap to Google Search Console"]
        }
    
    async def _check_ssl_and_security(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Check SSL and security features that impact SEO"""
        security_analysis = {
            "https": False,
            "hsts": False,
            "mixed_content": False,
            "security_headers": {},
            "score": 0
        }
        
        try:
            # Check HTTPS
            response = await client.get(f"https://{domain}")
            security_analysis["https"] = True
            security_analysis["score"] += 50
            
            # Check security headers
            headers = response.headers
            
            # HSTS
            if 'strict-transport-security' in headers:
                security_analysis["hsts"] = True
                security_analysis["score"] += 20
                
            # Other security headers
            security_headers = [
                'x-frame-options',
                'x-content-type-options',
                'x-xss-protection',
                'content-security-policy'
            ]
            
            for header in security_headers:
                if header in headers:
                    security_analysis["security_headers"][header] = True
                    security_analysis["score"] += 7.5
                    
        except Exception as e:
            security_analysis["https"] = False
            security_analysis["issues"] = ["HTTPS not properly configured - critical for SEO"]
            
        return security_analysis
    
    async def _analyze_page_speed_impact(self, client: httpx.AsyncClient, domain: str) -> Dict[str, Any]:
        """Quick page speed check for SEO impact"""
        try:
            import time
            start = time.time()
            response = await client.get(f"https://{domain}", timeout=10)
            load_time = time.time() - start
            
            speed_impact = {
                "load_time": round(load_time, 2),
                "seo_impact": "positive" if load_time < 3 else "negative",
                "score": max(0, 100 - int(load_time * 10)),
                "recommendations": []
            }
            
            if load_time > 3:
                speed_impact["recommendations"].append("Page load >3s hurts SEO - optimize performance")
            if load_time > 5:
                speed_impact["recommendations"].append("Critical: Page load >5s significantly impacts rankings")
                
            return speed_impact
            
        except Exception as e:
            return {"error": str(e), "load_time": 0, "seo_impact": "unknown"}
    
    def _calculate_seo_score(self, results: Dict[str, Any]) -> int:
        """Calculate comprehensive SEO score based on all factors"""
        scores = {
            "technical": 0,
            "content": 0,
            "keywords": 0,
            "user_experience": 0,
            "authority": 0
        }
        
        # Technical score
        if results.get("technical_seo"):
            tech = results["technical_seo"]
            if tech.get("robots_txt", {}).get("exists"):
                scores["technical"] += 20
            if tech.get("sitemap", {}).get("exists"):
                scores["technical"] += 20
            if tech.get("security", {}).get("https"):
                scores["technical"] += 30
            if tech.get("page_speed_seo_impact", {}).get("load_time", 10) < 3:
                scores["technical"] += 30
                
        # Content score
        if results.get("content_quality"):
            content = results["content_quality"]
            scores["content"] = content.get("content_depth_score", 0) * 0.5 + content.get("readability_score", 0) * 0.5
            
        # Keywords score
        if results.get("keyword_intelligence"):
            keywords = results["keyword_intelligence"]
            if not keywords.get("keyword_stuffing_risk"):
                scores["keywords"] = 80
            else:
                scores["keywords"] = 40
                
        # User experience score
        if results.get("meta_analysis"):
            meta = results["meta_analysis"]
            scores["user_experience"] += meta.get("title", {}).get("score", 0) * 0.5
            scores["user_experience"] += meta.get("description", {}).get("score", 0) * 0.5
            
        # Authority score (schema, links, etc.)
        if results.get("schema_markup", {}).get("found"):
            scores["authority"] += 50
        if results.get("internal_linking", {}).get("internal_count", 0) > 10:
            scores["authority"] += 50
            
        # Calculate weighted final score
        final_score = sum(
            scores[factor] * weight 
            for factor, weight in self.scoring_weights.items()
        )
        
        return min(95, max(20, int(final_score)))  # Cap at 95, minimum 20
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized, actionable recommendations"""
        recommendations = []
        
        # Priority 1: Critical Issues
        if results.get("meta_analysis", {}).get("title", {}).get("issues"):
            recommendations.append({
                "priority": 1,
                "category": "Critical",
                "issue": "Title tag problems",
                "action": "Fix title tag issues immediately",
                "impact": "High",
                "effort": "Low",
                "details": results["meta_analysis"]["title"]["issues"]
            })
            
        if results.get("technical_seo", {}).get("robots_txt", {}).get("ai_crawlers_blocked"):
            recommendations.append({
                "priority": 1,
                "category": "Critical",
                "issue": "AI crawlers blocked",
                "action": "Remove AI crawler blocks from robots.txt",
                "impact": "High",
                "effort": "Low",
                "details": f"Blocked crawlers: {', '.join(results['technical_seo']['robots_txt']['ai_crawlers_blocked'])}"
            })
            
        # Priority 2: High Impact, Low Effort
        if not results.get("schema_markup", {}).get("found"):
            recommendations.append({
                "priority": 2,
                "category": "Quick Win",
                "issue": "No structured data",
                "action": "Add Schema.org markup for rich snippets",
                "impact": "High",
                "effort": "Medium",
                "details": "Implement Organization, WebSite, and relevant schemas"
            })
            
        # Priority 3: Content Improvements
        if results.get("content_quality", {}).get("word_count", 0) < 800:
            recommendations.append({
                "priority": 3,
                "category": "Content",
                "issue": "Thin content",
                "action": "Expand content to 800+ words with valuable information",
                "impact": "Medium",
                "effort": "Medium",
                "details": f"Current word count: {results.get('content_quality', {}).get('word_count', 0)}"
            })
            
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _categorize_opportunities(self, results: Dict[str, Any]) -> None:
        """Categorize opportunities into quick wins and long-term strategies"""
        
        # Quick wins (can be done in <1 day)
        quick_wins = []
        
        if results.get("meta_analysis", {}).get("title", {}).get("issues"):
            quick_wins.append({
                "task": "Fix title tag",
                "time": "15 minutes",
                "impact": "Immediate CTR improvement"
            })
            
        if results.get("images_seo", {}).get("missing_alt", 0) > 0:
            quick_wins.append({
                "task": f"Add alt text to {results['images_seo']['missing_alt']} images",
                "time": "1 hour",
                "impact": "Better image search visibility"
            })
            
        results["quick_wins"] = quick_wins
        
        # Long-term opportunities
        long_term = []
        
        if results.get("content_quality", {}).get("word_count", 0) < 1500:
            long_term.append({
                "task": "Create comprehensive content hub",
                "time": "1-2 weeks",
                "impact": "Establish topical authority"
            })
            
        if not results.get("schema_markup", {}).get("found"):
            long_term.append({
                "task": "Implement complete structured data strategy",
                "time": "1 week",
                "impact": "Rich snippets and better SERP presence"
            })
            
        results["long_term_opportunities"] = long_term