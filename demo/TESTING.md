# Mini App de Exámenes — Pruebas y documentación

Guía de cómo correr la app y sus pruebas, qué hace cada pieza y el estado actual
del proyecto. Léelo de arriba hacia abajo: sirve para **ver cómo va quedando**
conforme avanzamos.

---

## 1. Qué hay dentro de `demo/`

Estructura separada por responsabilidad, pensada para escalar/reducir sin enredos:

| Pieza | Archivo(s) | Qué hace |
|---|---|---|
| Frontend: estructura | `webapp/index.html` | El único HTML (shell de la Mini App: cabe en Telegram sin scroll) |
| Frontend: estilos | `webapp/css/app.css` | Todo el CSS (tema claro/oscuro, tarjetas, botones, resultados) |
| Frontend: lógica | `webapp/js/app.js` | Vistas y controlador de la SPA (inicio, teoría, quizzes, alumno/profesor, modo individual) |
| Frontend: API | `webapp/js/api.js` | Cómo hablar con el backend (initData de Telegram + modo dev) |
| Frontend: contenido teoría | `webapp/js/teoria.js` | Los 9 temas del área de Teoría (con fórmulas LaTeX) — contenido puro |
| Backend | `server.py` | Sirve la webapp + API REST de sesiones (estilo Kahoot) y el modo individual |
| Bot | `bot.py` | Bot "tonto": botones inline que abren cada área (dan identidad) |
| Banco de preguntas | `data/banco/<tema>.json` | **Un archivo por tema**. Edita el archivo del tema y listo; los cambios se recargan solos. Si la carpeta está vacía/falta, se usan plantillas por defecto |
| Reportes | `data/resultados/` | Archivos `<codigo>_<fecha>.{json,csv}` generados al cerrar cada sesión |
| Prueba de API | `test_api.py` | Batería HTTP del flujo completo (crear/unirse/responder/reporte/permito) |
| Smoke test (frontend) | `../pruebas/smoke.js` | Carga los 3 JS en Node y dibuja todas las vistas sin navegador |

> HTML, CSS y JS viven separados a propósito: cambias una vista en `app.js`,
> un estilo en `app.css`, o una pregunta en `data/banco/...json`, sin tocar lo demás.

---

## 2. Cómo correr la app en local (sin Telegram)

```powershell
# 1. En la carpeta raiz del proyecto
$env:DEV_AUTHPASS="1"      # autenticación dev: no necesita Telegram
$env:BOT_TOKEN="x"         # token ficticio (no valida initData)
$env:PORT="8099"           # usa 8099 si el 8080 ya está ocupado por otra app
python demo\server.py      # arranca el backend + sirve la webapp
```

Abre en el navegador: `http://localhost:8099/?dev=1` — pedirá nombre habitual,
y así puedes probar toda la app sin abrir Telegram (modo dev).

### Probar dentro de Telegram (opcional, para el demo final)

```powershell
.\run.ps1                  # arranca servidor + ngrok + bot (lee el token real)
```
El bot responde con botones para abrir la Mini App. Requiere el token real y
red `ngrok` apuntando al puerto del servidor.

---

## 3. Cómo correr las pruebas

### 3a. API completa (la más importante)

En PowerShell, desde la **carpeta raíz del proyecto**:

```powershell
$env:DEV_AUTHPASS="1"; $env:BOT_TOKEN="test:token"; $env:PORT="8099"
Remove-Item demo\data\resultados -Recurse -Force -ErrorAction SilentlyContinue
# abrir una terminal aparte y arrancar el servidor:
python demo\server.py
# en otra terminal, correr la batería:
python demo\test_api.py
```

Resultado esperado (sin errores):

```
RESULTADO: 40 ok, 0 fallos     y  EXIT=0
```

>> Si algo deja la carpeta `data/resultados` con archivos de prueba, bórrala
>> antes de correr de nuevo (las pruebas la usan para verificar el CSV).

### 3b. Sintaxis y vistas del frontend

```powershell
python -m py_compile demo\server.py demo\test_api.py   # sintaxis Python
node --check demo\webapp\js\app.js                     # sintaxis JS
node pruebas\smoke.js                                   # dibuja todas las vistas en Node
```

Esperado en smoke: `PROF: vistas y parseo OK` + una línea `[ok] vista ...` por vista.

---

## 4. Qué prueba cada cosa (para debuggear rápido)

