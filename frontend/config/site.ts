export const siteConfig = {
  name: "AI Telegram Bot Dashboard",
  description: "Dashboard для мониторинга статистики диалогов AI Telegram бота",
  url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  links: {
    github: "https://github.com/JewishCoder/ai-tg-bot",
  },
}

export type SiteConfig = typeof siteConfig
