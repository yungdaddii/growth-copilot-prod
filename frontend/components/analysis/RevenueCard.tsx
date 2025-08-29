import { TrendingDown, AlertCircle } from 'lucide-react'

interface RevenueCardProps {
  data: {
    monthly_loss: number
    annual_loss: number
    biggest_issue: string
  }
}

export function RevenueCard({ data }: RevenueCardProps) {
  return (
    <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4 space-y-3 animate-slide-up">
      <div className="flex items-start gap-3">
        <TrendingDown className="w-5 h-5 text-destructive mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-sm flex items-center gap-2">
            Revenue Impact
            <AlertCircle className="w-4 h-4 text-muted-foreground" />
          </h3>
          <div className="mt-2 space-y-1">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-destructive">
                ${(data.monthly_loss / 1000).toFixed(0)}K
              </span>
              <span className="text-sm text-muted-foreground">per month</span>
            </div>
            <div className="text-sm text-muted-foreground">
              ${(data.annual_loss / 1000).toFixed(0)}K annually
            </div>
          </div>
          {data.biggest_issue && (
            <p className="mt-3 text-sm">
              Biggest issue: <span className="font-medium">{data.biggest_issue}</span>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}