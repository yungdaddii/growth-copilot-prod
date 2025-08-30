"""
Conversation Context Manager
Tracks user context, preferences, and conversation history for personalized responses
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog
from typing import Optional
import redis

from app.utils.cache import get_redis
from app.models.analysis import Industry

logger = structlog.get_logger()


class ConversationContext:
    """Manages conversation context and user preferences"""
    
    def __init__(self, session_id: str, redis_client: Optional[redis.Redis] = None):
        self.session_id = session_id
        self.redis = redis_client  # Don't auto-get redis for safety
        self.context_key = f"context:{session_id}"
        self.ttl = 3600 * 24  # 24 hours
        
        # Initialize or load context
        self.context = self._load_context()
    
    def _load_context(self) -> Dict[str, Any]:
        """Load existing context from Redis or create new"""
        try:
            if self.redis:
                data = self.redis.get(self.context_key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.warning(f"Failed to load context from Redis: {e}")
        
        # Default context structure
        return {
            "session_id": self.session_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "domains_analyzed": [],
            "current_domain": None,
            "user_profile": {
                "industry": None,
                "business_type": None,  # B2B, B2C, B2B2C
                "company_size": None,   # startup, smb, enterprise
                "role": None,          # marketer, founder, developer
                "priorities": [],      # conversion, traffic, technical, cost
                "technical_level": "medium"  # low, medium, high
            },
            "conversation_history": {
                "topics_discussed": [],
                "issues_highlighted": [],
                "recommendations_given": [],
                "questions_asked": [],
                "follow_ups_requested": []
            },
            "preferences": {
                "response_style": "balanced",  # concise, balanced, detailed
                "wants_code_examples": False,
                "wants_competitor_names": True,
                "focus_areas": []  # areas user cares about most
            },
            "current_analysis": {
                "domain": None,
                "top_issues": [],
                "quick_wins": [],
                "competitors": [],
                "key_metrics": {}
            }
        }
    
    def save(self) -> bool:
        """Save context to Redis"""
        try:
            if self.redis:
                self.context["updated_at"] = datetime.utcnow().isoformat()
                self.redis.setex(
                    self.context_key,
                    self.ttl,
                    json.dumps(self.context)
                )
                return True
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
        return False
    
    def update_user_profile(self, **kwargs) -> None:
        """Update user profile information"""
        for key, value in kwargs.items():
            if key in self.context["user_profile"]:
                self.context["user_profile"][key] = value
        self.save()
    
    def add_message(self, role: str, content: str, intent: Optional[str] = None) -> None:
        """Track a message in the conversation"""
        self.context["message_count"] += 1
        
        # Track topics and questions
        if role == "user":
            self.context["conversation_history"]["questions_asked"].append({
                "content": content[:200],  # First 200 chars
                "intent": intent,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Infer preferences from questions
            self._infer_preferences(content)
        
        # Keep only last 20 items in each history list
        for key in self.context["conversation_history"]:
            if isinstance(self.context["conversation_history"][key], list):
                self.context["conversation_history"][key] = \
                    self.context["conversation_history"][key][-20:]
        
        self.save()
    
    def _infer_preferences(self, message: str) -> None:
        """Infer user preferences from their messages"""
        message_lower = message.lower()
        
        # Detect technical level
        technical_indicators = {
            "high": ["api", "webhook", "json", "schema", "implementation", "code", 
                    "deploy", "git", "css", "javascript", "python"],
            "low": ["simple", "easy", "non-technical", "explain", "what is", 
                   "help me understand", "basics"]
        }
        
        for level, indicators in technical_indicators.items():
            if any(ind in message_lower for ind in indicators):
                self.context["user_profile"]["technical_level"] = level
                break
        
        # Detect focus areas
        focus_indicators = {
            "conversion": ["conversion", "signup", "trial", "demo", "form", "cta"],
            "traffic": ["traffic", "seo", "organic", "visitors", "growth"],
            "performance": ["speed", "slow", "performance", "loading", "optimize"],
            "competitors": ["competitor", "vs", "compare", "versus", "competition"],
            "mobile": ["mobile", "responsive", "phone", "tablet"],
            "cost": ["cost", "price", "budget", "roi", "expensive", "cheap"]
        }
        
        for area, indicators in focus_indicators.items():
            if any(ind in message_lower for ind in indicators):
                if area not in self.context["preferences"]["focus_areas"]:
                    self.context["preferences"]["focus_areas"].append(area)
        
        # Detect if user wants code
        if any(word in message_lower for word in ["code", "snippet", "example", "implement"]):
            self.context["preferences"]["wants_code_examples"] = True
        
        # Detect response style preference
        if any(word in message_lower for word in ["detail", "explain", "more", "deeper"]):
            self.context["preferences"]["response_style"] = "detailed"
        elif any(word in message_lower for word in ["quick", "summary", "brief", "short"]):
            self.context["preferences"]["response_style"] = "concise"
    
    def set_current_analysis(self, domain: str, analysis_results: Dict[str, Any]) -> None:
        """Store current analysis context"""
        self.context["current_domain"] = domain
        
        if domain not in self.context["domains_analyzed"]:
            self.context["domains_analyzed"].append(domain)
        
        # Extract key information for context
        self.context["current_analysis"]["domain"] = domain
        
        # Store top issues
        if "recommendations" in analysis_results:
            self.context["current_analysis"]["top_issues"] = [
                {
                    "category": rec.get("category"),
                    "issue": rec.get("issue"),
                    "priority": rec.get("priority")
                }
                for rec in analysis_results["recommendations"][:5]
            ]
        
        # Store quick wins
        if "quick_wins" in analysis_results:
            self.context["current_analysis"]["quick_wins"] = [
                qw.get("title") for qw in analysis_results["quick_wins"][:3]
            ]
        
        # Store competitors
        if "competitors" in analysis_results:
            self.context["current_analysis"]["competitors"] = [
                comp.get("name", comp.get("domain"))
                for comp in analysis_results.get("competitors", {}).get("competitors", [])[:3]
            ]
        
        # Store key metrics
        metrics = {}
        if "performance" in analysis_results:
            metrics["performance_score"] = analysis_results["performance"].get("score")
        if "conversion" in analysis_results:
            metrics["form_fields"] = analysis_results["conversion"].get("form_fields")
            metrics["has_pricing"] = analysis_results["conversion"].get("has_pricing")
        if "traffic" in analysis_results:
            metrics["monthly_visits"] = analysis_results["traffic"].get("estimated_monthly_visits")
        
        self.context["current_analysis"]["key_metrics"] = metrics
        self.save()
    
    def add_recommendation_given(self, recommendation: Dict[str, Any]) -> None:
        """Track recommendations that have been given"""
        self.context["conversation_history"]["recommendations_given"].append({
            "issue": recommendation.get("issue"),
            "category": recommendation.get("category"),
            "timestamp": datetime.utcnow().isoformat()
        })
        self.save()
    
    def add_topic_discussed(self, topic: str) -> None:
        """Track topics that have been discussed"""
        if topic not in self.context["conversation_history"]["topics_discussed"]:
            self.context["conversation_history"]["topics_discussed"].append(topic)
        self.save()
    
    def get_personalization_params(self) -> Dict[str, Any]:
        """Get parameters for personalizing responses"""
        return {
            "technical_level": self.context["user_profile"]["technical_level"],
            "response_style": self.context["preferences"]["response_style"],
            "wants_code": self.context["preferences"]["wants_code_examples"],
            "focus_areas": self.context["preferences"]["focus_areas"],
            "industry": self.context["user_profile"]["industry"],
            "message_count": self.context["message_count"],
            "topics_discussed": self.context["conversation_history"]["topics_discussed"][-5:],
            "current_domain": self.context["current_domain"]
        }
    
    def should_vary_response(self) -> bool:
        """Determine if we should vary the response to avoid repetition"""
        # Vary response if we've given similar recommendations recently
        recent_recs = self.context["conversation_history"]["recommendations_given"][-3:]
        if len(recent_recs) >= 2:
            categories = [r["category"] for r in recent_recs]
            # If we've talked about the same category multiple times, vary
            return len(set(categories)) < len(categories)
        return False
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation so far"""
        summary_parts = []
        
        if self.context["current_domain"]:
            summary_parts.append(f"Analyzing {self.context['current_domain']}")
        
        if self.context["conversation_history"]["topics_discussed"]:
            topics = ", ".join(self.context["conversation_history"]["topics_discussed"][-3:])
            summary_parts.append(f"Discussed: {topics}")
        
        if self.context["current_analysis"]["top_issues"]:
            summary_parts.append(f"Found {len(self.context['current_analysis']['top_issues'])} issues")
        
        return " | ".join(summary_parts) if summary_parts else "New conversation"
    
    def get_undiscussed_issues(self) -> List[Dict[str, Any]]:
        """Get issues that haven't been discussed yet"""
        discussed_categories = [
            rec["category"] 
            for rec in self.context["conversation_history"]["recommendations_given"]
        ]
        
        undiscussed = []
        for issue in self.context["current_analysis"]["top_issues"]:
            if issue["category"] not in discussed_categories:
                undiscussed.append(issue)
        
        return undiscussed
    
    def clear(self) -> None:
        """Clear the context"""
        if self.redis:
            self.redis.delete(self.context_key)
        self.context = self._load_context()