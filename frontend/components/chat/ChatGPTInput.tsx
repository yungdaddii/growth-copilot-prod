'use client'

import { useState, useRef, KeyboardEvent } from 'react'
import { ArrowUp, Paperclip, Mic } from 'lucide-react'

interface ChatGPTInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

export function ChatGPTInput({ onSendMessage, disabled = false }: ChatGPTInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
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
    <div className="w-full max-w-3xl mx-auto px-4 pb-6">
      <div className="relative flex items-end gap-2 bg-[#2f2f2f] rounded-3xl px-4 py-3.5 shadow-sm">
        <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
          <Paperclip className="w-[18px] h-[18px] text-gray-400" />
        </button>
        
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="Enter a domain to analyze (e.g., stripe.com)"
          disabled={disabled}
          rows={1}
          className="flex-1 bg-transparent text-white placeholder:text-gray-500 resize-none outline-none max-h-32 overflow-y-auto text-[15px]"
          style={{ lineHeight: '1.5' }}
        />

        {message.trim() ? (
          <button
            onClick={handleSubmit}
            disabled={disabled}
            className="p-1 bg-white hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
          >
            <ArrowUp className="w-[20px] h-[20px] text-black" />
          </button>
        ) : (
          <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
            <Mic className="w-[18px] h-[18px] text-gray-400" />
          </button>
        )}
      </div>
    </div>
  )
}