<template>
  <q-markup-table flat>
    <tbody class="table-rating">
      <tr
        v-for="user of usersCanRate"
        :key="user.id"
      >
        <td class="cell-icon">
          <q-icon
            :name="user.profile.icon || 'person'"
            size="md"
          />
        </td>

        <td class="cell-name">
          {{ user?.first_name ? user.first_name + " " + user?.last_name : user.username }}
        </td>

        <td class="cell-rating">
          <q-rating
            :model-value="userRating(user) + 1"
            :readonly="!edit"
            :icon="['thumb_down', 'star']"
            :color-selected="['grey', 'green-5']"
            :max="6"
            size="2em"
            :color="$q.dark.isActive ? 'grey-4' : 'primary'"
            @update:model-value="userSetRating(user, $event - 1)"
          />
          <q-tooltip> Текущая оценка: {{ userRating(user) || "-" }} </q-tooltip>
        </td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<script setup lang="ts">
import { useAuthStore } from "src/stores/auth"
import { computed, onMounted, PropType, ref } from "vue"
import { RecipeRead, User } from "src/client"

const defaultRating = {}

const props = defineProps({
  modelValue: { required: true, type: Object as PropType<RecipeRead> },
  edit: { required: true, type: Boolean },
})

const $emit = defineEmits(["update:model-value"])
const storeAuth = useAuthStore()

const loading = ref(false)

const users = computed(() => {
  return storeAuth.users
})

const usersCanRate = computed(() => {
  if (!users.value) {
    return users.value
  }
  return users.value.filter((u) => {
    return u?.profile?.show_rate
  })
})

function loadUsers() {
  const payload = {
    page_size: 1000,
    can_rate: true,
  }
  storeAuth.loadUsers(payload).finally(() => {
    loading.value = false
  })
}
function userRating(user: User): number {
  const exists = props.modelValue?.ratings?.filter((r) => {
    return typeof r.user == "number" ? r.user == user.id : r.user.id == user.id
  })
  // console.debug('userRating: ', user, exists);

  if (exists && exists.length > 0) {
    const rating = exists[0]?.rating
    return rating !== null && rating !== undefined ? rating : -2
  } else {
    return -1
  }
}
function userSetRating(user: User, rating: number | null) {
  if (!props.modelValue || !props.modelValue?.ratings) {
    return
  }
  if (rating == -1) {
    rating = null
  }

  const exists =
    props.modelValue?.ratings.filter((r) => {
      return r.user.id == user.id
    }) || false
  // console.debug('setUserRating: ', user, rating, exists);

  if (exists && exists.length > 0 && props.modelValue.ratings) {
    const mvalue = Object.assign({}, props.modelValue)
    mvalue.ratings = props.modelValue.ratings.map((r) => {
      if (r.user.id == user.id) {
        r.rating = rating
      }
      return r
    })
    $emit("update:model-value", mvalue)
  } else {
    const mvalue = Object.assign({}, props.modelValue)
    // @ts-expect-error: Rating will be created
    mvalue.ratings.push(
      // @ts-expect-error: Rating will be created
      Object.assign({}, defaultRating, {
        recipe: props.modelValue.id,
        user: user,
        rating: rating,
      })
    )
    $emit("update:model-value", mvalue)
  }
}

onMounted(() => {
  if (!users.value) {
    loadUsers()
  }
})
</script>
