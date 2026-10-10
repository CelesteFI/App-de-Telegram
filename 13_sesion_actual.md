# Sesión actual — rediseño de minijuegos (2026-10-04)

Documento de memoria para la siguiente sesión: qué se hizo, dónde quedó cada
cosa y qué falta. Leer esto + `README.md` antes de tocar nada.

## 1. Cómo arrancar (solo esto)

```powershell
.\run.ps1
```

- El token de Telegram está fijo en `run.ps1` (`$TOKEN_FIJO`).
- El modo pruebas en navegador viene **encendido por defecto**
  (`DEV_AUTHPASS=1`): en Telegram valida identidad real, en navegador entra
  como Invitado. Solo `.\run.ps1 -ExigirIdentidad` lo apaga.
  (`-SinIdentidad` quedó como alias legacy, ya no hace falta.)
- Si Windows bloquea con "no verificado": ExecutionPolicy ya quedó en
  `RemoteSigned` (CurrentUser) y existe `run.bat` (doble clic, usa Bypass).
- Verificación rápida: `python -m app.nucleo.principal --comprobar`.

## 2. Respaldo pre-rediseño

`backup\Respaldo_pre_rediseno_20261004_020433\` — copia completa del bot tal
como estaba antes del rediseño (sin `backup/`, `__pycache__`, `.git`).
No borrar: es el punto de retorno.

## 3. Decisión de producto (pedida por el usuario)

- El **quiz es un minijuego más**, no sección aparte. Vive en la pantalla
  **Practicar** (`#/juegos`): arriba "Quiz por tema" (8 temas), abajo los
  10 minijuegos. Se quitó la vista separada de quizzes en grupo.
- `bot.py` simplificado: un solo botón "Abrir Practicar" (+ Inicio).
- `webapp/js/vistas/inicio.js`: hub con hero + botón Practicar + historial.
- `webapp/js/vistas/juegos.js`: catálogo unificado quiz + minijuegos.
- `webapp/js/vistas/quiz.js`: look de show de concurso (usa
  `webapp/css/juegos/quiz.css`, cargado en `index.html`).
- Estructura separada preservada: **un CSS y un JS por minijuego**
  (`webapp/css/juegos/*.css`, `webapp/js/juegos/*.js`).

## 4. Rediseño visual (tema "Aula Fiesta")

- `webapp/css/base.css`: paleta viva (naranja→rosa→morado), tarjetas blancas
  con sombra, barra superior en gradiente, progreso arcoíris animado,
  rejilla `.hub__grid` + `.hub__card` para el catálogo, confeti `.fiesta`.
- Cada juego con temática propia y animaciones (ver sus CSS/JS):
  deslizador=Tinder con sellos, memoria=volteo 3D, columnas=cables SVG,
  completar=pergamino con hueco 🧩, intruso=sospechosos 🕵️,
  clasificador=**cestas 🧺 literales** con tarjeta que vuela,
  ordenar=línea de tiempo, grafico=laboratorio nocturno en canvas,
  palabra=concurso, globos=cielo con globos 🎈 y chispas.

## 5. Bugfixes aplicados (segunda ronda, 2026-10-04)

1. **Temporizador congelado**: `vistas/partida.js` usaba `setTimeout` de un
   disparo; los juegos lo llaman una vez esperando ticks. Cambiado a
   `setInterval` (+ `clearInterval` en `limpiar`). `clasificador.js` y
   `globos.js` consultan el reloj fresco (`getElementById`) en cada tick.
2. **Fórmulas sin renderizar**: los `pintar()` internos reinyectaban LaTeX
   crudo sin KaTeX. Todos los juegos con repintado llaman ahora a
   `pintarMatematica()` tras pintar.
3. **Contraste**: título de canasta en pastilla blanca (KaTeX negro sobre
   mimbre oscuro era ilegible); regla global `.katex { color: inherit }`;
   colores de texto explícitos en memoria, clasificador, columnas, intruso,
   ordenar, completar, deslizador; `text-shadow` en globos.
4. **Columnas**: rejilla fija `1fr 44px 1fr` con calle central
   (`.columnas__gutter`), cables de 5 px con nodos blancos, redibujo en
   `requestAnimationFrame` + `resize`.

## 6. Contratos que NO se deben romper

- Cada `webapp/js/juegos/<id>.js` exporta `default { id, crear(ctx) }` donde
  `ctx = { ronda, indice, total, intento, responder, temporizador }` y retorna
  `{ auto, html(), montar(), envio() }`.
