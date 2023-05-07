import { getDateOfISOWeek, getFirstDayOfWeek, getWeekNumber, getYearWeek, weekDelta } from "src/modules/WeekUtils"
import { test, expect, describe, vi } from "vitest"

describe("WeekUtils", () => {
  test("getWeekNumber", () => {
    expect(getWeekNumber(new Date(2000, 0, 1))).toEqual([1999, 52])
    expect(getWeekNumber(new Date(2000, 0, 3))).toEqual([2000, 1])
  })
  test("getYearWeek", () => {
    const date = new Date(2000, 0, 3)
    vi.setSystemTime(date)
    expect(getYearWeek()).toEqual([2000, 1])
  })
  test("getFirstDayOfWeek", () => {
    const date = new Date(2000, 0, 3)
    expect(getFirstDayOfWeek(date)).toEqual(3)
  })
  test("getDateOfISOWeek", () => {
    expect(getDateOfISOWeek(2000, 1).toDateString()).toEqual("Mon Jan 03 2000")
  })
  test("weekDelta", () => {
    expect(weekDelta(2000, 1, 1)).toEqual({ year: 2000, week: 2 })
    expect(weekDelta(2000, 52, 1)).toEqual({ year: 2001, week: 1 })
    expect(weekDelta(2000, 1, -1)).toEqual({ year: 1999, week: 52 })
  })
})
