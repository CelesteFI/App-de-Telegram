# 14. Estructura del proyecto, bancos de preguntas y plan de Git

Este documento es la referencia completa de **donde vive cada cosa** despues de
la reorganizacion, **que hace cada archivo**, **que se sube a Git y por que** y
**con que formato se guardan las preguntas/respuestas de cada minijuego y del
quiz** (para crear nuevos bancos y usarlos como contexto en Gemini Pro).

La app es una Mini App de Telegram sobre **Ecuaciones Diferenciales**: un quiz
de opcion multiple y 10 minijuegos con enfoque conceptual. El servidor es
Python puro (libreria estandar) y el front es HTML/CSS/JS sin build.

---

## 1. Arbol final del proyecto

```
Mejora de telegram/
├─ lanzamiento/                 Arranque local / desplegable (fuera del paquete app)
│  ├─ run.ps1                   Lanzador principal (servidor + tunel + bot)
│  ├─ run.bat                   Atajo de doble clic que llama a run.ps1
│  ├─ main.py                   Punto de entrada: arranca el servidor HTTP
│  ├─ bot.py                    Bot de Telegram (webhook/polling) que abre la Mini App
│  ├─ token.local.ps1           Token del bot (SECRETO, ignorado por Git)
│  └─ cloudflared.exe           Tunel local (binario pesado, ignorado por Git)
│
├─ app/                         Paquete Python del servidor
│  ├─ __init__.py               Marca el paquete y describe la estructura
│  ├─ nucleo/                   Infraestructura comun (sin juegos)
│  │  ├─ __init__.py
│  │  ├─ config.py              Rutas, puerto, token y variables de entorno
│  │  ├─ http.py                Servidor HTTP minimo + router por tabla + MIME
│  │  ├─ seguridad.py           Validacion de initData (HMAC) y modo pruebas
│  │  ├─ almacen.py             Lectura/cache de JSON (materias, quizzes, resultados)
│  │  └─ principal.py           Registra rutas, arranque y `--comprobar`
│  └─ minijuegos/               Un archivo por juego + el quiz
│     ├─ __init__.py            Registra los 10 juegos y sus rutas
│     ├─ base.py                Utilidades comunes + `contenido(<id>)` (lee JSON)
│     ├─ registro.py            Descubre juegos automaticamente (pkgutil)
│     ├─ servicio.py            Rutas /api/minijuegos/* (iniciar, responder, estado...)
│     ├─ plantilla.py           Plantilla para crear un juego nuevo
│     ├─ deslizador.py          Minijuego 1
│     ├─ memoria.py             Minijuego 2
│     ├─ columnas.py            Minijuego 3
│     ├─ completar.py           Minijuego 4
│     ├─ intruso.py             Minijuego 5
│     ├─ clasificador.py        Minijuego 6
│     ├─ ordenar.py             Minijuego 7
│     ├─ grafico.py             Minijuego 8
│     ├─ palabra.py             Minijuego 9
│     ├─ globos.py              Minijuego 10
│     └─ quiz/                  El quiz vive DENTRO de minijuegos
│        ├─ __init__.py         Rutas /api/quiz/* (materias, temas, intentos)
│        ├─ banco.py            Catalogo de materias/temas/preguntas
│        └─ servicio.py         Intentos, calificacion, reportes y records
│
├─ webapp/                      Mini App (se sirve como raiz estatica)
│  ├─ index.html                Unico HTML; carga KaTeX, Telegram y app.js
│  ├─ css/
│  │  ├─ base.css               Estilos base
│  │  └─ juegos/*.css           Estilos por juego (+ quiz.css)
│  ├─ js/
│  │  ├─ app.js                 Arranque del front
│  │  ├─ api.js                 Cliente fetch con timeout
│  │  ├─ avisos.js, dom.js, estado.js, navegacion.js
│  │  ├─ juegos/                Un JS por juego + index.js (registro)
│  │  └─ vistas/                Pantallas (inicio, quiz, tema, partida, juego, reporte)
│  └─ vendor/                   Terceros locales: katex/ y telegram-web-app.js
│
├─ data/                        TODO el contenido editable (sin codigo)
│  ├─ minijuegos/
│  │  ├─ deslizador.json        Contenido del minijuego 1
│  │  ├─ memoria.json           ... 2
│  │  ├─ columnas.json          ... 3
│  │  ├─ completar.json         ... 4
│  │  ├─ intruso.json           ... 5
│  │  ├─ clasificador.json      ... 6
│  │  ├─ ordenar.json           ... 7
│  │  ├─ grafico.json           ... 8
│  │  ├─ palabra.json           ... 9
│  │  ├─ globos.json            ... 10
│  │  └─ quiz/                  Banco del quiz por tema (misma carpeta que sus datos)
│  │     ├─ materias.json       Catalogo de materias y temas
│  │     ├─ quiz_tema_clasificacion.json
│  │     ├─ quiz_tema_exactas.json
│  │     ├─ quiz_tema_lineales1.json
│  │     ├─ quiz_tema_separable.json
│  │     ├─ quiz_tema_bernoulli.json
│  │     ├─ quiz_tema_segundo_orden.json
│  │     ├─ quiz_tema_laplace.json
│  │     └─ quiz_tema_series_edp.json
│  └─ resultados/               Salidas de intentos (generadas en ejecucion)
│     └─ .gitkeep               Mantiene la carpeta en Git
│
├─ pruebas/
│  ├─ test_api.py               Pruebas de la API (Python, sin dependencias)
│  └─ smoke.js                  Prueba del front con jsdom (dev)
│
├─ docs/                        Documentacion (00_sesion.md = contexto; 01-11 propuesta; 14 este archivo)
├─ logs/                        Logs de ejecucion (IGNORADO por Git)
├─ extras/                      demo anterior, PDF y capturas (IGNORADO por Git)
├─ backup/                      Respaldos historicos (IGNORADO por Git)
│
├─ README.md                    Resumen e instrucciones
├─ requirements.txt            Dependencias Python (python-telegram-bot)
├─ render.yaml                 Definicion de despliegue en Render
├─ .python-version             Version de Python para Render (3.13)
├─ .gitignore                  Archivos que NO se suben
├─ .gitattributes              Normalizacion de fin de linea
├─ package.json                Dependencia de desarrollo: jsdom
└─ package-lock.json
```

