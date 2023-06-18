import { useDebounceFn } from "@vueuse/core"
import { ref } from "vue"

export function useDebounceFnState(...parameters: Parameters<typeof useDebounceFn>) {
  const state = ref(false)
  if (!parameters[2]) {
    parameters.push({})
  }
  if (parameters) {
    parameters[2]["rejectOnCancel"] = true
  }
  const debounced = useDebounceFn(...parameters)

  const wrapped = (...args: Parameters<(typeof parameters)[0]>) => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    const prom = debounced(...args)
    const alreadyStarted = state.value
    if (!alreadyStarted) {
      state.value = true
      // console.debug("Started")
    }
    prom
      .then((value: unknown) => {
        // console.debug("Then", value)
        state.value = false
      })
      .catch((e) => {
        // console.debug("Cancelled", e)
      })
    return prom
  }

  return {
    state,
    debounced: wrapped,
  }
}
