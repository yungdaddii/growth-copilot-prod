# PostHog Analytics Setup Guide

## Overview
This guide explains how to set up PostHog analytics for Keelo (formerly Growth Co-pilot) to track user interactions and improve the product.

## Prerequisites
- PostHog account (sign up at https://posthog.com)
- Access to environment variables for both frontend and backend

## Setup Steps

### 1. Get Your PostHog Project API Key
1. Log in to your PostHog dashboard
2. Go to Project Settings → API Keys
3. Copy your Project API Key (starts with `phc_`)

### 2. Configure Environment Variables

#### Frontend (.env.local)
```env
NEXT_PUBLIC_POSTHOG_KEY=phc_YOUR_PROJECT_API_KEY
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_APP_VERSION=1.0.0
```

#### Backend (.env)
```env
POSTHOG_API_KEY=phc_YOUR_PROJECT_API_KEY
POSTHOG_HOST=https://app.posthog.com
ENV=production  # or development for testing
```

### 3. Verify Installation

#### Frontend Verification
1. Open browser developer tools
2. Go to Network tab
3. Filter by "posthog"
4. You should see requests to `https://app.posthog.com/e/` when interacting with the app

#### Backend Verification
1. Check backend logs for "PostHog analytics initialized"
2. Monitor PostHog dashboard for incoming events

## Events Being Tracked

### Frontend Events
- **Page Views**: Automatic tracking of all page visits
- **Analysis Events**:
  - `analysis_started`: When user initiates website analysis
  - `analysis_completed`: When analysis finishes
  - `analysis_failed`: When analysis encounters errors
- **User Actions**:
  - `send_message`: When user sends a chat message
  - `click_example`: When user clicks example domains
  - `toggle_theme`: When user switches dark/light mode
- **Engagement Metrics**:
  - `engagement_10s`, `engagement_30s`, `engagement_60s`: Time-based engagement tracking
  - `share_analysis`: When user shares analysis results

### Backend Events
- **WebSocket Events**:
  - `websocket_connected`: New WebSocket connection
  - `websocket_disconnected`: WebSocket disconnection
  - `websocket_message_received`: Message received from client
- **Analysis Tracking**:
  - `analysis_started`: Analysis begins
  - `analysis_completed`: Analysis successfully completes
  - `analysis_failed`: Analysis fails with error
- **Analyzer Performance**:
  - `analyzer_executed`: Individual analyzer performance metrics
- **API Requests**:
  - `api_request`: All API endpoint calls with timing
- **Errors**:
  - `error_occurred`: Application errors for monitoring

## Custom Properties

Each event includes relevant properties:
- `domain`: Website being analyzed
- `duration_seconds`: Time taken for operations
- `issues_found`: Number of issues discovered
- `analyzer`: Specific analyzer module
- `status_code`: HTTP response codes
- `environment`: Production/development
- `session_id`: User session identifier

## Using Feature Flags

PostHog feature flags can control feature rollout:

```python
# Backend usage
from app.utils.analytics import FeatureFlags

if FeatureFlags.is_enabled("new_analyzer", user_id):
    # Use new analyzer
    pass
```

```typescript
// Frontend usage
import { posthog } from '@/lib/posthog'

if (posthog.isFeatureEnabled('new_feature')) {
  // Show new feature
}
```

## Dashboard Setup

### Recommended Dashboards

1. **User Engagement Dashboard**
   - Daily active users
   - Analysis completion rate
   - Average session duration
   - Most analyzed domains

2. **Performance Dashboard**
   - Analysis duration by domain
   - Analyzer performance metrics
   - Error rates by component
   - API response times

3. **Conversion Funnel**
   - Landing → First message → Analysis started → Analysis completed
   - Drop-off points identification

## Privacy Considerations

- No personal data is collected beyond anonymous session IDs
- Domain names analyzed are tracked for product improvement
- IP addresses are not stored
- All tracking respects user privacy settings

## Troubleshooting

### Events Not Appearing
1. Check API key is correct
2. Verify network connectivity to PostHog
3. Check browser console for errors
4. Ensure ad blockers aren't blocking PostHog

### Backend Events Missing
1. Verify POSTHOG_API_KEY environment variable
2. Check backend logs for initialization message
3. Ensure PostHog package is installed: `pip install posthog`

### Feature Flags Not Working
1. Ensure feature flag is created in PostHog dashboard
2. Check flag targeting rules
3. Verify distinct_id matches between frontend and backend

## Support

For PostHog-specific issues: https://posthog.com/docs
For Keelo integration issues: Create an issue in the repository