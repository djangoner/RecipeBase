export const transitionStub = () => ({
  render: function (h) {
    return this.$options._renderChildren
  },
})

export const fakeResponse = (data: object, status?: number) => {
  return {
    status: status || 200,
    data: data,
  }
}
