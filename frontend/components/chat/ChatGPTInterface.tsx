'use client'

import { useState, useEffect, useRef } from 'react'
import { ChatGPTMessageList } from './ChatGPTMessageList'
import { ChatGPTInput } from './ChatGPTInput'
import { ChatGPTWelcome } from './ChatGPTWelcome'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useChatStore } from '@/store/chat'
import { Menu, ChevronDown } from 'lucide-react'

interface ChatInterfaceProps {
  onMenuClick: () => void
}

export function ChatGPTInterface({ onMenuClick }: ChatInterfaceProps) {
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
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
    },
  })

  const handleSendMessage = (content: string) => {
    addMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    })

    sendMessage({
      type: 'chat',
      payload: { content },
    })
    
    setIsTyping(true)
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const showWelcome = messages.length === 0

  return (
    <div className="flex flex-col h-full bg-[#212121]">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors lg:hidden"
          >
            <Menu className="w-5 h-5 text-gray-300" />
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 hover:bg-white/10 rounded-lg transition-colors">
            <span className="text-gray-200 font-medium">Growth Co-pilot</span>
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        
        {/* Try Pro button */}
        <button className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2">
          <span>✨</span>
          <span>Try Pro</span>
        </button>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto">
        {showWelcome ? (
          <ChatGPTWelcome onExampleClick={handleSendMessage} />
        ) : (
          <div className="max-w-3xl mx-auto">
            <ChatGPTMessageList 
              messages={messages} 
              isTyping={isTyping}
            />
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="relative">
        <ChatGPTInput 
          onSendMessage={handleSendMessage}
          disabled={connectionStatus !== 'connected' || isTyping}
        />
        <div className="text-center pb-4">
          <p className="text-xs text-gray-400">
            Growth Co-pilot can analyze websites and provide insights that may be inaccurate.
          </p>
        </div>
      </div>
    </div>
  )
}