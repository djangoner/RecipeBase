import ProductListItemMoveWeek from "./ProductListItemMoveWeek.vue"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { mount } from "@vue/test-utils"
import { QBtn, QSelect } from "quasar"
import { createPinia, setActivePinia } from "pinia"
import { nextTick } from "vue"
import { installQuasarPlugin } from "@quasar/quasar-app-extension-testing-unit-vitest"
import axios from "axios"
import { fakeResponse, transitionStub } from "src/modules/Test"

installQuasarPlugin()

const mockWeekList = {
  results: [
    {
      id: 1,
      year: 2000,
      week: 1,
    },
    {
      id: 2,
      year: 2000,
      week: 3,
    },
  ],
}

const mountComponent = () => {
  return mount(ProductListItemMoveWeek, {
    props: {
      modelValue: 0,
      week: {
        year: 2000,
        week: 2,
      },
      canEdit: true,
    },
    stubs: {
      transition: transitionStub(),
    },
  })
}

describe("ProductListItemMoveWeek", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("move to first week", async () => {
    const wrapper = mountComponent()

    await wrapper.getComponent(QBtn).trigger("click")

    await nextTick()
    // console.debug("Select: ", wrapper.getComponent(QSelect)) //.trigger("click")
    // vi.fn().mockImplementationOnce(axios.request, () => Promise.resolve({ data: mockWeekList }))
    await wrapper.getComponent(QSelect).trigger("click")
    wrapper.getComponent(QSelect).vm.toggleOption(mockWeekList.results[0])

    wrapper.vm.itemMoveWeek()
    await nextTick()

    expect(wrapper.emitted()["update:model-value"]).toBeTruthy()
    expect(wrapper.emitted()["update:model-value"][0][0]).toBe(1)
  })

  it("previous week btn", async () => {
    const wrapper = mountComponent()
    await wrapper.getComponent(QBtn).trigger("click")
    await nextTick()

    // console.debug(wrapper.findAllComponents(QBtn).map((c) => c.classes()))

    const btnPrev = wrapper.findAllComponents(QBtn)[0]

    expect(btnPrev.classes()).toContain("move-prev")

    vi.spyOn(axios, "request").mockResolvedValue(fakeResponse(mockWeekList.results[0]))

    const spy = vi.spyOn(wrapper.vm, "moveWeekDelta")
    await btnPrev.trigger("click")

    await nextTick()
    expect(spy).toHaveBeenCalledOnce()
    expect(spy).toHaveBeenCalledWith(-1)

    await wrapper.vm.moveWeekDelta(-1)
    await nextTick()

    wrapper.vm.itemMoveWeek()
    await nextTick()

    expect(wrapper.emitted()["update:model-value"][0][0]).toBe(1)
  })
  it("next week btn", async () => {
    const wrapper = mountComponent()
    await wrapper.getComponent(QBtn).trigger("click")
    await nextTick()

    const btnNext = wrapper.findAllComponents(QBtn)[1]
    expect(btnNext.classes()).toContain("move-next")

    vi.spyOn(axios, "request").mockResolvedValue(fakeResponse(mockWeekList.results[1]))
    const spy = vi.spyOn(wrapper.vm, "moveWeekDelta")
    await btnNext.trigger("click")

    await nextTick()
    expect(spy).toHaveBeenCalledOnce()
    expect(spy).toHaveBeenCalledWith(1)

    await wrapper.vm.moveWeekDelta(1)
    await nextTick()

    wrapper.vm.itemMoveWeek()
    await nextTick()

    expect(wrapper.emitted()["update:model-value"][0][0]).toBe(2)
  })
})
