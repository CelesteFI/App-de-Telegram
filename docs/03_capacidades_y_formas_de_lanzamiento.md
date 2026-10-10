# 03. Capacidades técnicas y formas de lanzamiento

> Basado en https://core.telegram.org/bots/webapps (Bot API 6.x → 10.x, 2026).

## 3.1 Cómo se "conecta" una Mini App

En el `<head>` de tu página, antes de cualquier otro script:

```html
<script src="https://telegram.org/js/telegram-web-app.js?63"></script>
```

Esto crea el objeto `window.Telegram.WebApp` con campos y métodos clave:

| Campo / método | Descripción |
|---|---|
| `initData` | Cadena cruda de datos (para **validar en el servidor**) |
| `initDataUnsafe` | Objeto ya parseado (**no confiar** hasta validar) |
| `themeParams` | Colores del tema actual (`bg_color`, `text_color`, etc.) + variables CSS `var(--tg-theme-...)` |
| `colorScheme` | `"light"` o `"dark"` |
| `platform` / `version` | Dónde corre y qué versión del Bot API soporta |
| `isExpanded`, `viewportStableHeight`, `safeAreaInset` | Medidas de la ventana (para UI móvil) |
| `MainButton`, `SecondaryButton` | Botones nativos de la barra inferior |
| `BackButton` | Botón "atrás" del encabezado |
| `SettingsButton` | Ítem de configuración del menú contextual |
| `HapticFeedback` | Vibración táctil (éxito/error/impacto) |
| `CloudStorage`, `DeviceStorage`, `SecureStorage` | Almacenamiento de datos |
| `BiometricManager` | Biometría del dispositvo |
| `LocationManager` | GPS con permisos |
| `Accelerometer`, `Gyroscope`, `DeviceOrientation` | Sensores (juegos, físico) |
| `requestFullscreen()`, `lockOrientation()`, `addToHomeScreen()` | Fullscreen, orientación, acceso directo al home |
| `showAlert()`, `showConfirm()`, `showPopup()`, `showScanQrPopup()` | Diálogos nativos, popups, lector QR |
| `readTextFromClipboard()` | Leer portapapeles (solo attachment menu) |
| `openInvoice()` | Abrir pago/factura |
| `requestContact()`, `requestWriteAccess()`, `requestChat()` | Pedir permiso de contacto, escritura, chat |
| `sendData(data)` | Enviar datos al bot (solo botón de teclado, máx 4096 bytes) |
| `switchInlineQuery(query)` | Volver al modo inline |
| `shareToStory()`, `shareMessage()`, `downloadFile()` | Compartir y descargar |
| `setEmojiStatus()`, `requestEmojiStatusAccess()` | Estado de emoji |
| `ready()`, `expand()`, `close()` | Ciclo de vida |
| `onEvent(eventType, handler)`, `offEvent(...)` | Escuchar eventos |

### Variables CSS que Telegram expone (para temas automáticos)

```
--tg-theme-bg-color           --tg-theme-text-color
--tg-theme-hint-color         --tg-theme-link-color
--tg-theme-button-color       --tg-theme-button-text-color
--tg-theme-secondary-bg-color --tg-theme-header-bg-color
--tg-theme-accent-text-color  --tg-theme-section-bg-color
--tg-viewport-height          --tg-viewport-stable-height
```

### Eventos principales (`onEvent`)

`themeChanged`, `viewportChanged`, `mainButtonClicked`, `secondaryButtonClicked`,
`backButtonClicked`, `settingsButtonClicked`, `popupClosed`, `invoiceClosed`,
`qrTextReceived`, `clipboardTextReceived`, `writeAccessRequested`,
`contactRequested`, `fullscreenChanged`, `safeAreaChanged`, `homeScreenAdded`,
`locationManagerUpdated`, `accelerometerChanged`, `gyroscopeChanged`,
`shareMessageSent`, `fileDownloadRequested`, `emojiStatusSet`,
`biometricAuthRequested`, `activated`, `deactivated`, etc.

> Regla de oro de diseño: usar las variables `--tg-theme-*` y llamar
> `Telegram.WebApp.ready()` lo antes posible para ocultar la pantalla de carga.

## 3.2 Las 7+ formas de abrir una Mini App

### 1. Botón de teclado (Keyboard Button) — la más simple

```python
from telegram import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
reply = ReplyKeyboardMarkup.from_button(
    KeyboardButton(text="Abrir Mini App",
                   web_app=WebAppInfo(url="https://mi-host/index.html"))
)
```

- Se abre desde un **botón de teclado de respuesta**.
- La Mini App puede devolver datos al bot con `Telegram.WebApp.sendData(data)`
  como **mensaje de servicio** (`message.web_app_data.data`), máx **4096 bytes**.
- **Ideal para**: formularios de entrada (seleccionar tema, fechas, opciones),
  sin servidor externo de por medio.

