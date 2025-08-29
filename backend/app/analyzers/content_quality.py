"""
Content quality analyzer that evaluates if content is actually effective
Goes beyond checking if content exists to evaluate its quality and impact
"""

import httpx
from typing import Dict, Any, List, Optional
import re
import structlog
from bs4 import BeautifulSoup
from textstat import flesch_reading_ease, flesch_kincaid_grade
import nltk
from collections import Counter
from urllib.parse import urljoin

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()

# Download required NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class ContentQualityAnalyzer:
    """
    Analyzes content quality, not just existence:
    - Reading level and complexity
    - Jargon density
    - Value proposition clarity
    - Social proof authenticity
    - Call-to-action strength
    - Emotional triggers and persuasion
    - Content freshness and updates
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(20.0, connect=10.0)
        
        # Industry jargon that confuses visitors
        self.jargon_terms = {
            "synergy", "leverage", "paradigm", "holistic", "disruptive",
            "revolutionary", "cutting-edge", "next-generation", "best-in-class",
            "turnkey", "scalable", "robust", "seamless", "innovative",
            "enterprise-grade", "world-class", "leading", "premier",
            "state-of-the-art", "breakthrough", "transformative"
        }
        
        # Power words that convert
        self.power_words = {
            "free", "instant", "easy", "simple", "proven", "guaranteed",
            "exclusive", "limited", "new", "save", "you", "your",
            "imagine", "discover", "unlock", "transform", "boost",
            "results", "success", "grow", "increase", "improve"
        }
        
        # Trust words
        self.trust_words = {
            "trusted", "secure", "safe", "certified", "verified",
            "guaranteed", "proven", "authentic", "reliable", "established"
        }
    
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze content quality across the website
        """
        cache_key = f"content_quality:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "overall_quality_score": 0,
            "readability_issues": [],
            "value_prop_clarity": {},
            "jargon_analysis": {},
            "cta_effectiveness": {},
            "social_proof_quality": {},
            "emotional_triggers": {},
            "content_freshness": {},
            "competitor_comparison": {},
            "improvement_priorities": [],
            "quick_content_wins": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Analyze key pages
                pages = await self._get_key_pages(domain, client)
                
                page_analyses = {}
                for page_name, url in pages.items():
                    if url:
                        page_analysis = await self._analyze_page_content(
                            url, page_name, client
                        )
                        page_analyses[page_name] = page_analysis
                
                # Aggregate results
                results["readability_issues"] = self._aggregate_readability(page_analyses)
                results["value_prop_clarity"] = self._assess_value_prop(page_analyses)
                results["jargon_analysis"] = self._analyze_jargon_usage(page_analyses)
                results["cta_effectiveness"] = self._evaluate_ctas(page_analyses)
                results["social_proof_quality"] = self._assess_social_proof(page_analyses)
                results["emotional_triggers"] = self._analyze_emotional_appeal(page_analyses)
                results["content_freshness"] = await self._check_content_freshness(pages, client)
                
                # Calculate overall score
                results["overall_quality_score"] = self._calculate_quality_score(results)
                
                # Generate improvement priorities
                results["improvement_priorities"] = self._prioritize_improvements(results)
                results["quick_content_wins"] = self._identify_quick_wins(results)
                
                # Compare to best practices
                results["competitor_comparison"] = self._compare_to_best_practices(results)
                
                # Cache for 24 hours
                await cache_result(cache_key, results, ttl=86400)
        
        except Exception as e:
            logger.error(f"Content quality analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _get_key_pages(self, domain: str, client: httpx.AsyncClient) -> Dict[str, str]:
        """Get URLs of key pages to analyze"""
        pages = {
            "homepage": f"https://{domain}",
            "about": None,
            "features": None,
            "pricing": None,
            "blog": None,
            "product": None
        }
        
        try:
            response = await client.get(pages["homepage"], follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    text = link.get_text().lower()
                    
                    if not pages["about"] and ("about" in href or "about" in text):
                        pages["about"] = urljoin(pages["homepage"], link['href'])
                    elif not pages["features"] and ("features" in href or "product" in href):
                        pages["features"] = urljoin(pages["homepage"], link['href'])
                    elif not pages["pricing"] and ("pricing" in href or "plans" in href):
                        pages["pricing"] = urljoin(pages["homepage"], link['href'])
                    elif not pages["blog"] and ("blog" in href or "resources" in href):
                        pages["blog"] = urljoin(pages["homepage"], link['href'])
        
        except Exception as e:
            logger.debug(f"Error getting key pages: {e}")
        
        return {k: v for k, v in pages.items() if v}
    
    async def _analyze_page_content(
        self, url: str, page_name: str, client: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Analyze content quality of a specific page"""
        analysis = {
            "url": url,
            "page": page_name,
            "readability": {},
            "jargon": {},
            "value_prop": {},
            "ctas": {},
            "social_proof": {},
            "emotional_appeal": {}
        }
        
        try:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                
                # Clean text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Analyze readability
                analysis["readability"] = self._analyze_readability(text)
                
                # Analyze jargon
                analysis["jargon"] = self._calculate_jargon_density(text)
                
                # Analyze value proposition (homepage and features pages)
                if page_name in ["homepage", "features"]:
                    analysis["value_prop"] = self._analyze_value_proposition(soup, text)
                
                # Analyze CTAs
                analysis["ctas"] = self._analyze_cta_quality(soup)
                
                # Analyze social proof
                analysis["social_proof"] = self._analyze_social_proof(soup, text)
                
                # Analyze emotional appeal
                analysis["emotional_appeal"] = self._analyze_emotions(text)
        
        except Exception as e:
            logger.debug(f"Error analyzing page {url}: {e}")
        
        return analysis
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability and complexity"""
        if len(text) < 100:
            return {"error": "Not enough text to analyze"}
        
        try:
            # Calculate readability scores
            flesch_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
            
            # Interpret scores
            if flesch_score < 30:
                difficulty = "Very difficult (post-graduate level)"
                issue = "Content too complex for most visitors"
            elif flesch_score < 50:
                difficulty = "Difficult (college level)"
                issue = "May lose non-technical audience"
            elif flesch_score < 60:
                difficulty = "Fairly difficult (high school senior)"
                issue = "Could be simplified"
            elif flesch_score < 70:
                difficulty = "Standard (8th-9th grade)"
                issue = None
            elif flesch_score < 80:
                difficulty = "Fairly easy (7th grade)"
                issue = None
            else:
                difficulty = "Very easy (5th grade)"
                issue = None
            
            # Calculate sentence complexity
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Check for passive voice (simple heuristic)
            passive_indicators = ["was", "were", "been", "being", "be", "is", "are"]
            passive_count = sum(1 for word in text.lower().split() if word in passive_indicators)
            passive_percentage = (passive_count / len(text.split())) * 100
            
            return {
                "flesch_score": flesch_score,
                "grade_level": grade_level,
                "difficulty": difficulty,
                "issue": issue,
                "avg_sentence_length": avg_sentence_length,
                "passive_voice_percentage": passive_percentage,
                "recommendations": self._get_readability_recommendations(
                    flesch_score, avg_sentence_length, passive_percentage
                )
            }
        
        except Exception as e:
            return {"error": f"Readability analysis failed: {e}"}
    
    def _calculate_jargon_density(self, text: str) -> Dict[str, Any]:
        """Calculate how much jargon is used"""
        words = text.lower().split()
        total_words = len(words)
        
        if total_words < 50:
            return {"error": "Not enough text"}
        
        # Count jargon usage
        jargon_found = []
        for word in words:
            if word in self.jargon_terms:
                jargon_found.append(word)
        
        jargon_count = len(jargon_found)
        jargon_density = (jargon_count / total_words) * 100
        
        # Determine severity
        if jargon_density > 5:
            severity = "high"
            impact = "Confusing visitors, reducing trust"
        elif jargon_density > 2:
            severity = "medium"
            impact = "Some confusion possible"
        else:
            severity = "low"
            impact = None
        
        return {
            "jargon_density": jargon_density,
            "jargon_count": jargon_count,
            "total_words": total_words,
            "severity": severity,
            "impact": impact,
            "top_jargon": Counter(jargon_found).most_common(5),
            "fix": "Replace with simple, concrete language"
        }
    
    def _analyze_value_proposition(self, soup: BeautifulSoup, text: str) -> Dict[str, Any]:
        """Analyze clarity and strength of value proposition"""
        analysis = {
            "has_clear_headline": False,
            "specificity_score": 0,
            "benefit_focused": False,
            "differentiation": False,
            "issues": []
        }
        
        # Check for clear headline (h1/h2)
        headlines = soup.find_all(['h1', 'h2'])[:3]
        
        if headlines:
            main_headline = headlines[0].get_text()
            analysis["has_clear_headline"] = True
            
            # Check if headline is specific
            vague_words = ["solution", "platform", "software", "tool", "system"]
            if any(word in main_headline.lower() for word in vague_words):
                analysis["issues"].append({
                    "type": "vague_headline",
                    "current": main_headline[:100],
                    "impact": "Visitors don't understand what you do",
                    "fix": "Be specific: 'Send 10x more emails without spam filters'"
                })
            
            # Check if benefit-focused
            benefit_words = ["increase", "reduce", "save", "grow", "improve", "boost", "get"]
            analysis["benefit_focused"] = any(word in main_headline.lower() for word in benefit_words)
            
            if not analysis["benefit_focused"]:
                analysis["issues"].append({
                    "type": "feature_focused_headline",
                    "impact": "Not speaking to customer desires",
                    "fix": "Lead with outcome, not features"
                })
        else:
            analysis["issues"].append({
                "type": "no_clear_headline",
                "impact": "Visitors bounce without understanding value",
                "fix": "Add clear H1 that explains what you do and why it matters"
            })
        
        # Check for specificity (numbers, concrete claims)
        numbers_found = re.findall(r'\d+[%x]?', text[:1000])
        analysis["specificity_score"] = min(len(numbers_found) * 20, 100)
        
        if analysis["specificity_score"] < 40:
            analysis["issues"].append({
                "type": "lack_of_specificity",
                "impact": "Generic claims don't build trust",
                "fix": "Add specific numbers: '50% faster', '10-minute setup'"
            })
        
        # Check for differentiation
        diff_words = ["unlike", "instead of", "better than", "only", "first"]
        analysis["differentiation"] = any(word in text[:1000].lower() for word in diff_words)
        
        if not analysis["differentiation"]:
            analysis["issues"].append({
                "type": "no_differentiation",
                "impact": "Not clear why choose you over competitors",
                "fix": "Add 'Unlike [alternative], we...'"
            })
        
        return analysis
    
    def _analyze_cta_quality(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze call-to-action effectiveness"""
        ctas = []
        
        # Find CTAs (buttons and prominent links)
        buttons = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta', re.I))
        
        for button in buttons[:10]:  # Analyze first 10
            text = button.get_text().strip()
            if text:
                cta_analysis = {
                    "text": text,
                    "quality": self._rate_cta_text(text),
                    "issues": []
                }
                
                # Check for weak CTAs
                weak_ctas = ["submit", "click here", "learn more", "read more", "continue"]
                if text.lower() in weak_ctas:
                    cta_analysis["issues"].append("Weak, generic CTA")
                
                # Check length
                if len(text.split()) > 5:
                    cta_analysis["issues"].append("Too long (>5 words)")
                
                # Check for value
                if not any(word in text.lower() for word in ["get", "start", "try", "free"]):
                    cta_analysis["issues"].append("No value proposition")
                
                ctas.append(cta_analysis)
        
        # Overall assessment
        avg_quality = sum(c["quality"] for c in ctas) / len(ctas) if ctas else 0
        
        return {
            "ctas_analyzed": len(ctas),
            "average_quality": avg_quality,
            "weak_ctas": [c for c in ctas if c["quality"] < 50],
            "recommendations": self._get_cta_recommendations(ctas)
        }
    
    def _rate_cta_text(self, text: str) -> int:
        """Rate CTA text quality 0-100"""
        score = 50  # Base score
        
        text_lower = text.lower()
        
        # Strong action words
        if any(word in text_lower for word in ["get", "start", "try", "claim", "unlock"]):
            score += 20
        
        # Value indicators
        if any(word in text_lower for word in ["free", "instant", "now", "today"]):
            score += 15
        
        # Personal
        if "your" in text_lower or "my" in text_lower:
            score += 10
        
        # Weak words
        if any(word in text_lower for word in ["submit", "click", "learn more"]):
            score -= 30
        
        # Length penalty
        if len(text.split()) > 4:
            score -= 10
        
        return max(0, min(100, score))
    
    def _analyze_social_proof(self, soup: BeautifulSoup, text: str) -> Dict[str, Any]:
        """Analyze quality and authenticity of social proof"""
        analysis = {
            "testimonials": [],
            "logos": 0,
            "metrics": [],
            "authenticity_score": 0,
            "issues": []
        }
        
        # Look for testimonials
        testimonial_patterns = [
            r'"[^"]{20,}"[^"]*[-–—]\s*\w+',  # "Quote" - Name
            r'["""][^"""]{20,}["""]',  # Various quote styles
        ]
        
        for pattern in testimonial_patterns:
            matches = re.findall(pattern, text)
            analysis["testimonials"].extend(matches[:5])
        
        # Check testimonial quality
        if analysis["testimonials"]:
            # Check for generic testimonials
            generic_phrases = ["great product", "awesome", "amazing", "excellent service"]
            generic_count = sum(
                1 for t in analysis["testimonials"] 
                if any(phrase in t.lower() for phrase in generic_phrases)
            )
            
            if generic_count > len(analysis["testimonials"]) / 2:
                analysis["issues"].append({
                    "type": "generic_testimonials",
                    "impact": "Don't build trust",
                    "fix": "Use specific, outcome-focused testimonials"
                })
        else:
            analysis["issues"].append({
                "type": "no_testimonials",
                "impact": "Missing social proof",
                "fix": "Add 3-5 customer testimonials with names and companies"
            })
        
        # Look for customer logos
        logo_indicators = soup.find_all('img', alt=re.compile(r'logo|client|customer', re.I))
        analysis["logos"] = len(logo_indicators)
        
        if analysis["logos"] < 5:
            analysis["issues"].append({
                "type": "insufficient_logos",
                "impact": "Not showing customer validation",
                "fix": "Add 'Trusted by' section with 5-8 logos"
            })
        
        # Look for metrics/numbers
        metric_patterns = [
            r'\d+[%+]?\s*(?:increase|improvement|growth|faster|ROI)',
            r'\d+\s*(?:customers|users|companies)',
            r'\$\d+[MKB]?\s*(?:saved|generated|revenue)'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text, re.I)
            analysis["metrics"].extend(matches[:5])
        
        # Calculate authenticity score
        score = 50
        if analysis["testimonials"]:
            score += 20
        if analysis["logos"] > 5:
            score += 15
        if analysis["metrics"]:
            score += 15
        if analysis["issues"]:
            score -= len(analysis["issues"]) * 10
        
        analysis["authenticity_score"] = max(0, min(100, score))
        
        return analysis
    
    def _analyze_emotions(self, text: str) -> Dict[str, Any]:
        """Analyze emotional triggers in content"""
        analysis = {
            "power_word_density": 0,
            "trust_word_density": 0,
            "urgency_indicators": 0,
            "fear_appeals": 0,
            "aspiration_appeals": 0,
            "effectiveness": "low"
        }
        
        words = text.lower().split()
        total_words = len(words)
        
        if total_words < 100:
            return analysis
        
        # Count power words
        power_count = sum(1 for word in words if word in self.power_words)
        analysis["power_word_density"] = (power_count / total_words) * 100
        
        # Count trust words
        trust_count = sum(1 for word in words if word in self.trust_words)
        analysis["trust_word_density"] = (trust_count / total_words) * 100
        
        # Urgency indicators
        urgency_words = ["now", "today", "limited", "ends", "hurry", "last chance"]
        analysis["urgency_indicators"] = sum(1 for word in urgency_words if word in text.lower())
        
        # Fear appeals (loss aversion)
        fear_phrases = ["don't miss", "avoid", "prevent", "stop losing", "risk"]
        analysis["fear_appeals"] = sum(1 for phrase in fear_phrases if phrase in text.lower())
        
        # Aspiration appeals
        aspiration_phrases = ["achieve", "become", "transform", "unlock", "reach"]
        analysis["aspiration_appeals"] = sum(1 for phrase in aspiration_phrases if phrase in text.lower())
        
        # Determine effectiveness
        total_emotional_elements = (
            analysis["power_word_density"] + 
            analysis["trust_word_density"] +
            analysis["urgency_indicators"] +
            analysis["fear_appeals"] +
            analysis["aspiration_appeals"]
        )
        
        if total_emotional_elements > 15:
            analysis["effectiveness"] = "high"
        elif total_emotional_elements > 8:
            analysis["effectiveness"] = "medium"
        else:
            analysis["effectiveness"] = "low"
        
        return analysis
    
    async def _check_content_freshness(self, pages: Dict[str, str], client: httpx.AsyncClient) -> Dict[str, Any]:
        """Check if content is fresh and updated"""
        freshness = {
            "last_updates": {},
            "stale_content": [],
            "missing_dates": []
        }
        
        for page_name, url in pages.items():
            if url and "blog" in page_name:
                try:
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for dates
                        date_patterns = [
                            r'20[2-9]\d-\d{2}-\d{2}',  # 2023-01-01
                            r'\d{1,2}/\d{1,2}/20[2-9]\d',  # 1/1/2023
                            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+20[2-9]\d'
                        ]
                        
                        dates_found = []
                        text = soup.get_text()
                        for pattern in date_patterns:
                            matches = re.findall(pattern, text)
                            dates_found.extend(matches)
                        
                        if dates_found:
                            freshness["last_updates"][page_name] = dates_found[0]
                        else:
                            freshness["missing_dates"].append(page_name)
                
                except Exception as e:
                    logger.debug(f"Error checking freshness for {url}: {e}")
        
        return freshness
    
    def _get_readability_recommendations(
        self, flesch_score: float, avg_sentence_length: float, passive_percentage: float
    ) -> List[str]:
        """Get specific readability improvements"""
        recommendations = []
        
        if flesch_score < 50:
            recommendations.append("Simplify language - aim for 8th grade reading level")
        
        if avg_sentence_length > 20:
            recommendations.append("Shorten sentences - aim for 15-20 words average")
        
        if passive_percentage > 20:
            recommendations.append("Use more active voice - reduces by 50%")
        
        return recommendations
    
    def _get_cta_recommendations(self, ctas: List[Dict]) -> List[str]:
        """Get CTA improvement recommendations"""
        recommendations = []
        
        weak_count = sum(1 for c in ctas if c["quality"] < 50)
        if weak_count > len(ctas) / 2:
            recommendations.append("Replace generic CTAs with value-focused ones")
            recommendations.append("Use pattern: 'Get/Start [Value] [Timeframe]'")
            recommendations.append("Examples: 'Get Your Free Analysis', 'Start Growing Today'")
        
        return recommendations
    
    def _aggregate_readability(self, page_analyses: Dict) -> List[Dict]:
        """Aggregate readability issues across pages"""
        issues = []
        
        for page_name, analysis in page_analyses.items():
            readability = analysis.get("readability", {})
            if readability.get("issue"):
                issues.append({
                    "page": page_name,
                    "issue": readability["issue"],
                    "score": readability.get("flesch_score", 0),
                    "fix": readability.get("recommendations", [])
                })
        
        return issues
    
    def _assess_value_prop(self, page_analyses: Dict) -> Dict:
        """Assess overall value proposition clarity"""
        homepage = page_analyses.get("homepage", {})
        value_prop = homepage.get("value_prop", {})
        
        return {
            "score": 100 - (len(value_prop.get("issues", [])) * 20),
            "issues": value_prop.get("issues", []),
            "has_clear_headline": value_prop.get("has_clear_headline", False),
            "benefit_focused": value_prop.get("benefit_focused", False),
            "specificity_score": value_prop.get("specificity_score", 0)
        }
    
    def _analyze_jargon_usage(self, page_analyses: Dict) -> Dict:
        """Analyze jargon usage across site"""
        total_jargon = 0
        total_words = 0
        
        for analysis in page_analyses.values():
            jargon = analysis.get("jargon", {})
            total_jargon += jargon.get("jargon_count", 0)
            total_words += jargon.get("total_words", 0)
        
        if total_words > 0:
            overall_density = (total_jargon / total_words) * 100
        else:
            overall_density = 0
        
        return {
            "overall_density": overall_density,
            "total_jargon_found": total_jargon,
            "severity": "high" if overall_density > 3 else "medium" if overall_density > 1 else "low"
        }
    
    def _evaluate_ctas(self, page_analyses: Dict) -> Dict:
        """Evaluate CTA effectiveness across site"""
        all_ctas = []
        
        for analysis in page_analyses.values():
            cta_data = analysis.get("ctas", {})
            all_ctas.extend(cta_data.get("weak_ctas", []))
        
        return {
            "weak_cta_count": len(all_ctas),
            "examples": all_ctas[:5],
            "recommendations": [
                "Replace 'Learn More' with 'See How It Works'",
                "Replace 'Submit' with 'Get Started'",
                "Add urgency: 'Start Free Trial Today'"
            ] if all_ctas else []
        }
    
    def _assess_social_proof(self, page_analyses: Dict) -> Dict:
        """Assess social proof quality"""
        all_issues = []
        total_score = 0
        count = 0
        
        for analysis in page_analyses.values():
            social = analysis.get("social_proof", {})
            if social:
                all_issues.extend(social.get("issues", []))
                total_score += social.get("authenticity_score", 0)
                count += 1
        
        return {
            "average_score": total_score / count if count > 0 else 0,
            "issues": all_issues,
            "missing_elements": [i["type"] for i in all_issues]
        }
    
    def _analyze_emotional_appeal(self, page_analyses: Dict) -> Dict:
        """Analyze emotional appeal effectiveness"""
        total_effectiveness = []
        
        for analysis in page_analyses.values():
            emotions = analysis.get("emotional_appeal", {})
            if emotions:
                total_effectiveness.append(emotions.get("effectiveness", "low"))
        
        # Determine overall effectiveness
        if not total_effectiveness:
            overall = "low"
        else:
            high_count = sum(1 for e in total_effectiveness if e == "high")
            if high_count > len(total_effectiveness) / 2:
                overall = "high"
            elif any(e == "medium" for e in total_effectiveness):
                overall = "medium"
            else:
                overall = "low"
        
        return {
            "overall_effectiveness": overall,
            "recommendation": "Add more power words and emotional triggers" if overall == "low" else None
        }
    
    def _calculate_quality_score(self, results: Dict) -> int:
        """Calculate overall content quality score"""
        score = 50  # Base score
        
        # Readability
        if not results["readability_issues"]:
            score += 15
        else:
            score -= len(results["readability_issues"]) * 5
        
        # Value proposition
        score += results["value_prop_clarity"].get("score", 0) / 10
        
        # Jargon
        if results["jargon_analysis"].get("severity") == "low":
            score += 10
        elif results["jargon_analysis"].get("severity") == "high":
            score -= 15
        
        # CTAs
        if results["cta_effectiveness"].get("weak_cta_count", 0) == 0:
            score += 10
        else:
            score -= results["cta_effectiveness"]["weak_cta_count"] * 2
        
        # Social proof
        score += results["social_proof_quality"].get("average_score", 0) / 10
        
        # Emotional appeal
        if results["emotional_triggers"].get("overall_effectiveness") == "high":
            score += 15
        elif results["emotional_triggers"].get("overall_effectiveness") == "low":
            score -= 10
        
        return max(0, min(100, score))
    
    def _prioritize_improvements(self, results: Dict) -> List[Dict]:
        """Prioritize content improvements by impact"""
        priorities = []
        
        # Value prop issues are highest priority
        for issue in results["value_prop_clarity"].get("issues", []):
            priorities.append({
                "priority": "critical",
                "area": "value_proposition",
                "issue": issue["type"],
                "fix": issue["fix"],
                "impact": "50% of visitors don't understand your value"
            })
        
        # Readability issues
        for issue in results["readability_issues"][:2]:
            priorities.append({
                "priority": "high",
                "area": "readability",
                "page": issue["page"],
                "fix": issue["fix"][0] if issue["fix"] else "Simplify content",
                "impact": "Losing non-technical audience"
            })
        
        # Social proof
        if results["social_proof_quality"].get("average_score", 0) < 50:
            priorities.append({
                "priority": "high",
                "area": "social_proof",
                "fix": "Add testimonials, logos, and case studies",
                "impact": "Missing 20-30% conversion boost"
            })
        
        return priorities[:5]
    
    def _identify_quick_wins(self, results: Dict) -> List[Dict]:
        """Identify quick content improvements"""
        quick_wins = []
        
        # CTA fixes are quick
        if results["cta_effectiveness"].get("weak_cta_count", 0) > 0:
            quick_wins.append({
                "fix": "Replace weak CTAs with action-oriented ones",
                "time": "30 minutes",
                "impact": "5-10% conversion improvement",
                "examples": results["cta_effectiveness"].get("recommendations", [])
            })
        
        # Adding dates to content
        if results["content_freshness"].get("missing_dates"):
            quick_wins.append({
                "fix": "Add publication dates to blog posts",
                "time": "15 minutes",
                "impact": "Builds trust and relevance"
            })
        
        return quick_wins
    
    def _compare_to_best_practices(self, results: Dict) -> Dict:
        """Compare to content best practices"""
        comparison = {
            "doing_well": [],
            "needs_improvement": [],
            "benchmark_scores": {
                "readability": 70,  # Target Flesch score
                "jargon_density": 1,  # Max 1%
                "value_prop_clarity": 80,
                "social_proof": 75,
                "emotional_appeal": "medium"
            }
        }
        
        # Compare scores
        if results["overall_quality_score"] > 70:
            comparison["doing_well"].append("Overall content quality")
        
        if results["jargon_analysis"].get("overall_density", 0) > 1:
            comparison["needs_improvement"].append({
                "area": "Jargon reduction",
                "current": f"{results['jargon_analysis']['overall_density']:.1f}%",
                "target": "< 1%"
            })
        
        return comparison