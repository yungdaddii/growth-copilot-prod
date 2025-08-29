'use client'

import { Plus, MessageSquare, Search, BookOpen, Sparkles, ChevronLeft } from 'lucide-react'
import { useChatStore } from '@/store/chat'
import { formatDistanceToNow } from 'date-fns'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function ChatGPTSidebar({ isOpen, onToggle }: SidebarProps) {
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

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        ${isOpen ? 'fixed' : 'fixed lg:relative'}
        top-0 left-0
        w-[260px] h-screen
        bg-[#171717] text-white
        transform transition-transform duration-200
        ${isOpen ? 'z-50' : 'z-auto'}
        flex flex-col
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Header */}
        <div className="p-3">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/10 transition-colors group"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm">New chat</span>
          </button>
        </div>

        {/* Quick Actions */}
        <div className="px-3 pb-3 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left">
            <Search className="w-4 h-4 opacity-70" />
            <span className="text-sm opacity-90">Search chats</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left">
            <BookOpen className="w-4 h-4 opacity-70" />
            <span className="text-sm opacity-90">Library</span>
          </button>
        </div>

        {/* Divider */}
        <div className="mx-3 border-t border-white/10" />

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto py-2">
          <div className="px-3 space-y-1">
            {conversations.length > 0 ? (
              <>
                <div className="px-2 py-2 text-xs font-medium text-gray-400">Chats</div>
                {conversations.map((conv) => {
                  const isActive = conv.id === conversationId
                  return (
                    <button
                      key={conv.id}
                      onClick={() => handleSelectConversation(conv.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors group flex items-center gap-2 ${
                        isActive ? 'bg-white/10' : 'hover:bg-white/5'
                      }`}
                    >
                      <MessageSquare className="w-4 h-4 opacity-50 flex-shrink-0" />
                      <span className="text-sm truncate flex-1 opacity-90">
                        {conv.title}
                      </span>
                    </button>
                  )
                })}
              </>
            ) : (
              <div className="px-3 py-4 text-center">
                <p className="text-sm text-gray-400">No conversations yet</p>
              </div>
            )}
          </div>
        </div>

        {/* User Section */}
        <div className="border-t border-white/10 p-3">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
              <span className="text-xs font-semibold">G</span>
            </div>
            <div className="flex-1">
              <div className="text-sm">Growth Co-pilot</div>
              <div className="text-xs opacity-60">Free</div>
            </div>
          </div>
        </div>

        {/* Mobile close button */}
        <button
          onClick={onToggle}
          className="absolute top-3 right-3 p-1 lg:hidden hover:bg-white/10 rounded"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
      </aside>
    </>
  )
}