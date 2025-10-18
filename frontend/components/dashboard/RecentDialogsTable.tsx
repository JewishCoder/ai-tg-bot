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
import { ChevronDown } from "lucide-react"
import { RecentDialog } from "@/types/api"
import { formatRelativeTime, formatDuration } from "@/lib/utils/date"

interface RecentDialogsTableProps {
  data: RecentDialog[]
  isLoading: boolean
}

export function RecentDialogsTable({ data, isLoading }: RecentDialogsTableProps) {
  const [isOpen, setIsOpen] = useState(false) // Скрыто по умолчанию

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Последние диалоги</CardTitle>
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
              <CardTitle>Последние диалоги</CardTitle>
              <p className="text-muted-foreground text-sm">{data.length} последних диалогов</p>
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
                  <TableHead>User ID</TableHead>
                  <TableHead className="text-right">Сообщений</TableHead>
                  <TableHead>Последняя активность</TableHead>
                  <TableHead className="text-right">Длительность</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((dialog) => (
                  <TableRow key={dialog.user_id}>
                    <TableCell className="font-mono text-sm">{dialog.user_id}</TableCell>
                    <TableCell className="text-right">
                      <Badge variant="secondary">{dialog.message_count}</Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {formatRelativeTime(dialog.last_message_at)}
                    </TableCell>
                    <TableCell className="text-right text-sm">
                      {formatDuration(dialog.duration_minutes)}
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
