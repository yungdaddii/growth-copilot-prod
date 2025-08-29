import posthog from 'posthog-js'
import { PostHogConfig } from 'posthog-js'

export const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY || ''
export const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'

export function initPostHog() {
  if (typeof window !== 'undefined' && POSTHOG_KEY) {
    const config: Partial<PostHogConfig> = {
      api_host: POSTHOG_HOST,
      // Capture pageviews automatically
      capture_pageview: true,
      // Capture sessions for replay
      session_recording: {
        // Don't record any text in inputs for privacy
        maskAllInputs: true,
      },
      // Feature flags
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') {
          console.log('PostHog loaded', posthog)
        }
      },
      // Privacy settings
      autocapture: true,
      cross_subdomain_cookie: true,
      persistence: 'localStorage+cookie',
      // Don't track certain sensitive pages
      opt_out_capturing_by_default: false,
    }

    posthog.init(POSTHOG_KEY, config)

    // Identify user properties we want to track
    if (typeof window !== 'undefined') {
      posthog.register({
        app_name: 'keelo',
        app_version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
      })
    }
  }
}

// Custom event tracking functions
export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  if (typeof window !== 'undefined' && posthog) {
    posthog.capture(eventName, properties)
  }
}

// Track analysis events
export const trackAnalysis = {
  started: (domain: string) => {
    trackEvent('analysis_started', {
      domain,
      timestamp: new Date().toISOString(),
    })
  },
  
  completed: (domain: string, duration: number, issuesFound: number) => {
    trackEvent('analysis_completed', {
      domain,
      duration_seconds: duration,
      issues_found: issuesFound,
      timestamp: new Date().toISOString(),
    })
  },
  
  failed: (domain: string, error: string) => {
    trackEvent('analysis_failed', {
      domain,
      error,
      timestamp: new Date().toISOString(),
    })
  },
}

// Track user actions
export const trackUserAction = {
  sendMessage: (message: string, messageType: 'domain' | 'question' | 'other') => {
    trackEvent('message_sent', {
      message_type: messageType,
      message_length: message.length,
      has_domain: message.includes('.com') || message.includes('.io') || message.includes('.co'),
    })
  },
  
  clickExample: (example: string) => {
    trackEvent('example_clicked', {
      example_text: example,
    })
  },
  
  toggleTheme: (theme: 'light' | 'dark') => {
    trackEvent('theme_toggled', {
      new_theme: theme,
    })
  },
  
  openPromptLibrary: () => {
    trackEvent('prompt_library_opened')
  },
  
  selectPrompt: (prompt: string, category: string) => {
    trackEvent('prompt_selected', {
      prompt_text: prompt,
      category,
    })
  },
  
  shareAnalysis: (domain: string) => {
    trackEvent('analysis_shared', {
      domain,
    })
  },
}

// Track performance metrics
export const trackPerformance = {
  websocketConnected: (duration: number) => {
    trackEvent('websocket_connected', {
      connection_time_ms: duration,
    })
  },
  
  websocketDisconnected: (reason: string) => {
    trackEvent('websocket_disconnected', {
      reason,
    })
  },
  
  pageLoadTime: (duration: number) => {
    trackEvent('page_load_time', {
      duration_ms: duration,
    })
  },
}

// Feature flags
export const getFeatureFlag = (flagName: string): boolean => {
  if (typeof window !== 'undefined' && posthog) {
    return posthog.isFeatureEnabled(flagName) || false
  }
  return false
}

// User identification
export const identifyUser = (userId: string, properties?: Record<string, any>) => {
  if (typeof window !== 'undefined' && posthog) {
    posthog.identify(userId, properties)
  }
}

// Reset user (on logout)
export const resetUser = () => {
  if (typeof window !== 'undefined' && posthog) {
    posthog.reset()
  }
}

export default posthog