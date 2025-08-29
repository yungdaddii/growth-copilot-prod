'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Copy, Check, User, Sparkles, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MessageProps {
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: any
  timestamp: Date
}

export function Message({ role, content, metadata, timestamp }: MessageProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const isUser = role === 'user'
  const isSystem = role === 'system'

  // System error messages
  if (isSystem && metadata?.type === 'error') {
    return (
      <div className="flex justify-center my-4">
        <div className="flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">{content}</span>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      "group relative py-6",
      !isUser && "bg-gray-50/50 dark:bg-gray-900/20"
    )}>
      <div className="max-w-3xl mx-auto px-4">
        <div className="flex gap-4">
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
              isUser 
                ? "bg-gray-900 dark:bg-white" 
                : "bg-gradient-to-br from-purple-500 to-purple-600"
            )}>
              {isUser ? (
                <User className="w-5 h-5 text-white dark:text-gray-900" />
              ) : (
                <Sparkles className="w-5 h-5 text-white" />
              )}
            </div>
          </div>

          {/* Message Content */}
          <div className="flex-1 space-y-2 overflow-hidden">
            {/* Name and timestamp */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {isUser ? 'You' : 'Keelo.ai'}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
              
              {/* Copy button for assistant messages */}
              {!isUser && (
                <button
                  onClick={handleCopy}
                  className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-200 dark:hover:bg-gray-800 rounded"
                  aria-label="Copy message"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Copy className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              )}
            </div>

            {/* Message text */}
            <div className="prose prose-sm max-w-none dark:prose-invert">
              {isUser ? (
                <p className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                  {content}
                </p>
              ) : (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => (
                      <p className="text-gray-700 dark:text-gray-300 mb-3 last:mb-0">
                        {children}
                      </p>
                    ),
                    a: ({ children, href }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 dark:text-purple-400 hover:underline"
                      >
                        {children}
                      </a>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc pl-5 mb-3 space-y-1">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal pl-5 mb-3 space-y-1">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-gray-700 dark:text-gray-300">
                        {children}
                      </li>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-semibold text-gray-900 dark:text-white">
                        {children}
                      </strong>
                    ),
                    h1: ({ children }) => (
                      <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-3 mt-4">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-2 mt-3">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-base font-bold text-gray-900 dark:text-white mb-2 mt-2">
                        {children}
                      </h3>
                    ),
                    code: ({ children, className, ...props }: any) => {
                      const isInline = !className
                      
                      if (isInline) {
                        return (
                          <code className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-purple-600 dark:text-purple-400 font-mono text-sm">
                            {children}
                          </code>
                        )
                      }
                      return (
                        <pre className="overflow-x-auto bg-gray-900 dark:bg-gray-950 rounded-lg p-4 my-3">
                          <code className="text-gray-100 font-mono text-sm">
                            {children}
                          </code>
                        </pre>
                      )
                    },
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-purple-500 pl-4 italic text-gray-600 dark:text-gray-400 my-3">
                        {children}
                      </blockquote>
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}