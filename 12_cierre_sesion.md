# 12. Cierre de sesión: estado del proyecto

> Bitácora para retomar el trabajo sin perder contexto.
> Carpeta: `D:\08 Semestre\Servicio Social\Mejora de telegram`
> Última sesión: 19 de septiembre de 2026.

---

## Qué se logró (resumen de todo)

1. **Investigación completa en español** sobre Telegram Mini Apps (08 documentos
   `01`–`08`), basada en las fuentes oficiales:
   - https://core.telegram.org/bots#replace-entire-websites
   - https://core.telegram.org/bots/webapps
2. **Material de presentación**: `09_presentacion_notebooklm.md` (fuente para
   NotebookLM), `10_diapositivas_presentar.md` (deck de 10 + guion + Q&A) y
   `11_mini_apps_con_librerias_listas.md` (catálogo de librerías listas:
   gráficas, quiz, flashcards, fórmulas, competencias).
3. **Demo funcional** (`demo/`) con bot de prueba y Mini App, automatizada con
   `run.ps1` (servidor + ngrok + bot). Incluye flujo **keyboard button**
   (`sendData`) y **inline/menú** (vía backend `POST /answer` y
   `answerWebAppQuery`).

## Cómo correr la demo (imprescindible para la presentación)

```
cd "D:\08 Semestre\Servicio Social\Mejora de telegram"
.\run.ps1
```

- Elige un puerto libre automáticamente (si 8080 está ocupado usa 8081+).
- Levanta `demo/server.py`, inicia ngrok (`D:\08 Semestre\Servicio Social\ngrok.exe`,
  authtoken ya configurado), verifica que la Mini App responda local y por la
  URL pública HTTPS, y corre el bot en primer plano.
- Parar con `Ctrl+C` (mata web + ngrok).

Pruebas en Telegram (en el bot de prueba):
- `/start` → botón "Abrir selector" (keyboard, manda datos vía `sendData`).
- `/inline` → botón "Abrir panel" (inline, manda vía `/answer` → `answerWebAppQuery`).
- `/menu` → igual que `/inline` desde el menú del chat.
- `/data` → ver el último dato recibido por el bot.

## Piezas técnicas (verificadas funcionando)

- `run.ps1` — automatiza todo. **Contiene el token real del bot** (no subirlo a
  GitHub ni compartirlo). Corregido en esta sesión:
  1. **Puerto libre automático** (8080 lo ocupaba otra app → 404).
  2. **Ruta entre comillas** al arrancar `server.py` con `Start-Process`
     (PowerShell no agrega comillas solas → Python fallaba con exit code 2).
  3. **Logs de `server.py`** en `server.log`/`server.err.log` (y se imprimen
     si algo falla al arrancar).
  4. Verificación de que la Mini App responde local y por la URL pública.
- `demo/server.py` — sirve la Mini App y valida `initData` (HMAC-SHA256,
  `secret_key = HMAC("WebAppData", token)`); publica resultados con
  `answerWebAppQuery`.
- `demo/bot.py` — python-telegram-bot 22.8 instalado (Python 3.13). Define
  comandos y botones web_app; maneja `filters.StatusUpdate.WEB_APP_DATA`.
- `demo/webapp/index.html` — Mini App vanilla (JS/CDN, sin build). Si hay
  `query_id` manda datos al backend; si no, `sendData()`.

## Notas y decisiones

- **Producción**: cuenta normal del bot + ngrok HTTPS. Sin usar test server.
  `TEST_SERVER=1` es opcional en `run.ps1` (base `/test/` de Telegram).
- La Mini App **solo funciona dentro de Telegram** (`window.Telegram.WebApp`).
  Abrir la URL ngrok en el navegador muestra la pantalla de aviso de ngrok
  (normal, no es un error).
- El RAG del chatbot (Bot Chatbot) **no se modifica**: la Mini App es solo la
  interfaz; el backend Python sigue siendo el mismo.
