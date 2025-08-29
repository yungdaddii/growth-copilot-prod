'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Copy, Check, User } from 'lucide-react'

interface MessageProps {
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: any
  timestamp: Date
}

export function ChatGPTMessage({ role, content, metadata, timestamp }: MessageProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const isUser = role === 'user'
  const isSystem = role === 'system'

  if (isSystem && metadata?.type === 'error') {
    return null // Hide error messages in ChatGPT style
  }

  return (
    <div className={`py-6 ${!isUser ? 'bg-[#2f2f2f]' : ''}`}>
      <div className="max-w-3xl mx-auto px-4">
        <div className="flex gap-4">
          {/* Avatar */}
          <div className="flex-shrink-0">
            {isUser ? (
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                <span className="text-sm font-semibold text-white">Y</span>
              </div>
            ) : (
              <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                <span className="text-sm font-semibold text-white">G</span>
              </div>
            )}
          </div>

          {/* Message Content */}
          <div className="flex-1 space-y-2 overflow-hidden">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-200">
                {isUser ? 'You' : 'Growth Co-pilot'}
              </span>
            </div>

            {/* Message text */}
            <div className="prose prose-invert max-w-none">
              {isUser ? (
                <p className="text-gray-200 whitespace-pre-wrap">
                  {content}
                </p>
              ) : (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => (
                      <p className="text-gray-200 mb-3 last:mb-0">
                        {children}
                      </p>
                    ),
                    a: ({ children, href }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:underline"
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
                      <li className="text-gray-200">
                        {children}
                      </li>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-semibold text-gray-100">
                        {children}
                      </strong>
                    ),
                    code: ({ children, className }: any) => {
                      const isInline = !className
                      
                      if (isInline) {
                        return (
                          <code className="px-1.5 py-0.5 rounded bg-[#1a1a1a] text-blue-400 font-mono text-sm">
                            {children}
                          </code>
                        )
                      }
                      return (
                        <pre className="overflow-x-auto bg-[#1a1a1a] rounded-lg p-4 my-3">
                          <code className="text-gray-200 font-mono text-sm">
                            {children}
                          </code>
                        </pre>
                      )
                    },
                  }}
                >
                  {content}
                </ReactMarkdown>
              )}
            </div>

            {/* Copy button for assistant messages */}
            {!isUser && (
              <button
                onClick={handleCopy}
                className="text-gray-400 hover:text-gray-200 text-sm flex items-center gap-1"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}