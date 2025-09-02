'use client'

import { useState, useEffect, useRef } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useChatStore } from '@/store/chat'
import { useAuth } from '@/hooks/useAuth'
import { Plus, MessageSquare, Search, BookOpen, ChevronLeft, ArrowUp, Paperclip, Mic, Sparkles, Plug } from 'lucide-react'
import { PromptLibrary } from '@/components/PromptLibrary'
import { IntegrationsPanel } from '@/components/integrations/IntegrationsPanel'
import { UserProfileMenu } from '@/components/UserProfileMenu'
import AuthModalStyled from '@/components/auth/AuthModalStyled'

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [promptLibraryOpen, setPromptLibraryOpen] = useState(false)
  const [integrationsOpen, setIntegrationsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { user, profile } = useAuth()
  const { messages, addMessage, conversations, conversationId, clearMessages, setConversationId } = useChatStore()
  const { sendMessage, connectionStatus } = useWebSocket({
    onMessage: (msg) => {
      console.log('Received WebSocket message:', msg)
      if (msg.type === 'connection') {
        console.log('WebSocket connection confirmed:', msg.payload)
      } else if (msg.type === 'chat') {
        addMessage({
          id: msg.payload.message_id || crypto.randomUUID(),
          role: 'assistant',
          content: msg.payload.content,
          metadata: msg.payload.metadata,
          timestamp: new Date(),
        })
        
        if (msg.payload.conversation_id) {
          setConversationId(msg.payload.conversation_id)
        }
        setIsTyping(false)
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
    },
  })

  const handleSendMessage = () => {
    if (message.trim() && connectionStatus === 'connected') {
      addMessage({
        id: crypto.randomUUID(),
        role: 'user',
        content: message.trim(),
        timestamp: new Date(),
      })

      sendMessage({
        type: 'chat',
        payload: { content: message.trim() },
      })
      
      setMessage('')
      setIsTyping(true)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handlePromptSelect = (prompt: string) => {
    setMessage(prompt)
    // Focus the input field after setting the prompt
    setTimeout(() => {
      const input = document.querySelector('input[type="text"]') as HTMLInputElement
      if (input) {
        input.focus()
      }
    }, 100)
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Listen for auth modal event from UserProfileMenu
  useEffect(() => {
    const handleOpenAuthModal = () => {
      setShowAuthModal(true)
    }
    
    window.addEventListener('openAuthModal', handleOpenAuthModal)
    return () => {
      window.removeEventListener('openAuthModal', handleOpenAuthModal)
    }
  }, [])

  const showWelcome = messages.length === 0

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#212121' }}>
      {/* Sidebar */}
      <div style={{ 
        width: '260px', 
        backgroundColor: '#171717', 
        height: '100vh',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ padding: '12px' }}>
          <button 
            onClick={() => clearMessages()}
            style={{
              width: '100%',
              padding: '10px 12px',
              backgroundColor: 'transparent',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px'
            }}
          >
            <Plus size={16} />
            New chat
          </button>
        </div>
        
        <div style={{ padding: '0 12px' }}>
          <button style={{
            width: '100%',
            padding: '8px 12px',
            backgroundColor: 'transparent',
            color: 'rgba(255,255,255,0.7)',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            textAlign: 'left'
          }}>
            <Search size={16} />
            Search chats
          </button>
          <button style={{
            width: '100%',
            padding: '8px 12px',
            backgroundColor: 'transparent',
            color: 'rgba(255,255,255,0.7)',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            textAlign: 'left'
          }}>
            <BookOpen size={16} />
            Library
          </button>
          <button 
            onClick={() => setIntegrationsOpen(true)}
            style={{
              width: '100%',
              padding: '8px 12px',
              backgroundColor: 'transparent',
              color: 'rgba(255,255,255,0.7)',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px',
              textAlign: 'left'
            }}
          >
            <Plug size={16} />
            Integrations
          </button>
        </div>

        <div style={{ 
          borderTop: '1px solid rgba(255,255,255,0.1)', 
          margin: '12px',
          paddingTop: '12px',
          flex: 1,
          overflowY: 'auto'
        }}>
          <div style={{ padding: '0 12px' }}>
            <div style={{ 
              fontSize: '12px', 
              color: 'rgba(255,255,255,0.5)',
              marginBottom: '8px',
              fontWeight: '600'
            }}>
              Chats
            </div>
            {conversations.map((conv) => (
              <button
                key={conv.id}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: conv.id === conversationId ? 'rgba(255,255,255,0.1)' : 'transparent',
                  color: 'rgba(255,255,255,0.9)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  textAlign: 'left',
                  marginBottom: '2px'
                }}
              >
                <MessageSquare size={16} style={{ opacity: 0.5 }} />
                <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {conv.title}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* User Profile Menu */}
        <UserProfileMenu />
      </div>

      {/* Main Content */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        position: 'relative'
      }}>
        {/* Header */}
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ color: '#fff', fontSize: '14px', fontWeight: '500' }}>Keelo.ai</div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button 
              onClick={() => setPromptLibraryOpen(true)}
              style={{
                padding: '6px 12px',
                backgroundColor: 'rgba(171, 104, 255, 0.2)',
                color: '#ab68ff',
                border: '1px solid rgba(171, 104, 255, 0.3)',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <BookOpen size={16} />
              Prompt Library
            </button>
            <button style={{
              padding: '6px 12px',
              backgroundColor: '#ab68ff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              ✨ Try Pro
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {showWelcome ? (
            <div style={{ 
              flex: 1,
              display: 'flex', 
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              padding: '20px'
            }}>
              <h1 style={{ 
                fontSize: '32px', 
                color: 'rgba(255,255,255,0.9)',
                fontWeight: 'normal',
                marginBottom: '20px',
                textAlign: 'center'
              }}>
                Hey there. Ready to analyze?
              </h1>
              
              {/* Example prompts */}
              <div style={{ 
                marginTop: '20px',
                maxWidth: '600px',
                width: '100%'
              }}>
                <p style={{
                  fontSize: '14px',
                  color: 'rgba(255,255,255,0.6)',
                  marginBottom: '16px',
                  textAlign: 'center'
                }}>
                  Try these popular examples:
                </p>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px'
                }}>
                  <button
                    onClick={() => {
                      const msg = 'stripe.com vs square.com'
                      setMessage(msg)
                      setTimeout(() => {
                        if (connectionStatus === 'connected') {
                          addMessage({
                            id: crypto.randomUUID(),
                            role: 'user',
                            content: msg,
                            timestamp: new Date(),
                          })
                          sendMessage({
                            type: 'chat',
                            payload: { content: msg },
                          })
                          setIsTyping(true)
                        }
                      }, 100)
                    }}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(171,104,255,0.1)'
                      e.currentTarget.style.borderColor = 'rgba(171,104,255,0.3)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'
                      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', fontWeight: '500' }}>
                      stripe.com vs square.com
                    </div>
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', marginTop: '4px' }}>
                      Compare payment platforms
                    </div>
                  </button>
                  
                  <button
                    onClick={() => {
                      const msg = 'Find revenue leaks on shopify.com'
                      setMessage(msg)
                      setTimeout(() => {
                        if (connectionStatus === 'connected') {
                          addMessage({
                            id: crypto.randomUUID(),
                            role: 'user',
                            content: msg,
                            timestamp: new Date(),
                          })
                          sendMessage({
                            type: 'chat',
                            payload: { content: msg },
                          })
                          setIsTyping(true)
                        }
                      }, 100)
                    }}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(171,104,255,0.1)'
                      e.currentTarget.style.borderColor = 'rgba(171,104,255,0.3)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'
                      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', fontWeight: '500' }}>
                      Find revenue leaks
                    </div>
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', marginTop: '4px' }}>
                      shopify.com e-commerce analysis
                    </div>
                  </button>
                  
                  <button
                    onClick={() => {
                      const msg = 'notion.so growth opportunities'
                      setMessage(msg)
                      setTimeout(() => {
                        if (connectionStatus === 'connected') {
                          addMessage({
                            id: crypto.randomUUID(),
                            role: 'user',
                            content: msg,
                            timestamp: new Date(),
                          })
                          sendMessage({
                            type: 'chat',
                            payload: { content: msg },
                          })
                          setIsTyping(true)
                        }
                      }, 100)
                    }}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(171,104,255,0.1)'
                      e.currentTarget.style.borderColor = 'rgba(171,104,255,0.3)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'
                      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', fontWeight: '500' }}>
                      notion.so growth tactics
                    </div>
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', marginTop: '4px' }}>
                      SaaS optimization strategies
                    </div>
                  </button>
                  
                  <button
                    onClick={() => {
                      const msg = 'SEO audit for techcrunch.com'
                      setMessage(msg)
                      setTimeout(() => {
                        if (connectionStatus === 'connected') {
                          addMessage({
                            id: crypto.randomUUID(),
                            role: 'user',
                            content: msg,
                            timestamp: new Date(),
                          })
                          sendMessage({
                            type: 'chat',
                            payload: { content: msg },
                          })
                          setIsTyping(true)
                        }
                      }, 100)
                    }}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(171,104,255,0.1)'
                      e.currentTarget.style.borderColor = 'rgba(171,104,255,0.3)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'
                      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'
                    }}
                  >
                    <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', fontWeight: '500' }}>
                      SEO audit
                    </div>
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', marginTop: '4px' }}>
                      techcrunch.com content strategy
                    </div>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '20px', maxWidth: '768px', margin: '0 auto', width: '100%' }}>
              {messages.map((msg) => (
                <div key={msg.id} style={{
                  marginBottom: '24px',
                  display: 'flex',
                  gap: '12px',
                  padding: '20px 0'
                }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    backgroundColor: msg.role === 'user' ? '#ab68ff' : '#10a37f',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    color: 'white',
                    fontWeight: '600',
                    flexShrink: 0
                  }}>
                    {msg.role === 'user' ? 'Y' : 'G'}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      color: 'rgba(255,255,255,0.9)', 
                      fontSize: '14px',
                      fontWeight: '600',
                      marginBottom: '8px'
                    }}>
                      {msg.role === 'user' ? 'You' : 'Keelo.ai'}
                    </div>
                    <div style={{ 
                      color: 'rgba(255,255,255,0.8)', 
                      fontSize: '15px',
                      lineHeight: '1.6',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {msg.content}
                    </div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div style={{
                  display: 'flex',
                  gap: '12px',
                  padding: '20px 0'
                }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    backgroundColor: '#10a37f',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    color: 'white',
                    fontWeight: '600'
                  }}>
                    G
                  </div>
                  <div style={{ paddingTop: '8px' }}>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <span style={{ 
                        width: '8px', 
                        height: '8px', 
                        borderRadius: '50%', 
                        backgroundColor: 'rgba(255,255,255,0.5)',
                        animation: 'pulse 1.4s infinite'
                      }} />
                      <span style={{ 
                        width: '8px', 
                        height: '8px', 
                        borderRadius: '50%', 
                        backgroundColor: 'rgba(255,255,255,0.5)',
                        animation: 'pulse 1.4s infinite',
                        animationDelay: '0.2s'
                      }} />
                      <span style={{ 
                        width: '8px', 
                        height: '8px', 
                        borderRadius: '50%', 
                        backgroundColor: 'rgba(255,255,255,0.5)',
                        animation: 'pulse 1.4s infinite',
                        animationDelay: '0.4s'
                      }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Input */}
        <div style={{
          padding: '0 20px 20px',
          width: '100%',
          maxWidth: '768px',
          margin: '0 auto',
          boxSizing: 'border-box'
        }}>
          <div style={{
            backgroundColor: '#2f2f2f',
            borderRadius: '24px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <button style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Paperclip size={18} color="rgba(255,255,255,0.5)" />
            </button>
            <input 
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter a domain to analyze (e.g., stripe.com)"
              style={{
                flex: 1,
                backgroundColor: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'white',
                fontSize: '15px'
              }}
            />
            {message && message.trim() ? (
              <button 
                onClick={handleSendMessage}
                disabled={connectionStatus !== 'connected'}
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: connectionStatus === 'connected' ? 'white' : 'rgba(255,255,255,0.3)',
                  border: 'none',
                  cursor: connectionStatus === 'connected' ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <ArrowUp size={20} color={connectionStatus === 'connected' ? 'black' : 'rgba(0,0,0,0.3)'} />
              </button>
            ) : (
              <button style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Mic size={18} color="rgba(255,255,255,0.5)" />
              </button>
            )}
          </div>
          <p style={{
            textAlign: 'center',
            fontSize: '12px',
            color: 'rgba(255,255,255,0.5)',
            marginTop: '8px'
          }}>
            Keelo.ai can analyze websites and provide insights that may be inaccurate.
          </p>
        </div>
      </div>
      
      {/* Prompt Library Sidebar */}
      <PromptLibrary 
        isOpen={promptLibraryOpen}
        onClose={() => setPromptLibraryOpen(false)}
        onSelectPrompt={handlePromptSelect}
      />
      
      {/* Integrations Panel */}
      <IntegrationsPanel
        isOpen={integrationsOpen}
        onClose={() => setIntegrationsOpen(false)}
      />
      
      {/* Auth Modal */}
      <AuthModalStyled
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </div>
  )
}