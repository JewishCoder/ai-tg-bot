'use client'

import { useState } from "react"
import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { Header } from "@/components/layout/Header"
import { Period } from "@/types/api"

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>('week')

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
          </div>
          {/* Здесь будут компоненты дашборда */}
          <div className="text-muted-foreground">
            Текущий период: {period}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

