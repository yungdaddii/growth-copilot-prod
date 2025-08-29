'use client'

import { useEffect, Suspense } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { initPostHog, trackEvent } from '@/lib/posthog'
import posthog from 'posthog-js'

function PostHogProviderInner({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  useEffect(() => {
    // Initialize PostHog
    initPostHog()

    // Track initial page view
    if (typeof window !== 'undefined' && posthog) {
      // Track UTM parameters if present
      const utmParams: Record<string, string> = {}
      const utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
      
      utmKeys.forEach(key => {
        const value = searchParams?.get(key)
        if (value) {
          utmParams[key] = value
        }
      })

      if (Object.keys(utmParams).length > 0) {
        posthog.capture('$set', {
          $set: utmParams
        })
      }

      // Track referrer
      if (document.referrer) {
        trackEvent('referrer_captured', {
          referrer: document.referrer,
          landing_page: pathname,
        })
      }
    }
  }, [])

  useEffect(() => {
    // Track route changes
    if (pathname && typeof window !== 'undefined' && posthog) {
      // PostHog will auto-capture pageviews, but we can add custom properties
      trackEvent('route_changed', {
        path: pathname,
        search: searchParams?.toString() || '',
      })
    }
  }, [pathname, searchParams])

  return <>{children}</>
}

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<>{children}</>}>
      <PostHogProviderInner>{children}</PostHogProviderInner>
    </Suspense>
  )
}