<template>
  <div class="window-width window-height row justify-center items-center">
    <q-card class="login-card col-xs-12 col-sm-6 col-md-4 q-pa-md">
      <q-card-section>
        <h4 class="text-center no-margin">Авторизация</h4>
      </q-card-section>
      <q-card-section>
        <q-form id="loginForm" class="q-gutter-md" @submit="onSubmit">
          <q-input
            outlined
            v-model="login.username"
            label="Имя пользователя"
            :rules="[(val) => (val !== null && val !== '') || 'Введите имя пользователя']"
          ></q-input>
          <q-input
            :type="login.passwordShow ? 'text' : 'password'"
            outlined
            v-model="login.password"
            label="Пароль"
            lazy-rules
            :rules="[(val) => (val !== null && val !== '') || 'Введите пароль']"
          ></q-input>
        </q-form>
      </q-card-section>

      <q-card-actions align="around">
        <q-btn
          type="submit"
          color="primary"
          :loading="loginStatus == 'request'"
          label="Войти"
          size="md"
          form="loginForm"
          class="q-px-lg"
        />
      </q-card-actions>
    </q-card>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import { useAuthStore } from 'stores/auth.js';

export default defineComponent({
  data() {
    const store = useAuthStore();
    return {
      store: store,
      login: {
        username: '',
        password: '',
        passwordShow: false,
      },
    };
  },
  methods: {
    onSubmit() {
      let payload = {
        username: this.login.username,
        password: this.login.password,
      };

      this.store
        .login(payload)
        .then(() => {
          this.$router.push({ name: 'index' });
        })
        .catch((err) => {
          console.warn(err);

          this.$q.notify({
            type: 'negative',
            message: 'Неверное имя пользователя или пароль',
            icon: '',
            progress: true,
          });
        });
    },
  },
  computed: {
    loginStatus() {
      return this.store.isAuthenticated;
    },
  },
});
</script>

<style lang="scss" scoped>
.login-card {
  max-width: 350px;
}
</style>
