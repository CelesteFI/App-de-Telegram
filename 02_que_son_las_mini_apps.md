# 02. ¿Qué son las Telegram Mini Apps?

## Terminología (importante: ha cambiado con el tiempo)

| Término | Qué significa |
|---|---|
| **Web App (WebApp)** | Nombre **antiguo** (Bot API 6.0, abril 2022). Aún aparece en muchos tutoriales, librerías y en el API (`WebAppInfo`, `web_app`). |
| **Mini App (MiniApp)** | Nombre **actual** (desde 2024–2025). Es lo mismo: una web que corre dentro de Telegram. |
| **Global App** | Nombre nuevo que Telegram usa para Mini Apps que además funcionan fuera de Telegram (web normal). |

En este documento se usa **Mini App** = Web App. Son equivalentes.

## ¿Qué es exactamente una Mini App?

Una Mini App es:

1. Una página web normal (HTML/CSS/JS, o un framework como React/Vue) que
   **no necesita instalarse**: se abre dentro de la app de Telegram.
2. Al abrirse, Telegram inyecta un objeto `window.Telegram.WebApp` con:
   - **`initData`**: datos del usuario y de la sesión (para validar en tu
     servidor que los datos sí vienen de Telegram — ver `08_seguridad...`).
   - **Tema** (colores claros/oscuros del usuario) y medidas de la ventana.
   - **Botones nativos** (MainButton, BackButton, SettingsButton).
   - Métodos para: vibrar (haptics), popups, QR, biometría, GPS, acelerómetro,
     compartir a historias, descargar archivos, pagos, etc.
3. Se sirve desde un **URL HTTPS** (en producción). En el **entorno de test** de
   Telegram se puede usar `http://localhost`.

En la práctica: el bot se queda como "anfitrión" (envía botones/links) y la
experiencia completa vive en el navegador embebido.

## ¿Por qué Telegram dice que "reemplazan sitios web"?

De `core.telegram.org/bots#replace-entire-websites`:

> "Telegram bots can host Mini Apps built with JavaScript. This allows for
> infinitely flexible interfaces that can power everything from online stores
> to arcade games. Unlike websites, bots support **seamless authorization**
> and notifications through Telegram out of the box."

Traducción libre de las ventajas frente a un sitio web normal:

| Ventaja | Sitio web normal | Mini App |
|---|---|---|
| Registro / login | Necesitas correo+contraseña, OAuth, etc. | **Ya está autenticado** (Telegram te da el `user id` validado) |
| Notificaciones | Push APIs complicadas | Telegram puede enviar mensajes al usuario automáticamente |
| Llegada al usuario | Necesitas que visiten tu URL | El usuario ya vive en Telegram; un tap y entran |
| Pagos | Integrar un gateway externo completo | Pagos integrados (Telegram Stars / Google Pay / Apple Pay) |
| Instalación | — | **Cero instalación**, y puede añadirse al home de Android |

Es decir: el "mini sitio web" **dentro** de Telegram elimina la fricción de
login, alcance y notificaciones que tiene un sitio web tradicional.

## Lo que puede hacer una Mini App hoy (Bot API 8.0+, 2024; 9.x, 2025–2026)

- **Pantalla completa** (fullscreen) vertical y horizontal.
- **Accesos directos al home** del teléfono (como una app instalada).
- **Localización (GPS)** y sensores: acelerómetro, giroscopio, orientación.
- **Almacenamiento**: en la nube (CloudStorage), en el dispositivo
  (DeviceStorage), segura (SecureStorage) y biometría.
- **Compartir**: mensajes, historias, archivos (descarga nativa).
- **Emoji status** del usuario.
- **Pagos y suscripciones**: Telegram Stars, facturas, subscriptions.
- **Notificaciones**: permisos de escritura para que el bot le escriba.
- **Teclado, tema, ventana**: control de colores de cabecera/fondo, botones
  nativos, haptic feedback.
- **Validación de datos** con HMAC-SHA256 y firma Ed25519 (ver documento 08).

## Estados de la industria (10+ millones de bots)

- Telegram reporta **más de 10 millones de bots** activos.
- Los Mini Apps populares (juegos como *Hamster Kombat*, tiendas, apps
  educativas tipo Flashcards, Quizzes) alcanzan **decenas de millones** de
  usuarios sin instalar nada.
- Existe un **Mini App Store**; Telegram promueve bots que habilitan Main Mini
  App + pagos en Stars.

---

## Conclusión

Una "Mini App" = "mini sitio web embebido en Telegram, con login ya hecho y
temas/UX nativos". Es la evolución oficial del bot por texto: cuando la
interacción requiere botones, formularios o visuales, la Mini App es la vía.
Para el chatbot del proyecto, esto significa poder pasar de "responde con
texto" a "ofrece una experiencia interactiva de estudio".