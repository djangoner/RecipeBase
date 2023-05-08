import { getDateOfISOWeek } from "./WeekUtils"

const storeWeeks = 5

export interface OfflineChanges {
  [id: string]: unknown
}

export function shouldStore(year1: number, week1: number, year2: number, week2: number): boolean {
  const date1 = getDateOfISOWeek(year1, week1)
  const date2 = getDateOfISOWeek(year2, week2)

  const difference = date2.getTime() - date1.getTime()
  const daysDiff = Math.ceil(difference / (1000 * 3600 * 24))
  return daysDiff < storeWeeks * 7
}

export function objectUnproxy<T>(obj: object | [] | null): T {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return JSON.parse(JSON.stringify(obj))
}

export function onlyChangedFields(obj: object, changed: OfflineChanges) {
  const res: { [id: string]: unknown } = {}
  for (const key in obj) {
    if (Object.hasOwn(changed, key)) {
      res[key] = changed[key]
    }
  }
  return res
}

export function mockedPaginatedResponse(items: unknown[], payload?: object) {
  // @ts-expect-error ignore
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const pageSize = payload?.pageSize || 20
  return {
    count: items.length,
    total_pages: Math.ceil(items.length) / pageSize,
    results: items,
  }
}

export function compareObjects(a: unknown, b: unknown) {
  if (Array.isArray(a) && Array.isArray(b)) {
    return JSON.stringify(a) === JSON.stringify(b)
  } else if (typeof a === "object" && typeof b === "object") {
    return JSON.stringify(a) === JSON.stringify(b)
  }

  return a === b
}

export function simpleDiff(a: object, b: object): string[] {
  "Return list of changed properties in last object"
  const res: string[] = []

  for (const key in a) {
    // @ts-expect-error ignore
    const oldVal: unknown = a[key]
    // @ts-expect-error ignore
    const newVal: unknown = b[key]

    const isEq = compareObjects(oldVal, newVal)

    if (!isEq) {
      // console.debug("Diff found: ", oldVal, newVal)
      res.push(key)
    }
  }
  return res
}
