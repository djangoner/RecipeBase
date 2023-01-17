import { AxiosError, AxiosResponse } from "axios";
import { defineComponent } from "vue";

interface RestError {
  code?: string;
  detail?: string;
  [key: string]: unknown;
}

interface HandleErrorsState {
  isOnLine: boolean;
  httpErrors: object;
}

export type CustomAxiosError = AxiosError<AxiosResponse>;

export const HandleErrorsMixin = defineComponent({
  data(): HandleErrorsState {
    return { isOnLine: navigator.onLine, httpErrors: {} };
  },
  mounted() {
    this.httpErrors = {};
    window.addEventListener("online", () => {
      this.isOnLine = true;
    });
    window.addEventListener("offline", () => {
      this.isOnLine = false;
    });
  },
  methods: {
    handleErrors(err: CustomAxiosError, title?: string) {
      console.warn({ err, resp: err.response, title });

      if (!title) {
        title = "Ошибка загрузки данных";
      }

      const data: RestError =
        (err?.response?.data as unknown as RestError) || {};
      let respText;

      if (
        !err.response &&
        (!err.code ||
          err.code === "ERR_NETWORK" ||
          err.code == "ERR_INTERNET_DISCONNECTED")
      ) {
        respText = "Ошибка подключения к серверу";
      } else {
        respText = [err.response?.status, err.response?.statusText].join(" ");
      }

      let errValidation = "";

      if (typeof data === "object") {
        console.debug("Err data: ", data);
        for (const [key, val] of Object.entries(data)) {
          // console.debug(key, val);
          if (Array.isArray(val)) {
            const errJoin = val.join(", ");
            errValidation += `${key}: ${errJoin}<br/>`;
          }
        }
      }

      const caption: string =
        data?.detail ||
        data?.code ||
        errValidation ||
        respText ||
        // data ||
        "Неизвестная ошибка";

      this.$q.notify({
        type: "negative",
        message: title,
        caption: caption,
        progress: true,
        html: true,
      });
    },
  },
});

export default HandleErrorsMixin;
