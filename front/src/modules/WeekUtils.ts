import { date } from "quasar"

export function getWeekNumber(d: Date): [number, number] {
  // Copy date so don't modify original
  d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
  // Set to nearest Thursday: current date + 4 - current day number
  // Make Sunday's day number 7
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7))
  // Get first day of year
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  // Calculate full weeks to nearest Thursday
  const weekNo = Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
  // Return array of year and week number
  return [d.getUTCFullYear(), weekNo]
}

export function getFirstDayOfWeek(d: Date): number {
  const date = new Date(d)
  const day = date.getDay()

  const diff = date.getDate() - day + (day === 0 ? -6 : 1)

  return diff
  // return new Date(date.setDate(diff));
}

export function getDateOfISOWeek(y: number, w: number): Date {
  const simple = new Date(y, 0, 1 + (w - 1) * 7)
  const dow = simple.getDay()
  const ISOweekStart = simple
  if (dow <= 4) ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1)
  else ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay())
  return ISOweekStart
}

export function getYearWeek(): [number, number] {
  const today = new Date()
  let year, week

  // If today is friday or weekend
  // console.debug('Today: ', today.getDay());
  if (today.getDay() >= 5 || today.getDay() == 0) {
    const date = new Date()
    date.setDate(date.getDate() + 7)
    ;[year, week] = getWeekNumber(date)
  } else {
    ;[year, week] = getWeekNumber(new Date())
  }

  return [year, week]
}

export function weekDelta(year: number, week: number, delta: number): YearWeek {
  week += delta

  if (week <= 0) {
    week = 52
    year -= 1
  } else if (week > 52) {
    week = 1
    year += 1
  }

  return { year: year, week: week }
}

export const WeekDays: { [key: number]: string } = {
  0: "Вс (прошлый)",
  1: "Понедельник",
  2: "Вторник",
  3: "Среда",
  4: "Четверг",
  5: "Пятница",
  6: "Суббота",
  7: "Восскресенье",
}
export const WeekDaysShort: { [key: number]: string } = {
  1: "Пн",
  2: "Вт",
  3: "Ср",
  4: "Чт",
  5: "Пт",
  6: "Сб",
  7: "Вс",
}

export interface YearWeek {
  year: number
  week: number
}

export interface YearWeekNullable {
  year: number | null
  week: number | null
}

export interface DatePicker {
  from: Date | string
  to: Date | string
}

export const WeekDaysColors: { [key: number]: string } = {
  0: "text-light-green-6",
  1: "text-teal",
  2: "text-cyan",
  3: "text-light-blue",
  4: "text-blue-10",
  5: "text-indigo",
  6: "text-purple",
  7: "text-deep-purple",
}

export const priorityColors: { [key: number]: string } = {
  1: "red",
  2: "orange",
  3: "yellpw",
  4: "green",
  5: "grey",
}
