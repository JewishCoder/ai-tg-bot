"use client"

import { useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Trophy, ChevronDown } from "lucide-react"
import { TopUser } from "@/types/api"
import { formatRelativeTime } from "@/lib/utils/date"
import { formatNumber } from "@/lib/utils/formatters"

interface TopUsersTableProps {
  data: TopUser[]
  isLoading: boolean
}

const getRankBadge = (rank: number) => {
  const variants = {
    1: { color: "bg-yellow-500", label: "🥇" },
    2: { color: "bg-gray-400", label: "🥈" },
    3: { color: "bg-amber-700", label: "🥉" },
  }

  const badge = variants[rank as keyof typeof variants]

  if (badge) {
    return (
      <span
        className={`inline-flex h-8 w-8 items-center justify-center rounded-full ${badge.color} font-bold text-white`}
      >
        {badge.label}
      </span>
    )
  }

  return <span className="text-muted-foreground">#{rank}</span>
}

export function TopUsersTable({ data, isLoading }: TopUsersTableProps) {
  const [isOpen, setIsOpen] = useState(false) // Скрыто по умолчанию

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Топ пользователи</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5" />
                Топ пользователи
              </CardTitle>
              <p className="text-muted-foreground text-sm">По количеству сообщений</p>
            </div>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm">
                <ChevronDown
                  className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
                />
              </Button>
            </CollapsibleTrigger>
          </div>
        </CardHeader>
        <CollapsibleContent>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">Ранг</TableHead>
                  <TableHead>User ID</TableHead>
                  <TableHead className="text-right">Сообщений</TableHead>
                  <TableHead className="text-right">Диалогов</TableHead>
                  <TableHead>Последняя активность</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((user, index) => (
                  <TableRow key={user.user_id}>
                    <TableCell>{getRankBadge(index + 1)}</TableCell>
                    <TableCell className="font-mono text-sm">{user.user_id}</TableCell>
                    <TableCell className="text-right font-medium">
                      {formatNumber(user.total_messages)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant="outline">{user.dialog_count}</Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {formatRelativeTime(user.last_activity)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  )
}
