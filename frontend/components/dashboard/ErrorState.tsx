import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

interface ErrorStateProps {
  error: Error
  onRetry?: () => void
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Ошибка загрузки данных</AlertTitle>
      <AlertDescription className="flex flex-col gap-2">
        <span>{error.message}</span>
        {onRetry && (
          <Button variant="outline" size="sm" onClick={onRetry} className="w-fit">
            Повторить попытку
          </Button>
        )}
      </AlertDescription>
    </Alert>
  )
}
