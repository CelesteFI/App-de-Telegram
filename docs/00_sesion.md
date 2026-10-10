# 00. Sesión y contexto del proyecto

> **Documento vivo.** Léelo (junto con `README.md`) antes de tocar nada: reúne
> qué es el proyecto, cómo se arranca y prueba, las decisiones tomadas, los
> contratos que no se deben romper y lo que queda pendiente.
>
> Consolida los antiguos `12_cierre_sesion.md`, `13_sesion_actual.md` y
> `COMO_PROBAR.md` en un único archivo de contexto.
>
> Carpeta: `D:\08 Semestre\Servicio Social\Mejora de telegram` · Última
> actualización: **10 de octubre de 2026**.

---

## 1. Qué es el proyecto hoy

Mini App de Telegram para **repasar Ecuaciones Diferenciales**:

- **8 temas de quiz** de opción múltiple y **10 minijuegos** conceptuales, todo
  junto en la pantalla **"Practicar"** (`#/juegos`). El quiz es **un minijuego
  más**, no una sección aparte.
- Cada persona entra con su **identidad de Telegram**; sus marcas e historial
  quedan separados sin códigos ni cuentas.
- **Backend**: Python puro (librería estándar), sin frameworks.
- **Front**: HTML/CSS/JS sin build; **KaTeX** y `telegram-web-app.js` locales en
  `webapp/vendor/` (la app no depende de CDN externos).
- **Desplegable** en un servidor externo (Render, plan free) en un solo proceso.
- La versión anterior (chatbot de Análisis Numérico con sesiones tipo Kahoot)
  sigue **intacta** en `extras/demo/` (ignorada por Git).

Estructura (detalle completo en `14_estructura_y_contenido.md`):
`lanzamiento/` (arranque) · `app/` (servidor: `nucleo/` + `minijuegos/`, con
`minijuegos/quiz/`) · `webapp/` (interfaz) · `data/minijuegos/` (contenido JSON,
incl. `quiz/`) · `pruebas/` · `docs/` · `logs/` · `extras/` · `backup/`.

## 2. Cómo arrancar y probar

### 2.1 Local

El **token** ya no vive en `run.ps1`. Se toma, en orden: `-BotToken` →
`$env:BOT_TOKEN` → `lanzamiento/token.local.ps1` → prompt oculto. Lo normal es
tener el archivo (ignorado por Git):

```powershell
# lanzamiento\token.local.ps1
$TOKEN_FIJO = "123456:AAABBB..."
```

```powershell
.\lanzamiento\run.ps1          # servidor + túnel (Cloudflare) + bot
```

Opciones útiles: `-SinTunel` (solo navegador), `-Tunel ngrok`, `-SinBot`,
`-ExigirIdentidad` (apaga el modo de pruebas), `-Comprobar` (valida y sale).
El **modo de pruebas en navegador viene encendido por defecto**: en Telegram se
valida tu identidad real y en el navegador entras como Invitado para probar los
juegos.

### 2.2 Abrir en el navegador / Telegram

- **Navegador**: copia la **URL pública HTTPS** que imprime `run.ps1` (Cloudflare
  no muestra pantalla de aviso). También sirve `http://localhost:8081`. En la
  primera prueba, recarga con **Ctrl+Shift+R**.
- **Telegram**: busca el bot → `/start` → pulsa el **botón nuevo** del mensaje
  (apunta a la URL de *esta* corrida). El botón de menú «Repaso ED» se actualiza
  solo al arrancar. No abras la app desde mensajes viejos.
- Si la app no carga, muestra un aviso con botón **Reintentar** (ya no se queda
  en "Cargando…" para siempre).

### 2.3 Pruebas automáticas

```powershell
python -m app.nucleo.principal --comprobar   # valida quiz + 10 juegos, sin servidor
python pruebas\test_api.py                   # API por HTTP real
npm install                                  # una vez: trae jsdom
node pruebas\smoke.js                        # front real (jsdom) contra el backend
Get-ChildItem webapp\js -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }
```

