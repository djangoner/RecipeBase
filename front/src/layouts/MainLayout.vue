<template>
  <q-layout view="lHh Lpr lFf">
    <q-header
      class="print-hide"
      elevated
    >
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />
        <q-toolbar-title> База рецептов </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      :width="220"
      :breakpoint="1200"
      class="print-hide"
      show-if-above
      bordered
    >
      <q-list class="text-grey-9">
        <!-- <q-item-label header>База рецептов</q-item-label> -->

        <q-item class="cursor-pointer">
          <q-item-section avatar>
            <q-icon
              name="account_circle"
              size="lg"
            />
          </q-item-section>
          <q-item-section>
            {{ userReadable }}
          </q-item-section>

          <q-menu
            anchor="bottom middle"
            self="top middle"
            auto-close
          >
            <q-list dense>
              <q-item
                class="justify-center text-negative"
                clickable
                @click="askLogout"
              >
                Выйти
              </q-item>
            </q-list>
          </q-menu>
        </q-item>
        <q-item
          class="text-center text-white q-py-xs"
          :class="[websocketStateBg]"
          style="min-height: auto"
        >
          <q-item-section class="q-py-none">
            {{ websocketStateStr }}
            <q-tooltip>
              Обновление данных в режиме RealTime
            </q-tooltip>
          </q-item-section>
        </q-item>

        <q-separator class="q-mb-md" />

        <q-item
          v-if="!isOnLine"
          class="bg-orange text-white"
        >
          <q-item-section avatar>
            <q-icon name="wifi_off" />
          </q-item-section>
          <q-item-section>Нет подключения к интернету</q-item-section>
        </q-item>

        <q-item
          :to="{ name: 'index' }"
          exact
        >
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>Главная</q-item-section>
        </q-item>
        <q-item
          v-if="storeAuth.hasPerm('recipes.view_recipe')"
          :to="{ name: 'recipes' }"
        >
          <q-item-section avatar>
            <q-icon name="article" />
          </q-item-section>
          <q-item-section>Рецепты</q-item-section>
        </q-item>
        <q-item
          v-if="storeAuth.hasPerm('recipes.view_recipeplanweek')"
          :to="{ name: 'week_plan' }"
        >
          <q-item-section avatar>
            <q-icon name="calendar_month" />
          </q-item-section>
          <q-item-section>План</q-item-section>
        </q-item>
        <q-item
          v-if="storeAuth.hasPerm('recipes.view_productlistweek')"
          :to="{ name: 'product_list' }"
        >
          <q-item-section avatar>
            <q-icon name="shopping_cart" />
          </q-item-section>
          <q-item-section>Список продуктов</q-item-section>
        </q-item>
        <q-item
          v-if="storeAuth.hasPerm('recipes.view_ingredient')"
          :to="{ name: 'ingredients' }"
        >
          <q-item-section avatar>
            <q-icon name="shopping_basket" />
          </q-item-section>
          <q-item-section>Ингредиенты</q-item-section>
        </q-item>
        <q-item
          v-if="storeAuth.hasPerm('tasks.view_task')"
          :to="{ name: 'tasks' }"
        >
          <q-item-section avatar>
            <q-icon name="list" />
          </q-item-section>
          <q-item-section>Задачи</q-item-section>
        </q-item>

        <q-separator />

        <q-item
          clickable
          @click="toggleDark"
        >
          <q-item-section avatar>
            <q-icon :name="darkIcon()" />
          </q-item-section>
          <q-item-section> Тёмная тема </q-item-section>
        </q-item>
        <q-item
          v-if="user?.is_staff"
          clickable
          dense
          href="/admin"
        >
          <q-item-section avatar>
            <q-icon name="settings" />
          </q-item-section>
          <q-item-section> Администрирование </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <q-item
        v-if="!isOnLine"
        class="bg-orange text-white"
      >
        <q-item-section avatar>
          <q-icon name="wifi_off" />
        </q-item-section>
        <q-item-section>Нет подключения к интернету</q-item-section>
      </q-item>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { useQuasar } from "quasar"
import { User } from "src/client"
import { useAuthStore } from "src/stores/auth"
import { defineComponent, ref } from "vue"
import IsOnlineMixin from "src/modules/IsOnlineMixin"
import { useBaseStore } from "src/stores/base"
import {websocketState} from 'src/boot/websocketsRealtime'

type DarkMode = boolean | "auto"
const darkModes: Array<DarkMode> = ["auto", true, false]

export default defineComponent({
  name: "MainLayout",

  components: {},
  mixins: [IsOnlineMixin],
  setup() {
    const leftDrawerOpen = ref(false)
    const store = useBaseStore()
    const storeAuth = useAuthStore()
    const $q = useQuasar()

    const preferredMode: DarkMode | null = $q.localStorage.getItem("preferredMode")

    if (preferredMode !== null) {
      $q.dark.set(preferredMode)
    }

    return {
      store,
      storeAuth,
      leftDrawerOpen,
      darkModes,
      websocketState,

      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value
      },
      toggleDark() {
        const mode = $q.dark.mode
        const idxCurr = darkModes.indexOf(mode)
        let idxNew = idxCurr + 1
        if (idxNew >= darkModes.length) {
          idxNew = 0
        }
        const newMode: DarkMode = darkModes[idxNew]
        // set
        $q.dark.set(newMode)
        $q.localStorage.set("preferredMode", newMode)
      },
      darkIcon() {
        const mode = $q.dark.mode
        switch (mode) {
          case false:
            return "light_mode"
          case true:
            return "dark_mode"
          case "auto":
            return "brightness_auto"
          default:
            return "dark_mode"
        }
      },
    }
  },

  computed: {
    user(): User | null {
      return this.storeAuth.account
    },
    userReadable(): string | undefined {
      if (!this.user) {
        return
      }
      return this.user.first_name ? [this.user.first_name, this.user.last_name].join(" ").trim() : "@" + this.user.username
    },
    websocketStateBg(){
      switch (this.websocketState) {
        case true:
          return "bg-green"
        case false:
          return "bg-red"
        default:
          return "bg-orange"
      }
    },
    websocketStateStr(){
      switch (this.websocketState) {
        case true:
          return "Ок"
        case false:
          return "Нет подключения"
        default:
          return "Подключение..."
      }
    }
  },
  watch: {
    "store.printMode": {
      handler(val) {
        if (val) {
          sessionStorage.setItem("leftDrawerOpen", this.leftDrawerOpen ? "1" : "0")
          this.leftDrawerOpen = false
        } else {
          this.leftDrawerOpen = sessionStorage.getItem("leftDrawerOpen") !== "0"
        }
      },
    },
  },

  methods: {
    askLogout() {
      this.$q
        .dialog({
          title: "Подтверждение",
          message: "Вы уверены что хотите выйти из аккаунта?",
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          this.logout()
        })
    },
    logout() {
      void this.storeAuth.logout()
      void this.$router.push({ name: "login" })
    },
  },
})
</script>
