import { boot } from "quasar/wrappers"
import { useBaseStore } from "src/stores/base"
import ReconnectingWebSocket from "reconnecting-websocket"
import { RealTime, StoreMappingObject, ModelUpdateData } from "src/modules/RealTime"
import { Ref, ref } from "vue"

const URL = (location.protocol == "https:" ? "wss" : "ws") + "://" + location.host + "/ws/realtime"

const socket = new ReconnectingWebSocket(URL, [], {
  connectionTimeout: 1000,
  startClosed: !navigator.onLine, // Don't connect when started offline
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

const store = useBaseStore()

const storeMapping: StoreMappingObject = {
  // const storeMapping = {
  ProductListItem: {
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
    single_attr: "week_plan",
  },
  Recipe: {
    single_attr: "recipe",
    array_attr: "recipes",
  },
  RecipePlan: {
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

export default boot((/* { app, router, ... } */) => {
  socket.onmessage = (evt) => {
    let data: StructureWebsocketData

    try {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      data = JSON.parse(evt.data as string)
    } catch (error) {
      console.error("[Socker] message decoding error: ", error)
      return
    }

    console.debug("[Socket] message: ", data)

    if (data.type == "model_update") {
      try {
        realTime.onModelUpdate(data as ModelUpdateData)
      } catch (error) {
        console.error("[Socker] model update error: ", error)
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
