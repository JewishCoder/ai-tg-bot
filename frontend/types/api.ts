export interface Summary {
  total_users: number
  total_messages: number
  active_dialogs: number
}

export interface ActivityPoint {
  timestamp: string
  message_count: number
  active_users: number
}

export interface RecentDialog {
  user_id: number
  message_count: number
  last_message_at: string
  duration_minutes: number
}

export interface TopUser {
  user_id: number
  total_messages: number
  dialog_count: number
  last_activity: string
}

export interface StatsResponse {
  summary: Summary
  activity_timeline: ActivityPoint[]
  recent_dialogs: RecentDialog[]
  top_users: TopUser[]
}

export type Period = "day" | "week" | "month"

