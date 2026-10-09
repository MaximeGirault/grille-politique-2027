// Mode hors connexion : réseau d'abord, dernière version enregistrée sinon.
const CACHE = "grille-2027";
const FICHIERS = ["./", "index.html", "style.css", "app.js", "manifest.webmanifest", "icone-180.png", "icone-192.png", "icone-512.png"];

self.addEventListener("install", (ev) => {
  ev.waitUntil(caches.open(CACHE).then((c) => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (ev) => ev.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (ev) => {
  if (ev.request.method !== "GET" || new URL(ev.request.url).origin !== location.origin) return;
  ev.respondWith(
    fetch(ev.request)
      .then((reponse) => {
        const copie = reponse.clone();
        caches.open(CACHE).then((c) => c.put(ev.request, copie));
        return reponse;
      })
      .catch(() => caches.match(ev.request, { ignoreSearch: true }).then((r) => r || caches.match("index.html")))
  );
});
