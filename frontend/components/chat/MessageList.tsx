'use client'

import { Message } from './Message'
import { AnalysisUpdate } from './AnalysisUpdate'
import { TypingIndicator } from './TypingIndicator'
import type { ChatMessage } from '@/types/chat'

interface MessageListProps {
  messages: ChatMessage[]
  isTyping?: boolean
  analysisProgress?: number
}

export function MessageList({ messages, isTyping, analysisProgress = 0 }: MessageListProps) {
  // Group consecutive analysis updates
  const processedMessages = messages.reduce((acc: any[], message, index) => {
    if (message.metadata?.type === 'analysis_update') {
      // Skip individual analysis updates, we'll show a single progress bar
      return acc
    }
    acc.push(message)
    return acc
  }, [])

  // Check if currently analyzing
  const isAnalyzing = analysisProgress > 0 && analysisProgress < 100

  return (
    <div className="py-8 px-4">
      {processedMessages.map((message) => (
        <Message
          key={message.id}
          role={message.role}
          content={message.content}
          metadata={message.metadata}
          timestamp={message.timestamp}
        />
      ))}
      
      {isAnalyzing && (
        <div className="flex justify-center my-4">
          <AnalysisUpdate
            message="Analyzing website..."
            progress={analysisProgress}
          />
        </div>
      )}
      
      {isTyping && !isAnalyzing && (
        <TypingIndicator />
      )}
    </div>
  )
}