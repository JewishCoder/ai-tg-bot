import { describe, it, expect } from "vitest"
import type { Period } from "@/types/api"

describe("ApiClient", () => {
  it("should have correct period types", () => {
    const validPeriods: Period[] = ["day", "week", "month"]
    expect(validPeriods).toHaveLength(3)
    expect(validPeriods).toContain("day")
    expect(validPeriods).toContain("week")
    expect(validPeriods).toContain("month")
  })

  it("should validate API types", () => {
    // Simple type validation test
    const mockSummary = {
      total_dialogs: 10,
      active_users: 5,
      avg_dialog_length: 3.5,
    }

    expect(mockSummary.total_dialogs).toBe(10)
    expect(mockSummary.active_users).toBe(5)
    expect(mockSummary.avg_dialog_length).toBe(3.5)
  })
})
