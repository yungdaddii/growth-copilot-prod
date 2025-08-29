import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { ChatMessage } from '@/types/chat'

interface Conversation {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

interface ChatStore {
  messages: ChatMessage[]
  conversationId: string | null
  isAnalyzing: boolean
  conversations: Conversation[]
  
  addMessage: (message: ChatMessage) => void
  clearMessages: () => void
  setConversationId: (id: string) => void
  setAnalyzing: (analyzing: boolean) => void
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void
  saveConversation: () => void
  loadConversation: (id: string) => void
  deleteConversation: (id: string) => void
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      messages: [],
      conversationId: null,
      isAnalyzing: false,
      conversations: [],

      addMessage: (message) => {
        set((state) => ({
          messages: [...state.messages, message],
        }))
        // Auto-save after each message
        if (get().conversationId) {
          get().saveConversation()
        }
      },

      clearMessages: () =>
        set({
          messages: [],
          conversationId: null,
        }),

      setConversationId: (id) => {
        set({ conversationId: id })
        // Create or update conversation
        get().saveConversation()
      },

      setAnalyzing: (analyzing) =>
        set({ isAnalyzing: analyzing }),

      updateMessage: (id, updates) =>
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
          ),
        })),

      saveConversation: () => {
        const state = get()
        if (!state.conversationId || state.messages.length === 0) return

        const title = state.messages[0]?.content.slice(0, 50) || 'New Conversation'
        const existingIndex = state.conversations.findIndex(
          (c) => c.id === state.conversationId
        )

        const conversation: Conversation = {
          id: state.conversationId,
          title,
          messages: state.messages,
          createdAt: existingIndex >= 0 
            ? state.conversations[existingIndex].createdAt 
            : new Date(),
          updatedAt: new Date(),
        }

        if (existingIndex >= 0) {
          // Update existing conversation
          set((state) => ({
            conversations: state.conversations.map((c, i) =>
              i === existingIndex ? conversation : c
            ),
          }))
        } else {
          // Add new conversation
          set((state) => ({
            conversations: [conversation, ...state.conversations],
          }))
        }
      },

      loadConversation: (id) => {
        const conversation = get().conversations.find((c) => c.id === id)
        if (conversation) {
          set({
            conversationId: conversation.id,
            messages: conversation.messages,
          })
        }
      },

      deleteConversation: (id) => {
        set((state) => ({
          conversations: state.conversations.filter((c) => c.id !== id),
          // Clear current conversation if it's the one being deleted
          ...(state.conversationId === id && {
            conversationId: null,
            messages: [],
          }),
        }))
      },
    }),
    {
      name: 'growth-copilot-chat',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        conversations: state.conversations,
      }),
    }
  )
)