### 2. Botón inline (Inline Keyboard Button) — la más usada

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
reply = InlineKeyboardMarkup([[InlineKeyboardButton(
    text="Abrir Mini App",
    web_app=WebAppInfo(url="https://mi-host/index.html"))]])
```

- Se abre desde un **botón bajo un mensaje**. Recibe datos del usuario
  (`id`, nombre, username, idioma) + `query_id`.
- El bot responde con **`answerWebAppQuery`** para enviar un mensaje en nombre
  del usuario y cerrar la app.
- **Ideal para**: servicios completos (lo que usa `@DurgerKingBot`).

### 3. Botón de menú del chat (Menu Button)

- Se configura con `setChatMenuButton` (API) o `@BotFather` → `/setmenubutton`.
- Abre la Mini App igual que el inline; es **el acceso permanente** del bot.
- Con `setChatMenuButton` se puede personalizar por usuario/idioma.

### 4. Main Mini App (botón "Launch app" en el perfil)

- Se configura en `@BotFather` → `/mybots` → Bot Settings → Configure Mini App.
- Aparece botón **"Launch App"** + previews (video/imágenes) en el perfil.
- Abre por enlace directo: `https://t.me/mi_bot?startapp` o `?startapp=cmd`.
- Con `chat_type`/`chat_instance` soporta uso compartido en grupos
  (pizarras, pedidos, multijugador).
- Botones con la app "main" + pagos en Stars pueden aparecer en el
  **Mini App Store**.

### 5. Modo inline

- Botón "Switch to Mini App" sobre los resultados de `answerInlineQuery`.
- La app vuelve a inline con `Telegram.WebApp.switchInlineQuery(query)`.
- No tiene acceso al chat; útil para búsquedas/compartir contenido.

### 6. Enlace directo (Direct Link)

- `https://t.me/mi_bot/app` (o `?app`; también `?startapp=cmd&mode=compact`).
- Se puede pegar en **cualquier chat**. Sabe el chat de origen
  (`chat_type`/`chat_instance`). No puede enviar mensajes él mismo.

### 7. Menú de adjuntos (Attachment Menu)

- Bot se añade al menú "clip"/adjuntar de cualquier chat.
- **Producción: solo para anunciantes grandes** (+50k usuarios / Ads).
- **Entorno de TEST: gratis para todos** (en `@BotFather` del test server,
  comando `/setattach`).
- Links: `https://t.me/mi_bot?startattach` y
  `https://t.me/usuario?attach=mi_bot`.

### 8 (bonus). Solicitudes de unión a chats (chat join requests)

- Si el bot es "guard bot" de un grupo, puede abrir la Mini App a quien pide
  unirse (`sendChatJoinRequestWebApp` + `answerChatJoinRequestQuery`).

## 3.3 Bot API recomendado para el proyecto

- **Bot API 6.0+** ya permite lo esencial (WebAppInfo, menú button, sendData).
- **Bot API 8.0+** agrega fullscreen, home shortcuts, GPS, sensores,
  suscripciones con Stars (nov 2024).
- **9.5+** (mar 2026) `iconCustomEmojiId`; **9.6** (abr 2026) `requestChat`;
  **10.1** (jun 2026) `chat_join_request_query_id`.
- En el cliente se consulta `Telegram.WebApp.isVersionAtLeast("8.0")` para
  saber si una característica está disponible antes de usarla.

## 3.4 Qué recibe la Mini App al abrirse (`initData`)

Si se abrió desde botón inline / menú / main app / enlace / attachment:

```jsonc
{
  "query_id": "...",          // para answerWebAppQuery
  "user": { "id", "first_name", "last_name", "username", "language_code",
            "is_premium", "photo_url", ... },
  "chat": { "id", "type", "title", "username" },
  "chat_type": "private",     // solo enlaces directos
  "chat_instance": "...",     // solo enlaces directos
  "start_param": "tema5",     // valor de ?startapp=
  "auth_date": 1725000000,    // época Unix
  "hash": "...",              // para validar (ver documento 08)
  "signature": "..."          // firma Ed25519 opcional
}
```

Desde **botón de teclado** los campos de usuario llegan **vacíos** (es la
limitación de ese método). Desde **inline** tampoco hay `user`.

## 3.5 Ciclo de vida recomendado en el código de la app

```js
Telegram.WebApp.ready();          // 1) avisar que ya cargó
Telegram.WebApp.expand();         // 2) expandir a máxima altura
// 3) suscribirse a eventos de tema / ventana
Telegram.WebApp.onEvent('themeChanged', () => aplicar(Telegram.WebApp.themeParams));
// 4) usar MainButton / SecondaryButton para la acción principal
Telegram.WebApp.MainButton.setText('Enviar').show()
  .onClick(() => { Telegram.WebApp.sendData('{"tema":"biseccion"}'); });
```