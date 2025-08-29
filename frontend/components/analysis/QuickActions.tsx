import { ChevronRight } from 'lucide-react'
import { useChatStore } from '@/store/chat'

interface QuickActionsProps {
  actions: Array<{
    label: string
    action: string
  }>
}

export function QuickActions({ actions }: QuickActionsProps) {
  const { addMessage } = useChatStore()

  const handleAction = (action: string) => {
    // Add user message requesting this action
    addMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content: action,
      timestamp: new Date(),
    })
    
    // TODO: Send via WebSocket
  }

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {actions.map((action, index) => (
        <button
          key={index}
          onClick={() => handleAction(action.action)}
          className="inline-flex items-center gap-1 px-3 py-1.5 text-sm rounded-md bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
        >
          {action.label}
          <ChevronRight className="w-3 h-3" />
        </button>
      ))}
    </div>
  )
}