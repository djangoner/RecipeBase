import { Pinia } from "pinia"

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
  idField?: string
  single_attr?: MappingValue
  array_attr?: MappingValue
}

export interface StoreMappingObject {
  [key: string]: Mapping
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

  onModelUpdate(data: ModelUpdateData) {
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

    // console.debug("Model info: ", modelInfo, getStore(modelInfo.single_attr))

    if (modelInfo.single_attr) {
      // console.debug("Updated single attr")
      if (data.deleted) {
        this.setStore(modelInfo.single_attr, null)
      } else {
        const currValue = this.getStore(modelInfo.single_attr)
        if (currValue && currValue[idField] == newModel[idField]) {
          this.setStore(modelInfo.single_attr, newModel)
        }
      }
    }
    if (modelInfo.array_attr) {
      const arr_before_copy: unknown[] = this.getStore(modelInfo.array_attr)
      const arr_before_idx = arr_before_copy?.findIndex((i) => i[idField] == newModel[idField])
      if (data.created) {
        // Create
        arr_before_copy.push(newModel)
      } else if (data.deleted) {
        // Delete
        if (arr_before_idx) {
          arr_before_copy.splice(arr_before_idx, 1)
        }
      } else {
        // Update
        if (arr_before_idx) {
          arr_before_copy[arr_before_idx] = newModel
        }
      }
      this.setStore(modelInfo.array_attr, arr_before_copy)
      // console.debug("Updated array attr")
    }
  }
}
