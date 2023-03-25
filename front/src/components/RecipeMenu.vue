<template>
  <q-menu context-menu>
    <q-list dense>
      <!-- Add to plan -->
      <q-item
        clickable
        @click="addToPlanPreload()"
      >
        <q-item-section side>
          <q-icon name="calendar_month" />
        </q-item-section>
        <q-item-section>Добавить в план</q-item-section>
        <q-item-section side>
          <q-icon name="keyboard_arrow_right" />
        </q-item-section>

        <q-menu
          anchor="top end"
          self="top start"
        >
          <q-list dense>
            <template v-for="(day, idx) of WeekDays">
              <q-item
                v-if="idx > 0"
                :key="idx"
                clickable
              >
                <q-item-section
                  :class="isDayFilled(Number(idx)) ? 'text-underline text-bold' : ''"
                >
                  {{ day }}
                </q-item-section>
                <q-item-section side>
                  <q-icon name="keyboard_arrow_right" />
                </q-item-section>

                <q-menu
                  auto-close
                  anchor="top end"
                  self="top start"
                >
                  <q-list dense>
                    <q-item
                      v-for="mtime of meal_time"
                      :key="mtime.id"
                      v-close-popup
                      clickable
                      @click="addToPlan(idx, mtime, recipe)"
                    >
                      <q-item-section
                        :class="
                          isMtimeFilled(idx, mtime) ? 'text-underline text-bold' : ''
                        "
                      >
                        {{ mtime.title }}
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-item>
            </template>
          </q-list>
        </q-menu>
      </q-item>

      <!-- Archive management -->
      <q-item
        clickable
        @click="actionArchive()"
      >
        <q-item-section side>
          <q-icon name="archive" />
        </q-item-section>
        <q-item-section>
          <template v-if="recipe.is_archived">
            Убрать из архива
          </template><template v-else>
            В архив
          </template>
        </q-item-section>
      </q-item>
    </q-list>
  </q-menu>
</template>

<script lang="ts">
import { getYearWeek, WeekDays, YearWeek } from 'src/modules/WeekUtils';
import { useBaseStore } from 'src/stores/base';
import { defineComponent, PropType } from 'vue';
import { MealTime, RecipeRead } from 'src/client';
import HandleErrorsMixin, { CustomAxiosError } from 'src/modules/HandleErrorsMixin';
import { RecipePlanWeekFromRead } from 'src/Convert';

export default defineComponent({
  mixins: [HandleErrorsMixin],
  props: {
    recipe: { required: true, type: Object as PropType<RecipeRead> },
  },
  emits: ['updateItem'],
  setup() {
    const store = useBaseStore();
    const [year, week] = getYearWeek();
    const week_p: YearWeek = {
      year: year,
      week: week,
    };
    return { store, WeekDays, week: week_p };
  },

  computed: {
    plan() {
      return this.store.week_plan;
    },
    meal_time() {
      return this.store.meal_time;
    },
  },
  methods: {
    emitUpdated() {
      this.$emit('updateItem');
    },
    actionArchive() {
      const recipe_title: string = this.recipe?.title || '';
      this.$q
        .dialog({
          title: 'Подтверждение',
          message: this.recipe.is_archived
            ? `Вы уверены что хотите убрать рецепт '${recipe_title}' из архива?`
            : `Вы уверены что хотите перевести рецепт '${recipe_title}' в архив?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          const patchRecipe = {
            is_archived: !this.recipe.is_archived,
          };
          this.store
            .patchRecipe(this.recipe.id, patchRecipe)
            .then(() => {
              this.emitUpdated();
            })
            .catch((err: CustomAxiosError) => {
              this.handleErrors(err, 'Ошибка сохранения рецепта');
            });
        });
    },
    addToPlan(day: number, mtime: MealTime, recipe: RecipeRead) {
      console.debug('Add to plan: ', day, mtime, recipe);
      this.$q
        .dialog({
          title: 'Подтверждение',
          message: `Добавить '${recipe?.title}' на '${mtime?.title}' в  ${this.WeekDays[day]}?`,
          cancel: true,
          persistent: true,
        })
        .onOk(async () => {
          // Load current plan
          await this.loadWeekPlan();
          // Update plan
          const plans =
            this.plan?.plans.filter((plan) => {
              return plan.day == day && plan.meal_time.id == mtime.id;
            }) || [];
          const plan = plans[0];
          if (plan) {
            plan.recipe = recipe;
          } else {
            // @ts-expect-error: Plan will be created
            this.plan.plans.push({
              day: day,
              meal_time: mtime,
              recipe: recipe,
            });
          }
          // Save plan
          this.saveWeekPlan()
            .then(() => {
              this.$q.notify({
                type: 'positive',
                message: `План успешно изменен`,
              });
            })
            .catch((err: CustomAxiosError) => {
              this.handleErrors(err, 'Ошибка изменения плана');
            });
        });
    },

    addToPlanPreload() {
      if (!this.meal_time) {
        this.loadMealTime();
      }
      if (!this.plan) {
        void this.loadWeekPlan();
      }
    },

    isDayFilled(day: number): boolean {
      const plans = this.plan?.plans;
      const plansFilled =
        plans?.filter((p) => p.meal_time.is_primary && p.day === day).length || 0;
      const plansTotal = plans?.filter((p) => p.day == day).length || 0;

      return plansFilled >= plansTotal && plansTotal > 0;
    },
    isMtimeFilled(day: number, mtime: MealTime): boolean {
      const plans = this.plan?.plans;
      const plansFilled =
        plans?.filter((p) => p.meal_time.id == mtime.id && p.day == day).length || 0;
      return plansFilled > 0;
    },

    //
    loadWeekPlan(): Promise<void> {
      return new Promise((resolve, reject) => {
        if (!this.week?.year || !this.week?.week) {
          reject();
          return;
        }
        const payload = {
          year: this.week.year,
          week: this.week.week,
        };
        this.store
          .loadWeekPlan(payload)
          .then(() => {
            resolve();
          })
          .catch((err: CustomAxiosError) => {
            reject(err);
            this.handleErrors(err, 'Ошибка загрузки плана');
          });
      });
    },
    loadMealTime() {
      const payload = {
        pageSize: 1000,
      };
      // this.loading = true;

      this.store
        .loadMealTime(payload)
        .then(() => {
          // this.loading = false;
        })
        .catch((err: CustomAxiosError) => {
          // this.loading = false;
          this.handleErrors(err, 'Ошибка загрузки времени приема пищи');
        });
    },
    saveWeekPlan(): Promise<void> {
      return new Promise((resolve, reject) => {
        const payload = RecipePlanWeekFromRead(this.plan);
        console.debug('Save plan: ', payload);

        this.store
          .saveWeekPlan(payload)
          .then(() => {
            resolve();
          })
          .catch((err: CustomAxiosError) => {
            reject();
            this.handleErrors(err, 'Ошибка загрузки плана');
          });
      });
    },
  },
});
</script>
