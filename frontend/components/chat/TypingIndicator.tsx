'use client'

import { Sparkles } from 'lucide-react'

export function TypingIndicator() {
  return (
    <div className="py-6">
      <div className="max-w-3xl mx-auto px-4">
        <div className="flex gap-4">
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Typing animation */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800">
              <span className="inline-block w-2 h-2 rounded-full bg-gray-400 animate-typing-dot" style={{ animationDelay: '0ms' }} />
              <span className="inline-block w-2 h-2 rounded-full bg-gray-400 animate-typing-dot" style={{ animationDelay: '150ms' }} />
              <span className="inline-block w-2 h-2 rounded-full bg-gray-400 animate-typing-dot" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}