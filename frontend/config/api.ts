export const apiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  endpoints: {
    stats: "/stats",
    health: "/health",
  },
  timeout: 10000,
}

export type ApiConfig = typeof apiConfig