---

## 2. Que hace cada parte (por carpeta)

### `lanzamiento/` — arranque
- **run.ps1**: el unico comando que hace falta en local. Carga el token (param
  `-BotToken` → `$env:BOT_TOKEN` → `token.local.ps1` → prompt oculto), arranca
  el servidor, opcionalmente el tunel de Cloudflare y el bot, y manda los logs
  a `logs/`. Calcula la raiz subiendo un nivel desde su propia carpeta.
- **main.py**: entrada del servidor. Agrega la raiz al `sys.path` y llama a
  `app.nucleo.principal`. Es lo que ejecuta Render (`python lanzamiento/main.py`).
- **bot.py**: bot de Telegram que publica el boton de la Mini App.
- **token.local.ps1 / cloudflared.exe**: secretos y binarios locales.

### `app/nucleo/` — infraestructura
- **config.py**: calcula `RAIZ` (sube 3 niveles desde el archivo), resuelve
  rutas (`data/minijuegos`, `data/minijuegos/quiz`, `data/resultados`) y lee
  variables de entorno (`PUERTO`/`PORT`, `BOT_TOKEN`, `DEV_AUTHPASS`...).
- **http.py**: servidor `http.server` con router por tabla (`@ruta`), manejo
  JSON, tipos MIME correctos (fuentes, `text/javascript`) y `no-store`.
- **seguridad.py**: valida el `initData` de Telegram (HMAC) y permite un modo
  de pruebas para navegador.
- **almacen.py**: lee JSON de disco con cache por fecha de modificacion.
- **principal.py**: importa/registra los modulos, arranca el servidor y corre
  `--comprobar` (valida quiz + los 10 juegos sin levantar el server).

