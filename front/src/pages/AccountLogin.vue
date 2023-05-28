<template>
  <div class="window-width window-height row justify-center items-center">
    <q-card
      class="login-card col-xs-12 col-sm-6 col-md-4 q-pa-md"
      flat
      bordered
    >
      <q-card-section>
        <h4 class="text-center no-margin">
          Авторизация
        </h4>
      </q-card-section>
      <q-card-section>
        <q-form
          id="loginForm"
          class="q-gutter-sm"
          @submit="onSubmit"
        >
          <q-input
            v-model="login.username"
            outlined
            label="Имя пользователя"
            :rules="[(val) => (val !== null && val !== '') || 'Введите имя пользователя']"
          />
          <q-input
            v-model="login.password"
            :type="login.passwordShow ? 'text' : 'password'"
            outlined
            label="Пароль"
            lazy-rules
            :rules="[(val) => (val !== null && val !== '') || 'Введите пароль']"
          />
        </q-form>
      </q-card-section>

      <q-card-actions
        class="q-px-md"
        align="around"
      >
        <q-btn
          type="submit"
          color="primary"
          unelevated
          no-caps
          :loading="loading"
          label="Войти"
          size="md"
          form="loginForm"
          class="col"
        />
      </q-card-actions>
    </q-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useAuthStore } from 'src/stores/auth.js';
import { AuthToken } from 'src/client';

export default defineComponent({
  data() {
    const store = useAuthStore();
    return {
      store: store,
      loading: false,
      login: {
        username: '',
        password: '',
        passwordShow: false,
      },
    };
  },
  computed: {
    loginStatus(): boolean {
      return this.store.isAuthenticated;
    },
  },
  methods: {
    onSubmit() {
      const payload = {
        username: this.login.username,
        password: this.login.password,
      } as AuthToken;

      this.loading = true;

      this.store
        .login(payload)
        .then(() => {
          this.loading = false;
          void this.$router.push({ name: 'index' });
        })
        .catch((err) => {
          this.loading = false;
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
});
</script>

<style lang="scss" scoped>
.login-card {
  max-width: 350px;
}
</style>
