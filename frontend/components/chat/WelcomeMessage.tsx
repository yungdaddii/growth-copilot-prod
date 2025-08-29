'use client'

import { Zap, TrendingUp, Search, Clock } from 'lucide-react'

interface WelcomeMessageProps {
  onExampleClick: (message: string) => void
}

export function WelcomeMessage({ onExampleClick }: WelcomeMessageProps) {
  const examples = [
    { domain: 'stripe.com', description: 'Payment infrastructure' },
    { domain: 'shopify.com', description: 'E-commerce platform' },
    { domain: 'notion.so', description: 'Productivity tool' },
    { domain: 'linear.app', description: 'Project management' },
  ]

  return (
    <div className="flex flex-col items-center justify-center min-h-full px-4 py-12 animate-fade-in">
      <div className="max-w-2xl w-full space-y-6">
        {/* Hero */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-400 bg-clip-text text-transparent">
            Growth Co-pilot
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            AI that finds hidden revenue opportunities in 60 seconds
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-100 dark:bg-gray-800/50">
            <Zap className="w-5 h-5 text-purple-500 mt-0.5" />
            <div>
              <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">Instant Analysis</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Complete website audit in under 60 seconds
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-100 dark:bg-gray-800/50">
            <TrendingUp className="w-5 h-5 text-purple-500 mt-0.5" />
            <div>
              <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">Revenue Focused</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Find conversion blockers and quick wins
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-100 dark:bg-gray-800/50">
            <Search className="w-5 h-5 text-purple-500 mt-0.5" />
            <div>
              <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">Competitor Intel</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                See what competitors do better
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-100 dark:bg-gray-800/50">
            <Clock className="w-5 h-5 text-purple-500 mt-0.5" />
            <div>
              <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">Quick Fixes</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Get actionable improvements instantly
              </p>
            </div>
          </div>
        </div>

        {/* Examples */}
        <div className="space-y-3">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            Try these popular examples:
          </p>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => onExampleClick('stripe.com vs square.com')}
              className="flex flex-col items-start p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 transition-all text-left group"
            >
              <span className="font-medium text-sm text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                stripe.com vs square.com
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Compare payment platforms
              </span>
            </button>
            
            <button
              onClick={() => onExampleClick('Find revenue leaks on shopify.com')}
              className="flex flex-col items-start p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 transition-all text-left group"
            >
              <span className="font-medium text-sm text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                Find revenue leaks
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                shopify.com e-commerce analysis
              </span>
            </button>
            
            <button
              onClick={() => onExampleClick('notion.so growth opportunities')}
              className="flex flex-col items-start p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 transition-all text-left group"
            >
              <span className="font-medium text-sm text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                notion.so growth tactics
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                SaaS optimization strategies
              </span>
            </button>
            
            <button
              onClick={() => onExampleClick('SEO audit for techcrunch.com')}
              className="flex flex-col items-start p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 transition-all text-left group"
            >
              <span className="font-medium text-sm text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                SEO audit
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                techcrunch.com content strategy
              </span>
            </button>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Just type <span className="font-mono text-purple-500">analyze domain.com</span> to start
          </p>
        </div>
      </div>
    </div>
  )
}