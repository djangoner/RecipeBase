import { Pinia } from "pinia"
import { simpleDiff } from "./SyncUtils"

export interface AnyData {
  [key: string]: unknown
}

export interface StructureWebsocketData {
  type: string
  data: AnyData
}

export interface ModelUpdateData extends StructureWebsocketData {
  created: boolean
  deleted: boolean
  model: string
}

export interface MappingGetSet {
  get: CallableFunction
  set: CallableFunction
}

export type MappingValue = string | MappingGetSet

export interface Mapping {
  name?: string
  idField?: string
  single_attr?: MappingValue
  array_attr?: MappingValue
}

export interface StoreMappingObject {
  [key: string]: Mapping
}

export interface UpdatedCallback {
  type: "single" | "array"
  old?: object
  new?: object
  changed?: string[]
  update: ModelUpdateData
}

export class RealTime {
  store: Pinia
  storeMapping: StoreMappingObject

  constructor(store: Pinia, storeMapping: StoreMappingObject) {
    this.store = store
    this.storeMapping = storeMapping
  }

  getStore(attr: MappingValue): unknown | unknown[] {
    if (typeof attr === "string") {
      // String
      if (!Object.hasOwn(this.store, attr)) {
        console.warn(`getStore hasn't attribute '${attr}'`)
        return null
      }
      return this.store[attr]
    } else {
      // Getter
      return attr.get()
    }
  }

  setStore(attr: MappingValue, value: unknown) {
    if (typeof attr === "string") {
      // String
      if (!Object.hasOwn(this.store, attr)) {
        console.warn(`setStore hasn't attribute '${attr}'`)
        return null
      }
      this.store[attr] = value
    } else {
      // Setter
      attr.set(value)
    }
  }

  onModelUpdate(data: ModelUpdateData, callback?: (data: UpdatedCallback) => void) {
    // console.debug("Processing model update...")
    // -- Get model info

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const modelInfo = this.storeMapping[data.model]
    if (!modelInfo) {
      console.info(`Model info for ${data.model} not found, update was ignored.`)
      return
    }

    const idField = modelInfo.idField || "id"
    const newModel = data.data

    console.debug("[RealTime] Processing model update: ", modelInfo)

    if (modelInfo.single_attr) {
      if (data.deleted) {
        this.setStore(modelInfo.single_attr, null)
      } else {
        const currValue = this.getStore(modelInfo.single_attr)
        if (currValue && currValue[idField] == newModel[idField]) {
          this.setStore(modelInfo.single_attr, newModel)
        }
      }
      console.debug("[RealTime] Updated single attr: ", newModel)
    }
    if (modelInfo.array_attr) {
      const arr_before_copy: unknown[] = this.getStore(modelInfo.array_attr)
      const arr_before_idx = arr_before_copy?.findIndex((i) => i[idField] == newModel[idField])
      const callbackData = {
        type: "array",
        old: arr_before_idx ? (Object.assign({}, arr_before_copy[arr_before_idx]) as object) : undefined,
        new: newModel,
        changed: [] as string[],
        update: data,
      }

      if (data.created) {
        // Create
        if (!arr_before_idx) {
          arr_before_copy.push(newModel)
        }
      } else if (data.deleted) {
        // Delete
        if (arr_before_idx !== -1) {
          arr_before_copy.splice(arr_before_idx, 1)
        }
      } else {
        // Update
        if (arr_before_idx !== -1) {
          arr_before_copy[arr_before_idx] = newModel
        }
      }
      if (callback) {
        if (callbackData.old) {
          callbackData.changed = simpleDiff(callbackData.old, callbackData.new).filter((i) => i !== "idLocal")
        }
        callback(callbackData)
      }
      this.setStore(modelInfo.array_attr, arr_before_copy)
      console.debug("[RealTime] Updated array attr: ", arr_before_idx, arr_before_copy)
    }
  }
}
