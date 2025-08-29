"""
Pricing Intelligence Extractor
Extracts and analyzes pricing strategy from websites
"""

import httpx
import re
import json
from typing import Dict, Any, List, Optional, Tuple
import structlog
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class PricingIntelligenceAnalyzer:
    """
    Extracts and analyzes pricing intelligence:
    - Price points and tiers
    - Pricing model (subscription, one-time, usage-based)
    - Free trial/freemium availability
    - Money-back guarantees
    - Price anchoring tactics
    - Competitor price positioning
    - Discount strategies
    - Currency and localization
    - Hidden costs analysis
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(20.0, connect=10.0)
        
        # Currency symbols and patterns
        self.currency_symbols = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR',
            'R$': 'BRL',
            'A$': 'AUD',
            'C$': 'CAD'
        }
        
        # Pricing model indicators
        self.subscription_indicators = [
            '/month', '/mo', 'per month', 'monthly',
            '/year', '/yr', 'per year', 'annual', 'yearly',
            'subscription', 'subscribe', 'billed'
        ]
        
        self.usage_based_indicators = [
            'per user', 'per seat', 'per gb', 'per api call',
            'pay as you go', 'usage-based', 'per transaction',
            'per employee', 'per contact', 'per lead'
        ]
        
    async def analyze(self, domain: str, competitor_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract and analyze pricing intelligence
        """
        cache_key = f"pricing_intelligence:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "has_pricing_page": False,
            "pricing_transparency": "hidden",
            "pricing_model": None,
            "price_points": [],
            "tiers": [],
            "free_options": {},
            "guarantees": [],
            "discounts": [],
            "psychological_tactics": [],
            "hidden_costs": [],
            "pricing_complexity": "simple",
            "competitor_comparison": {},
            "pricing_opportunities": [],
            "revenue_optimization": {},
            "pricing_score": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Find pricing page
                pricing_url = await self._find_pricing_page(domain, client)
                
                if pricing_url:
                    results["has_pricing_page"] = True
                    
                    # Extract pricing data
                    pricing_data = await self._extract_pricing_data(pricing_url, client)
                    
                    # Analyze pricing structure
                    results["pricing_transparency"] = self._assess_transparency(pricing_data)
                    results["pricing_model"] = self._identify_pricing_model(pricing_data)
                    results["price_points"] = pricing_data.get("prices", [])
                    results["tiers"] = self._analyze_tiers(pricing_data)
                    results["free_options"] = self._analyze_free_options(pricing_data)
                    results["guarantees"] = self._find_guarantees(pricing_data)
                    results["discounts"] = self._find_discounts(pricing_data)
                    results["psychological_tactics"] = self._identify_psychological_tactics(pricing_data)
                    results["hidden_costs"] = self._find_hidden_costs(pricing_data)
                    results["pricing_complexity"] = self._assess_complexity(pricing_data)
                    
                    # Revenue optimization analysis
                    results["revenue_optimization"] = self._analyze_revenue_optimization(
                        pricing_data, results["tiers"]
                    )
                else:
                    # No pricing page found - analyze homepage for clues
                    homepage_data = await self._extract_homepage_pricing_clues(domain, client)
                    results.update(homepage_data)
                
                # Competitor comparison if provided
                if competitor_domains:
                    results["competitor_comparison"] = await self._compare_competitor_pricing(
                        results, competitor_domains, client
                    )
                
                # Identify opportunities
                results["pricing_opportunities"] = self._identify_opportunities(results)
                
                # Calculate pricing score
                results["pricing_score"] = self._calculate_pricing_score(results)
                
                # Cache for 24 hours
                await cache_result(cache_key, results, ttl=86400)
        
        except Exception as e:
            logger.error(f"Pricing intelligence analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _find_pricing_page(self, domain: str, client: httpx.AsyncClient) -> Optional[str]:
        """Find the pricing page URL"""
        try:
            # Start with homepage
            homepage_url = f"https://{domain}"
            response = await client.get(homepage_url, follow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for pricing links
                pricing_patterns = [
                    'pricing', 'price', 'plans', 'cost', 'buy',
                    'subscribe', 'purchase', 'upgrade', 'rates'
                ]
                
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    text = link.get_text().lower()
                    
                    if any(pattern in href or pattern in text for pattern in pricing_patterns):
                        absolute_url = urljoin(homepage_url, link['href'])
                        
                        # Verify it's actually a pricing page
                        try:
                            pricing_response = await client.get(absolute_url, follow_redirects=True)
                            if pricing_response.status_code == 200:
                                # Check if page contains pricing information
                                if any(symbol in pricing_response.text for symbol in self.currency_symbols.keys()):
                                    return absolute_url
                        except:
                            continue
                
                # Try common pricing URLs
                common_paths = ['/pricing', '/plans', '/price', '/pricing-plans', '/subscribe']
                for path in common_paths:
                    try:
                        test_url = f"https://{domain}{path}"
                        test_response = await client.get(test_url, follow_redirects=True)
                        if test_response.status_code == 200:
                            if any(symbol in test_response.text for symbol in self.currency_symbols.keys()):
                                return test_url
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Error finding pricing page for {domain}: {e}")
        
        return None
    
    async def _extract_pricing_data(self, url: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Extract all pricing data from a page"""
        data = {
            "url": url,
            "prices": [],
            "raw_text": "",
            "structured_data": None,
            "features_by_tier": {},
            "cta_buttons": []
        }
        
        try:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                data["raw_text"] = soup.get_text()
                
                # Extract structured data if present
                json_ld = soup.find('script', type='application/ld+json')
                if json_ld:
                    try:
                        data["structured_data"] = json.loads(json_ld.string)
                    except:
                        pass
                
                # Extract prices using multiple methods
                prices = self._extract_prices_from_html(soup)
                data["prices"] = prices
                
                # Extract tier information
                data["features_by_tier"] = self._extract_tier_features(soup)
                
                # Extract CTAs
                data["cta_buttons"] = self._extract_ctas(soup)
        
        except Exception as e:
            logger.debug(f"Error extracting pricing data from {url}: {e}")
        
        return data
    
    def _extract_prices_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all price points from HTML"""
        prices = []
        
        # Method 1: Look for price patterns in text
        price_pattern = r'([$€£¥₹]\s*\d+(?:,\d{3})*(?:\.\d{2})?)'
        text = soup.get_text()
        matches = re.findall(price_pattern, text)
        
        for match in matches:
            # Clean and parse price
            currency_symbol = match[0]
            amount_str = re.sub(r'[^\d.]', '', match)
            try:
                amount = float(amount_str)
                
                # Find context (monthly, yearly, etc.)
                context = self._find_price_context(match, text)
                
                prices.append({
                    "amount": amount,
                    "currency": self.currency_symbols.get(currency_symbol, "USD"),
                    "period": context.get("period"),
                    "tier": context.get("tier"),
                    "raw": match
                })
            except:
                continue
        
        # Method 2: Look for price in specific elements
        price_elements = soup.find_all(class_=re.compile(r'price|cost|amount', re.I))
        for element in price_elements:
            element_text = element.get_text()
            element_matches = re.findall(price_pattern, element_text)
            for match in element_matches:
                # Avoid duplicates
                if match not in [p["raw"] for p in prices]:
                    currency_symbol = match[0]
                    amount_str = re.sub(r'[^\d.]', '', match)
                    try:
                        amount = float(amount_str)
                        
                        # Get tier name from parent elements
                        tier_name = self._find_tier_name(element)
                        
                        prices.append({
                            "amount": amount,
                            "currency": self.currency_symbols.get(currency_symbol, "USD"),
                            "tier": tier_name,
                            "raw": match
                        })
                    except:
                        continue
        
        # Remove duplicates and sort by amount
        unique_prices = []
        seen = set()
        for price in prices:
            key = (price["amount"], price.get("tier", ""))
            if key not in seen:
                seen.add(key)
                unique_prices.append(price)
        
        return sorted(unique_prices, key=lambda x: x["amount"])
    
    def _find_price_context(self, price: str, text: str) -> Dict[str, str]:
        """Find the context around a price (period, tier name, etc.)"""
        context = {}
        
        # Find position of price in text
        try:
            price_index = text.index(price)
            # Get surrounding text (100 chars before and after)
            start = max(0, price_index - 100)
            end = min(len(text), price_index + 100)
            surrounding = text[start:end].lower()
            
            # Check for period
            for indicator in self.subscription_indicators:
                if indicator in surrounding:
                    if 'month' in indicator:
                        context["period"] = "monthly"
                    elif 'year' in indicator or 'annual' in indicator:
                        context["period"] = "yearly"
                    break
            
            # Check for tier names
            tier_patterns = ['starter', 'basic', 'pro', 'professional', 'business', 'enterprise', 'premium', 'plus']
            for tier in tier_patterns:
                if tier in surrounding:
                    context["tier"] = tier.title()
                    break
        except:
            pass
        
        return context
    
    def _find_tier_name(self, element) -> Optional[str]:
        """Find tier name from element or its parents"""
        # Check element and parents for tier names
        tier_patterns = ['starter', 'basic', 'pro', 'professional', 'business', 'enterprise', 'premium', 'plus', 'free']
        
        current = element
        depth = 0
        while current and depth < 5:
            text = current.get_text().lower()
            for pattern in tier_patterns:
                if pattern in text:
                    return pattern.title()
            current = current.parent
            depth += 1
        
        return None
    
    def _extract_tier_features(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract features for each pricing tier"""
        features_by_tier = {}
        
        # Look for pricing cards/columns
        pricing_cards = soup.find_all(class_=re.compile(r'pricing-card|price-card|tier|plan', re.I))
        
        for card in pricing_cards:
            # Get tier name
            tier_name = None
            heading = card.find(['h2', 'h3', 'h4'])
            if heading:
                tier_name = heading.get_text().strip()
            
            if tier_name:
                # Get features (usually in lists)
                features = []
                for li in card.find_all('li'):
                    feature_text = li.get_text().strip()
                    if feature_text and len(feature_text) < 100:  # Avoid long paragraphs
                        features.append(feature_text)
                
                if features:
                    features_by_tier[tier_name] = features
        
        return features_by_tier
    
    def _extract_ctas(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract CTA buttons and their text"""
        ctas = []
        
        # Find all buttons and CTA links
        cta_elements = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta', re.I))
        
        for element in cta_elements:
            text = element.get_text().strip()
            if text and len(text) < 50:  # Reasonable CTA length
                ctas.append({
                    "text": text,
                    "type": self._classify_cta(text)
                })
        
        return ctas
    
    def _classify_cta(self, text: str) -> str:
        """Classify CTA type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['free', 'trial', 'try']):
            return "free_trial"
        elif any(word in text_lower for word in ['demo', 'schedule', 'book']):
            return "demo"
        elif any(word in text_lower for word in ['buy', 'purchase', 'get started']):
            return "purchase"
        elif any(word in text_lower for word in ['contact', 'talk', 'sales']):
            return "contact_sales"
        else:
            return "other"
    
    def _assess_transparency(self, pricing_data: Dict) -> str:
        """Assess pricing transparency level"""
        prices = pricing_data.get("prices", [])
        raw_text = pricing_data.get("raw_text", "").lower()
        
        if len(prices) >= 3:
            return "transparent"
        elif len(prices) > 0:
            return "partial"
        elif "contact" in raw_text and "sales" in raw_text:
            return "contact_only"
        else:
            return "hidden"
    
    def _identify_pricing_model(self, pricing_data: Dict) -> str:
        """Identify the pricing model used"""
        raw_text = pricing_data.get("raw_text", "").lower()
        
        # Check for subscription
        if any(indicator in raw_text for indicator in self.subscription_indicators):
            if any(indicator in raw_text for indicator in self.usage_based_indicators):
                return "hybrid_subscription_usage"
            return "subscription"
        
        # Check for usage-based
        if any(indicator in raw_text for indicator in self.usage_based_indicators):
            return "usage_based"
        
        # Check for one-time
        if any(indicator in raw_text for indicator in ['one-time', 'lifetime', 'perpetual']):
            return "one_time"
        
        # Check for freemium
        if 'free plan' in raw_text or 'free tier' in raw_text:
            return "freemium"
        
        return "unknown"
    
    def _analyze_tiers(self, pricing_data: Dict) -> List[Dict]:
        """Analyze pricing tiers structure"""
        tiers = []
        prices = pricing_data.get("prices", [])
        features_by_tier = pricing_data.get("features_by_tier", {})
        
        # Group prices by tier
        tier_prices = {}
        for price in prices:
            tier = price.get("tier", "Unknown")
            if tier not in tier_prices:
                tier_prices[tier] = []
            tier_prices[tier].append(price)
        
        # Build tier information
        for tier_name, tier_price_list in tier_prices.items():
            tier_info = {
                "name": tier_name,
                "prices": tier_price_list,
                "features": features_by_tier.get(tier_name, []),
                "positioning": self._determine_tier_positioning(tier_name, tier_price_list)
            }
            
            # Find lowest price for this tier
            if tier_price_list:
                min_price = min(p["amount"] for p in tier_price_list)
                tier_info["starting_price"] = min_price
            
            tiers.append(tier_info)
        
        # Sort by price
        tiers.sort(key=lambda x: x.get("starting_price", float('inf')))
        
        # Analyze tier strategy
        if len(tiers) >= 3:
            # Check for decoy effect (middle tier pricing)
            if len(tiers) == 3:
                prices = [t.get("starting_price", 0) for t in tiers]
                if prices[1] and prices[2]:  # Middle and high tier have prices
                    ratio = prices[1] / prices[2] if prices[2] > 0 else 0
                    if 0.6 < ratio < 0.8:
                        # Middle tier is priced to make high tier look better
                        tiers[1]["psychological_role"] = "decoy"
                        tiers[2]["psychological_role"] = "target"
        
        return tiers
    
    def _determine_tier_positioning(self, tier_name: str, prices: List[Dict]) -> str:
        """Determine how a tier is positioned"""
        tier_lower = tier_name.lower()
        
        if any(word in tier_lower for word in ['free', 'starter', 'basic']):
            return "entry"
        elif any(word in tier_lower for word in ['pro', 'professional', 'business']):
            return "mainstream"
        elif any(word in tier_lower for word in ['enterprise', 'premium', 'ultimate']):
            return "premium"
        else:
            return "standard"
    
    def _analyze_free_options(self, pricing_data: Dict) -> Dict[str, Any]:
        """Analyze free trial and freemium options"""
        free_options = {
            "has_free_trial": False,
            "trial_length": None,
            "requires_credit_card": None,
            "has_free_plan": False,
            "free_plan_limits": []
        }
        
        raw_text = pricing_data.get("raw_text", "").lower()
        
        # Check for free trial
        trial_patterns = [
            r'(\d+)[\s-]?day(?:s)?\s+(?:free\s+)?trial',
            r'try\s+(?:free\s+)?for\s+(\d+)\s+days?',
            r'free\s+trial'
        ]
        
        for pattern in trial_patterns:
            match = re.search(pattern, raw_text)
            if match:
                free_options["has_free_trial"] = True
                if match.groups():
                    try:
                        free_options["trial_length"] = int(match.group(1))
                    except:
                        pass
                break
        
        # Check for credit card requirement
        if free_options["has_free_trial"]:
            if 'no credit card' in raw_text or 'no card' in raw_text:
                free_options["requires_credit_card"] = False
            elif 'credit card required' in raw_text:
                free_options["requires_credit_card"] = True
        
        # Check for free plan
        if 'free plan' in raw_text or 'free forever' in raw_text or '$0' in raw_text:
            free_options["has_free_plan"] = True
            
            # Extract limits
            limit_patterns = [
                r'up to (\d+) users?',
                r'(\d+) projects?',
                r'(\d+(?:gb|mb|kb))',
                r'limited to (\d+)'
            ]
            
            for pattern in limit_patterns:
                matches = re.findall(pattern, raw_text)
                for match in matches:
                    free_options["free_plan_limits"].append(match)
        
        return free_options
    
    def _find_guarantees(self, pricing_data: Dict) -> List[Dict]:
        """Find money-back guarantees and other assurances"""
        guarantees = []
        raw_text = pricing_data.get("raw_text", "").lower()
        
        guarantee_patterns = [
            (r'(\d+)[\s-]?day(?:s)?\s+money[\s-]?back', 'money_back'),
            (r'money[\s-]?back\s+guarantee', 'money_back'),
            (r'(?:full\s+)?refund', 'refund'),
            (r'no\s+risk', 'no_risk'),
            (r'satisfaction\s+guarantee', 'satisfaction'),
            (r'cancel\s+(?:anytime|any\s+time)', 'cancel_anytime')
        ]
        
        for pattern, guarantee_type in guarantee_patterns:
            match = re.search(pattern, raw_text)
            if match:
                guarantee = {
                    "type": guarantee_type,
                    "text": match.group(0)
                }
                
                # Extract duration if present
                if match.groups():
                    try:
                        guarantee["duration_days"] = int(match.group(1))
                    except:
                        pass
                
                guarantees.append(guarantee)
        
        return guarantees
    
    def _find_discounts(self, pricing_data: Dict) -> List[Dict]:
        """Find discount strategies"""
        discounts = []
        raw_text = pricing_data.get("raw_text", "").lower()
        
        # Annual discount
        annual_patterns = [
            r'save\s+(\d+)%?\s+(?:with\s+)?annual',
            r'(\d+)%?\s+off\s+(?:with\s+)?annual',
            r'annual(?:ly)?\s+billing\s+saves?\s+(\d+)%?'
        ]
        
        for pattern in annual_patterns:
            match = re.search(pattern, raw_text)
            if match:
                try:
                    discount_amount = int(match.group(1))
                    discounts.append({
                        "type": "annual_discount",
                        "amount": discount_amount,
                        "unit": "percent"
                    })
                    break
                except:
                    pass
        
        # Volume discounts
        if 'volume discount' in raw_text or 'bulk pricing' in raw_text:
            discounts.append({
                "type": "volume_discount",
                "description": "Volume discounts available"
            })
        
        # Limited time offers
        limited_patterns = [
            r'limited\s+time',
            r'ends\s+soon',
            r'special\s+offer',
            r'(\d+)%\s+off'
        ]
        
        for pattern in limited_patterns:
            if re.search(pattern, raw_text):
                discounts.append({
                    "type": "limited_time_offer",
                    "creates_urgency": True
                })
                break
        
        return discounts
    
    def _identify_psychological_tactics(self, pricing_data: Dict) -> List[Dict]:
        """Identify psychological pricing tactics"""
        tactics = []
        prices = pricing_data.get("prices", [])
        raw_text = pricing_data.get("raw_text", "").lower()
        
        # Charm pricing (ending in 9)
        charm_prices = [p for p in prices if str(p["amount"]).endswith(('9', '.99', '.95'))]
        if charm_prices:
            tactics.append({
                "type": "charm_pricing",
                "description": "Prices ending in 9 to appear cheaper",
                "examples": [p["amount"] for p in charm_prices[:3]]
            })
        
        # Anchoring (showing high price first)
        if prices and len(prices) >= 3:
            if prices[0]["amount"] > prices[-1]["amount"]:
                tactics.append({
                    "type": "price_anchoring",
                    "description": "Showing expensive option first",
                    "anchor_price": prices[0]["amount"]
                })
        
        # Decoy effect (middle option)
        tiers = pricing_data.get("features_by_tier", {})
        if len(tiers) == 3 and len(prices) >= 3:
            # Check if middle tier is positioned to make high tier attractive
            middle_price = prices[1]["amount"] if len(prices) > 1 else 0
            high_price = prices[2]["amount"] if len(prices) > 2 else 0
            if middle_price and high_price:
                ratio = middle_price / high_price
                if 0.7 < ratio < 0.85:
                    tactics.append({
                        "type": "decoy_effect",
                        "description": "Middle tier priced to make premium look better",
                        "decoy_price": middle_price,
                        "target_price": high_price
                    })
        
        # Most popular badge
        if 'most popular' in raw_text or 'recommended' in raw_text:
            tactics.append({
                "type": "social_proof_nudge",
                "description": "Using 'Most Popular' to influence choice"
            })
        
        # Loss aversion
        if 'save' in raw_text or 'discount' in raw_text:
            tactics.append({
                "type": "loss_aversion",
                "description": "Emphasizing savings/discounts"
            })
        
        return tactics
    
    def _find_hidden_costs(self, pricing_data: Dict) -> List[Dict]:
        """Identify potential hidden costs"""
        hidden_costs = []
        raw_text = pricing_data.get("raw_text", "").lower()
        
        # Setup fees
        if 'setup fee' in raw_text or 'implementation' in raw_text:
            hidden_costs.append({
                "type": "setup_fee",
                "description": "Additional setup or implementation costs"
            })
        
        # Overage charges
        if 'overage' in raw_text or 'additional usage' in raw_text:
            hidden_costs.append({
                "type": "overage_charges",
                "description": "Charges for exceeding limits"
            })
        
        # Add-ons
        if 'add-on' in raw_text or 'additional features' in raw_text:
            hidden_costs.append({
                "type": "required_addons",
                "description": "Essential features cost extra"
            })
        
        # Support costs
        if 'support sold separately' in raw_text or 'premium support' in raw_text:
            hidden_costs.append({
                "type": "support_costs",
                "description": "Support requires additional payment"
            })
        
        # Transaction fees
        if 'transaction fee' in raw_text or 'processing fee' in raw_text:
            hidden_costs.append({
                "type": "transaction_fees",
                "description": "Per-transaction charges"
            })
        
        return hidden_costs
    
    def _assess_complexity(self, pricing_data: Dict) -> str:
        """Assess pricing complexity"""
        prices = pricing_data.get("prices", [])
        features_by_tier = pricing_data.get("features_by_tier", {})
        
        # Count complexity factors
        complexity_score = 0
        
        # Many price points
        if len(prices) > 6:
            complexity_score += 2
        elif len(prices) > 4:
            complexity_score += 1
        
        # Many tiers
        if len(features_by_tier) > 4:
            complexity_score += 2
        elif len(features_by_tier) > 3:
            complexity_score += 1
        
        # Usage-based components
        raw_text = pricing_data.get("raw_text", "").lower()
        if any(indicator in raw_text for indicator in self.usage_based_indicators):
            complexity_score += 1
        
        # Hidden costs
        if self._find_hidden_costs(pricing_data):
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "moderate"
        else:
            return "simple"
    
    def _analyze_revenue_optimization(self, pricing_data: Dict, tiers: List[Dict]) -> Dict[str, Any]:
        """Analyze revenue optimization potential"""
        optimization = {
            "expansion_revenue_potential": "low",
            "pricing_ladder_quality": "poor",
            "upsell_opportunities": [],
            "recommendations": []
        }
        
        if len(tiers) >= 3:
            # Check pricing ladder
            prices = [t.get("starting_price", 0) for t in tiers if t.get("starting_price")]
            if len(prices) >= 3:
                # Good ladder has 2-3x jumps
                if prices[0] > 0:
                    jump1 = prices[1] / prices[0] if prices[0] > 0 else 0
                    jump2 = prices[2] / prices[1] if prices[1] > 0 else 0
                    
                    if 2 <= jump1 <= 3 and 2 <= jump2 <= 3:
                        optimization["pricing_ladder_quality"] = "excellent"
                        optimization["expansion_revenue_potential"] = "high"
                    elif 1.5 <= jump1 <= 4 and 1.5 <= jump2 <= 4:
                        optimization["pricing_ladder_quality"] = "good"
                        optimization["expansion_revenue_potential"] = "medium"
        
        # Check for upsell opportunities
        raw_text = pricing_data.get("raw_text", "").lower()
        
        if 'add-on' not in raw_text and 'additional' not in raw_text:
            optimization["upsell_opportunities"].append({
                "opportunity": "No add-ons offered",
                "potential": "15-25% revenue increase",
                "recommendation": "Add premium support, training, or API add-ons"
            })
        
        if 'annual' not in raw_text and 'yearly' not in raw_text:
            optimization["upsell_opportunities"].append({
                "opportunity": "No annual billing",
                "potential": "20-30% cash flow improvement",
                "recommendation": "Offer annual plans with 15-20% discount"
            })
        
        # Generate recommendations
        if optimization["pricing_ladder_quality"] == "poor":
            optimization["recommendations"].append(
                "Restructure pricing tiers with 2-3x price jumps"
            )
        
        if len(tiers) < 3:
            optimization["recommendations"].append(
                "Add a third tier to leverage decoy effect"
            )
        
        return optimization
    
    async def _extract_homepage_pricing_clues(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Extract pricing clues from homepage when no pricing page exists"""
        clues = {
            "pricing_mentions": [],
            "cta_strategy": "unknown"
        }
        
        try:
            response = await client.get(f"https://{domain}", follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text().lower()
                
                # Look for pricing mentions
                if 'contact sales' in text or 'get a quote' in text:
                    clues["cta_strategy"] = "enterprise_sales"
                    clues["pricing_mentions"].append("Enterprise/contact sales model")
                
                if 'free trial' in text:
                    clues["cta_strategy"] = "free_trial"
                    clues["pricing_mentions"].append("Offers free trial")
                
                if 'request demo' in text or 'book demo' in text:
                    clues["cta_strategy"] = "demo_first"
                    clues["pricing_mentions"].append("Demo-first approach")
        
        except Exception as e:
            logger.debug(f"Error extracting homepage pricing clues: {e}")
        
        return clues
    
    async def _compare_competitor_pricing(
        self, our_pricing: Dict, competitor_domains: List[str], client: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Compare pricing with competitors"""
        comparison = {
            "positioning": "unknown",
            "price_comparison": {},
            "feature_comparison": {},
            "insights": []
        }
        
        our_prices = our_pricing.get("price_points", [])
        our_min = min(p["amount"] for p in our_prices) if our_prices else 0
        
        competitor_prices = []
        
        for comp_domain in competitor_domains[:3]:  # Limit to 3 competitors
            comp_pricing = await self.analyze(comp_domain)
            if comp_pricing.get("price_points"):
                comp_min = min(p["amount"] for p in comp_pricing["price_points"])
                competitor_prices.append({
                    "domain": comp_domain,
                    "starting_price": comp_min,
                    "model": comp_pricing.get("pricing_model"),
                    "transparency": comp_pricing.get("pricing_transparency")
                })
        
        if competitor_prices and our_min:
            avg_competitor = sum(c["starting_price"] for c in competitor_prices) / len(competitor_prices)
            
            if our_min < avg_competitor * 0.7:
                comparison["positioning"] = "budget"
                comparison["insights"].append("Priced significantly below competitors")
            elif our_min > avg_competitor * 1.3:
                comparison["positioning"] = "premium"
                comparison["insights"].append("Premium pricing vs competitors")
            else:
                comparison["positioning"] = "competitive"
                comparison["insights"].append("Competitively priced")
            
            comparison["price_comparison"] = {
                "our_starting": our_min,
                "competitor_average": avg_competitor,
                "competitors": competitor_prices
            }
        
        return comparison
    
    def _identify_opportunities(self, results: Dict) -> List[Dict]:
        """Identify pricing optimization opportunities"""
        opportunities = []
        
        # No pricing page
        if not results["has_pricing_page"]:
            opportunities.append({
                "type": "missing_pricing_page",
                "impact": "high",
                "issue": "No pricing page found",
                "recommendation": "Create transparent pricing page",
                "potential": "50-70% more qualified leads"
            })
        
        # Hidden pricing
        if results["pricing_transparency"] in ["hidden", "contact_only"]:
            opportunities.append({
                "type": "hidden_pricing",
                "impact": "high",
                "issue": "Pricing not transparent",
                "recommendation": "Show at least starting prices",
                "potential": "67% of buyers skip vendors without pricing"
            })
        
        # No free trial
        if not results["free_options"].get("has_free_trial") and not results["free_options"].get("has_free_plan"):
            opportunities.append({
                "type": "no_free_option",
                "impact": "high",
                "issue": "No free trial or freemium",
                "recommendation": "Add 14-day free trial",
                "potential": "2-3x more signups"
            })
        
        # No annual discount
        discounts = results.get("discounts", [])
        if not any(d["type"] == "annual_discount" for d in discounts):
            opportunities.append({
                "type": "no_annual_discount",
                "impact": "medium",
                "issue": "No annual billing discount",
                "recommendation": "Offer 15-20% annual discount",
                "potential": "30% better cash flow"
            })
        
        # Too few tiers
        if len(results["tiers"]) < 3:
            opportunities.append({
                "type": "insufficient_tiers",
                "impact": "medium",
                "issue": f"Only {len(results['tiers'])} pricing tiers",
                "recommendation": "Add 3-4 tiers with clear value ladder",
                "potential": "20% higher average contract value"
            })
        
        # Complex pricing
        if results["pricing_complexity"] == "complex":
            opportunities.append({
                "type": "overly_complex",
                "impact": "medium",
                "issue": "Pricing too complex",
                "recommendation": "Simplify to 3-4 clear tiers",
                "potential": "Reduce decision fatigue"
            })
        
        return opportunities
    
    def _calculate_pricing_score(self, results: Dict) -> int:
        """Calculate overall pricing strategy score (0-100)"""
        score = 0
        
        # Has pricing page (20 points)
        if results["has_pricing_page"]:
            score += 20
        
        # Transparency (20 points)
        transparency_scores = {
            "transparent": 20,
            "partial": 10,
            "contact_only": 5,
            "hidden": 0
        }
        score += transparency_scores.get(results["pricing_transparency"], 0)
        
        # Free options (15 points)
        if results["free_options"].get("has_free_trial"):
            score += 10
        if results["free_options"].get("has_free_plan"):
            score += 5
        
        # Pricing model clarity (10 points)
        if results["pricing_model"] and results["pricing_model"] != "unknown":
            score += 10
        
        # Tiers (15 points)
        tier_count = len(results["tiers"])
        if tier_count >= 3:
            score += 15
        elif tier_count == 2:
            score += 10
        elif tier_count == 1:
            score += 5
        
        # Guarantees (10 points)
        if results["guarantees"]:
            score += 10
        
        # Discounts (5 points)
        if results["discounts"]:
            score += 5
        
        # Complexity penalty
        if results["pricing_complexity"] == "complex":
            score -= 10
        
        # No major hidden costs (5 points)
        if not results["hidden_costs"]:
            score += 5
        
        return max(0, min(100, score))