- Formatos de `envio()` por juego (los valida el backend en
  `app/minijuegos/*.py`, función `califica`):
  deslizador→boolean, memoria→`{completas, errores}`, columnas→array de
  índices (-1 si vacío), completar→índice, intruso→índice,
  clasificador→`{itemId: clave}`, ordenar→array orden, grafico→índice,
  palabra→string, globos→`{ids: [...]}`.
- Formas de `ronda` que usa cada JS (items/tex, canastas/clave/nombre,
  izquierda/derecha, cartas/id/texto/pares, globos/id/tex, formula/attr,
  enunciado/opciones, tarjetas/tex, pasos, ecuacion/tipos,
  pista/longitud/teclado). Si cambia el backend, actualizar el JS a la par.
- `partida.js`: `temporizador(fn, ms)` = ticks repetidos; `limpiar()` los
  cancela al responder. No volver a `setTimeout` simple.

## 7. Verificación hecha

- `python -m app.nucleo.principal --comprobar` → todo correcto (8 temas × 12
  preguntas, 10 juegos × 3 niveles).
- `node --check` en los 10 juegos + vistas → OK.
- Servidor real en puerto de prueba: `/` sirve app con `quiz.css`,
  `/api/config?dev_uid=1` responde `dev:true, usuario 1`;
  `partida.js` servido contiene `setInterval`.
- `python pruebas/test_api.py` → OK (nota: una aserción del memorama
  "dos cartas distintas se rechazan" es flaky preexistente por tableros
  aleatorios donde dos cartas sí son pareja; pasa al reintentar).

## 8. Pendientes / ideas para la próxima sesión

- Probar en celular real vía Telegram (ngrok + bot) el vuelo a la cesta,
  los cables y el temporizador llegando a 0.
- Si se pide, añadir sonidos con WebAudio (pasos/ chained) sin librerías.
- Posible mejora: arrastrar (pointer events) en clasificador/completar en
  lugar de tocar-origen + tocar-destino.
- No mover el token fuera de `$TOKEN_FIJO` sin avisar: `run.ps1` depende de
  él para validar `initData`.

## 9. Arreglo de conexión / carga (sesión nueva)

Síntoma: la Mini App abría la ventana pero se quedaba en "Cargando la app…"
(Telegram) y en el navegador tardaba muchísimo. Causas y arreglos:

1. **Recursos externos (CDN)**: `index.html` cargaba KaTeX y
   `telegram-web-app.js` desde jsdelivr/telegram.org con `<script>` bloqueante.
   Si la red del celular no los alcanza, el WebView no termina nunca.
   → Ahora TODO es local en `webapp/vendor/` (KaTeX 0.16.9 + fuentes +
   auto-render + telegram-web-app.js). No queda ninguna URL externa en
   `webapp/`. KaTeX va con `defer` (no frena el primer pintado).
2. **Túnel con pantalla de aviso**: ngrok gratis muestra un interstitial que
   deja la Mini App colgada. → `run.ps1` usa **Cloudflare Tunnel**
   (`cloudflared`, se auto-descarga en `cloudflared.exe`) por defecto y deja
   ngrok como respaldo (`-Tunel ngrok`). Verificación con reintentos (el 530
   inicial es transitorio).
3. **Botón de menú viejo**: «Repaso ED» es persistente y apuntaba a la URL del
   túnel anterior. → `bot.py` fija el botón de menú en `post_init` en cada
   arranque (`set_chat_menu_button` sin `chat_id`).
4. **Corridas solapadas**: quedaban bots/servidores/túneles viejos (409,
   puertos ocupados). → `run.ps1` los cierra al arrancar (`.run-pids.json` +
   búsqueda por línea de comando).
5. **Nunca colgarse en silencio**: `api.js` corta a los 15 s con error claro;
   `app.js` muestra aviso + botón **Reintentar**; `index.html` tiene un
   respaldo a los 12 s por si el módulo no llega a ejecutarse.
6. **MIME de fuentes**: `http.py` sirve `.woff2/.woff/.ttf/.otf` como
   `font/*` (WKWebView de iOS rechaza `application/octet-stream`).
7. `--chequeo-identidad` ya no abre un segundo servidor en el mismo puerto:
   solo consulta al que ya corre.

Verificado: servidor local sirve `/`, `/vendor/...` y `/js/...` con MIME
correcto y sin referencias CDN; túnel Cloudflare real devuelve 200 con la app;
`--comprobar` y el chequeo de identidad en verde.
