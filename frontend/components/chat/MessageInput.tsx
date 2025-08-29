'use client'

import { useState, useRef, KeyboardEvent } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MessageInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function MessageInput({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Enter a domain to analyze..."
}: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = async () => {
    if (message.trim() && !disabled && !isSubmitting) {
      setIsSubmitting(true)
      onSendMessage(message.trim())
      setMessage('')
      setIsSubmitting(false)
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  return (
    <div className="relative flex items-end gap-2">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder={placeholder}
          disabled={disabled || isSubmitting}
          rows={1}
          className={cn(
            "w-full resize-none rounded-lg border border-gray-200 dark:border-gray-700",
            "bg-white dark:bg-gray-900 px-4 py-3 pr-12",
            "text-sm placeholder:text-gray-500 dark:placeholder:text-gray-400",
            "focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "max-h-32 overflow-y-auto"
          )}
        />
        
        <button
          onClick={handleSubmit}
          disabled={!message.trim() || disabled || isSubmitting}
          className={cn(
            "absolute right-2 bottom-2.5 rounded-md p-1.5",
            "text-gray-500 hover:text-gray-900 dark:hover:text-gray-100",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "transition-colors"
          )}
          aria-label="Send message"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <kbd className="px-1.5 py-0.5 rounded border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800">Enter</kbd>
        <span>to send</span>
      </div>
    </div>
  )
}