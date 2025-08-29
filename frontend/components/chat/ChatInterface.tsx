'use client'

import { useState, useEffect, useRef } from 'react'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { WelcomeMessage } from './WelcomeMessage'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useChatStore } from '@/store/chat'
import { Menu, Sparkles, ChevronRight } from 'lucide-react'
import { trackAnalysis, trackUserAction } from '@/lib/posthog'

interface ChatInterfaceProps {
  onMenuClick: () => void
}

export function ChatInterface({ onMenuClick }: ChatInterfaceProps) {
  const [isTyping, setIsTyping] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { messages, addMessage, setConversationId } = useChatStore()
  const { sendMessage, connectionStatus } = useWebSocket({
    onMessage: (message) => {
      console.log('Received WebSocket message:', message)
      if (message.type === 'connection') {
        console.log('WebSocket connection confirmed:', message.payload)
      } else if (message.type === 'chat') {
        addMessage({
          id: message.payload.message_id || crypto.randomUUID(),
          role: 'assistant',
          content: message.payload.content,
          metadata: message.payload.metadata,
          timestamp: new Date(),
        })
        
        if (message.payload.conversation_id) {
          setConversationId(message.payload.conversation_id)
        }
        setIsTyping(false)
      } else if (message.type === 'typing') {
        setIsTyping(message.payload.is_typing)
      } else if (message.type === 'analysis_update') {
        // Show analysis progress
        setAnalysisProgress(message.payload.progress || 0)
        addMessage({
          id: crypto.randomUUID(),
          role: 'system',
          content: message.payload.message,
          metadata: {
            type: 'analysis_update',
            progress: message.payload.progress,
          },
          timestamp: new Date(),
        })
        
        // Track analysis completion
        if (message.payload.progress === 100) {
          const userMessages = messages.filter(m => m.role === 'user')
          const lastUserMessage = userMessages[userMessages.length - 1]
          if (lastUserMessage && lastUserMessage.content.includes('.')) {
            trackAnalysis.completed(
              lastUserMessage.content,
              10, // Default duration, could calculate from timestamps
              message.payload.issues_found || 0
            )
          }
        }
      }
    },
    onError: (error: any) => {
      console.error('WebSocket error:', error)
      // Only add error message if it's a significant error
      if (error?.message && !error.message.includes('WebSocket is already')) {
        addMessage({
          id: crypto.randomUUID(),
          role: 'system',
          content: 'Connection interrupted. Reconnecting...',
          metadata: { type: 'error' },
          timestamp: new Date(),
        })
      }
    },
  })

  const handleSendMessage = (content: string) => {
    // Track user action
    const isDomain = content.includes('.') && !content.includes(' ')
    const messageType = isDomain ? 'domain' : content.split(' ').length < 5 ? 'question' : 'other'
    trackUserAction.sendMessage(content, messageType)
    
    // Track analysis if it's a domain
    if (isDomain) {
      trackAnalysis.started(content)
    }
    
    // Add user message to store
    addMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    })

    // Send via WebSocket
    sendMessage({
      type: 'chat',
      payload: { content },
    })
    
    setIsTyping(true)
  }

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const showWelcome = messages.length === 0

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors lg:hidden"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-500" />
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              Growth Co-pilot
            </h1>
          </div>
        </div>
        
        {/* Connection Status and Theme Toggle */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500' : 
              connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
            }`} />
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
            </span>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto bg-white dark:bg-gray-950">
        {showWelcome ? (
          <WelcomeMessage onExampleClick={handleSendMessage} />
        ) : (
          <div className="max-w-3xl mx-auto">
            <MessageList 
              messages={messages} 
              isTyping={isTyping}
              analysisProgress={analysisProgress}
            />
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
        <div className="max-w-3xl mx-auto">
          <div className="p-4">
            <MessageInput 
              onSendMessage={handleSendMessage}
              disabled={connectionStatus !== 'connected' || isTyping}
              placeholder={
                connectionStatus === 'connected' 
                  ? "Enter a domain to analyze (e.g., stripe.com)" 
                  : "Connecting..."
              }
            />
            <div className="mt-2 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Powered by AI • Analyzes websites in 60 seconds
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}