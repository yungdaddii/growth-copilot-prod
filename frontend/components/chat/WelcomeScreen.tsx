'use client'

import { Sparkles, TrendingUp, Search, Zap, Target, ChartBar } from 'lucide-react'

interface WelcomeScreenProps {
  onExampleClick: (example: string) => void
}

export function WelcomeScreen({ onExampleClick }: WelcomeScreenProps) {
  const examples = [
    {
      icon: <TrendingUp className="w-5 h-5" />,
      title: "Analyze Stripe.com",
      subtitle: "See how a top SaaS company converts",
      query: "stripe.com"
    },
    {
      icon: <Search className="w-5 h-5" />,
      title: "Check my competitor",
      subtitle: "Compare against industry leaders",
      query: "analyze salesforce.com and show me what they do better"
    },
    {
      icon: <Zap className="w-5 h-5" />,
      title: "Quick wins for Shopify",
      subtitle: "Find instant improvements",
      query: "shopify.com quick wins"
    },
    {
      icon: <Target className="w-5 h-5" />,
      title: "AI search optimization",
      subtitle: "Check ChatGPT visibility",
      query: "Is notion.so optimized for AI search?"
    }
  ]

  const capabilities = [
    { icon: <ChartBar className="w-4 h-4" />, text: "Competitor analysis with specific names" },
    { icon: <Target className="w-4 h-4" />, text: "Conversion optimization insights" },
    { icon: <Search className="w-4 h-4" />, text: "AI search & ChatGPT visibility" },
    { icon: <Zap className="w-4 h-4" />, text: "Quick wins you can implement today" },
  ]

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 py-12">
      {/* Logo and Title */}
      <div className="flex items-center gap-3 mb-2">
        <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-2xl">
          <Sparkles className="w-8 h-8 text-purple-600 dark:text-purple-400" />
        </div>
      </div>
      
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Growth Co-pilot
      </h1>
      
      <p className="text-gray-600 dark:text-gray-400 text-center mb-8 max-w-md">
        AI-powered revenue intelligence that finds hidden growth opportunities in 60 seconds
      </p>

      {/* Capabilities */}
      <div className="flex flex-wrap gap-2 justify-center mb-8">
        {capabilities.map((cap, i) => (
          <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
            <span className="text-gray-600 dark:text-gray-400">{cap.icon}</span>
            <span className="text-sm text-gray-700 dark:text-gray-300">{cap.text}</span>
          </div>
        ))}
      </div>

      {/* Example Cards */}
      <div className="w-full max-w-2xl">
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">
          Try an example
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {examples.map((example, i) => (
            <button
              key={i}
              onClick={() => onExampleClick(example.query)}
              className="flex items-start gap-3 p-4 text-left border border-gray-200 dark:border-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors group"
            >
              <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg group-hover:bg-purple-100 dark:group-hover:bg-purple-900/30 transition-colors">
                <span className="text-gray-600 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400">
                  {example.icon}
                </span>
              </div>
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white text-sm">
                  {example.title}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {example.subtitle}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-12 text-center">
        <p className="text-xs text-gray-500 dark:text-gray-500">
          Powered by Claude 3.5 Sonnet • No integrations required
        </p>
      </div>
    </div>
  )
}