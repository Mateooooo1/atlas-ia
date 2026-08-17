# Lo que encontraron los agentes · 17 ago 2026

Dos baterías en paralelo sobre `atlas_pwa/index.html` y `atlas_android/`.
Las dos se quedaron **a medias por límite de sesión**, así que hay que leer los
números con cuidado. Está anotado en cada sitio.

---

## A · Fallos de funcionamiento — **confirmados**

3 rondas · 10 áreas · cada fallo lo **reprodujo un segundo agente** cuyo trabajo
era refutarlo. 25 candidatos → **19 confirmados**. De la última ronda murieron
20 agentes por el límite, así que la lista está **incompleta por abajo**: hay
áreas que no llegaron a agotarse.

### Ya arreglados (commit `90652be`)

| Fallo | Dónde |
| --- | --- |
| Marcar descanso sumaba al contador «Día X de N» (28 en vez de 16) | `diasEntrenados` |
| Quitar un ejercicio descolocaba `DB.swapOrig` → alternativas de otro músculo | `quitarExDia` |
| «undefined: 0 series/semana» al quitar del plan por defecto | `quitarExDia` |
| `atlas_ads_vistos` con basura rompía el tope diario **para siempre** | `adsMarca` |
| Dos `adsMostrar` solapados → dos intersticiales seguidos | `adsMostrar` |

Los cuatro últimos los introduje yo el mismo día. El primero venía de antes.

### Pendientes · gravedad alta

1. **`goalTimeline` da 1 semana** con objetivo «Ganar fuerza» y meta solo en kg de
   grasa. La propia interfaz ofrece ese camino. Resultado: «pierdes 8 kg y bajas
   del 25 % al 17,2 % de grasa en 1 semana», y `planTerminado()` da la meta por
   cumplida a los 7 días. Línea ~11800.
2. **`planVolume` cuenta la 2.ª mitad de una superserie como secundaria (×0,5).**
   Tríceps sale 9 en vez de 10,5 y dispara el aviso «por debajo de 10» que no
   toca. La app declara la superserie como dos estaciones en todas partes menos
   aquí. Línea ~11320.
3. **`importData` acepta cualquier JSON** (un escalar, un array) y **deja la app
   muerta de forma permanente**: `save()` corre antes de los renders dentro del
   try/catch, así que el estado envenenado se persiste. Tres fallos distintos,
   mismo origen. Línea ~3594.
4. **El filtro `!BOT_MUS[w]`** borra justo la palabra que distingue el ejercicio,
   y el chat devuelve uno de otro músculo. Línea ~12655.

### Pendientes · gravedad media

- `generatePlan` devuelve planes a medio equilibrar (llamar otra vez a
  `balanceVolume` les cambia el volumen).
- `VENTANA_FATIGA` cuenta 8 días (o 6) en el cambio de hora — es exactamente la
  regresión que el comentario dice haber arreglado.
- `today()` es UTC, no la hora local: el mapa de fatiga pinta un rango que no es
  el día del usuario.
- `calcPlates` propone pesos que no se pueden montar (redondea a 1,25 en barras
  que suben de 2,5 en 2,5).
- `duoAnalizar` valida propuesta a propuesta pero `duoAplicarSel` las aplica
  todas de golpe, y vienen premarcadas.
- Una lista de copias ilegible desactiva `autoBackup` de forma permanente.
- «Buenos días» es inalcanzable por nombre; pedirlo cae en «Curl con barra».

### Pendiente · baja

- `duoLeer` no descarta una pareja formada por el mismo perfil dos veces.

---

## B · Seguridad — **candidatos SIN verificar**

10 superficies, **41 hallazgos**. El panel de refutación estaba diseñado con
3 escépticos por hallazgo (123 pasadas): **solo corrieron 38**, y la síntesis
final murió. Conclusión honesta: **esto no es una lista de vulnerabilidades
confirmadas.** Cada punto hay que reproducirlo antes de tocar nada.

Dicho eso, los que más pinta tienen —y varios los corrobora la batería A—:

### Marcados como críticos por quien los encontró

- **Nombre de perfil crudo en `innerHTML`** del resumen del plan. XSS persistente
  con el propio nombre. (La batería A confirma que hay campos que llegan sin
  escapar, así que este tiene respaldo cruzado.)
- **`importData()` mete el JSON crudo en el DOM**: solo se limpia `plan`, los
  otros seis campos no. Mismo origen que el fallo A-3, ya confirmado.
- **Borrar la cuenta no toca Storage** y aun así dice «tus datos se han
  borrado». Si se confirma, contradice `privacidad.html`, que promete borrado
  inmediato — eso es un problema de ficha, no solo de código.
- **Se ejecuta código de `esm.run`** al abrir el asistente, sin SRI.

### Recurrentes en varias superficies (señal de que algo hay)

- `android:allowBackup="true"` sin reglas de exclusión: sale del móvil el token
  de Supabase, el historial y las fotos de progreso. Lo señalaron **tres**
  superficies distintas por su cuenta.
- El ciclo de vida de las fotos en Storage: borrar una foto, purgar antiguas o
  borrar un atleta deja la copia en la nube y pierde la ruta.
- `keystore.properties` con la contraseña de firma en claro en el repositorio.
- `atlas_pro='1'` es todo el candado de Pro. **Esto ya lo sabemos y es
  deliberado** mientras no haya Play Billing: sin cobro no hay nada que
  proteger.

### Lo que NO me preocupa

- El arnés de diagnóstico en cada arranque: la puerta es `hostname===localhost`.
- Falsificar `localStorage` con el teléfono desbloqueado en la mano: solo te
  haces daño a ti mismo.

---

## Cómo seguir

1. Reproducir los 4 de gravedad alta de A y arreglarlos. Son concretos y traen
   el comando de reproducción en el informe del workflow.
2. Volver a lanzar la parte de seguridad **entera**, con sesión fresca, para que
   el panel de refutación corra completo. Sin eso, la sección B es una lista de
   sospechas.
3. `allowBackup` y `keystore.properties` se pueden mirar a mano en cinco
   minutos, sin esperar a nada.

Informes completos:
`~/.claude/projects/…/subagents/workflows/wf_c0cc0b2b-696/` (A)
`~/.claude/projects/…/subagents/workflows/wf_e3a9b1e6-6df/` (B)