### `app/minijuegos/` — juegos y quiz
- **base.py**: utilidades compartidas (`nivel_limite`, `tomar`, `barajar`,
  `puntos`, `normalizar_nivel`) y **`contenido(<id>)`**, que lee
  `data/minijuegos/<id>.json`.
- **registro.py**: recorre la carpeta, importa cada `.py` con diccionario
  `JUEGO` y funciones `rondas/publico/califica`. La lista `NO_ES_JUEGO`
  (`base`, `registro`, `servicio`, `plantilla`, `quiz`) evita importar
  infraestructura como si fueran juegos.
- **servicio.py**: rutas `/api/minijuegos/*`. Decide respuestas correctas en
  el servidor; el navegador nunca recibe la solucion.
- **quiz/**: el quiz, separado en `banco.py` (catalogo/preguntas),
  `servicio.py` (intentos, calificacion, reportes) y `__init__.py` (rutas).

### `webapp/` — interfaz
- **index.html** + `js/app.js`: arranque. KaTeX y el script de Telegram se
  cargan **desde `vendor/`** (local), no de CDN.
- **js/juegos/**: un modulo por juego y `index.js` que los registra.
- **js/vistas/**: pantallas de la app.

### `data/` — contenido (lo unico que hay que tocar para agregar preguntas)
- **data/minijuegos/<id>.json**: contenido de cada minijuego.
- **data/minijuegos/quiz/**: `materias.json` + un `quiz_tema_<tema>.json` por tema.
- **data/resultados/**: archivos de intentos (se generan solos).

---

## 3. Reorganizacion: origen -> destino

Resumen de los movimientos hechos, con el motivo.

| Origen (antes) | Destino (ahora) | Por que |
|---|---|---|
| `ArchivosMD/01..11` + `ConceptualesED.md` + `Minijuegos.md` | `docs/` | Toda la documentacion en un solo lugar |
| `12_cierre_sesion.md`, `13_sesion_actual.md` (raiz) + `COMO_PROBAR.md` | `docs/00_sesion.md` | Se unifican en un solo archivo de contexto/bitacora |
| `MejorasTelegram.pdf`, `rzones errores.png` | `extras/` | Material de trabajo que no usa Render |
| `demo/` (app anterior) | `extras/demo/` | Respaldo del prototipo, fuera del codigo activo |
| `server.log`, `server.err.log`, `tunel.log`, `tunel.err.log` | `logs/` | Artefactos de ejecucion en una sola carpeta |
| `run.ps1`, `run.bat`, `main.py`, `bot.py`, `token.local.ps1`, `cloudflared.exe` | `lanzamiento/` | Separar el arranque del paquete `app/` |
| `app/quiz/{__init__,banco,servicio}.py` | `app/minijuegos/quiz/` | Todos los juegos (y el quiz) juntos bajo `minijuegos/` |
| `data/quizzes/<tema>.json` | `data/minijuegos/quiz/quiz_tema_<tema>.json` | Nombres controlados (`quiz_tema_*`) en la carpeta del quiz |
| `data/config/materias.json` | `data/minijuegos/quiz/materias.json` | Un unico arbol de datos bajo `data/minijuegos/` |
| Constantes en `app/minijuegos/*.py` | `data/minijuegos/<id>.json` | El contenido sale del codigo y pasa a JSON editable |

Ajustes de codigo que acompanan al move:
- Imports del quiz: `from ..nucleo` → `from ...nucleo` (un nivel mas).
- `app/nucleo/principal.py`: `from ..quiz ...` → `from ..minijuegos.quiz ...`.
- `app/nucleo/config.py`: `MATERIAS_FILE`/`QUIZZ_DIR` apuntan a
  `data/minijuegos/quiz/`; nuevo `MINIJUEGOS_DIR`.
- `app/minijuegos/registro.py`: se agrega `"quiz"` a `NO_ES_JUEGO`.
- `render.yaml`: `startCommand: python lanzamiento/main.py`.

---

## 4. Plan de Git: que se sube y por que

### 4.1 Se sube (necesario para que Render funcione)
- `lanzamiento/` **excepto** `token.local.ps1` y `cloudflared.exe`.
- `app/` completo (servidor).
- `webapp/` completo, **incluido** `vendor/` (KaTeX y Telegram local: la app no
  depende de internet para pintar formulas).
- `data/minijuegos/` (todo el contenido) y `data/resultados/.gitkeep`.
- `pruebas/`, `docs/`, `README.md`.
- Archivos de despliegue: `requirements.txt`, `render.yaml`, `.python-version`.
- `package.json` / `package-lock.json` (solo hacen falta para `pruebas/smoke.js`).

### 4.2 NO se sube (por que) — ver `.gitignore`
| Patron | Motivo |
|---|---|
| `__pycache__/`, `*.py[cod]` | Artefactos de Python |
| `node_modules/` | Se reinstala con `npm install` |
| `cloudflared.exe`, `ngrok.exe` | Binarios pesados; Render no los usa |
| `*.log`, `logs/`, `.run-pids.json`, `lanzamiento/.run-pids.json` | Estado local de ejecucion |
| `token.local.ps1`, `.env`, `*.secret` | **Secretos** (nunca al repositorio) |
| `data/resultados/*` (salvo `.gitkeep`) | Datos generados en ejecucion |
| `backup/` | Copias historicas |
| `extras/` | Demo anterior + PDF/capturas de trabajo |
| `Thumbs.db`, `desktop.ini`, `.DS_Store`, `.vscode/`, `.idea/` | Basura de sistema operativo y editores |

> El token del bot **no es un archivo que se suba**: en Render se configura como
> variable de entorno `BOT_TOKEN` en el panel del servicio.

### 4.3 Pasos sugeridos para confirmar los cambios
```powershell
git -C "D:\08 Semestre\Servicio Social\Mejora de telegram" status --short
git -C "D:\08 Semestre\Servicio Social\Mejora de telegram" add -A
git -C "D:\08 Semestre\Servicio Social\Mejora de telegram" commit -m "Reorganiza estructura, mueve quiz y externaliza contenido a JSON"
```
No se ejecuta ninguno de estos comandos sin pedirlo explicitamente.

---

## 5. Formato de las preguntas / respuestas por minijuego

Regla general: **los `.py` no contienen contenido**; cada juego lo lee de
`data/minijuegos/<id>.json` con `base.contenido("<id>")`. El campo `d` es la
**dificultad (1..3)**: `1` = facil, `2` = medio, `3` = dificil. El servidor
decide la respuesta correcta; al navegador solo se le manda lo publico.

Los textos admiten **LaTeX entre `$...$`** (se renderiza con KaTeX).

### 5.1 `deslizador.json` — Desliza el Atributo
```json
{ "casos": [ { "attr": "Es lineal", "tex": "y'' + 3y' + 2y = 0",
               "valor": true, "d": 1, "porque": "..." } ] }
```
- `attr`: propiedad que debe juzgarse (texto).
- `tex`: ecuacion en LaTeX.
- `valor`: `true`/`false` (si la propiedad es verdadera).
- `porque`: explicacion al calificar.

### 5.2 `memoria.json` — Memorama de Conceptos
```json
{ "cantidad_por_nivel": { "facil": 4, "medio": 5, "dificil": 6 },
  "pares": [ { "concepto": "Factor integrante",
               "mate": "\\mu(x) = e^{\\int P(x)\\,dx}", "d": 1 } ] }
```
- `pares[].concepto` / `.mate`: las dos caras que forman pareja.
- `cantidad_por_nivel`: cuantas parejas por tablero segun nivel.

### 5.3 `columnas.json` — Relacion de Columnas
```json
{ "tableros": [ [ { "izq": "y' + P(x)y = f(x)",
                    "der": "Factor integrante",
                    "porque": "Es lineal de primer orden.", "d": 1 } ] ] }
```
- Un **tablero** es una lista de filas; la columna derecha se baraja.
- `izq`/`der`: los dos lados a emparejar; `porque`: explicacion por fila.

### 5.4 `completar.json` — Completa la Forma Estandar
```json
{ "casos": [ { "enunciado": "... y' + P(x)y = Q(x)y^{\\,\\_\\_\\_}",
               "opciones": ["n", "2", "0"], "correcta": 0,
               "porque": "...", "d": 1 } ] }
```
- `enunciado`: el hueco se marca con `___`.
- `opciones`: alternativas; `correcta`: **indice** de la opcion valida.
- Las opciones se vuelven a barajar en cada partida.

### 5.5 `intruso.json` — El Intruso
```json
{ "conjuntos": [ { "pista": "Tres son lineales homogeneas",
                   "tarjetas": ["y' + 3y = 0", "y' - 5y = 0", "y' + x\\,y = 0", "y'' + y = 0"],
                   "intruso": 3, "porque": "La cuarta es de segundo orden.", "d": 1 } ] }
```
- `tarjetas`: 4 ecuaciones; `intruso`: **indice** de la que no encaja.
- Las tarjetas se barajan al mostrar.

### 5.6 `clasificador.json` — Clasificador Rapido
```json
{ "pozo": { "separable": ["y' = x^{2}y"], "exacta": ["y\\,dx + x\\,dy = 0"] },
  "etiquetas": { "separable": "Separable", "exacta": "Exacta" },
  "rondas": [ { "categorias": ["separable", "homogenea", "exacta"],
                "por_categoria": 6, "segundos": 45, "d": 1 } ],
  "explicar": { "separable": "$y' = f(x)g(y)$: se separan las variables." } }
```
- `pozo`: ecuaciones por categoria. Evita las ambiguas (dos categorias a la vez).
- `etiquetas`: nombre visible de cada categoria.
- `rondas`: que canastas salen, cuantas ecuaciones y cuantos segundos.
- `explicar`: aclaracion por categoria (se muestra al fallar).

### 5.7 `ordenar.json` — Ordena la Secuencia
```json
{ "secuencias": [ { "titulo": "ED separable",
                    "pasos": ["Identificar la forma $y' = f(x)g(y)$.", "..."], "d": 1 } ] }
```
- `pasos` va **en el orden correcto** (el servidor los baraja al mostrar).

### 5.8 `grafico.json` — El Grafico Falso
```json
{ "casos": [ { "ecuacion": "\\dfrac{dy}{dx} = y", "correcto": "bandas_y",
               "distractores": ["todo_horizontal", "verticales_x"],
               "porque": "...", "d": 1 } ] }
```
- `correcto`: tipo de campo de pendientes correcto.
- `distractores`: tipos incorrectos mostrados como opciones.
- Los `tipo` deben existir en `CAMPOS` de `webapp/js/juegos/grafico.js`
  (`todo_horizontal`, `constante`, `bandas_y`, `bandas_y_neg`, `verticales_x`,
  `creciente_x`, `circular`, `seno`, `pendiente_alta`, `divergente`).

### 5.9 `palabra.json` — La Palabra Oculta
```json
{ "letras_trampa": "ZQJXKW",
  "casos": [ { "pista": "Tipo de solucion con constantes ya fijadas.",
               "palabra": "PARTICULAR", "porque": "...", "d": 1 } ] }
```
- `palabra` en **MAYUSCULAS**; el teclado usa sus letras + trampas.
- `letras_trampa`: letras extra para el teclado virtual.

### 5.10 `globos.json` — Tiro al Blanco Teorico
```json
{ "segundos": 12,
  "rondas": [ { "instruccion": "Explota las soluciones de $y'' + y = 0$",
                "globos": [ { "tex": "\\sin x", "cumple": true },
                            { "tex": "e^{x}", "cumple": false } ],
                "porque": "...", "d": 1 } ] }
```
- `globos[].cumple`: si ese globo es una solucion valida.
- `segundos`: duracion de la ronda.

---

## 6. Formato del banco del quiz

El quiz vive en `data/minijuegos/quiz/` y tiene **dos tipos** de archivo.

### 6.1 `materias.json` — catalogo (que temas existen)
```json
{ "materias": [ {
    "id": "ed", "nombre": "Ecuaciones Diferenciales", "icono": "\uD83D\uDCD0",
    "descripcion": "...",
    "temas": [ { "id": "exactas", "nombre": "ED exactas", "resumen": "..." } ]
} ] }
```
- `temas[].id` debe coincidir con el campo `tema` del archivo de preguntas.
- Un tema sin archivo aparece como `disponible: false` (no rompe la app).

### 6.2 `quiz_tema_<tema>.json` — preguntas de un tema
```json
{
  "id": "quiz_exactas",
  "tema": "exactas",
  "titulo": "Quiz de ED exactas",
  "descripcion": "Condicion de exactitud, factor integrante y solucion implicita.",
  "preguntas": [
    {
      "id": "ex01",
      "p": "Antes de resolver $M\\,dx + N\\,dy = 0$, lo primero es...",
      "f": "",
      "opciones": ["Integrar $M$ respecto a $x$", "Comparar $\\partial M/\\partial y$ con $\\partial N/\\partial x$", "..."],
      "correcta": 1,
      "explicacion": "Primero se verifica la exactitud; si falla, se busca el factor integrante."
    }
  ]
}
```
Campos de cada pregunta:
| Campo | Obligatorio | Descripcion |
|---|---|---|
| `p` | si | Enunciado (admite LaTeX entre `$...$`) |
| `opciones` | si | Lista de 2 o mas alternativas |
| `correcta` | si | **Indice** (base 0) de la opcion correcta |
| `f` | no | Formula o dato que se muestra aparte |
| `explicacion` | recomendado | Por que esa es la correcta |
| `id`, `tipo`, `tag` | no | Metadatos para trazabilidad |

Reglas de limpieza que aplica `banco.py`: enunciado y opciones se recortan en
longitud; una pregunta sin `p`, con menos de 2 opciones o con `correcta` fuera
de rango **se descarta silenciosamente**. El nombre del archivo debe empezar por
`quiz_tema_` (si el JSON no trae `tema`, se deduce del nombre).

---

## 7. Como usar estos JSON como contexto en Gemini Pro

Cada archivo es **autodescriptivo** y usa las mismas claves que el codigo. Para
generar contenido nuevo:

1. Elige el minijuego (por ejemplo `data/minijuegos/intruso.json`) o el tema del
   quiz (`data/minijuegos/quiz/quiz_tema_*.json`).
2. Pega el JSON completo (o la seccion **5/6** de este documento) en el chat.
3. Pide mas entradas respetando el formato, por ejemplo:

   > Te paso el JSON del minijuego "El Intruso". Genera 6 conjuntos nuevos con
   > las mismas claves (`pista`, `tarjetas` de 4 elementos, `intruso` como
   > indice, `porque`, `d` de 1 a 3). Mantén LaTeX entre `$...$` y escapa las
   > barras invertidas con `\\` en el JSON. Devuelve **solo** el JSON valido.

4. Verifica con:
   ```powershell
   python -m app.nucleo.principal --comprobar
   ```
   La app valida el formato; si algo no cuadra, lo reporta y no arranca el juego.

Consejos:
- En JSON, cada `\` de LaTeX debe ir **doblado**: `\\partial`, `\\dfrac`, `\\,`.
- Respeta `d` (dificultad) para que el nivel facil/medio/dificil siga teniendo
  contenido.
- No dupliques `id` de pregunta dentro de un mismo archivo.

---

## 8. Verificacion (comandos usados)

```powershell
# 1. Valida quiz + los 10 minijuegos sin levantar el servidor
python -m app.nucleo.principal --comprobar

# 2. Pruebas de la API (respuestas, parejas, etc.)
python pruebas\test_api.py

# 3. Prueba del front real con jsdom (requiere "npm install" una vez)
node pruebas\smoke.js

# 4. Sintaxis de los modulos JS del front
Get-ChildItem webapp\js -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }

# 5. Arranque real (servidor en el puerto 8099, sin bot)
$env:PORT=8099; python lanzamiento\main.py
```

Todas deben terminar en `todo correcto` (Python) o sin errores (JS).

---

## 9. Como navega la app (rutas por hash)

La Mini App es **una sola pagina** (`webapp/index.html`). No hay varias URLs ni
recargas: se navega cambiando el **hash** de la URL (`#/...`). El router vive en
`webapp/js/navegacion.js` y la tabla de rutas se define en `webapp/js/app.js:148`
(`nav.definirRutas([...])`).

| Ruta (hash) | Vista | Que muestra |
|---|---|---|
| `#/inicio` | `vistas/inicio.js` | Portada (hub) con el boton **Practicar** |
| `#/juegos` | `vistas/juegos.js` | **Practicar**: quiz por tema (8) + 10 minijuegos |
| `#/tema/<materia>/<tema>` | `vistas/tema.js` | Configuracion del quiz de un tema y "Empezar" |
| `#/quiz` | `vistas/quiz.js` | Pregunta del quiz en curso / reporte final |
| `#/juego/<id>` | `vistas/juego.js` | Configuracion de un minijuego y "Jugar" |
| `#/partida/<id>` | `vistas/partida.js` | Ronda del minijuego en curso / reporte final |

Detalles:
- **Ruta por defecto**: si no hay hash, `navegacion.iniciar()` pone `#/inicio`
  (`navegacion.js:57`).
- **Boton "volver"**: aparece cuando la ruta tiene mas de un segmento
  (`navegacion.js:20`, `nivel()`), es decir, fuera de `#/inicio`.
- Una ruta que no existe muestra "Esa pantalla no existe." y vuelve a `inicio`
  (`app.js:105`).

El bot enlaza a estas rutas:
- Inicio: `WEBAPP_URL/` (sin hash).
- Practicar: `WEBAPP_URL/#/juegos` (`lanzamiento/bot.py:38`).

> **No se usa `?startapp=`.** La navegacion es por hash (`#/...`). Los ejemplos
> con `startapp` que aparecen en `docs/03`, `04`, `05`, `09` y `10` son material
> generico del tema, no describen esta app.

---

## 10. Cambiar de bot o de token

Cambiar de bot **no requiere tocar codigo**: no hay `chat_id` ni `@username`
hardcodeados. Solo hay que poner el token en **dos lugares** (el mismo valor en
ambos):

1. **Local** (correr en tu PC): `lanzamiento/token.local.ps1`
   ```powershell
   $TOKEN_FIJO = "123456:AAABBB..."
   ```
   Ese archivo esta en `.gitignore`, nunca se sube.
2. **Render** (desplegado): panel del servicio → *Environment* → `BOT_TOKEN`
   (declarado `sync: false` en `render.yaml`, se captura como secreto).

**Por que el mismo token en los dos sitios**: el bot hace *long polling* con el,
y el servidor HTTP valida la firma `initData` de cada usuario usando el mismo
valor (`app/nucleo/seguridad.py:52`). Si difieren, todos entran con 403.

Pasos para un bot nuevo:
1. En `@BotFather` → `/newbot` → nombre + username (termina en `bot`). Anota el
   token y el `@username`.
2. Pon el token en `lanzamiento/token.local.ps1` y en el secreto `BOT_TOKEN` de
   Render.
3. Listo. La URL publica se deduce sola en Render (`RENDER_EXTERNAL_URL`) y el
   boton de menu se reconfigura en cada arranque (`bot.py` → `post_init`).

Notas:
- **Un solo polling a la vez**: no corras el bot local y el de Render con el
  mismo token a la vez (Telegram responde 409).
- Si un token se filtro, `/revoke` en BotFather te da uno nuevo para el **mismo**
  bot (conserva `@username` y usuarios); `/newbot` crea uno distinto.
- Los enlaces `tu_bot` / `mi_bot` de los docs son **ejemplos**: nunca los lee el
  codigo. Sustituirlos por el `@usuario_real` es cosmetico y opcional.
