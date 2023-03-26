import { Task, TaskCategory } from "src/client"

export interface TablePaginationOnRequest {
  rowsPerPage: number
  page: number
  sortBy: string
  descending: boolean
}

export interface TablePagination {
  rowsPerPage?: number
  rowsNumber?: number
  page?: number
  sortBy?: string
  descending?: boolean
}

export interface TableProps {
  pagination?: TablePagination
  filter?: string
}

export interface TablePropsOnRequest {
  pagination: TablePaginationOnRequest
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

export type TaskOrCategory = Task | TaskCategory

export interface AmountType {
  id: string
  title: string
}

export type AmountTypesTypes = AmountType[]
export interface AmountTypesConvert {
  [id: string]: number
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

export const priorityOptions = [
  {
    id: 1,
    name: "Наивысший",
  },
  {
    id: 2,
    name: "Высокий",
  },
  {
    id: 3,
    name: "Средний",
  },
  {
    id: 4,
    name: "Низкий",
  },
  {
    id: 5,
    name: "Низший",
  },
]

export interface WarnedPlan {
  priority: string | null
  icon: string | null
}

export interface WarnedPlans {
  [id: number]: WarnedPlan
}

export const WarningPriorities = ["low", "medium", "high"]

export const IngredientTypes = {
  grocery: "Зелень/фрукты/овощи",
  liq: "Жидкость (в литрах)",
  kilo: "Измеряется в КГ",
}

export interface RangeValue {
  min: number
  max: number
}

export interface RecipesFilters {
  cooking_time: {
    min: number
    max: number
  }
  tags_include: number[]
  tags_exclude: number[]
  ingredients_include: number[]
  ingredients_exclude: number[]
  ratings: {
    [key: number]: RangeValue
  }
}
