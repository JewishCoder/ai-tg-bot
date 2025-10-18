import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { Period } from "@/types/api"

export function useStats(period: Period) {
  return useQuery({
    queryKey: ["stats", period],
    queryFn: () => apiClient.getStats(period),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60, // 1 minute
  })
}
