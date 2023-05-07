import { installQuasarPlugin } from "@quasar/quasar-app-extension-testing-unit-vitest"
import { it, test, expect, describe, beforeEach, vi } from "vitest"
import WeekSelect from "./WeekSelect.vue"
import { mount } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"

installQuasarPlugin()

const defaultParams = {
  props: {
    modelValue: {},
  },
}
const getInstance = (params?: object) => {
  return mount(WeekSelect, Object.assign({}, defaultParams, params))
}
const date = new Date(2000, 0, 1)

describe("WeekSelect", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.setSystemTime(date)
  })

  test("default week_pick", async () => {
    const wrapper = getInstance()
    expect(wrapper.exists()).toBeTruthy()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.week_pick).toStrictEqual({ year: 2000, week: 1 })
  })

  test("date picker", async () => {
    const wrapper = getInstance()
    expect(wrapper.exists()).toBeTruthy()
    wrapper.vm.date_picker = "2000/01/10"
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted("update:model-value")).toBeDefined()
    expect(wrapper.emitted("update:model-value")[0][0]).toEqual({ year: 2000, week: 2 })
    expect(wrapper.vm.week_pick).toEqual({ year: 2000, week: 2 })
    expect(wrapper.vm.date_picker).toStrictEqual({ from: "2000/01/10", to: "2000/01/16" })
  })

  test("changed date from parent", async () => {
    const wrapper = getInstance()
    expect(wrapper.vm.week_pick).toEqual({ year: 2000, week: 1 })

    wrapper.setProps({ modelValue: { year: 2000, week: 10 } })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.week_pick).toEqual({ year: 2000, week: 10 })
  })
})
