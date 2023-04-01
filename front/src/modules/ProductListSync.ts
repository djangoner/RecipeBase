/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable no-case-declarations */
// export async function updateItem() {}

import { ProductListItemRead, ProductListWeekRead, RecipePlanWeekRead } from "src/client"
import { IDBPDatabase, openDB, deleteDB } from "idb"
import { objectUnproxy, shouldStore, simpleDiff } from "./SyncUtils"
import { getYearWeek } from "./WeekUtils"
import { useBaseStore } from "src/stores/base"

const DBVersion = 1

export interface OfflineChanges {
  [id: string]: unknown
}

export interface ProductListItemSyncable extends ProductListItemRead {
  idLocal?: number
  is_changed?: boolean
  changed?: OfflineChanges
}

export async function getDB() {
  const db = await openDB("recipebase", DBVersion, {
    upgrade(db, oldVersion, newVersion, transaction) {
      console.debug("[IDB] Upgrading DB" + `${oldVersion} -> ${newVersion || ""}`)
      // switch (oldVersion) {
      //   case 0:
      //   case 1:
      if (oldVersion <= 1) {
        const recipe_plan_week = db.createObjectStore("recipe_plan_week", {
          autoIncrement: true,
          keyPath: "id",
        })
        recipe_plan_week.createIndex("year_week", ["year", "week"], { unique: true })
        const recipe_plan_items = db.createObjectStore("recipe_plan_items", {
          autoIncrement: true,
          keyPath: "id",
        })
        recipe_plan_items.createIndex("week", ["week"], { unique: false })

        const product_list_week = db.createObjectStore("product_list_week", {
          autoIncrement: true,
          keyPath: "id",
        })
        product_list_week.createIndex("year_week", ["year", "week"], { unique: true })
        const product_list_items = db.createObjectStore("product_list_items", {
          autoIncrement: true,
          keyPath: "idLocal",
        })
        product_list_items.createIndex("week", ["week"], { unique: false })
        const meal_time = db.createObjectStore("meal_time", {
          autoIncrement: true,
          keyPath: "id",
        })
        const shops = db.createObjectStore("shops", {
          autoIncrement: true,
          keyPath: "id",
        })
        const ing_categories = db.createObjectStore("ing_categories", {
          autoIncrement: true,
          keyPath: "id",
        })
        const ingredients = db.createObjectStore("ingredients", {
          autoIncrement: true,
          keyPath: "id",
        })
      }
      // }
    },
  })
  return db
}

export async function getDBSafe() {
  return await getDB()
}

export async function destroyDB() {
  console.log("Deleting indexed DB...")
  await deleteDB("recipebase")
  console.log("indexed DB deleted.")
}

export async function autocleanDB() {
  // TODO: implement
  const db = await getDB()
  console.debug("[IDB] running autoclean...")
}

async function productListWeekAdd(db: IDBPDatabase, product_list: ProductListWeekRead) {
  "Update product_list_week object in DB"
  const listWithoutItems = Object.assign({}, product_list, { items: [] })
  const tx = db.transaction("product_list_week", "readwrite")
  const store = tx.objectStore("product_list_week")
  await store.put(objectUnproxy(listWithoutItems))

  await tx.done
}

async function productListItemsPut(db: IDBPDatabase, product_list: ProductListWeekRead) {
  const tx = db.transaction("product_list_items", "readwrite")
  const store = tx.objectStore("product_list_items")

  for (const item of product_list.items) {
    let itemCopy = Object.assign({}, item, { idLocal: item.id })
    const itemId = itemCopy.idLocal || itemCopy.id
    const itemExists = (await store.get(itemId)) as ProductListItemSyncable | null

    if (itemExists) {
      itemCopy = Object.assign({}, itemExists, itemCopy)
    }
    await store.put(objectUnproxy(itemCopy))
  }

  await tx.done
}

export async function productListUpdateFromServer(product_list: ProductListWeekRead) {
  // console.debug("[IDB] updating local with server data...")
  const [year, week] = getYearWeek()
  const needStore = shouldStore(year, week, product_list.year, product_list.week)

  if (!needStore) {
    console.debug("Shouldn't store this products list", product_list)
    return
  }

  const db = await getDB()
  // Add product list week
  await productListWeekAdd(db, product_list)

  // Sync items
  await productListItemsPut(db, product_list)
  // const tx_items = await db.transaction("product_list_item", "readwrite")
}

export async function recipePlansListUpdateFromServer(plan: RecipePlanWeekRead) {
  const [year, week] = getYearWeek()
  const needStore = shouldStore(year, week, plan.year, plan.week)

  if (!needStore) {
    console.debug("Shouldn't store this plan list", plan)
    return
  }

  const db = await getDB()
  const withoutItems = Object.assign({}, plan, { plans: [] })
  console.debug("PUT", withoutItems)
  await db.put("recipe_plan_week", withoutItems)

  for (const item of plan.plans) {
    await db.put("recipe_plan_items", objectUnproxy(item))
  }
}

