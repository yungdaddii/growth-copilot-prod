'use client'

import { ThemeProvider } from 'next-themes'
import { ReactNode } from 'react'
import { PostHogProvider } from '@/components/providers/PostHogProvider'
import { AuthProvider } from '@/hooks/useAuth'

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AuthProvider>
        <PostHogProvider>
          {children}
        </PostHogProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}