import { FileQuestion } from "lucide-react"

interface EmptyStateProps {
  message?: string
}

export function EmptyState({ message = "Нет данных для отображения" }: EmptyStateProps) {
  return (
    <div className="flex h-[300px] flex-col items-center justify-center text-center">
      <FileQuestion className="text-muted-foreground mb-4 h-12 w-12" />
      <h3 className="text-lg font-semibold">Нет данных</h3>
      <p className="text-muted-foreground text-sm">{message}</p>
    </div>
  )
}
