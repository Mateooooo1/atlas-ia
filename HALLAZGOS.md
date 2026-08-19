# Lo que encontraron los agentes

## C · El contador de días · 18 ago 2026

Queja: *«Sigue sin funcionar bien el contador. De los días.»*

6 agentes con lentes distintas, obligados a reproducir con `node`. **Cinco de los
seis llegaron al mismo sitio sin coordinarse.** Reproducido otra vez a mano antes
de tocar nada.

### La causa · commit `f33615a`

**`today()` daba la fecha de Greenwich, no la suya.** Él entrena de tarde en
Colombia (UTC−5), donde el día UTC cambia **a las 19:00**. Una sesión de 18:40 a
19:10 repartía sus marcas entre dos fechas, ninguna completaba el día y el
contador **no subía nunca**. Al dar las 19:00, además, los chulitos ya puestos
desaparecían de la pantalla y no salía la tarjeta de cierre.

Probado en el navegador, en `America/Bogota`, a las 23:31 del 18:

| | fecha guardada |
| --- | --- |
| antes | `2026-08-19` ← mañana |
| ahora | `2026-08-18` |

Es la regresión que **introdujo el arreglo anterior**: con la regla vieja (bastaba
una marca) el reparto en dos fechas daba igual e incluso inflaba el número; con la
regla nueva (día entero) dejó de contar del todo.

### Lo segundo, que salió buscando lo primero

`diaCompletado` comparaba las marcas de **ayer** contra el plan de **hoy**, así que
editar el plan reescribía el pasado sin entrenar:

| | antes | ahora |
| --- | --- | --- |
| quitar un ejercicio | Día 0 → **Día 3** | Día 0 |
| añadir un ejercicio | Día 2 → **Día 0** | Día 2 |

Arreglado con un sello (`DB.fin`) que se pone al terminar el día y ya no se
discute. `sellaHistorial()` congela una vez lo ya entrenado para no perder el
historial, y corre también al importar una copia vieja. El sello va en un mapa
aparte y no dentro de `DB.done[fecha]` **a propósito**: hay tres sitios que cuentan
las claves de esa fecha y una clave de control les habría sumado un ejercicio.

### Lo que NO se arregló

Reproducido por los agentes, pero fuera de la queja y sin pasar por un escéptico
(los verificadores murieron por límite de sesión):

- Un perfil sin `profile.weeks` deja el total en `DAYS.length`: dice «Día 3 de 4»
  en vez de «de 132» y se congela al llegar.
- `swapExercise` deja huérfana la marca del ejercicio viejo: al cambiar de
  ejercicio el avance de hoy retrocede («hoy 4/8» → «hoy 3/8»).
- `migrarDone` reasigna una marca vieja al día equivocado si la rotación semanal
  ya había cambiado ese ejercicio.

### Aviso sobre la versión publicada

Corrección al informe anterior: **la 2.2 no está en revisión, está publicada**
desde el 17 ago 21:35 («Disponible para determinados testers»). Eso encaja con la
queja: en su teléfono corre la regla del día entero **con** el fallo de la fecha,
que es justo el combo que deja el contador clavado.

La **2.3 (`versionCode 14`)** ya está compilada y firmada con el arreglo dentro,
verificado en el propio `.aab`:

    atlas_android/android/app/build/outputs/bundle/release/app-release.aab

Queda subirla a mano: son 18,4 MB y el puente del navegador corta en 10 MB, así
que ese paso no se puede automatizar desde aquí. La PWA de GitHub Pages ya sirve
el arreglo sin esperar a Google.

---

# Lo de antes · 17 ago 2026

Dos baterías sobre `atlas_pwa/index.html` y `atlas_android/`: una de
funcionamiento y otra de seguridad. Cada hallazgo pasó por agentes independientes
cuyo trabajo era **tumbarlo**, no confirmarlo.

---

## A · Fallos de funcionamiento

3 rondas · 10 áreas · cada fallo reproducido por un segundo agente.
25 candidatos → **19 confirmados**. De la última ronda murieron 20 agentes por
límite de sesión, así que la lista está **incompleta por abajo**: hay áreas que
no llegaron a agotarse.

### Arreglados

**Commit `90652be`**

| Fallo | Dónde |
| --- | --- |
| Marcar descanso sumaba al contador «Día X de N» (28 en vez de 16) | `diasEntrenados` |
| Quitar un ejercicio descolocaba `DB.swapOrig` → alternativas de otro músculo | `quitarExDia` |
| «undefined: 0 series/semana» al quitar del plan por defecto | `quitarExDia` |
| `atlas_ads_vistos` con basura rompía el tope diario **para siempre** | `adsMarca` |
| Dos `adsMostrar` solapados → dos intersticiales seguidos | `adsMostrar` |

Los cuatro últimos los introduje yo el mismo día. El primero venía de antes.

**Commit `b04f11c`** — los cuatro de gravedad alta

| Fallo | Antes | Ahora |
| --- | --- | --- |
| `goalTimeline` con ritmo cero | «pierdes 8 kg, del 25 % al 17,2 %, en 1 semana» | inalcanzable, proyección honesta, aviso |
| `planVolume` y las superseries | tríceps 9 → aviso falso | 10,5 · isquios 14 |
| `importData` / `applyBackup` | un JSON malo **mataba la app para siempre** | rechazado, no se toca nada |
| `botBuscaCatalogo` | «curl femoral» → *Curl con barra* (bíceps) | → *Curl femoral* (isquios) |