Las pruebas escriben en una carpeta temporal y la borran al terminar (no tocan
`data/resultados/`).

### 2.4 Desplegar en Render / subir a GitHub

- `lanzamiento/main.py` levanta en **un solo proceso** el servidor HTTP (hilo) y
  el bot (hilo principal). En Render, `WEBAPP_URL` se deduce de
  `RENDER_EXTERNAL_URL`. Sin `BOT_TOKEN`, publica la web y no arranca el bot.
- **Render**: New + Blueprint → conecta el repo → captura el secreto
  **`BOT_TOKEN`** (el de @BotFather). El resto ya está en `render.yaml`.
- **Pinger** cada ~10 min a `https://<app>.onrender.com/api/config` para que no
  duerma (no uses `/robots.txt`).
- Subir a GitHub:
  ```powershell
  git add -A
  git commit -m "Mini App de repaso lista para desplegar"
  git remote add origin https://github.com/<usuario>/<repo>.git
  git push -u origin main
  ```
- Plan free de Render: duerme a los **15 min** sin tráfico; **filesystem
  efímero** (lo escrito en `data/resultados/` se pierde al reiniciar); **750
  h/mes** = un solo servicio despierto.

## 3. Decisiones de producto y arquitectura

- El **quiz es un minijuego más**. Vive en la pantalla **Practicar** (`#/juegos`):
  arriba "Quiz por tema" (8 temas), abajo los 10 minijuegos. Se quitó la vista
  separada de quizzes en grupo.
- `bot.py` simplificado: un solo botón **"Abrir Practicar"** (+ Inicio).
- Vistas del front: `inicio` (hub), `juegos` (catálogo), `tema` (config del quiz),
  `quiz`, `juego` (config de minijuego), `partida`, `reporte`. Navegación por
  **hash** (`#/inicio`, `#/juegos`, `#/tema/<materia>/<tema>`, `#/quiz`,
  `#/juego/<id>`, `#/partida/<id>`); detalle en `14_estructura_y_contenido.md` §9.
- Estructura separada preservada: **un CSS y un JS por minijuego**
  (`webapp/css/juegos/*.css`, `webapp/js/juegos/*.js`).
- **Contenido externalizado a JSON** en `data/minijuegos/<id>.json` y
  `data/minijuegos/quiz/` (ver `14_estructura_y_contenido.md` §5–6). Los `.py` no
  contienen contenido.
- La **respuesta correcta se decide siempre en el servidor**; al navegador solo
  llega la ronda mezclada y sin solución.
- El memorama usa `POST /api/minijuegos/pareja` porque su tablero llega sin la
  solución; el servidor dice si dos cartas forman pareja.

## 4. Rediseño visual (tema "Aula Fiesta")

- `webapp/css/base.css`: paleta viva (naranja→rosa→morado), tarjetas blancas con
  sombra, barra superior en gradiente, progreso arcoíris animado, rejilla
  `.hub__grid` + `.hub__card` para el catálogo y confeti `.fiesta`.
- Cada juego con temática propia y animaciones: deslizador = Tinder con sellos,
  memoria = volteo 3D, columnas = cables SVG, completar = pergamino con hueco 🧩,
  intruso = sospechosos 🕵️, clasificador = cestas 🧺 con tarjeta que vuela,
  ordenar = línea de tiempo, grafico = laboratorio nocturno en canvas,
  palabra = concurso, globos = cielo con globos 🎈 y chispas.

## 5. Contratos que NO se deben romper

Cada `webapp/js/juegos/<id>.js` exporta un **default `{ id, crear(ctx) }`** donde
`ctx = { ronda, indice, total, intento, responder, temporizador }`, y devuelve
`{ auto, html(), montar(), envio() }`.

Formatos de `envio()` (los valida `califica()` en `app/minijuegos/*.py`):

