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
      <q-list class="text-grey-9">
        <!-- <q-item-label header>База рецептов</q-item-label> -->

        <q-item class="cursor-pointer">
          <q-item-section avatar>
            <q-icon name="account_circle" size="lg"></q-icon>
          </q-item-section>
          <q-item-section>
            {{ userReadable }}
          </q-item-section>

          <q-menu anchor="bottom middle" self="top middle" auto-close>
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

        <q-item :to="{ name: 'index' }" exact
          ><q-item-section avatar><q-icon name="home"></q-icon></q-item-section>
          <q-item-section>Главная</q-item-section>
        </q-item>
        <q-item :to="{ name: 'recipes' }" v-if="store.hasPerm('recipes.view_recipe')"
          ><q-item-section avatar><q-icon name="article"></q-icon></q-item-section>
          <q-item-section>Рецепты</q-item-section>
        </q-item>
        <q-item
          :to="{ name: 'week_plan' }"
          v-if="store.hasPerm('recipes.view_recipeplanweek')"
          ><q-item-section avatar><q-icon name="calendar_month"></q-icon></q-item-section>
          <q-item-section>План</q-item-section>
        </q-item>
        <q-item
          :to="{ name: 'product_list' }"
          v-if="store.hasPerm('recipes.view_productlistweek')"
          ><q-item-section avatar><q-icon name="shopping_cart"></q-icon></q-item-section>
          <q-item-section>Список продуктов</q-item-section>
        </q-item>
        <q-item
          :to="{ name: 'ingredients' }"
          v-if="store.hasPerm('recipes.view_ingredient')"
          ><q-item-section avatar
            ><q-icon name="shopping_basket"></q-icon
          ></q-item-section>
          <q-item-section>Ингредиенты</q-item-section>
        </q-item>
        <q-item :to="{ name: 'tasks' }" v-if="store.hasPerm('tasks.view_task')"
          ><q-item-section avatar><q-icon name="list"></q-icon></q-item-section>
          <q-item-section>Задачи</q-item-section>
        </q-item>

        <q-separator />

        <q-item clickable @click="toggleDark">
          <q-item-section avatar>
            <q-icon :name="darkIcon()"></q-icon>
          </q-item-section>
          <q-item-section> Тёмная тема </q-item-section>
        </q-item>
        <q-item clickable dense href="/admin" v-if="user?.is_staff">
          <q-item-section avatar>
            <q-icon name="settings"></q-icon>
          </q-item-section>
          <q-item-section> Администрирование </q-item-section>
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

<script lang="ts">
import { useQuasar } from 'quasar';
import { User } from 'src/client';
import { useAuthStore } from 'src/stores/auth';
import { defineComponent, ref } from 'vue';
import IsOnlineMixin from 'src/modules/IsOnlineMixin';

type DarkMode = boolean | 'auto';
const darkModes: Array<DarkMode> = ['auto', true, false];

export default defineComponent({
  name: 'MainLayout',

  components: {},
  mixins: [IsOnlineMixin],
  setup() {
    const leftDrawerOpen = ref(false);
    const store = useAuthStore();
    const $q = useQuasar();

    const preferredMode: DarkMode | null = $q.localStorage.getItem('preferredMode');

    if (preferredMode !== null) {
      $q.dark.set(preferredMode);
    }

    return {
      store,
      leftDrawerOpen,
      darkModes,

      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
      toggleDark() {
        let mode = $q.dark.mode;
        let idxCurr = darkModes.indexOf(mode);
        let idxNew = idxCurr + 1;
        if (idxNew >= darkModes.length) {
          idxNew = 0;
        }
        let newMode: DarkMode = darkModes[idxNew];
        // set
        $q.dark.set(newMode);
        $q.localStorage.set('preferredMode', newMode);
      },
      darkIcon() {
        let mode = $q.dark.mode;
        switch (mode) {
          case false:
            return 'light_mode';
          case true:
            return 'dark_mode';
          case 'auto':
            return 'brightness_auto';
          default:
            return 'dark_mode';
        }
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
      void this.store.logout();
      void this.$router.push({ name: 'login' });
    },
  },

  computed: {
    user(): User | null {
      return this.store.account;
    },
    userReadable(): string | undefined {
      if (!this.user) {
        return;
      }
      return this.user.first_name
        ? [this.user.first_name, this.user.last_name].join(' ').trim()
        : '@' + this.user.username;
    },
  },
});
</script>
