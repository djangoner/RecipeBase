export let handleErrors = {
  mounted() {
    this.httpErrors = {};
  },
  methods: {
    handleErrors(err, title) {
      console.warn(err, err.response, title);

      if (!title) {
        title = "Ошибка загрузки данных";
      }

      this.loading = false;
      let data = err.response.data || {};
      let respText = [err.response.status, err.response.statusText].join(" ");
      let errValidation = "";

      if (typeof data === "object") {
        console.debug("Err data: ", data);
        for (const [key, val] of Object.entries(data)) {
          // console.debug(key, val);
          let errJoin = val.join(", ");
          errValidation += `${key}: ${errJoin}<br/>`;
        }
      }
      this.$q.notify({
        type: "negative",
        message: title,
        caption:
          data.detail ||
          data.code ||
          errValidation ||
          respText ||
          // data ||
          "Неизвестная ошибка",
        icon: "",
        progress: true,
        html: true,
      });
    },
  },
};

export default handleErrors;
