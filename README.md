# Repaso de Ecuaciones Diferenciales — Mini App de Telegram

Aplicación individual de repaso para Ecuaciones Diferenciales: 8 temas con quiz
y 10 minijuegos conceptuales, **todo junto en la pantalla "Practicar"**
(el quiz es un juego más, no una sección aparte). Cada persona entra con su
propia identidad de Telegram, así que sus marcas y su historial quedan
separados sin códigos ni cuentas.

La versión anterior del chatbot (Análisis Numérico, sesiones tipo Kahoot) sigue
intacta en `extras/demo/`.

## Arrancar

```powershell
.\lanzamiento\run.ps1          # app + túnel + bot (basta con esto)
```

> Si Windows dice que el script "no está verificado" o no te deja correrlo,
> es el ExecutionPolicy: ya quedó en `RemoteSigned` para tu usuario, y además
> tienes `lanzamiento\run.bat` (doble clic) que hace lo mismo sin pedir nada.

El token del bot ya **no** vive en `run.ps1`: se toma de
`lanzamiento\token.local.ps1` (ignorado por git), de `$env:BOT_TOKEN` o del
parámetro `-BotToken`. Basta con crear
`lanzamiento\token.local.ps1` con una línea: `$TOKEN_FIJO = "123456:AAABBB..."`.
El modo de pruebas en navegador viene **encendido por defecto**: en Telegram
se valida tu identidad real y en el navegador entras como Invitado para probar
los juegos. Solo con `.\lanzamiento\run.ps1 -ExigirIdentidad` se apaga ese modo.

Por defecto el túnel es **Cloudflare Tunnel** (`cloudflared`), que da una URL
HTTPS **sin pantalla de aviso**, ideal para Telegram. La primera vez se
descarga solo (una sola vez) a `lanzamiento\cloudflared.exe`. Si prefieres
ngrok: `.\lanzamiento\run.ps1 -Tunel ngrok`. Para probar solo en el navegador:
`.\lanzamiento\run.ps1 -SinTunel`.

La Mini App carga **todo desde el mismo servidor** (carpeta `webapp/vendor/`):
ya no depende de CDN externos, así que abre igual en el navegador, en la red
del salón y dentro del WebView de Telegram. Si algo no responde, la propia app
muestra un aviso con botón **Reintentar** en vez de quedarse cargando.


## Qué hay dentro

| Ruta | Contenido |
|---|---|
| `lanzamiento/` | Arranque: `run.ps1`, `run.bat`, `main.py`, `bot.py` y el token local. |
| `app/nucleo/` | Servidor HTTP, autenticación de Telegram, configuración y almacenamiento. |
| `app/minijuegos/` | Los diez minijuegos y sus contratos (`rondas`, `publico`, `califica`). |
| `app/minijuegos/quiz/` | Intentos de quiz, calificación, reportes y récords. |
| `webapp/` | La aplicación: vistas, motor de juegos y CSS. |
| `data/minijuegos/*.json` | Contenido de cada minijuego (un archivo por juego). |
| `data/minijuegos/quiz/` | `materias.json` y un `quiz_tema_*.json` por tema (12 preguntas c/u). |
| `data/resultados/` | Reportes y marcas por usuario (se crea sola). |
| `pruebas/` | Pruebas de API (Python) y de interfaz (Node). |
| `docs/` | Documentación del proyecto (contexto en `00_sesion.md`; estructura en `14_estructura_y_contenido.md`). |
| `extras/` | La app anterior (`demo/`), PDF y capturas de trabajo (no se sube). |

## Los diez minijuegos

| Juego | Qué se practica |
|---|---|
| Desliza el Atributo | Reconocer si una ED es lineal y homogénea. |
| Memorama de Conceptos | Emparejar cada concepto con su fórmula. |
| Relacion de Columnas | Emparejar ED con su nombre y método. |
| Completa la Forma Estandar | Reconocer la forma canónica de cada método. |
| El Intruso | Detectar la ED que no pertenece al grupo. |
| Clasificador Rapido | Clasificar varias ED bajo tiempo. |
| Ordena la Secuencia | Poner en orden los pasos de un método. |
| El Grafico Falso | Reconocer qué curva cumple la ED. |
| La Palabra Oculta | Escribir el nombre del concepto letra a letra. |
| Tiro al Blanco Teorico | Identificar entre varias ED cuáles comparten estructura. |

Cada juego tiene tres niveles y de 3 a 15 rondas.

## Cómo se califica

La respuesta correcta se decide **siempre en Python**. El navegador recibe la
ronda ya mezclada y sin solución, y solo manda lo que el jugador eligió. Los
minijuegos con tiempo o con emparejamiento tienen un caso especial:

- El memorama manda `POST /api/minijuegos/pareja` porque el tablero llega sin
  la solución; el servidor responde si dos cartas forman pareja.
- El tiempo límite vive en el cliente, pero la ronda termina al responder y el
  puntaje lo calcula el servidor.

## Pruebas

```powershell
python pruebas\test_api.py    # API por HTTP real: identidad, quiz, 10 juegos
npm install                   # una vez, trae jsdom
node pruebas\smoke.js         # la interfaz real contra el backend real
python -m app.nucleo.principal --comprobar
```

Las dos primeras pruebas escriben sus resultados en una carpeta temporal y la
borran al terminar: `data/resultados/` queda como está.

## Publicar

Telegram exige HTTPS. Para una prueba rápida, `run.ps1` levanta un túnel
(Cloudflare por defecto, ngrok como respaldo) y pasa la URL al bot. El túnel
cambia de URL en cada corrida y depende de tu PC encendida, así que para algo
permanente conviene un servidor externo.

### Desplegar en Render (plan free)

`lanzamiento/main.py` levanta en **un solo proceso** el servidor de la Mini App
y el bot; en Render la URL pública se toma sola de `RENDER_EXTERNAL_URL`.

1. Sube el repo a GitHub (abajo; el token **no** se incluye).
2. En https://render.com: **New + Blueprint**, conecta el repositorio y aplica
   el `render.yaml`. Render pide el secreto **BOT_TOKEN** (el de @BotFather);
   el resto ya queda configurado.
3. Al terminar, la app vive en `https://<nombre>.onrender.com` y el bot apunta
   solo a esa URL.

Ojo con el plan free: el servicio **duerme a los 15 min** sin tráfico (y el bot
queda offline). Se resuelve con un pinger externo cada 10 min (por ejemplo
https://uptimerobot.com o https://cron-job.org) apuntando a
`https://<nombre>.onrender.com/api/config`. No uses `/robots.txt`: ese no
despierta al servicio. El plan free da 750 horas de instancia al mes, justo
para **un** servicio encendido.

### Subir a GitHub

```powershell
git add -A
git commit -m "Mini App de repaso lista para desplegar"
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

`lanzamiento/token.local.ps1`, `lanzamiento/cloudflared.exe`, `node_modules/`,
`logs/`, `extras/` y `backup/` están en `.gitignore`: no se suben.

## Documentación del proyecto

En `docs/` viven los documentos `01_` a `11_` (contexto de la propuesta
original, seguridad de `initData`, comparación de bots, presentación),
`00_sesion.md` (bitácora y contexto del trabajo por sesiones) y
`14_estructura_y_contenido.md` (estructura final y formato de los bancos de
preguntas). Siguen vigentes como material de referencia.