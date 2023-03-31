// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { ComponentCustomProperties } from "vue"
import QuerySynchronizer from "@oarepo/vue-query-synchronizer"

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $query: QuerySynchronizer
  }
}

interface SyncManager {
  getTags(): Promise<string[]>
  register(tag: string): Promise<void>
}

declare global {
  interface ServiceWorkerRegistration {
    readonly sync: SyncManager
  }

  interface SyncEvent extends ExtendableEvent {
    readonly lastChance: boolean
    readonly tag: string
  }

  interface ServiceWorkerGlobalScopeEventMap {
    sync: SyncEvent
  }
}