| ¿Falló el flujo en vivo? | Revisa |
|---|---|
| No abre el código en Telegram / webhook | `run.ps1`: ngrok y puerto; el token en `run.ps1` |
| La webapp no carga en el navegador | `index.html` + `js/` se sirven desde `webapp/`; revisa la ruta `WEBAPP_DIR` |
| No aparecen quizzes | `data/banco/` tiene los `.json` por tema; verifica con `http://localhost:8099/api/examenes` |
| Los quizzes cambian pero no se reflejan | La cache se invalida sola por fecha; guarda el archivo y recarga la app |
| Error de permiso al responder / ver reporte | Repasa `initData` (modo Telegram) o `?dev=1` (modo dev) |
| El alumno ve la respuesta correcta | Es a propósito en `final/cerrada`; en `activa` se oculta |

---

## 5. La API de un vistazo

- `GET /api/config` — ¿requiere PIN de profesor?
- `GET /api/examenes` — catálogo por tema (sin respuestas).
- `GET /api/practica/<examen_id>` — quiz **individual** completo (con `correcta`).
- `POST /api/crear` — profesor crea sesión con código de 4 dígitos.
- `POST /api/unirse` — alumno entra con el código.
- `GET /api/estado?code&uid` — estado del alumno (sin claves mientras la pregunta está activa).
- `POST /api/responder` — alumno responde.
- `POST /api/siguiente` — profesor avanza / ver resultados / cerrar.
- `GET /api/profesor/estado?code&uid` — estado completo para el profesor.
- `GET /api/reporte[.csv|.html]` — reporte final (solo profesor).

---

## 6. Checklist de progreso (estado actual)

Marca lo que vas viendo funcionar:

### Núcleo
- [x] Servidor sirve la webapp (`/` → `index.html`, `/js/*`, `/css/*`)
- [x] API REST de sesiones Kahoot (crear, unirse, responder, avanzar, cerrar)
- [x] Código de 4 dígitos y sala en vivo con contadores por opción
- [x] Reporte por alumno + análisis por pregunta + exportar CSV / HTML
- [x] La respuesta correcta se oculta al alumno en la pregunta activa
- [x] Validación `initData` HMAC-SHA256 + modo dev `DEV_AUTHPASS`
- [ ] (pendiente) Temporizador por pregunta en el examen en vivo

### Modo individual (nuevo)
- [x] Quizzes agrupados por tema dentro del área de Quizzes
- [x] Vista "🎯 Practicar individual": elige tema sin sala ni código
- [x] Respuesta de una en una con retroalimentación inmediata (marca la correcta)
- [x] Resultado final con repaso pregunta por pregunta y botón de repetir
- [x] Mejor puntaje guardado en el dispositivo (`mejor X/N`)
- [x] Preguntas de **plantilla** (la profesora las reemplazará por el banco real)

### Banco de preguntas por tema
- [x] Un archivo por tema: `data/banco/<tema>.json` (9 archivos)
- [x] Se agrega/elimina un tema creando/borrando su archivo
- [x] Fallback automático a plantillas si la carpeta está vacía o falta

### Organización del código
- [x] HTML / CSS / JS separados (`index.html`, `app.css`, `app.js`, `api.js`, `teoria.js`)
- [x] Backend, bot y pruebas en archivos propios
- [x] Guía de pruebas en este mismo documento

### Pruebas
- [x] Batería HTTP `test_api.py` → **40 ok, 0 fallos**
- [x] Smoke test de vistas en Node → OK
- [x] Sintaxis Python y JS validada en cada cambio

---

## 7. Recetas de mantenimiento rápido

| Quiero... | Hago... |
|---|---|
| Cambiar/reemplazar las preguntas de un tema | Edito `data/banco/<tema>.json` (las recarga el servidor al guardar; Campo `f` acepta LaTeX con `$...$`) |
| Agregar un tema nuevo con su quiz | Copio un archivo de `data/banco/`, cambio `id`/`tema`/`titulo`, y (opcional) añado su entrada en `webapp/js/teoria.js` |
| Quitar un quiz | Borro su archivo de `data/banco/` |
| Cambiar el nombre que se muestra de la app | `server.py` → `GET /api/config` → `nombre` |
| Probar sin Telegram | `DEV_AUTHPASS=1` + abrir `http://.../?dev=1` |
| Escalar a más alumnos | Subir recursos; el polling (2.5s/2s) aguanta decenas en una laptop (ver `12_cierre_sesion.md`) |

---

## 8. Documentación de contexto (repositorio)

Para la memoria del servicio social, consulta en la raíz:

- `README.md` — índice general de todos los documentos.
- `12_cierre_sesion.md` — estado del proyecto, decisiones técnicas y cómo retomar.
- `08_seguridad_validacion_initdata.md` — por qué se valida `initData`.
- `04_comparativa_y_recomendaciones.md` — por qué HTML/JS vanilla y esta arquitectura.