import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Keelo.ai - AI Growth Engine',
  description: 'AI-powered growth engine that analyzes websites and unlocks revenue opportunities in seconds',
  keywords: 'AI growth engine, website analysis, revenue optimization, conversion intelligence, Keelo.ai',
  authors: [{ name: 'Keelo.ai' }],
  openGraph: {
    title: 'Keelo.ai - AI Growth Engine',
    description: 'AI-powered growth engine that analyzes websites and unlocks revenue opportunities',
    type: 'website',
    url: 'https://keelo.ai',
    siteName: 'Keelo.ai',
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