- Seguridad: el token vive solo en `run.ps1` (lado servidor); la web jamás lo
  ve. Validación HMAC obligatoria en `/answer`.

## Pendiente / próximo paso

1. **Redecidir la propuesta para el profe** (documento 06): quiz (B) rápido,
   navegador de apuntes con fórmulas (C) de mayor valor.
2. Decidir si se agrega a `demo/bot.py` la impresión en consola de cada
   `web_app_data` recibido (útil durante la presentación).
3. Precio del PDF incluido: `MejorasTelegram.pdf` (copia exportada).

---

## ✅ Sesión posterior: Mini App de Examenes implementada (estilo Kahoot)

La demo pasó de ser "selector de prueba" a una **Mini App de Examenes** real
para 30-40 alumnos. El bot sigue siendo "tonto" (solo botones, sin chatbot).

### Qué se construyó (todo en `demo/`)

| Pieza | Archivo | Qué hace |
|---|---|---|
| Backend | `demo/server.py` | Sirve la webapp + API REST de sesiones (estilo Kahoot) |
| Banco de preguntas | `demo/data/banco/<tema>.json` | 9 quizzes de **plantilla** (un archivo por tema de la App) con "Pregunta 1..N" / Correcta y 3 Incorrectas; la profesora los reemplazará por el banco real. Si la carpeta está vacía o falta, el servidor usa las mismas plantillas por defecto |
| Frontend | `demo/webapp/index.html` + `css/app.css` + `js/api.js` + `js/app.js` + `js/teoria.js` | SPA con 2 áreas: **Teoría** (apuntes con fórmulas KaTeX) y **Quizzes** |
| Bot | `demo/bot.py` | Bot tonto: botones inline para abrir cada área (dan identidad `initData`) |
| Prueba | `demo/test_api.py` + `demo/TESTING.md` | Smoke test de la API y guía de pruebas (40/40 OK) |

### Cómo funciona el flujo

1. `/start` en el bot → botones **📖 Area de Teoria** / **📝 Area de Quizzes**.
2. En Quizzes hay **dos modos**:
   - **🎯 Practicar individual**: sin sala ni código. Elige un tema → responde a
     su ritmo con retroalimentación inmediata (marca la correcta) → resultado
     final con repaso pregunta por pregunta y botón de repetir. Guarda tu mejor
     puntaje (`mejor X/N`) en el dispositivo.
   - **Examen en vivo tipo Kahoot**:
     1. El profesor ("Soy profesor(a)") elige el examen (listados **por tema**) y se
        genera un **código de 4 dígitos**.
     2. Los alumnos ("Soy alumno") teclean el código.
     3. El profesor va avanzando pregunta por pregunta; en su pantalla ve las
        **barras de respuestas en vivo** (cuántos eligieron cada opción y cuál es
        la correcta).
     4. Al final: reporte por alumno (tabla) + análisis por pregunta + **exportar
        CSV** / versión imprimible. El servidor guarda los reportes en
        `demo/data/resultados/<codigo>_<fecha>.{json,csv}`.

### Decisiones técnicas

- **Identidad**: se usa el botón inline/menú (manda `initData` → uid de Telegram).
  El botón de teclado (keyboard) **no** da identidad, así que para entrar al
  examen se usan botones inline.
- **Tiempo real**: sin websockets. Polling simple: alumnos cada 2.5 s, profesor
  cada 2 s. Con `ThreadingHTTPServer` aguanta 30-40 alumnos en una laptop.
- **La correcta se oculta** al alumno en la pregunta activa; solo aparece en el
  repaso final (`/api/estado` en estado `final`/`cerrada`).
- **Seguridad**: cada POST valida `initData` (HMAC-SHA256). El profesor se
  identifica por su uid de Telegram; endpoints de profesor deniegan a cualquiera
  que no sea el creador. PIN opcional del profesor con `PIN_PROFESOR` (en
  `run.ps1`, descomentar).
