import { useActiveElement, useDebounceFn, useMagicKeys } from "@vueuse/core"
import { computed, ref, watch } from "vue"

const aliasMap = {
  й: "q",
  ц: "w",
  у: "e",
  к: "r",
  е: "t",
  н: "y",
  г: "u",
  ш: "i",
  щ: "o",
  з: "p",
  х: "[",
  ъ: "]",
  ф: "a",
  ы: "s",
  в: "d",
  а: "f",
  п: "g",
  р: "h",
  о: "j",
  л: "k",
  д: "l",
  ж: ";",
  э: "'",
  я: "z",
  ч: "x",
  с: "c",
  м: "v",
  и: "b",
  т: "n",
  ь: "m",
  б: ",",
  ю: ".",
  ".": "/",
}

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

interface KeyBindingMap {
  [keybinding: string]: (keys: string[]) => void
}
interface ShortcutsOptions {
  allowInput: boolean
}

export function useShortcutcs(keymap: KeyBindingMap, options?: ShortcutsOptions) {
  const keys = useMagicKeys({ aliasMap: aliasMap })
  const activeElement = useActiveElement()
  const notUsingInput = computed(() => activeElement.value?.tagName !== "INPUT" && activeElement.value?.tagName !== "TEXTAREA")

  watch(keys.current, () => {
    if (!(options?.allowInput || notUsingInput.value)) {
      return
    }
    const keysActive = Array.from(keys.current.values())
    const keysStr = keysActive.join("_")

    const keybindingActive = Object.keys(keymap).find((keys) => keysStr.indexOf(keys) !== -1)
    // console.debug("[Keys]: ", { keysStr, keybindingActive })
    if (keybindingActive) {
      keymap[keybindingActive](keysActive)
    }
  })
}
