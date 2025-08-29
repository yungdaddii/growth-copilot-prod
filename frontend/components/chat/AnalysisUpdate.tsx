'use client'

import { Loader2, CheckCircle, XCircle } from 'lucide-react'
import { useState, useEffect } from 'react'

interface AnalysisUpdateProps {
  message: string
  progress?: number
}

export function AnalysisUpdate({ message, progress = 0 }: AnalysisUpdateProps) {
  const [animatedProgress, setAnimatedProgress] = useState(0)
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(progress)
    }, 100)
    return () => clearTimeout(timer)
  }, [progress])

  const isComplete = progress >= 100
  const hasError = message.toLowerCase().includes('error')

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4 shadow-sm animate-fade-in">
        <div className="flex items-center gap-3">
          {hasError ? (
            <XCircle className="w-5 h-5 text-red-500" />
          ) : isComplete ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : (
            <Loader2 className="w-5 h-5 text-purple-500 animate-spin" />
          )}
          
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {message}
            </p>
            
            {!hasError && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Progress
                  </span>
                  <span className="text-xs font-mono text-gray-600 dark:text-gray-300">
                    {animatedProgress}%
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-500 ease-out rounded-full"
                    style={{ width: `${animatedProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}