Dos cosas salieron **probando el arreglo**, no leyéndolo: un `plan` basura sale
de `planLimpio` como array vacío y pintar un plan vacío no lanza error, así que
pasaba el try/catch y te dejaba sin rutina; y `goalTimeline` seguía devolviendo
`semanas:1` aun marcado inalcanzable, que llegaba a `p.weeks` y daba la meta por
cumplida a los 7 días.

### Pendientes · media

- `generatePlan` devuelve planes a medio equilibrar (llamar otra vez a
  `balanceVolume` les cambia el volumen).
- `VENTANA_FATIGA` cuenta 8 días (o 6) en el cambio de hora — exactamente la
  regresión que el comentario dice haber arreglado.
- `today()` es UTC, no la hora local: el mapa de fatiga pinta un rango que no es
  el día del usuario.
- `calcPlates` propone pesos que no se pueden montar (redondea a 1,25 en barras
  que suben de 2,5 en 2,5).
- `duoAnalizar` valida propuesta a propuesta pero `duoAplicarSel` las aplica
  todas de golpe, y vienen premarcadas.
- Una lista de copias ilegible desactiva `autoBackup` de forma permanente.
- «Buenos días» es inalcanzable por nombre.

### Pendiente · baja

- `duoLeer` no descarta una pareja formada por el mismo perfil dos veces.

---

## B · Seguridad

10 superficies · 92 agentes · **0 errores** · 81 refutaciones previstas,
**81 corridas**, `panelIncompleto: 0`. 27 candidatos → **23 sobrevivieron** al
panel de tres escépticos → 10 problemas tras fusionar.

Lo más valioso del informe: **lo que más daño hace no es el XSS, son dos fallos
deterministas que se disparan solos, sin atacante.**

### Arreglados (commit `2abe148`)

| | |
| --- | --- |
| Nombre de perfil crudo como clave y saneado en la lista → **la app dejaba de guardar en silencio** | `generateFromOnboarding`, `nubeBajar` |
| `planLimpio` ponía `wd:0`, que es domingo → «hoy descansas» 6 días de 7 | `planLimpio` |
| `dbSaneado` validaba el tipo y dejaba el contenido crudo → XSS con robo de la sesión de Supabase | `dbSaneado` |
| `allowBackup="true"` → fotos, DB y token en la copia de Google | manifiesto + `configurar_android.js` |
| Los autotests corrían en el APK en cada arranque | la puerta `localhost` |

**Commit `21a9fd1`**

| | |
| --- | --- |
| Las fotos no se borraban de Storage por ninguno de los cuatro caminos | `fotosBorrarRutas`, `deletePhoto`, `purgarFotos`, `deleteUser`, `nubeBorrarCuenta` |

El único `DELETE` contra el bucket solo se alcanzaba apagando el interruptor, y
no miraba `r.ok`: sin red borraba el puntero, cantaba «N fotos borradas» y la
foto seguía ahí. Ahora hay una función que borra y dice la verdad; si falla, no
se borra nada en local.

El primero le pasa a cualquiera que se llame **D'Angelo, O'Brien, Ana & Luis**,
que ponga dos espacios seguidos o que pase de 24 caracteres. Ningún atacante:
solo un apóstrofo. Y el tercero era código que yo mismo había escrito una hora
antes — comprobaba el tipo y daba por hecho que con eso bastaba.

### Lo que queda

- **Pronto ·** Cambiar de atleta no reinicia el asistente.
- **Algún día ·** El módulo de `esm.run` se ejecuta antes de aceptar el Modo IA.
- **Algún día ·** `MainActivity` en `singleTask` sin `taskAffinity`, y
  `play-services-ads` con versión dinámica `24.9.+`.
- **No hace falta ·** Un perfil llamado `__proto__` se guarda y no sale en la
  lista.

### Aparte del informe

`keystore.properties` tiene la contraseña de firma en claro en el repositorio.
No lo tocó esta pasada porque no estaba en ninguna superficie, pero conviene
mirarlo.

### Nota sobre la primera pasada

La de por la mañana quedó inservible: 41 hallazgos pedían 123 refutaciones y solo
cupieron 38 antes de agotarse la sesión, y la síntesis murió. Se relanzó
limitando a **4 hallazgos por superficie** y con eso el panel cupo entero. La
lección: más hallazgos no es mejor si no se pueden verificar.

---

## Cómo seguir

**Hecho:** la **v2.2 (`versionCode 13`)** está enviada a revisión con todos estos
arreglos dentro, verificados en el propio `.aab`. La publicada sigue siendo la
2.0 hasta que Google apruebe.

Queda:

1. Los siete de gravedad media de la sección A.
2. Volver a lanzar la batería A: quedó incompleta por abajo y hay áreas sin
   agotar.
3. `keystore.properties` con la contraseña en claro.

### Nota sobre Play Console

Esa consola tarda tanto en pintar la pantalla de versiones que llegué a leerla a
medio cargar y creí que el bundle no se había adjuntado, cuando sí. Estuve
reintentando algo que ya estaba hecho. Si vuelve a pasar: **esperar a que la
página esté quieta antes de creerse lo que muestra.**

Informes completos:
`~/.claude/projects/…/subagents/workflows/wf_c0cc0b2b-696/` (A)
`~/.claude/projects/…/subagents/workflows/wf_2b9bd3dc-d26/` (B, la buena)
