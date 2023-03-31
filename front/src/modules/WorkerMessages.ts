/* eslint-disable @typescript-eslint/unbound-method */
import { defineComponent } from "vue"

export interface WorkerMessageData {
  [key: string]: unknown
  type: string
  status: string
}

export interface WorkerMessage {
  data: WorkerMessageData
}

export const WorkerMessagesMixin = defineComponent({
  data() {
    return {}
  },
  created: function () {
    try {
      navigator.serviceWorker.addEventListener("message", this.onWorkerMessage)
      console.debug("Listening for worker messages")
    } catch (error) {
      console.debug("Failed to listen for worker messages")
    }
  },
  beforeUnmount: function () {
    try {
      navigator.serviceWorker.removeEventListener("message", this.onWorkerMessage)
    } catch (error) {
      console.debug("Failed to unlisten for worker messages")
    }
  },
  methods: {
    onWorkerMessage(msg: WorkerMessage) {
      console.debug("Worker message: ", msg)
    },
  },
})

export default WorkerMessagesMixin
