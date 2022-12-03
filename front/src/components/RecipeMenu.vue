<template>
  <q-menu context-menu>
    <q-list dense>
      <q-item clickable>
        <q-item-section side><q-icon name="calendar_month" /></q-item-section>
        <q-item-section>Добавить в план</q-item-section>
        <q-item-section side>
          <q-icon name="keyboard_arrow_right" />
        </q-item-section>

        <q-menu anchor="top end" self="top start">
          <q-list dense>
            <template v-for="(day, idx) of WeekDays" :key="idx">
              <q-item v-if="idx > 0" clickable>
                <q-item-section>{{ day }}</q-item-section>
                <q-item-section side>
                  <q-icon name="keyboard_arrow_right" />
                </q-item-section>

                <q-menu auto-close anchor="top end" self="top start">
                  <q-list dense>
                    <q-item
                      @click="addToPlan(idx, mtime, recipe)"
                      v-for="mtime of meal_time"
                      :key="mtime.id"
                      clickable
                      v-close-popup
                    >
                      <q-item-section>{{ mtime.title }}</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-item>
            </template>
          </q-list>
        </q-menu>
      </q-item>

      <q-item clickable @click="actionArchive()">
        <q-item-section side><q-icon name="archive" /></q-item-section>
        <q-item-section
          ><template v-if="recipe.is_archived">Убрать из архива</template
          ><template v-else>В архив</template></q-item-section
        >
      </q-item>
    </q-list>
  </q-menu>
</template>

<script>
import weekSelect, {
  getDateOfISOWeek,
  WeekDays,
  getWeekNumber,
  getYearWeek,
} from 'components/WeekSelect.vue';
import { useBaseStore } from 'src/stores/base';

export default {
  emits: ['updateItem'],
  props: {
    recipe: { required: true },
  },
  setup() {
    const store = useBaseStore();
    let [year, week] = getYearWeek();
    let week_p = {};
    week_p.year = year;
    week_p.week = week;
    return { store, WeekDays, week: week_p };
  },
  methods: {
    emitUpdated() {
      this.$emit('updateItem');
    },
    actionArchive() {
      this.$q
        .dialog({
          title: 'Подтверждение',
          message: this.recipe.is_archived
            ? `Вы уверены что хотите убрать рецепт '${this.recipe?.title}' из архива?`
            : `Вы уверены что хотите перевести рецепт '${this.recipe?.title}' в архив?`,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          let recipe = {
            id: this.recipe.id,
            is_archived: !this.recipe.is_archived,
          };
          this.store
            .saveRecipe(recipe)
            .then(() => {
              this.emitUpdated();
            })
            .catch((err) => {
              this.handleErrors(err, 'Ошибка сохранения рецепта');
            });
        });
    },
    addToPlan(day, mtime, recipe) {
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
          let plans = this.plan.plans.filter((plan) => {
            return plan.day == day && plan.meal_time.id == mtime.id;
          });

          let plan = plans[0];
          if (plan) {
            plan.recipe = recipe;
          } else {
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
            .catch((err) => {
              this.handleErrors(err, 'Ошибка изменения плана');
            });
        });
    },

    //
    loadWeekPlan() {
      return new Promise((resolve, reject) => {
        if (!this.week?.year || !this.week?.week) {
          reject();
          return;
        }
        let payload = {
          year: this.week.year,
          week: this.week.week,
        };
        this.store
          .loadWeekPlan(payload)
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject(err);
            this.handleErrors(err, 'Ошибка загрузки плана');
          });
      });
    },
    saveWeekPlan() {
      return new Promise((resolve, reject) => {
        // let payload = Object.assign({}, this.plan);
        let payload = JSON.parse(JSON.stringify(this.plan));

        payload.plans.map((p) => {
          if (typeof p.recipe == 'object') {
            p.recipe = p.recipe?.id;
          }
          if (typeof p.meal_time == 'object') {
            p.meal_time = p.meal_time.id;
          }
        });

        payload.plans = payload.plans.filter((p) => {
          return p.recipe && p.meal_time;
        });

        console.debug('Save plan: ', payload);

        this.store
          .saveWeekPlan(payload)
          .then(() => {
            resolve();
          })
          .catch((err) => {
            reject();
            this.handleErrors(err, 'Ошибка загрузки плана');
          });
      });
    },
  },

  computed: {
    plan() {
      return this.store.week_plan;
    },
    meal_time() {
      return this.store.meal_time?.results;
    },
  },
};
</script>
