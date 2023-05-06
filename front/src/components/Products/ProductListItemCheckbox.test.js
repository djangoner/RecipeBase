import { installQuasar } from "@quasar/quasar-app-extension-testing-unit-vitest"
import { mount } from "@vue/test-utils"
import { QCheckbox } from "quasar"
import { describe, expect, it } from "vitest"
import { nextTick } from 'vue'
import ProductListItemCheckbox from "./ProductListItemCheckbox.vue"

installQuasar()

const item = {
  id: 0,
  is_completed: false,
  is_already_completed: false,
}


const mountComponent = () => {
  return mount(ProductListItemCheckbox, {
    props: {
      modelValue: item,
    },
  })
}

describe("ProductListItemCheckbox", () => {
  it("checkbox click", async () => {

    const wrapper = mountComponent()

    // Toggle to true
    await wrapper.findComponent(QCheckbox).trigger("click")
    await nextTick()

    expect(wrapper.emitted()['update:model-value']).toBeTruthy()
    expect(wrapper.emitted()['update:model-value'][0]).toStrictEqual([Object.assign(item, { is_completed: true })])
  })

  it("toggle disabled", async () => {
    const wrapper = mountComponent()

    await wrapper.setProps({ disable: true })
    await nextTick()

    expect(wrapper.findComponent(QCheckbox).classes().includes("disabled")).toBeTruthy()
  })
})