- **Modo dev**: `?dev=1` en el navegador + `$env:DEV_AUTHPASS="1"` en el server
  permite probar todo desde un navegador normal (sin Telegram) identificándose
  arbitrariamente. Útil para ensayar con varias pestañas.

### Cómo probar

```
.\run.ps1                                  # levanta server + ngrok + bot (producción)
   # opcional antes:  $env:PIN_PROFESOR="2026"
   # para probar local sin Telegram: desde PowerShell:
   $env:DEV_AUTHPASS="1"; $env:BOT_TOKEN="x"; $env:PORT="8099"
   python demo\server.py                    # luego abrir http://localhost:8099/?dev=1
```

Reportes generados se guardan en `demo/data/resultados/`. El banco de preguntas
se edita archivo por archivo en `demo/data/banco/<tema>.json` (un quiz por tema):
cada pregunta lleva `p`, `f` (fórmula LaTeX opcional), `opciones` y `correcta`.
Agregar un tema nuevo = crear su archivo; borrarlo = quitar el archivo. Si la
carpeta queda vacía o no existe, el servidor usa las plantillas por defecto.

Para **probar todo** (API, vistas y estáticos) sigue la guía en
[`demo/TESTING.md`](demo/TESTING.md) — incluye el checklist de progreso.

---

## ✅ Sesión más reciente (19-sep-2026): modo individual, quizzes por tema y banco por archivo

### Lo que se agregó/cambió en esta sesión

1. **Modo "🎯 Practicar individual"** en el área de Quizzes:
   - Sin sala ni código: el alumno elige un tema y responde a su ritmo.
   - Retroalimentación inmediata (marca la correcta), resultado final con repaso
     pregunta por pregunta, botón de repetir y mejor puntaje en el dispositivo
     (`localStorage` -> `mejor X/N`).
   - Backend nuevo: `GET /api/practica/<examen_id>` devuelve el quiz COMPLETO
     (con `correcta`) para que la app haga el feedback.
2. **Quizzes divididos por tema** (igual que el área de Teoría): 9 temas con ids
   `biseccion, newton, falsaPosicion, puntoFijo, lagrange, diferenciasDivididas,
   trapecio, simpson, derivadas`. Los quizzes se agrupan por tema en la lista del
   alumno y del profesor.
3. **Plantillas básicas**: no se construyó banco real (la profesora lo dará).
   Cada quiz usa "Pregunta 1..N" con opciones `Correcta / Incorrecta x3`.
4. **Banco de preguntas por archivo**: se eliminó `demo/data/preguntas.json`;
   ahora hay un archivo por tema en `demo/data/banco/<tema>.json` (9 archivos).
   - `server.py` carga toda la carpeta; si falta o está vacía usa las mismas
     plantillas por defecto.
   - Variable nueva: `BANCO_DIR` (default `demo/data/banco`).
   - Se agrega/quita un tema creando o borrando su archivo.
5. **Guía de pruebas y doc**: nuevo `demo/TESTING.md` (cómo correr app y pruebas,
   qué prueba cada cosa, checklist de progreso).
6. **Smoke test reubicado**: `C:\Users\...\Temp\opencode\smoke.js` → movido al
   proyecto en `pruebas/smoke.js` con rutas relativas (ya no depende de Temp).
   Borra la copia temporal vieja si aún existe.
7. **Puerto 8080 ocupado**: la app `ApplicationWebServer` (PID que varía) toma el
   puerto 8080 en esta máquina → para pruebas locales se usa `PORT=8099`.
   `run.ps1` ya elige puerto libre automáticamente.

### Estado verificado al cerrar la sesión

- `python demo/test_api.py` → **40 ok, 0 fallos** (flujo Kahoot completo +
  `/api/practica` 200/404 + banco por tema + fallback por defecto).
- `node pruebas\smoke.js` → todas las vistas OK (incluye el flujo de práctica
  individual: responder → final → repetir).
