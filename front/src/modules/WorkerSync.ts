/* eslint-disable @typescript-eslint/require-await */
/* Run in server worker */

import { ProductListItemRead, ProductListWeekRead } from "src/client"
import { productListItemFromRead } from "src/Convert"
import { productListGetChanged, productListUpdateFromServer, ProductListItemSyncable, productListMarkUnchanged } from "./ProductListSync"
import { onlyChangedFields } from "./SyncUtils"
import { getYearWeek } from "./WeekUtils"

async function safeRequest(url: string, token: string, params?: RequestInit) {
  if (!params) {
    params = {}
  }
  if (!params.headers) {
    params.headers = {}
  }
  params.headers = Object.assign({}, params.headers, {
    // Add authorization header
    Authorization: "Bearer " + token,
  })

  const allParams = Object.assign(params, {})
  const resp = await fetch(url, allParams)

  if (!resp.ok) {
    console.debug("Fetch error:", resp.status, resp.statusText)
    throw new Error("Fetch error:", resp.status, resp.statusText)
  }

  return resp.json() as unknown
}

async function loadProductListWeekSafe(payload: { year: number; week: number }, token: string): Promise<ProductListWeekRead> {
  const id = `${payload?.year}_${payload?.week}`
  // ProductListWeekService.productListWeekRetrieve({ id: id })

  return (await safeRequest(`/api/v1/product_list_week/${id}/`, token)) as ProductListWeekRead
}

async function updateItemSafe(item: ProductListItemSyncable, token: string) {
  if (!item.changed) {
    return
  }
  console.debug("Updating item:", item)
  const itemExists = item.id
  const itemCleared = itemExists ? (onlyChangedFields(productListItemFromRead(item), item.changed) as ProductListItemRead) : productListItemFromRead(item)
  const url = itemExists ? `/api/v1/product_list_item/${item.id}/` : `/api/v1/product_list_item/`

  const params = {
    method: itemExists ? "PATCH" : "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(itemCleared),
  }
  return (await safeRequest(url, token, params)) as ProductListItemRead
}

async function sendSyncedNotif(payload: { year: number; week: number }, token: string) {
  const id = `${payload?.year}_${payload?.week}`
  const url = `/api/v1/product_list_week/${id}/send_synced`
  return (await safeRequest(url, token)) as ProductListItemRead
}

/* eslint-disable @typescript-eslint/require-await */
export async function runBackgroundSyncProductList(token: string) {
  console.debug("[Sync] Running background sync (productList)...")
  const [year, week] = getYearWeek()
  console.debug("Current year/week: ", year, week)

  //   const store = useBaseStore()
  const productWeek = await loadProductListWeekSafe({ year, week }, token)
  console.debug("[Sync] Loaded week from server: ", productWeek)
  await productListUpdateFromServer(productWeek)

  const itemsChanged = await productListGetChanged()
  console.debug("[Sync] Uploading updates...", "count: ", itemsChanged.length)

  itemsChanged.forEach(async (item, index) => {
    if (!item.changed) {
      return
    }
    const prc = Math.round(((index + 1) / itemsChanged.length) * 100)
    console.debug(`[Sync] ${prc}% ${index + 1}/${itemsChanged.length}`)

    await updateItemSafe(item, token)
    await productListMarkUnchanged(item)
  })

  console.debug("[Sync] Downloading new week from server...")
  const productWeek2 = await loadProductListWeekSafe({ year, week }, token)
  console.debug("[Sync] Loaded week from server: ", productWeek2)
  await productListUpdateFromServer(productWeek2)

  console.debug("[Sync] Background sync completed.")
  await sendSyncedNotif({ year, week }, token)
  return true
}
