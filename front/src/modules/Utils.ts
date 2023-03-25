import { date } from "quasar";
import { IngredientRead, Task, TaskCategory } from "src/client";
import { TaskOrCategory, WarnedPlan } from "./Globals";

export function isTaskCategory(
  item: Task | TaskCategory
): item is TaskCategory {
  return !("is_completed" in item);
}

export function TaskCategoryCountCompleted(category: TaskOrCategory) {
  return category.childrens.filter((t) => t.is_completed).length;
}
export function TaskCategoryCountAll(category: TaskOrCategory) {
  return category.childrens.length;
}

export function dateFormat(dt: Date | string): string {
  return date.formatDate(dt, "YYYY.MM.DD");
}

export function clearPayload(payload: object): object {
  return Object.fromEntries(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    Object.entries(payload).filter(([_, v]) => v != null && v != "")
  );
}

export function getWarningPriorityColor(priority: string | null): string {
  switch (priority) {
    case "high":
      return "red";
    case "low":
      return "green";
    default:
      return "orange";
  }
}

export function getPackSuffix(ingredient: IngredientRead): string {
  switch (ingredient.type) {
    case "liq":
      return "л";
    case "kilo":
      return "кг";
    case "grocery":
      return "кг";

    default:
      return "шт";
  }
}
