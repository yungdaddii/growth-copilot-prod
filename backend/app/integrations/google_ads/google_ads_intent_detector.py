"""
Google Ads Intent Detector

Detects when users want to connect or query Google Ads data.
Integrates with the main NLP processor.
"""

from typing import Dict, Any, Optional
import re


class GoogleAdsIntentDetector:
    """Detect Google Ads related intents in user queries."""
    
    # Connection intent patterns
    CONNECT_PATTERNS = [
        r"connect.*google ads",
        r"link.*google ads",
        r"add.*google ads",
        r"setup.*google ads",
        r"integrate.*google ads",
        r"connect.*ads account",
        r"link.*campaigns",
        r"connect my ads"
    ]
    
    # Query intent patterns
    QUERY_PATTERNS = {
        "wasted_spend": [
            r"wast(e|ing|ed).*money",
            r"wast(e|ing|ed).*spend",
            r"wast(e|ing|ed).*budget",
            r"bleeding.*money",
            r"keywords.*not converting",
            r"zero conversion",
            r"no conversion"
        ],
        "performance": [
            r"how are.*ads",
            r"ads performance",
            r"campaign performance",
            r"google ads.*doing",
            r"ppc performance",
            r"ads metrics",
            r"ads results"
        ],
        "campaigns": [
            r"show.*campaigns",
            r"list.*campaigns",
            r"campaign.*status",
            r"which campaigns",
            r"campaign.*analysis"
        ],
        "cost": [
            r"cost per",
            r"cpa",
            r"cost.*acquisition",
            r"spend.*much",
            r"ads cost",
            r"expensive.*keywords"
        ],
        "optimization": [
            r"optimize.*ads",
            r"improve.*ads",
            r"better.*performance",
            r"increase.*conversions",
            r"reduce.*cost",
            r"improve.*roas"
        ],
        "disconnect": [
            r"disconnect.*google ads",
            r"remove.*google ads",
            r"unlink.*google ads",
            r"delete.*google ads.*connection"
        ]
    }
    
    @classmethod
    def detect_intent(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        Detect Google Ads related intent from user text.
        
        Args:
            text: User's query text
            
        Returns:
            Intent dict or None if no Google Ads intent detected
        """
        text_lower = text.lower()
        
        # Check for explicit Google Ads mention
        if not any(term in text_lower for term in ["google ads", "google ad", "adwords", "ppc", "campaigns"]):
            # Also check for implicit ads context
            if not any(term in text_lower for term in ["ads", "advertising", "keywords", "cpc", "cpa", "roas"]):
                return None
        
        # Check for connection intent
        for pattern in cls.CONNECT_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "type": "google_ads_connect",
                    "action": "initiate_oauth",
                    "platform": "google_ads"
                }
        
        # Check for disconnect intent
        for pattern in cls.QUERY_PATTERNS["disconnect"]:
            if re.search(pattern, text_lower):
                return {
                    "type": "google_ads_disconnect",
                    "action": "disconnect",
                    "platform": "google_ads"
                }
        
        # Check for query intents
        for query_type, patterns in cls.QUERY_PATTERNS.items():
            if query_type == "disconnect":
                continue
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return {
                        "type": "google_ads_query",
                        "query_type": query_type,
                        "platform": "google_ads",
                        "original_query": text
                    }
        
        # Default Google Ads query if mentioned but no specific pattern
        if "google ads" in text_lower or "adwords" in text_lower:
            return {
                "type": "google_ads_query",
                "query_type": "general",
                "platform": "google_ads",
                "original_query": text
            }
        
        return None
    
    @classmethod
    def extract_metrics(cls, text: str) -> Dict[str, Any]:
        """
        Extract specific metrics or values mentioned in query.
        
        Args:
            text: User's query text
            
        Returns:
            Dict of extracted metrics
        """
        metrics = {}
        
        # Extract time periods
        if "last month" in text.lower():
            metrics["period"] = "last_month"
        elif "this month" in text.lower():
            metrics["period"] = "this_month"
        elif "last week" in text.lower():
            metrics["period"] = "last_week"
        elif "today" in text.lower():
            metrics["period"] = "today"
        else:
            metrics["period"] = "last_30_days"  # Default
        
        # Extract threshold values
        cost_match = re.search(r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)", text)
        if cost_match:
            metrics["threshold_cost"] = float(cost_match.group(1).replace(",", ""))
        
        # Extract campaign names if mentioned
        if '"' in text:
            quoted = re.findall(r'"([^"]*)"', text)
            if quoted:
                metrics["campaign_names"] = quoted
        
        return metrics