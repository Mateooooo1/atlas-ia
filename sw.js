/* Atlas IA · service worker
   ---------------------------------------------------------------------------
   La app ya funciona sin conexion por diseno (todo vive en el HTML), asi que
   este fichero solo tiene un trabajo: que el HTML de 2 MB este disponible sin
   red y que las actualizaciones no te dejen a medias.

   Estrategia, y el porque de cada una:

   · El HTML: primero la red, con la cache como respaldo. Al reves -cache
     primero- es lo habitual, pero aqui significaria que al publicar una version
     nueva la gente seguiria con la vieja hasta vaciar el navegador. Con este
     orden, si hay cobertura te llevas lo ultimo; si no, tiras de lo guardado.

   · Supabase: SOLO red, nunca cache. Guardar respuestas de la API seria
     ensenarte datos viejos como si fueran de ahora, y en una app que sincroniza
     entre moviles eso es peor que un error.

   · El modelo de lenguaje (esm.run / huggingface): fuera. Son cientos de megas
     y WebLLM ya tiene su propia cache.
*/

/* ⚠ SUBE ESTE NUMERO EN CADA DESPLIEGUE QUE TOQUE index.html, el manifiesto o
   los iconos. No es decorativo: `activate` borra las caches cuyo nombre no sea
   este, asi que mientras no cambie el movil sigue sirviendo la copia vieja y da
   igual lo que haya en el servidor.
   Se quedo en 'atlas-v1' durante ocho despliegues y el sintoma fue justo ese:
   iconos y textos antiguos en un movil ya instalado. */
const VERSION = 'atlas-v2-20260803';
/* Lo que espera a la red TENIENDO copia guardada. Corto a proposito: pasado esto
   abrir la app importa mas que abrir la ultima version. */
const RED_MS  = 2500;
const NUCLEO  = [
  './',
  './index.html',
  './manifest.webmanifest',
  './iconos/icono-192.png',
  './iconos/icono-512.png',
];

self.addEventListener('install', e=>{
  e.waitUntil(
    caches.open(VERSION)
      .then(c=>c.addAll(NUCLEO))
      /* skipWaiting NO va aqui a proposito: si el service worker nuevo toma el
         control mientras estas registrando una serie, la pagina se recarga y
         pierdes lo que estabas escribiendo. Espera a que la app lo pida. */
      .catch(err=>console.warn('[sw] no pude precachear:', err))
  );
});

self.addEventListener('activate', e=>{
  e.waitUntil((async()=>{
    const viejas = (await caches.keys()).filter(k=>k!==VERSION);
    await Promise.all(viejas.map(k=>caches.delete(k)));
    await self.clients.claim();
  })());
});

/* La app manda este mensaje cuando el usuario acepta actualizar. */
self.addEventListener('message', e=>{
  if(e.data === 'ACTUALIZA_YA') self.skipWaiting();
});

self.addEventListener('fetch', e=>{
  const req = e.request;
  if(req.method !== 'GET') return;

  const url = new URL(req.url);
  const fuera = url.origin !== self.location.origin;
  const esApi = /supabase\.co/.test(url.hostname);
  const esModelo = /esm\.run|jsdelivr|huggingface|raw\.githack/.test(url.hostname);
  if(esApi || esModelo || (fuera && !NUCLEO.includes(url.pathname))) return;   // red directa

  e.respondWith((async()=>{
    const guardada = await caches.match(req);

    const desdeRed = (async()=>{
      const res = await fetch(req);
      /* Solo se guarda lo que salio bien: cachear un 404 o un 500 seria
         servirte el error para siempre. */
      if(res && res.status === 200 && res.type === 'basic'){
        const copia = res.clone();
        caches.open(VERSION).then(c=>c.put(req, copia)).catch(()=>{});
      }
      return res;
    })();
    desdeRed.catch(()=>{});          // el fallo se gestiona abajo, no aqui

    /* Sin copia guardada no hay alternativa: toca esperar a la red. */
    if(!guardada){
      try{ return await desdeRed; }
      catch(err){
        if(req.mode === 'navigate'){
          const inicio = await caches.match('./index.html');
          if(inicio) return inicio;
        }
        throw err;
      }
    }

    /* Teniendo copia, la red dispone de RED_MS y ni un milisegundo mas.
       Antes se esperaba a la red SIN limite, y "sin red" no es lo mismo que "red
       que no responde": con el wifi de portal cautivo —ese que te pide aceptar
       condiciones— fetch no falla, se queda colgado. El catch no llegaba nunca y
       la app NO ABRIA, teniendo una copia entera a un centimetro.
       La descarga sigue por detras y deja la cache al dia para la proxima: como
       mucho abres una version por detras, que es infinitamente mejor que no
       abrir. */
    const reloj = new Promise(res=>setTimeout(()=>res(null), RED_MS));
    const gana = await Promise.race([ desdeRed.catch(()=>null), reloj ]);
    return gana || guardada;
  })());
});
