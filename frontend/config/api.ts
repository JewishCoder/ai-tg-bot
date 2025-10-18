export const apiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081",
  timeout: 30000,
  auth: {
    username: process.env.NEXT_PUBLIC_API_USERNAME || "",
    password: process.env.NEXT_PUBLIC_API_PASSWORD || "",
  },
  endpoints: {
    stats: "/api/v1/stats",
    health: "/health",
  },
}

export type ApiConfig = typeof apiConfig
