import { boot } from "quasar/wrappers"
import { useBaseStore } from "src/stores/base"
import ReconnectingWebSocket from "reconnecting-websocket"
import { RealTime, StoreMappingObject, ModelUpdateData, UpdatedCallback } from "src/modules/RealTime"
import { Ref, ref } from "vue"
import { Notify } from "quasar"

const URL = (location.protocol == "https:" ? "wss" : "ws") + "://" + location.host + "/ws/realtime"
const store = useBaseStore()

const socket = new ReconnectingWebSocket(URL, [], {
  connectionTimeout: 1000,
  startClosed: !navigator.onLine || !store.enableWebsocket, // Don't connect when started offline
  // maxRetries: 10,
})

window.addEventListener("online", () => {
  console.debug("[Socket] reconnecting by online state")
  socket.reconnect()
})
window.addEventListener("offline", () => {
  console.debug("[Socket] closed by offline state")
  socket.close()
})

interface AnyData {
  [key: string]: unknown
}
interface StructureWebsocketData {
  type: string
  data: AnyData
}

interface RenameField {
  [key: string]: unknown
}
interface RenameFields {
  [key: string]: RenameField
}

const storeMapping: StoreMappingObject = {
  // const storeMapping = {
  ProductListItem: {
    name: "Продукты",
    single_attr: "product_list_item",
    array_attr: {
      get() {
        return store.product_list?.items
      },
      set(val: unknown) {
        if (!store.product_list?.items) {
          return
        }
        store.product_list.items = val
      },
    },
  },
  RecipePlanWeek: {
    name: "План на неделю",
    single_attr: "week_plan",
  },
  Recipe: {
    name: "Рецепт",
    single_attr: "recipe",
    array_attr: "recipes",
  },
  RecipePlan: {
    name: "План на неделю",
    array_attr: {
      get() {
        return store.week_plan?.plans
      },
      set(val: unknown) {
        if (!store.week_plan?.plans) {
          return
        }
        store.week_plan.plans = val
      },
    },
  },
}

const realTime = new RealTime(store, storeMapping)

export const websocketState: Ref<boolean | null> = ref(null)

const updatedCallback = (data: UpdatedCallback) => {
  console.debug("Updated callback: ", data.changed, data)

  let title = ""
  let text = ""
  const renameFields: RenameFields = {
    is_completed: {
      true: "Отмечено",
      false: "Отметка отменена",
    },
  }

  const modelName = storeMapping[data.update.model]?.name || data.update.model
  title = modelName

  if (["ProductListItem"].includes(data.update.model)) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const objName: string | undefined = data.new?.title || data.new?.name
    if (objName) {
      title += `: ${objName}`
    }
  }

  if (data.changed && data.changed.length > 0) {
    if (data.changed.length === 1) {
      const changedField = data.changed[0]
      let actName
      const changedMap = renameFields[changedField]
      if (typeof changedMap == "object") {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
        actName = changedMap[data.new[changedField]] as string | undefined
      } else {
        actName = changedMap as string
      }

      text = actName || "Изменено: " + changedField
    } else {
      const changesStr = data.changed.map((change) => change)
      text = "Изменено: " + changesStr.join(", ")
    }
  } else {
    text = "Неизвестное изменение"
  }

  Notify.create({
    type: "info",
    caption: text,
    message: title,
    group: "websocketUpd",
  })
}

export default boot((/* { app, router, ... } */) => {
  socket.onmessage = (evt) => {
    let data: StructureWebsocketData

    try {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      data = JSON.parse(evt.data as string)
    } catch (error) {
      console.error("[Socket] message decoding error: ", error)
      return
    }

    console.debug("[Socket] message: ", data)

    if (data.type == "model_update") {
      try {
        realTime.onModelUpdate(data as ModelUpdateData, updatedCallback)
      } catch (error) {
        console.error("[Socket] model update error: ", error)
      }
    }
  }

  socket.onopen = () => {
    console.debug("[Socket] connected")
    websocketState.value = true
  }
  socket.onclose = (evt) => {
    console.debug("[Socket] closed", evt)
    websocketState.value = false
  }
  socket.onerror = (evt) => {
    console.debug("[Socket] error", evt)
    websocketState.value = false
  }
})
