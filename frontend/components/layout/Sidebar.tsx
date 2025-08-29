'use client'

import { Plus, MessageSquare, Trash2, ChevronLeft, Sparkles } from 'lucide-react'
import { useChatStore } from '@/store/chat'
import { formatDistanceToNow } from 'date-fns'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { 
    conversations, 
    conversationId, 
    loadConversation, 
    deleteConversation,
    clearMessages 
  } = useChatStore()

  const handleNewChat = () => {
    clearMessages()
    if (window.innerWidth < 1024) {
      onToggle()
    }
  }

  const handleSelectConversation = (id: string) => {
    loadConversation(id)
    if (window.innerWidth < 1024) {
      onToggle()
    }
  }

  const handleDeleteConversation = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    deleteConversation(id)
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:sticky top-0
        w-64 h-screen
        bg-gray-900 text-white
        transform transition-transform duration-200
        z-50 lg:z-auto
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-800">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              <Plus className="w-5 h-5" />
              <span className="text-sm font-medium">New Analysis</span>
            </button>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-2">
              {conversations.length > 0 ? (
                <>
                  <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Recent Analyses
                  </div>
                  {conversations.map((conv) => {
                    const isActive = conv.id === conversationId
                    const lastMessage = conv.messages[conv.messages.length - 1]
                    const preview = lastMessage?.role === 'assistant' 
                      ? lastMessage.content.slice(0, 50) + '...'
                      : conv.messages[0]?.content.slice(0, 50) + '...'
                    
                    return (
                      <button
                        key={conv.id}
                        onClick={() => handleSelectConversation(conv.id)}
                        className={`w-full text-left px-3 py-3 rounded-lg transition-colors group ${
                          isActive ? 'bg-gray-800' : 'hover:bg-gray-800'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <MessageSquare className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                            isActive ? 'text-purple-400' : 'text-gray-400'
                          }`} />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-gray-200 truncate">
                              {conv.title}
                            </div>
                            <div className="text-xs text-gray-500 truncate mt-1">
                              {preview}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              {formatDistanceToNow(new Date(conv.updatedAt), { addSuffix: true })}
                            </div>
                          </div>
                          <Trash2 
                            onClick={(e) => handleDeleteConversation(e, conv.id)}
                            className="w-4 h-4 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-400" 
                          />
                        </div>
                      </button>
                    )
                  })}
                </>
              ) : (
                <div className="px-3 py-8 text-center">
                  <MessageSquare className="w-8 h-8 text-gray-600 mx-auto mb-3" />
                  <p className="text-sm text-gray-500">No conversations yet</p>
                  <p className="text-xs text-gray-600 mt-1">Start a new analysis to begin</p>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-center gap-3 px-3 py-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              <div className="flex-1">
                <div className="text-sm font-medium">Keelo.ai</div>
                <div className="text-xs text-gray-500">Powered by Claude 3.5</div>
              </div>
            </div>
          </div>

          {/* Mobile close button */}
          <button
            onClick={onToggle}
            className="absolute top-4 right-4 p-1 lg:hidden hover:bg-gray-800 rounded"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        </div>
      </aside>
    </>
  )
}