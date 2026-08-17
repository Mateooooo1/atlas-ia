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

/* NO SE TOCA A MANO. Lo pone `sellar_sw.py` a partir del hash de index.html,
   el manifiesto y los iconos: si cambia cualquiera, cambia la version y activate
   tira la cache vieja.
   Antes habia aqui un aviso en mayusculas pidiendo subirlo en cada despliegue.
   Se ignoro seis veces seguidas -por quien lo escribio- y el sintoma siempre fue
   el mismo: el movil mostrando la version anterior. Un recordatorio que falla
   seis veces no es un recordatorio, es un paso que tiene que hacer la maquina. */
const VERSION = 'atlas-7b901540a679';
/* Lo que espera a la red TENIENDO copia guardada. Corto a proposito: pasado esto
   abrir la app importa mas que abrir la ultima version. */
/* 2500 ms era demasiado poco. El index.html son 1,3 MB comprimidos: en datos
   moviles a 500 KB/s tarda ~2,6 s, o sea que el limite se agotaba SIEMPRE y el
   telefono servia la copia vieja aunque tuviera cobertura de sobra. Sintoma
   exacto que aparecio: "en el movil sigue igual" tras varios despliegues.
   8 s no penaliza al que esta sin red -ahi fetch falla solo, no espera- y le da
   margen al que tiene una conexion normal para llevarse lo ultimo. */
const RED_MS  = 8000;
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
