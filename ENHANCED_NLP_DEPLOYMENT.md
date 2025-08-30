# Enhanced NLP Deployment Guide

## Overview
This guide explains how to safely deploy the Enhanced NLP with Context Awareness feature to production.

## What's New
1. **ConversationContext** - Tracks user preferences and conversation history
2. **EnhancedNLPProcessor** - Generates personalized, specific responses
3. **Feature Flags** - Safe gradual rollout without risk

## Files Added/Modified
- `app/core/conversation_context.py` - NEW: Context management
- `app/core/enhanced_nlp.py` - NEW: Enhanced NLP processor
- `app/api/websocket_enhanced.py` - NEW: Enhanced WebSocket handler
- `app/utils/feature_flags.py` - NEW: Feature flag management
- `test_enhanced_nlp.py` - NEW: Test script

## Deployment Steps

### Step 1: Local Testing
```bash
# Run the test script
cd backend
python test_enhanced_nlp.py

# If all tests pass, continue
```

### Step 2: Environment Variables
Add to your `.env` file:
```env
# Start with disabled
ENABLE_ENHANCED_NLP=false
ENABLE_CONTEXT_MEMORY=false
ENABLE_SPECIFIC_RECS=false
ENABLE_CODE_EXAMPLES=false
ENABLE_DYNAMIC_PROMPTS=false
```

### Step 3: Test with Docker
```bash
# Build and run locally
docker-compose up --build

# Test with flag disabled (should work as before)
# Then enable flag and restart
ENABLE_ENHANCED_NLP=true docker-compose up
```

### Step 4: Deploy to Railway (Backend)

1. **Add environment variables in Railway:**
   ```
   ENABLE_ENHANCED_NLP=false
   ```

2. **Deploy the code:**
   ```bash
   git add .
   git commit -m "Add enhanced NLP with context (disabled by default)"
   git push railway main
   ```

3. **Test with flag disabled** - Everything should work as before

4. **Gradual rollout:**
   - Start with 10%: `ENABLE_ENHANCED_NLP=10%`
   - Monitor for 24 hours
   - Increase to 50%: `ENABLE_ENHANCED_NLP=50%`
   - Monitor for 24 hours
   - Full rollout: `ENABLE_ENHANCED_NLP=true`

### Step 5: Deploy to Vercel (Frontend)
No frontend changes required! The backend handles everything.

## Monitoring

### What to Watch
1. **Response Times** - Should stay under 2 seconds
2. **Redis Memory** - Context adds ~5KB per session
3. **Error Rates** - Should not increase
4. **User Feedback** - Check PostHog for engagement

### PostHog Events to Track
The system automatically tracks:
- `enhanced_nlp_enabled` - When feature is active
- `context_personalization` - When context affects response
- `specific_recommendation` - When specific data is provided

## Rollback Plan

### If Issues Occur:
1. **Immediate:** Set `ENABLE_ENHANCED_NLP=false` in Railway
2. **No restart needed** - Feature flag takes effect immediately
3. **Monitor** - Ensure normal operation resumes

### Fallback Behavior:
- If Redis fails → System uses standard NLP
- If context corrupted → New context created
- If enhanced NLP errors → Falls back to original

## Performance Impact

### Expected:
- **Memory:** +5KB per active session (Redis)
- **Response Time:** +100-200ms (for context lookup)
- **Redis Ops:** +3 operations per message

### Actual Limits:
- 10,000 concurrent sessions = 50MB Redis
- Well within Railway/Redis limits

## Testing Checklist

### Before Enabling in Production:
- [ ] Run `test_enhanced_nlp.py` locally
- [ ] Test with Docker Compose
- [ ] Verify Redis connection works
- [ ] Check feature flags work
- [ ] Test fallback behavior
- [ ] Monitor memory usage

### After Enabling:
- [ ] Check PostHog for errors
- [ ] Verify response times acceptable
- [ ] Monitor Redis memory
- [ ] Get user feedback
- [ ] Check conversation quality

## Code Integration

### To use enhanced WebSocket handler:
```python
# In app/main.py, replace:
from app.api import websocket

# With:
from app.api import websocket_enhanced as websocket
```

Or use feature flag to conditionally import:
```python
import os
if os.getenv("ENABLE_ENHANCED_NLP", "false").lower() == "true":
    from app.api import websocket_enhanced as websocket
else:
    from app.api import websocket
```

## Benefits Once Enabled

### Users Will Experience:
1. **Personalized Responses** - Adapts to their technical level
2. **Better Continuity** - Remembers previous topics
3. **Specific Recommendations** - Names exact fields, files, competitors
4. **Code Examples** - When technically proficient
5. **Progressive Disclosure** - Information revealed as needed

### Examples:

**Before (Generic):**
> "Your form has too many fields. Reduce them."

**After (Specific):**
> "Remove these 3 fields to increase conversions by 21%: Company Size (line 47), Phone Number (make optional), Job Title (infer from email domain)."

**Before (No Context):**
> "Your site has performance issues."

**After (With Context):**
> "Since you mentioned mobile users are important, the 4.2s load time on mobile is costing you ~500 visitors/day based on your 60% bounce rate."

## Support

If issues arise:
1. Check Railway logs: `railway logs`
2. Check Redis: `redis-cli ping`
3. Disable feature: Set flag to `false`
4. Report issue with PostHog event data

## Success Metrics

After 1 week, measure:
- User engagement increase (target: +20%)
- Follow-up questions (target: +30%)
- Session duration (target: +15%)
- Positive feedback (via PostHog surveys)

---

**Remember:** The beauty of feature flags is you can turn this off instantly if needed. Start small, monitor closely, and scale gradually!