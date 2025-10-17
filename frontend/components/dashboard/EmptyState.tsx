import { FileQuestion } from 'lucide-react'

interface EmptyStateProps {
  message?: string
}

export function EmptyState({ message = 'Нет данных для отображения' }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-[300px] text-center">
      <FileQuestion className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold">Нет данных</h3>
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  )
}

