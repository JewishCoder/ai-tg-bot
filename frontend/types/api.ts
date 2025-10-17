export interface Summary {
  total_dialogs: number
  active_users: number
  avg_dialog_length: number
}

export interface ActivityPoint {
  timestamp: string
  message_count: number
  active_users: number
}

export interface RecentDialog {
  dialog_id: string
  user_id: number
  message_count: number
  last_activity: string
  duration_minutes: number
}

export interface TopUser {
  user_id: number
  username: string
  message_count: number
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

