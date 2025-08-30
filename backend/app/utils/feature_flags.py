"""
Feature Flags for gradual rollout of new features
Safe deployment without breaking production
"""

import os
from typing import Optional
import structlog

logger = structlog.get_logger()


class FeatureFlags:
    """Manage feature flags for safe rollout"""
    
    # Feature flag environment variables
    FLAGS = {
        "enhanced_nlp": "ENABLE_ENHANCED_NLP",
        "context_memory": "ENABLE_CONTEXT_MEMORY",
        "specific_recommendations": "ENABLE_SPECIFIC_RECS",
        "code_examples": "ENABLE_CODE_EXAMPLES",
        "dynamic_prompts": "ENABLE_DYNAMIC_PROMPTS"
    }
    
    @classmethod
    def is_enabled(cls, feature: str, user_id: Optional[str] = None) -> bool:
        """Check if a feature is enabled"""
        
        # Check environment variable
        env_var = cls.FLAGS.get(feature)
        if not env_var:
            return False
        
        env_value = os.getenv(env_var, "false").lower()
        
        # Handle different values
        if env_value == "true":
            return True
        elif env_value == "false":
            return False
        elif env_value.endswith("%"):
            # Percentage rollout
            try:
                percentage = int(env_value[:-1])
                if user_id:
                    # Consistent hashing for user
                    import hashlib
                    hash_val = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
                    return (hash_val % 100) < percentage
                else:
                    # Random for anonymous
                    import random
                    return random.randint(1, 100) <= percentage
            except ValueError:
                logger.warning(f"Invalid percentage value for {feature}: {env_value}")
                return False
        else:
            return False
    
    @classmethod
    def get_enabled_features(cls, user_id: Optional[str] = None) -> dict:
        """Get all enabled features for a user"""
        return {
            feature: cls.is_enabled(feature, user_id)
            for feature in cls.FLAGS.keys()
        }
    
    @classmethod
    def log_feature_usage(cls, feature: str, user_id: Optional[str] = None):
        """Log when a feature is used"""
        logger.info(
            "Feature flag used",
            feature=feature,
            enabled=cls.is_enabled(feature, user_id),
            user_id=user_id
        )