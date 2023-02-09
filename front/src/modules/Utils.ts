import { date } from "quasar";
import { Task, TaskCategory } from "src/client";
import { TaskOrCategory } from "./Globals";

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