| Juego | `envio()` |
|---|---|
| deslizador | boolean |
| memoria | `{completas, errores}` |
| columnas | array de índices (`-1` si vacío) |
| completar | índice |
| intruso | índice |
| clasificador | `{itemId: clave}` |
| ordenar | array con el orden |
| grafico | índice |
| palabra | string |
| globos | `{ids: [...]}` |

Formas de `ronda` que usa cada JS: items/tex, canastas/clave/nombre,
izquierda/derecha, cartas/id/texto/pares, globos/id/tex, formula/attr,
enunciado/opciones, tarjetas/tex, pasos, ecuacion/tipos, pista/longitud/teclado.
**Si cambia el backend, actualizar el JS a la par.**

`partida.js`: `temporizador(fn, ms)` son **ticks repetidos** (`setInterval`);
`limpiar()` los cancela al responder. No volver a `setTimeout` simple.

## 6. Arreglos y bugfixes aplicados

- **Temporizador congelado**: `partida.js` usaba `setTimeout` de un disparo;
  cambiado a `setInterval` (`clasificador.js` y `globos.js` consultan el reloj
  fresco en cada tick).
- **Fórmulas sin renderizar**: los repintados reinyectaban LaTeX crudo; ahora
  todos llaman a `pintarMatematica()` tras pintar.
- **Contraste**: pastilla blanca para el título de canasta; regla global
  `.katex { color: inherit }`; colores de texto explícitos; `text-shadow` en globos.
- **Columnas**: rejilla fija `1fr 44px 1fr` con calle central, cables de 5 px con
  nodos blancos, redibujo en `requestAnimationFrame` + `resize`.
- **Recursos externos (CDN)**: `index.html` cargaba KaTeX y `telegram-web-app.js`
  desde jsdelivr/telegram.org con `<script>` bloqueante → ahora **todo local** en
  `webapp/vendor/` (KaTeX va con `defer`). Ya no queda ninguna URL externa en
  `webapp/`.
- **Túnel con pantalla de aviso**: ngrok gratis mostraba un interstitial que
  colgaba la Mini App → **Cloudflare Tunnel** por defecto (se autodescarga
  `cloudflared.exe`), ngrok como respaldo.
- **Botón de menú viejo**: apuntaba a la URL del túnel anterior → `bot.py` fija
  el menú en `post_init` en cada arranque (`set_chat_menu_button` sin `chat_id`).
- **Corridas solapadas**: bots/servidores/túneles viejos (409, puertos ocupados)
  → `run.ps1` los cierra al arrancar (`.run-pids.json` + búsqueda por línea de
  comando).
- **Nunca colgarse en silencio**: `api.js` corta a los **15 s** con error claro;
  `app.js` muestra aviso + **Reintentar**; `index.html` tiene un respaldo a los
  **12 s**.
- **MIME de fuentes**: `http.py` sirve `.woff2/.woff/.ttf/.otf` como `font/*`
  (WKWebView de iOS rechaza `application/octet-stream`).
- **`--chequeo-identidad`** ya no abre un segundo servidor en el mismo puerto.
- **Cache-bust**: assets de `index.html` a `?v=2.2.0`; captura de errores de
  carga en `<head>` (`window.__repasoErrores`).

## 7. Verificación hecha

- `python -m app.nucleo.principal --comprobar` → **todo correcto** (8 temas × 12
  preguntas; 10 juegos × 3 niveles).
- `python pruebas\test_api.py` → **todo correcto**.
- `node pruebas\smoke.js` → **todo correcto**.
- `node --check` en `webapp/js` y `pruebas/` → sin errores.
- `main.py` en puerto 8099 sin `BOT_TOKEN`: `/` → 200, `/api/config` → 200,
  `/js/app.js` → `text/javascript`.
