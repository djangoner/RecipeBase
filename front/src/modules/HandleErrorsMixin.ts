// API Errors handler v0.2

import { ApiError } from "src/client"
import { defineComponent } from "vue"
import { Notify } from "quasar"

interface RestError {
  code?: string
  detail?: string
  [key: string]: unknown
}

export type CustomAxiosError = ApiError

export function handleErrors(err: CustomAxiosError, title?: string) {
  console.warn("[ErrHandler]", { err, title })

  if (!title) {
    title = "Ошибка загрузки данных"
  }

  const data: RestError = (err?.body as unknown as RestError) || {}
  let respText

  if (!err.body && (!err.statusText || err.statusText === "ERR_NETWORK" || err.statusText == "ERR_INTERNET_DISCONNECTED")) {
    respText = "Ошибка подключения к серверу"
  } else {
    respText = [err.status, err.statusText].join(" ")
  }

  let errValidation = ""

  if (typeof data === "object") {
    console.debug("Err data: ", data)
    for (const [key, val] of Object.entries(data)) {
      // console.debug(key, val);
      if (Array.isArray(val)) {
        const errJoin = val.join(", ")
        errValidation += `${key}: ${errJoin}<br/>`
      }
    }
  }

  const caption: string =
    data?.detail ||
    data?.code ||
    errValidation ||
    respText ||
    // data ||
    `Неизвестная ошибка (${err.url})`

  Notify.create({
    type: "negative",
    message: title,
    caption: caption,
    progress: true,
    html: true,
  })
}

export const HandleErrorsMixin = defineComponent({
  methods: {
    handleErrors(err: CustomAxiosError, title?: string) {
      return handleErrors(err, title)
    },
  },
})

export default HandleErrorsMixin
