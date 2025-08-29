'use client'

import { ChatGPTMessage } from './ChatGPTMessage'
import { TypingIndicator } from './TypingIndicator'
import type { ChatMessage } from '@/types/chat'

interface MessageListProps {
  messages: ChatMessage[]
  isTyping?: boolean
}

export function ChatGPTMessageList({ messages, isTyping }: MessageListProps) {
  return (
    <div>
      {messages.map((message) => (
        <ChatGPTMessage
          key={message.id}
          role={message.role}
          content={message.content}
          metadata={message.metadata}
          timestamp={message.timestamp}
        />
      ))}
      
      {isTyping && (
        <div className="py-6 bg-[#2f2f2f]">
          <div className="max-w-3xl mx-auto px-4">
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                <span className="text-sm font-semibold text-white">G</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <span className="inline-block w-2 h-2 rounded-full bg-gray-400 animate-typing-dot" style={{ animationDelay: '0ms' }} />
                  <span className="inline-block w-2 h-2 rounded-full bg-gray-400 animate-typing-dot" style={{ animationDelay: '150ms' }} />
                  <span className="inline-block w-2 h-2 rounded-full bg-gray-400 animate-typing-dot" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}