- `run.ps1` pasa el parser de PowerShell; `git check-ignore` deja fuera
  `cloudflared.exe`, `node_modules/`, `token.local.ps1`, `logs/`, `backup/` y
  `data/resultados/`.

## 8. Bitácora histórica

- **Investigación y propuesta** (`docs/01`–`08`): Telegram Mini Apps en español,
  capacidades y formas de lanzamiento, comparativa de bots, seguridad de
  `initData` (HMAC-SHA256).
- **Presentación** (`docs/09`–`11`): fuente para NotebookLM, deck de 10
  diapositivas + guion + Q&A y catálogo de librerías listas.
- **Demo anterior** (hoy en `extras/demo/`, ignorada por Git): pasó de "selector
  de prueba" a una **Mini App de Exámenes estilo Kahoot** para 30–40 alumnos
  (`extras/demo/server.py`, banco por tema en `extras/demo/data/banco/*.json`,
  `extras/demo/bot.py`, `extras/demo/test_api.py`, `extras/demo/TESTING.md`).
  Incluía modo "Practicar individual" (feedback inmediato + mejor puntaje) y
  examen en vivo (código de 4 dígitos, barras en vivo, reporte y export CSV) con
  polling simple (sin websockets). Se conserva como respaldo/contexto.

## 9. Pendientes / próximos pasos

1. Crear el repo en GitHub y desplegar en Render (secreto `BOT_TOKEN`) + pinger.
   (El usuario lo hará con GitHub Desktop.)
2. **Probar en celular real** vía Telegram: el vuelo a la cesta, los cables y el
   temporizador llegando a 0.
3. (Opcional) Sonidos con WebAudio, sin librerías.
4. (Opcional) Arrastrar con *pointer events* en clasificador/completar (en lugar
   de tocar origen + tocar destino).
5. Ensayar la **presentación** con `docs/10_diapositivas_presentar.md`.

## 10. Recordatorios clave

- **Nunca** subir el token ni `token.local.ps1` (secretos). En Render va como
  variable de entorno `BOT_TOKEN`.
- **Un solo polling a la vez**: no corras el bot local y el de Render con el
  mismo token (Telegram responde **409**).
- La Mini App **solo funciona dentro de Telegram**; el modo de pruebas en
  navegador es solo para el navegador.
- Al cerrar sesiones de prueba, borra `data/resultados/` para no mezclar
  reportes reales con los de práctica.
- Deja la ventana de `.\lanzamiento\run.ps1` abierta; se detiene todo con
  **Ctrl+C**.

## 11. Índice de documentos (`docs/`)

| Documento | Contenido |
|---|---|
| `00_sesion.md` (este) | Contexto y bitácora del proyecto |
| `01_resumen_ejecutivo.md` | Resumen de 2 min para profesores |
| `02_que_son_las_mini_apps.md` | Conceptos y terminología |
| `03_capacidades_y_formas_de_lanzamiento.md` | API, objetos y formas de abrir una Mini App |
| `04_comparativa_y_recomendaciones.md` | Tablas comparativas y qué conviene |
| `05_guia_bot_de_prueba_paso_a_paso.md` | Tutorial paso a paso con bot tonto |
| `06_propuesta_para_profesores.md` | Plan: objetivos, alcance, cronograma, entregables |
| `07_recursos_y_referencias.md` | Enlaces, repositorios y plantillas |
| `08_seguridad_validacion_initdata.md` | Validación HMAC de `initData` |
| `09_presentacion_notebooklm.md` | Fuente fusionada para NotebookLM |
| `10_diapositivas_presentar.md` | Deck de 10 diapositivas + guion + Q&A |
| `11_mini_apps_con_librerias_listas.md` | Catálogo de librerías listas para integrar |
| `14_estructura_y_contenido.md` | Estructura final, plan de Git y formato de los bancos |
| `ConceptualesED.md` | Examen diagnóstico original (fuente del quiz) |
| `Minijuegos.md` | Especificación original de los 10 minijuegos |
