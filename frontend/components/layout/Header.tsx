'use client'

import { useState } from 'react'
import { Sparkles, Share2, RefreshCw, User, LogOut } from 'lucide-react'
import { useChatStore } from '@/store/chat'
import { useAuth } from '@/hooks/useAuth'
import AuthModal from '@/components/auth/AuthModal'

export function Header() {
  const { conversationId, clearMessages } = useChatStore()
  const { user, profile, logout } = useAuth()
  const [showAuthModal, setShowAuthModal] = useState(false)

  const handleShare = () => {
    if (conversationId) {
      const shareUrl = `${window.location.origin}/share/${conversationId}`
      navigator.clipboard.writeText(shareUrl)
      // TODO: Show toast notification
    }
  }

  const handleNewChat = () => {
    clearMessages()
    window.location.reload() // Reset WebSocket connection
  }

  const handleLogout = async () => {
    await logout()
    window.location.reload()
  }

  return (
    <>
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <h1 className="font-semibold text-lg">Keelo.ai</h1>
            <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
              Beta
            </span>
          </div>

          <div className="flex items-center gap-2">
          {conversationId && (
            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md hover:bg-muted transition-colors"
              aria-label="Share conversation"
            >
              <Share2 className="w-4 h-4" />
              <span className="hidden sm:inline">Share</span>
            </button>
          )}
          
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md hover:bg-muted transition-colors"
            aria-label="New chat"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">New Chat</span>
          </button>
          
          {user ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 text-sm">
                <User className="w-4 h-4" />
                <span className="hidden sm:inline">{profile?.displayName || profile?.email || 'User'}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md hover:bg-muted transition-colors"
                aria-label="Sign out"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              aria-label="Sign in"
            >
              <User className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </header>
    
    <AuthModal
      isOpen={showAuthModal}
      onClose={() => setShowAuthModal(false)}
    />
    </>
  )
}