'use client'

import { Users, MessageSquare, Activity } from "lucide-react"
import { StatsCard } from "./StatsCard"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Summary } from "@/types/api"
import { formatNumber } from "@/lib/utils/formatters"

interface SummarySectionProps {
  data: Summary | undefined
  isLoading: boolean
}

export function SummarySection({ data, isLoading }: SummarySectionProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <Skeleton className="h-4 w-[100px]" />
              <Skeleton className="h-8 w-[120px] mt-2" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <StatsCard
        title="Всего пользователей"
        value={formatNumber(data.total_users)}
        icon={Users}
        description="Уникальные пользователи"
      />
      <StatsCard
        title="Всего сообщений"
        value={formatNumber(data.total_messages)}
        icon={MessageSquare}
        description="За выбранный период"
      />
      <StatsCard
        title="Активные диалоги"
        value={formatNumber(data.active_dialogs)}
        icon={Activity}
        description="Диалоги с активностью"
      />
    </div>
  )
}

