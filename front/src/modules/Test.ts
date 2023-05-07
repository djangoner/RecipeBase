export const fakeResponse = (data: object, status?: number) => {
  return {
    status: status || 200,
    data: data,
  }
}
