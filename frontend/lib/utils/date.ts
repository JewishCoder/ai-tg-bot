import { format, formatDistanceToNow, parseISO } from "date-fns"
import { ru } from "date-fns/locale"
import { Period } from "@/types/api"

export function formatTimestamp(timestamp: string, formatString: string): string {
  return format(parseISO(timestamp), formatString, { locale: ru })
}

export function formatChartDate(timestamp: string, period: Period): string {
  const date = parseISO(timestamp)

  switch (period) {
    case "day":
      return format(date, "HH:mm", { locale: ru })
    case "week":
    case "month":
      return format(date, "dd MMM", { locale: ru })
    default:
      return format(date, "dd MMM", { locale: ru })
  }
}

export function formatRelativeTime(timestamp: string): string {
  return formatDistanceToNow(parseISO(timestamp), {
    addSuffix: true,
    locale: ru,
  })
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} мин`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}ч ${mins}м` : `${hours}ч`
}
