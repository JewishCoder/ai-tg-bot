'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ActivityPoint, Period } from '@/types/api'
import { formatChartDate } from '@/lib/utils/date'
import { formatNumber } from '@/lib/utils/formatters'

interface ActivityChartProps {
  data: ActivityPoint[]
  period: Period
  isLoading: boolean
}

export function ActivityChart({ data, period, isLoading }: ActivityChartProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Активность по времени</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    )
  }

  const chartData = data.map((point) => ({
    timestamp: formatChartDate(point.timestamp, period),
    messages: point.message_count,
    users: point.active_users,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Активность по времени</CardTitle>
        <p className="text-sm text-muted-foreground">
          Сообщения и активные пользователи
        </p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              fontSize={12}
              tickMargin={10}
            />
            <YAxis 
              yAxisId="left"
              fontSize={12}
              tickFormatter={(value: number) => formatNumber(value)}
            />
            <YAxis 
              yAxisId="right" 
              orientation="right"
              fontSize={12}
              tickFormatter={(value: number) => formatNumber(value)}
            />
            <Tooltip 
              formatter={(value: number) => formatNumber(value)}
              labelStyle={{ color: 'hsl(var(--foreground))' }}
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px',
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="messages"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              name="Сообщения"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="users"
              stroke="hsl(var(--chart-2))"
              strokeWidth={2}
              name="Пользователи"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

