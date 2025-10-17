'use client'

import { useState } from "react"
import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { PeriodFilter } from "@/components/dashboard/PeriodFilter"
import { SummarySection } from "@/components/dashboard/SummarySection"
import { ActivityChart } from "@/components/dashboard/ActivityChart"
import { RecentDialogsTable } from "@/components/dashboard/RecentDialogsTable"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { Header } from "@/components/layout/Header"
import { Period } from "@/types/api"
import { useStats } from "@/lib/hooks/useStats"

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>('week')
  const { data: stats, isLoading } = useStats(period)

  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>
        <Header />
        <div className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
              <p className="text-muted-foreground">
                Статистика диалогов Telegram бота
              </p>
            </div>
            <PeriodFilter value={period} onChange={setPeriod} />
          </div>
          
          <SummarySection data={stats?.summary} isLoading={isLoading} />
          
          <ActivityChart 
            data={stats?.activity_timeline || []} 
            period={period}
            isLoading={isLoading}
          />
          
          <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
            <RecentDialogsTable 
              data={stats?.recent_dialogs || []} 
              isLoading={isLoading}
            />
            {/* Здесь будет TopUsersTable */}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

