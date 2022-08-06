<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title> База рецептов </q-toolbar-title>

        <!-- <div>Quasar v{{ $q.version }}</div> -->
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      :width="220"
      :breakpoint="1200"
      show-if-above
      bordered
    >
      <q-list>
        <!-- <q-item-label header>База рецептов</q-item-label> -->

        <q-item class="cursor-pointer">
          <q-item-section avatar>
            <q-icon name="account_circle" size="lg"></q-icon>
          </q-item-section>
          <q-item-section>
            {{ userReadable }}
          </q-item-section>

          <q-menu fit auto-close>
            <q-list dense>
              <q-item class="justify-center text-negative" clickable @click="askLogout">
                Выйти
              </q-item>
            </q-list>
          </q-menu>
        </q-item>

        <q-separator class="q-mb-md" />

        <q-item v-if="!isOnLine" class="bg-orange text-white">
          <q-item-section avatar><q-icon name="wifi_off"></q-icon></q-item-section>
          <q-item-section>Нет подключения к интернету</q-item-section>
        </q-item>

        <q-item :to="{ name: 'index' }"
          ><q-item-section avatar><q-icon name="home"></q-icon></q-item-section>
          <q-item-section>Главная</q-item-section>
        </q-item>
        <q-item :to="{ name: 'recipes' }"
          ><q-item-section avatar><q-icon name="article"></q-icon></q-item-section>
          <q-item-section>Рецепты</q-item-section>
        </q-item>
        <q-item :to="{ name: 'week_plan' }"
          ><q-item-section avatar><q-icon name="calendar_month"></q-icon></q-item-section>
          <q-item-section>План</q-item-section>
        </q-item>
        <q-item :to="{ name: 'product_list' }"
          ><q-item-section avatar
            ><q-icon name="shopping_basket"></q-icon
          ></q-item-section>
          <q-item-section>Список продуктов</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <q-item v-if="!isOnLine" class="bg-orange text-white">
        <q-item-section avatar><q-icon name="wifi_off"></q-icon></q-item-section>
        <q-item-section>Нет подключения к интернету</q-item-section>
      </q-item>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { useAuthStore } from 'src/stores/auth';
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'MainLayout',

  components: {},

  setup() {
    const leftDrawerOpen = ref(false);
    const store = useAuthStore();

    return {
      store,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
    };
  },

  methods: {
    askLogout() {
      this.$q
        .dialog({
          title: 'Подтверждение',
          message: 'Вы уверены что хотите выйти из аккаунта?',
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.logout();
        });
    },
    logout() {
      this.store.logout();
      this.$router.push({ name: 'login' }).catch(() => {});
    },
  },

  computed: {
    user() {
      return this.store.account;
    },
    userReadable() {
      if (!this.user) {
        return;
      }
      return this.user.first_name
        ? this.user.first_name + ' ' + this.user.last_name
        : '@' + this.user.username;
    },
  },
});
</script>
