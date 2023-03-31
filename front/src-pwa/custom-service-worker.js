/* eslint-env serviceworker */

/*
 * This file (which will be your service worker)
 * is picked up by the build system ONLY if
 * quasar.config.js > pwa > workboxMode is set to "injectManifest"
 */

import { runBackgroundSyncProductList } from "src/modules/WorkerSync";
import { clientsClaim } from "workbox-core";
import {
  precacheAndRoute,
  cleanupOutdatedCaches,
  createHandlerBoundToURL,
} from "workbox-precaching";
import { registerRoute, NavigationRoute } from "workbox-routing";

self.skipWaiting();
clientsClaim();

// Use with precache injection
precacheAndRoute(self.__WB_MANIFEST);

if (process.env.DEV) {
  precacheAndRoute([{ url: "/" }]);
}

cleanupOutdatedCaches();

// Non-SSR fallback to index.html
// Production SSR fallback to offline.html (except for dev)
if (process.env.MODE !== "ssr" || process.env.PROD) {
  registerRoute(
    new NavigationRoute(
      createHandlerBoundToURL(process.env.DEV ? '/' : process.env.PWA_FALLBACK_HTML),
      {
        denylist: [/sw\.js$/, /workbox-(.)*\.js$/, /admin(.)*$/, /api(.)*$/],
      }
    )
  );
}

function postMessageAll(msg) {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => client.postMessage(msg));
  })
}

self.addEventListener('sync', event => {
  console.debug("[Worker] Sync signal raw: ", event)
  let option = event.tag.replace(/(.*?)\:.*?$/, "$1");
  let token = event.tag.replace(/.*?\:(.*?)$/, "$1");
  console.debug("[Worker] Sync signal: ", option, "| Token:", token)

  if (option === 'product-list-sync') {
    const productListSync = async () => {
      postMessageAll({
        type: "product-list-sync-start",
        status: "success"
      })

      console.debug("[Worker] sync start")
      let res = await runBackgroundSyncProductList(token)
      console.debug("[Worker] sync finish")
      if (res) {
        postMessageAll({
          type: "product-list-sync",
          status: "success"
        });
        console.debug("[Worker] message sended")
      }
    }
    event.waitUntil(productListSync());
  }
});
