/* eslint-disable @typescript-eslint/unbound-method */
import { defineComponent } from "vue";

export const IsOnlineMixin = defineComponent({
  data() {
    return { isOnLine: navigator.onLine, httpErrors: {} };
  },
  created() {
    this.httpErrors = {};
    window.addEventListener("online", this._handleNowOnline);
    window.addEventListener("offline", this._handleNowOffline);
  },
  methods: {
    _handleNowOnline() {
      this.isOnLine = true;
    },
    _handleNowOffline() {
      this.isOnLine = false;
    },
  },
  beforeUnmount() {
    window.removeEventListener("online", this._handleNowOnline);
    window.removeEventListener("offline", this._handleNowOffline);
  },
});

export default IsOnlineMixin;
