import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Growth Co-pilot - AI that finds hidden revenue in 60 seconds',
  description: 'Analyze any website and discover revenue opportunities with AI-powered insights',
  keywords: 'growth marketing, website analysis, conversion optimization, AI analysis',
  authors: [{ name: 'Growth Co-pilot' }],
  openGraph: {
    title: 'Growth Co-pilot - Find Hidden Revenue',
    description: 'AI that analyzes websites and finds revenue opportunities in 60 seconds',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}