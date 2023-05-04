import { boot, store } from "quasar/wrappers"
import { useBaseStore } from "src/stores/base"
import ReconnectingWebSocket from "reconnecting-websocket"
import { RealTime, StoreMappingObject, ModelUpdateData } from "src/modules/RealTime"
import { Ref, ref } from "vue"

const URL = (location.protocol == "https" ? "wss" : "ws") + "://" + location.host + "/ws/realtime"

const socket = new ReconnectingWebSocket(URL, [], {
  connectionTimeout: 1000,
  // maxRetries: 10,
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
}

const realTime = new RealTime(store, storeMapping)

export const websocketState: Ref<boolean | null> = ref(null)

export default boot((/* { app, router, ... } */) => {
  console.debug("Socket init: ", socket)

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
      realTime.onModelUpdate(data as ModelUpdateData)
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
