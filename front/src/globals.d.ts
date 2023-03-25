// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { ComponentCustomProperties } from "vue"
import QuerySynchronizer from "@oarepo/vue-query-synchronizer"

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $query: QuerySynchronizer
  }
}
