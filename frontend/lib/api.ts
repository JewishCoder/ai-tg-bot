import axios, { AxiosInstance } from "axios"
import { apiConfig } from "@/config/api"
import { StatsResponse, Period } from "@/types/api"

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: apiConfig.baseUrl,
      timeout: apiConfig.timeout,
      headers: { "Content-Type": "application/json" },
    })
  }

  async getStats(period: Period): Promise<StatsResponse> {
    const response = await this.client.get<StatsResponse>(apiConfig.endpoints.stats, {
      params: { period },
    })
    return response.data
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get(apiConfig.endpoints.health)
    return response.data
  }
}

export const apiClient = new ApiClient()
