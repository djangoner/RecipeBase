import { ref } from "vue"

export const isOnline = ref(navigator.onLine)

window.addEventListener("online", function () {
  console.debug("[isOnline] now online")
  isOnline.value = true
})
window.addEventListener("offline", function () {
  console.debug("[isOnline] now offline")
  isOnline.value = false
})