export async function recipePlansGetOffline(year: number, week: number) {
  const db = await getDB()
  const objWeek = (await db.getFromIndex("recipe_plan_week", "year_week", [year, week])) as RecipePlanWeekRead | null
  if (!objWeek) {
    console.error("Can't resolve product week!", { year, week })
    return
  }
  console.debug("[IDB] fetched offline plan week: ", objWeek)
  const items = await db.getAllFromIndex("recipe_plan_items", "week", [objWeek.id])
  console.debug("[IDB] fetched offline plans list: ", items)

  const resObj = Object.assign({}, objWeek, { plans: items }) as RecipePlanWeekRead
  return resObj
}

export async function productListUpdateItem(updatedItem: ProductListItemSyncable): Promise<number> {
  const db = await getDB()
  const tx = db.transaction("product_list_items", "readwrite")
  const store = tx.objectStore("product_list_items")

  const itemId = updatedItem.idLocal || updatedItem.id
  let savedItem

  if (itemId) {
    savedItem = (await store.get(itemId)) as ProductListItemSyncable
  } else {
    savedItem = {}
  }
  if (updatedItem.id) {
    updatedItem.idLocal = updatedItem.id
  }

  const diffList = simpleDiff(savedItem, objectUnproxy(updatedItem))

  const changesList = {}
  for (const key of diffList) {
    // @ts-expect-error ignore
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    changesList[key] = updatedItem[key] // || savedItem[key] // Don't use saved item keys, they can be false
  }
  console.debug("Updating item: ", diffList, savedItem, changesList)
  // const changesList = diffList.map((key) => {
  //   return { key: updatedItem[key] || savedItem[key] }
  // })

  const putItem = objectUnproxy(Object.assign({}, savedItem, updatedItem, { changed: changesList, is_changed: Boolean(diffList) }))

  const newKey = await store.put(putItem)
  await tx.done
  return newKey as number
}

export async function productListUpdateRawItem(updatedItem: ProductListItemSyncable) {
  const db = await getDB()
  const tx = db.transaction("product_list_items", "readwrite")
  const store = tx.objectStore("product_list_items")
  const itemId = updatedItem.idLocal || updatedItem.id
  let savedItem
  if (itemId) {
    savedItem = (await store.get(itemId)) as ProductListItemSyncable
  } else {
    savedItem = {}
  }
  if (!updatedItem.idLocal && updatedItem.id) {
    updatedItem.idLocal = updatedItem.id
  }
  const putItem = objectUnproxy(Object.assign({}, savedItem, updatedItem))
  const newKey = await store.put(putItem)
  await tx.done
  return newKey
}

export async function productListMarkUnchanged(updatedItem: ProductListItemSyncable) {
  const db = await getDB()
  const tx = db.transaction("product_list_items", "readwrite")
  const store = tx.objectStore("product_list_items")

  const itemId = updatedItem.idLocal || updatedItem.id
  const savedItem = (await store.get(itemId)) as ProductListItemSyncable

  const putItem = objectUnproxy(Object.assign({}, savedItem, { changed: [], is_changed: false }))

  await store.put(putItem)
  await tx.done
}

async function productListWeekResolve(year: number, week: number) {
  const db = await getDB()
  return (await db.getFromIndex("product_list_week", "year_week", [year, week])) as ProductListWeekRead
}

export async function productListGetOffline(year: number, week: number) {
  const db = await getDB()
  // const tx = db.transaction("product_list_items", "readwrite")
  // const store = tx.objectStore("product_list_items")

  const productWeek = await productListWeekResolve(year, week)
  if (!productWeek) {
    console.error("Can't resolve product week!", { year, week })
    return
  }
  console.debug("[IDB] fetched offline product week: ", productWeek)

  const items = (await db.getAllFromIndex("product_list_items", "week", [productWeek.id])) as ProductListItemSyncable[]
  console.debug("[IDB] fetched offline product list: ", items)

  return {
    week: productWeek,
    items: items,
  }
}

export async function productListGetChanged() {
  const db = await getDB()
  // const productWeek = await productListWeekResolve(year, week)
  //
  const tx = db.transaction("product_list_items", "readwrite")
  const store = tx.objectStore("product_list_items")

  const res: ProductListItemSyncable[] = []

  for (const itemRaw of await store.getAll()) {
    const item = itemRaw as unknown as ProductListItemSyncable
    // console.debug("Checking item: ", item.is_changed, item)

    if (item.is_changed) {
      res.push(item)
    }
  }
  // console.debug("Changed items: ", res)
  await tx.done
  //
  return res
}
