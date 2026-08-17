# Lo que encontraron los agentes · 17 ago 2026

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

El primero le pasa a cualquiera que se llame **D'Angelo, O'Brien, Ana & Luis**,
que ponga dos espacios seguidos o que pase de 24 caracteres. Ningún atacante:
solo un apóstrofo. Y el tercero era código que yo mismo había escrito una hora
antes — comprobaba el tipo y daba por hecho que con eso bastaba.

### Lo que queda

- **Pronto ·** Las fotos no se borran de Supabase Storage: ni al borrar la foto,
  ni al borrar el atleta, ni al borrar la cuenta. `nubeBorrarCuenta` promete
  borrarlas y solo toca la tabla. Contradice `privacidad.html` y el requisito de
  borrado de Play. Solo afecta a quien encendió el interruptor de la nube.
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

1. Las fotos de Storage. Es lo único pendiente que toca una promesa escrita en
   `privacidad.html`, así que además de código es asunto de ficha.
2. Los siete de gravedad media de la sección A.
3. Volver a lanzar la batería A: quedó incompleta por abajo y hay áreas sin
   agotar.

Informes completos:
`~/.claude/projects/…/subagents/workflows/wf_c0cc0b2b-696/` (A)
`~/.claude/projects/…/subagents/workflows/wf_2b9bd3dc-d26/` (B, la buena)
