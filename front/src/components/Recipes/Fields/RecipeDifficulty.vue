<template>
  <div class="q-mx-md">
    <q-slider
      v-model="modelValue"
      :min="1"
      :max="5"
      snap
      marker-labels
      switch-marker-labels-side
    >
      <template #marker-label-group="scope">
        <div
          v-for="marker in scope.markerList"
          :key="marker.index"
          class="cursor-pointer"
          :class="[ marker.classes ]"
          :style="marker.style"
          @click="modelValue = marker.value"
        >
          {{ marker.value }}

          <q-tooltip>
            <q-icon
              v-for="i in marker.value"
              :key="i"
              size="xs"
              color="white"
              name="star_rate"
            />
            <div
              v-for="user in difficultyUsersEqual(marker.value)"
              :key="user.id"
            >
              - {{ userReadable(user) }}
            </div>
            <q-separator
              v-if="difficultyUsersEqual(marker.value)?.length"
              color="white"
              class="q-my-xs"
            />
            <div
              v-for="user in difficultyUsersGreater(marker.value)"
              :key="user.id"
            >
              - {{ userReadable(user) }}
            </div>
          </q-tooltip>
        </div>
      </template>
    </q-slider>
  </div>
</template>


<script setup lang="ts">
import { userReadable } from 'src/modules/Utils';
import { useAuthStore } from 'src/stores/auth';
import { computed } from 'vue';


const props = defineProps({
  modelValue: {
    type: Number,
    required: true,
  }
})

const $emit = defineEmits(["update:model-value"])

const store = useAuthStore()

const modelValue = computed({
  get(){
    return props.modelValue
  },
  set(value){
    $emit("update:model-value", value)
  }
})

function difficultyUsersGreater(level: number){
  return store.users?.filter(u => (u.profile.cook_difficulty || 0) > level)
}
function difficultyUsersEqual(level: number){
  return store.users?.filter(u => (u.profile.cook_difficulty || 0) == level)
}

</script>