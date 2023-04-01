import { Notify } from 'quasar'
import { register } from 'register-service-worker'

// The ready(), registered(), cached(), updatefound() and updated()
// events passes a ServiceWorkerRegistration instance in their arguments.
// ServiceWorkerRegistration: https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration

register(process.env.SERVICE_WORKER_FILE, {
  // The registrationOptions object will be passed as the second argument
  // to ServiceWorkerContainer.register()
  // https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/register#Parameter

  // registrationOptions: { scope: './' },

  ready(/* registration */) {
    // console.log('Service worker is active.')
  },

  registered(/* registration */) {
    // console.log('Service worker has been registered.')
  },

  cached(/* registration */) {
    // console.log('Content has been cached for offline use.')
  },

  updatefound(/* registration */) {
    Notify.create({
      type: "info",
      group: 'sw-state',
      caption: "Обнаружена новая версия приложения, выполняется обновление...",
    })
    // console.log('New content is downloading.')
  },

  updated(/* registration */) {
    Notify.create({
      type: "info",
      caption: "Обновление установлено, обновите страницу чтобы увидеть изменения",
      group: 'sw-state',
      actions: [
        { label: 'Обновить', color: 'yellow', handler: () => { location.reload() } },
        { label: 'Закрыть', color: 'white', handler: () => { /* ... */ } },
      ]
    })
    // console.log('New content is available; please refresh.')
  },

  offline() {
    // console.log('No internet connection found. App is running in offline mode.')
  },

  error(err) {
    Notify.create({
      type: "error",
      caption: "Ошибка ServiceWorker",
      description: err.message
    })
    // console.error('Error during service worker registration:', err)
  }
})
