import { boot, store } from "quasar/wrappers"
import { useBaseStore } from "src/stores/base"
import ReconnectingWebSocket from "reconnecting-websocket"

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

interface ModelUpdateData extends StructureWebsocketData {
  created: boolean
  model: string
}

interface MappingGetSet {
  get: CallableFunction
  set: CallableFunction
}

type MappingValue = string | MappingGetSet

interface Mapping {
  idField?: string
  single_attr?: MappingValue
  array_attr?: MappingValue
}

interface MappingObject {
  [key: string]: Mapping
}

function getStore(attr: MappingValue): unknown | unknown[] {
  if (typeof attr === "string") {
    // String
    if (!Object.hasOwn(store, attr)) {
      console.warn(`getStore hasn't attribute '${attr}'`)
      return null
    }
    return store[attr]
  } else {
    // Getter
    return attr.get()
  }
}

function setStore(attr: MappingValue, value: unknown) {
  if (typeof attr === "string") {
    // String
    if (!Object.hasOwn(store, attr)) {
      console.warn(`setStore hasn't attribute '${attr}'`)
      return null
    }
    store[attr] = value
  } else {
    // Setter
    attr.set(value)
  }
}

function onModelUpdate(data: ModelUpdateData) {
  // console.debug("Processing model update...")
  // -- Get model info

  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const modelInfo = storeMapping[data.model]
  if (!modelInfo) {
    console.info(`Model info for ${data.model} not found, update was ignored.`)
    return
  }

  const idField = modelInfo.idField || "id"
  const newModel = data.data

  // console.debug("Model info: ", modelInfo, getStore(modelInfo.single_attr))

  if (modelInfo.single_attr) {
    console.debug("Updated single attr")
    setStore(modelInfo.single_attr, newModel)
  }
  if (modelInfo.array_attr) {
    const arr_before_copy: unknown[] = getStore(modelInfo.array_attr)
    const arr_before_idx = arr_before_copy?.findIndex((i) => i[idField] == newModel[idField])
    if (arr_before_idx !== undefined) {
      if (data.created) {
        // Create
        arr_before_copy.push(newModel)
      } else {
        // Update
        arr_before_copy[arr_before_idx] = newModel
      }
      setStore(modelInfo.array_attr, arr_before_copy)
      console.debug("Updated array attr")
    }
  }
}

const store = useBaseStore()

const storeMapping: MappingObject = {
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
      onModelUpdate(data as ModelUpdateData)
    }
  }

  socket.onopen = () => {
    console.debug("[Socket] connected")
  }
  socket.onclose = () => {
    console.debug("[Socket] disconnected")
  }
})
