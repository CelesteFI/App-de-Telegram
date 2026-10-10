# 05. Guía: Bot de prueba con Mini Apps en minutos (sin chatbot)

> Objetivo: crear un **bot tonto** que NO responda preguntas — solo sirva para
> abrir y probar Mini Apps. Al final tendrás un bot con:
> - botón de teclado que abre una Mini App y devuelve datos al bot,
> - botón inline que abre la Mini App,
> - botón de menú que abre la app,
> - perfil con "Launch App" (Main Mini App).
>
> Tiempo estimado: **30–60 minutos**. Costo: $0.

---

## Paso 0. Decide cómo probar: entorno de TEST vs producción

### Opción A — Test server (RECOMENDADO para empezar, gratis y sin HTTPS)

- Entorno separado de producción; los bots de test **permiten `http://localhost`**
  (no hacen falta dominios ni HTTPS).
- Cómo entrar a la cuenta:
  - **Escritorio (Windows):** menú lateral de Telegram → sobre "Añadir cuenta",
    `Shift + Alt + click derecho` → **"Test Server"**.
  - **Mobile iOS:** encendido de ajustes ×10 → agregar cuenta → *Test*.
  - **Mobile Android:** Ajustes → "..." → *Switch to Test Server*.
- Ahí creas una **cuenta nueva** y un **bot nuevo** con `@BotFather` (el del
  test server existe dentro de esa cuenta).
- El API de test se llama así: `https://api.telegram.org/bot<TOKEN>/test/METHOD`.
  Las librerías (`python-telegram-bot`, `aiogram`) permiten prefijarlo.

> ⚡ Para probar en el **celular real o en PC** contra `localhost`,
> abre el bot en la misma cuenta de test y apunta la Mini App a
> `http://localhost:8080` (en PC) o a la IP local de tu laptop (`http://192.168.x.x:8080`)
> — en test server HTTP no es requerido TLS.

### Opción B — Producción (para mostrar a profesores fuera del test)

- Necesitas un **URL HTTPS público**. Opciones gratis:
  - `ngrok http 8080` (túnel temporal; útil para demos en el momento).
  - `cloudflared tunnel --url http://localhost:8080` (igual).
  - GitHub Pages / Vercel / Netlify (estático, permanente).
- BotFather solo acepta URL **HTTPS** en producción.

---

## Paso 1. Crear el bot (2 min)

1. Entrar a `@BotFather` (en la cuenta elegida arriba).
2. Comando `/newbot` → nombre, username (termina en `bot`).
3. Guarda el **token** (lo usará `demo/bot.py`).
4. (Opcional para Main Mini App): `/mybots` → tu bot → Bot Settings →
   *Configure Mini App* → *Enable Mini App* → pega la URL (en test:
   `http://localhost:8080`) y define un corto `?short_name` (p. ej. `start`).

---

## Paso 2. Servir la Mini App (2 min)

En una terminal, dentro de `demo/webapp/`:

```powershell
python -m http.server 8080
```

- En el navegador abre `http://localhost:8080` para ver que carga.
- Si pruebas con celular en test server: sive la carpeta y abre
  `http://192.168.X.X:8080` (usa la IP local de tu PC; o crea una mini app
  apuntando a esa IP).
- Para demostración en producción: `ngrok http 8080` y usar el enlace `https`.

---

## Paso 3. Correr el bot de prueba (3 min)

```powershell
pip install python-telegram-bot
$env:BOT_TOKEN = "123456:ABC..."   # tu token
$env:WEBAPP_URL = "http://localhost:8080"   # o el de ngrok / IP
python demo\bot.py
```

El bot responde:

| Comando | Qué hace |
|---|---|
| `/start` | Envía **botón de teclado** "Abrir selector" → Mini App con `sendData` (prueba el Keyborad Button) |
| `/inline` | Envía **botón inline** "Abrir panel" → Mini App con identidad de usuario (prueba el Inline Button) |
| `/menu` | Configura el **botón de menú** del chat para abrir la app |
| `/data` | Muestra el último dato recibido desde la Mini App |

Todo mensaje de texto recibido se responde con un "echar" para que veas en la
consola qué llega (`message.web_app_data`).

### Qué debe observarse

1. Al tocar "Abrir selector" se abre la Mini App; eliges un tema y tocas
   "Enviar" → la app devuelve el JSON al bot (aparece en consola y al
   enviar `/data`).
2. Al tocar "Abrir panel" (inline) la app muestra **tu nombre de Telegram**
   (significa que recibió `initData.user`) y los colores de tu tema.
3. El `/menu` pone el botón debajo del cuadro de texto para abrir la app
   siempre.

---

## Paso 4. Configurar el botón de menú SIN código (opcional)

En BotFather: `/setmenubutton` → selecciona el bot → botón de texto "Abrir app"
→ URL de la Mini App. O con el código del bot (comando `/menu`).

## Paso 5. Probar las demás formas (rápidas)

- **Main Mini App / direct link:** agrega un botón en el mensaje de inicio con
  el enlace `https://t.me/tu_bot?startapp=tema5`
  (en el chat de test, si está activo) o `https://t.me/tu_bot/inicio`.
- **Pasar parámetro:** en la Mini App, `Telegram.WebApp.initDataUnsafe.start_param`
  o el GET `tgWebAppStartParam` → ya se puede pre-seleccionar el tema.

---

## Paso 6. Depurar (si algo no carga)

| Síntoma | Solución |
|---|---|
| Pantalla de Telegram que no carga la app | URL no accesible: revisa que el servidor http corra y el puerto esté bien; si es producción, debe ser HTTPS |
| `ReferenceError: Telegram is not defined` | Abriste la URL en un navegador normal (fuera de Telegram). Ábrela **dentro** del bot (o usa el modo debug del repo `zenhtml/telegram-mini-app`) |
| En Android no se ve bien | Habilita WebView debug: Ajustes → mantener presionado "Versión" ×2 → Enable Web View Debug; luego `chrome://inspect` |
| En iOS | Ajustes → encendido ×10 → *Allow Web View Inspection*; conecta USB y depura desde Safari → Develop |
| En escritorio | Usa Telegram Desktop **Beta** → Ajustes → Avanzado → Experimentales → *Enable WebView Inspection* → click derecho en la app → Inspeccionar |
| El bot no responde | Token mal puesto, o el bot está en el test server pero estás hablando en producción (y viceversa) |

---

## Resumen de comandos (scripts incluidos)

```powershell
# 1) Mini App
python -m http.server 8080            # (en demo/webapp)

# 2) Bot
$env:BOT_TOKEN  = "TOKEN_DE_BOTFATHER"
$env:WEBAPP_URL = "http://localhost:8080"
python demo\bot.py

# 3) Producción opcional
ngrok http 8080                        # copia la URL https y úsala como WEBAPP_URL
```

> 💡 Si quieres **cero instalación de Python**, la Mini App (HTML/JS) se puede
> abrir igualmente: solo necesitas que BotFather apunte a un servidor donde
> esté `index.html`. El bot Python solo aporta los botones y la recepción de
> datos.