- `python -m py_compile` y `node --check` sin errores.
- Resultados de prueba en `demo/data/resultados/` ya limpiados.

### Próximos pasos para retomar

1. **[Principal] Reemplazar plantillas por el banco real** que dará la profesora:
   editar `demo/data/banco/<tema>.json` (cada pregunta: `p` = enunciado,
   `f` = fórmula LaTeX opcional entre `$...$`, `opciones[]`, `correcta` = índice).
   El servidor recarga solo al guardar (cache por fecha).
2. **(Opcional) Temporizador por pregunta** en el examen en vivo (está marcado
   como pendiente en `demo/TESTING.md` §6): requiere campo de tiempo en
   `server.py` + cuenta regresiva en `app.js` y cierre automático de pregunta.
3. **Probar en Telegram real** con `run.ps1` (ngrok + bot) para el demo final:
   abrir Mini App desde el bot y recorrer los 3 flujos (Teoría, Practicar, examen
   en vivo con 2-3 pestañas del modo dev como "alumnos").
4. Si se quiere PIN de profesor, descomentar `PIN_PROFESOR` en `run.ps1`.
5. Ensayar la **presentación** con `10_diapositivas_presentar.md`.

### Recordatorios clave

- **No subir `run.ps1` a ningún repo** (contiene el token real del bot).
- Abrir la Mini App solo funciona dentro de Telegram (`?dev=1` es solo para
  pruebas locales en el navegador).
- Al cerrar sesiones de prueba, borrar `demo/data/resultados/` para no confundir
  reportes reales con los de práctica.

## Índice de la carpeta

| Documento | Contenido |
|---|---|
| `README.md` | Portada e índice general. |
| `01_resumen_ejecutivo.md` | Resumen de 2 min para profesores. |
| `02_que_son_las_mini_apps.md` | Conceptos y terminología. |
| `03_capacidades_y_formas_de_lanzamiento.md` | API, objetos y 7+ formas de abrir una Mini App. |
| `04_comparativa_y_recomendaciones.md` | Tablas comparativas y qué conviene. |
| `05_guia_bot_de_prueba_paso_a_paso.md` | Tutorial paso a paso con bot tonto. |
| `06_propuesta_para_profesores.md` | Plan: objetivos, alcance, cronograma, entregables. |
| `07_recursos_y_referencias.md` | Enlaces, repositorios y plantillas. |
| `08_seguridad_validacion_initdata.md` | Validación HMAC de `initData`. |
| `09_presentacion_notebooklm.md` | Fuente fusionada para NotebookLM. |
| `10_diapositivas_presentar.md` | Deck de 10 diapositivas + guion + Q&A. |
| `11_mini_apps_con_librerias_listas.md` | Catálogo de librerías listas para integrar. |
| `12_cierre_sesion.md` (este) | Estado del proyecto para retomar. |
| `run.ps1` | Lanzador (servidor + ngrok + bot). **Contiene el token real.** |
| `demo/` | Código funcional de la demo. Incluye `TESTING.md` (guía de pruebas y progreso). |
| `pruebas/` | Smoke test de las vistas en Node (`pruebas/smoke.js`). |
| `MejorasTelegram.pdf` | PDF exportado del material. |

## Comandos útiles

- Lanzar demo: `.\run.ps1`
- Probar backend local sin Telegram (validación):
  ```powershell
  $env:DEV_AUTHPASS="1"; $env:BOT_TOKEN="x"; $env:PORT="8099"
  python demo\server.py                # abre http://localhost:8099/?dev=1
  ```
- Batería de la API: `python demo\test_api.py` (espera 40 ok, 0 fallos)
- Smoke test vistas: `node pruebas\smoke.js`
- Sintaxis: `python -m py_compile demo\server.py demo\test_api.py` y
  `node --check demo\webapp\js\app.js`
- ngrok manual si se necesita: `& "D:\08 Semestre\Servicio Social\ngrok.exe" http 8081`