export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: {
    type?: string
    progress?: number
    revenue_card?: {
      monthly_loss: number
      annual_loss: number
      biggest_issue: string
    }
    quick_actions?: Array<{
      label: string
      action: string
    }>
    quick_wins?: Array<{
      title: string
      current_state: string
      recommended_state: string
      improvement_potential: string
      implementation_time: string
      implementation_steps: string[]
      impact_score: number
    }>
    [key: string]: any
  }
  timestamp: Date
}

export interface Analysis {
  id: string
  domain: string
  status: 'pending' | 'analyzing' | 'completed' | 'failed'
  results?: {
    performance_score: number
    conversion_score: number
    mobile_score: number
    seo_score: number
    issues_found: any[]
    quick_wins: any[]
  }
}