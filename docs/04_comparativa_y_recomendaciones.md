# 04. Comparativa y recomendaciones

> ¿Cuál opción se ajusta mejor a las necesidades del chatbot de Análisis
> Numérico? Aquí las comparaciones que importan para proponer a profesores.

## 4.1 Bot de texto vs Mini App

| Criterio | Bot de texto (actual) | Con Mini App |
|---|---|---|
| Fórmulas LaTeX | Renderizado depende de Telegram (marcado) | Rendistas con MathJax/KaTeX **dentro** de la app: siempre perfectas |
| Entrada del usuario | Libre (se tipea todo) | Botones y formularios con opciones (menos errores) |
| Flujos largos (examen de N preguntas) | Conversación tediosa | Página con pasos, barra de progreso, botón nativo |
| Tema claro/oscuro | Manual | Automático con `--tg-theme-*` |
| Login/identidad | ID del chat de Telegram | ID validado de Telegram, sin registro |
| Ranking/resultados | Texto | Gráficos, tablas, medallas |
| Complejidad de desarrollo | Baja | Media (HTML/CSS/JS + hosting) |
| Sin internet (plantel) | ✔ funciona 100% local | ⚠ requiere servir la web; con test server se puede usar localhost |

**Veredicto:** La Mini App no reemplaza el motor RAG (embeddings + FAISS +
Qwen), que sigue en la parte Python. La Mini App es la **capa de interfaz** que
mejora cómo el usuario le pregunta y consume respuestas.

## 4.2 Qué método de apertura usar para qué

| Método | Esfuerzo | Ideal para este proyecto | ¿Cumple? |
|---|---|---|---|
| **Keyboard button** | Muy bajo | Selector de tema/formulario que devuelve la elección al bot con `sendData` (sin servidor extra) | ★★★★★ |
| **Inline button** | Bajo | "Abrir quiz", "Ver apuntes", "Resultados" bajo un mensaje del bot | ★★★★★ |
| **Menu button** | Bajo | Acceso permanente "Inicio" que abre la app | ★★★★☆ |
| **Main Mini App** | Bajo | Perfil profesional con "Launch App" + previews (para presentación) | ★★★★☆ |
| **Direct link** | Bajo | Compartir `t.me/mi_bot/app?startapp=temaX` en grupos/avisos | ★★★☆☆ |
| **Inline mode** | Medio | Buscar apuntes desde cualquier chat y compartirlos | ★★★☆☆ |
| **Attachment menu** | Alto (solo test gratis) | No necesario ahora | ★☆☆☆☆ |

**Recomendación para empezar:** keyboard button (selector de tema) + menu
button + main mini app. Es lo que hace `@DurgerKingBot`, el bot de ejemplo
oficial.

## 4.3 Stack de desarrollo recomendado

| Capa | Opciones | Recomendación para el proyecto |
|---|---|---|
| Bot (Python) | `python-telegram-bot` (ya conocido), `aiogram`, `pyTelegramBotAPI` | **python-telegram-bot** (mismo ecosistema; ejemplos oficiales de WebApp) o aiogram |
| Mini App (frontend) | HTML/CSS/JS vanilla, React, Vue, Svelte | **HTML/JS vanilla** para el prototipo de prueba; React si el quiz crece |
| SDK de Mini Apps | `@tma.js/sdk`, `@twa-dev/sdk`, o **el script oficial `telegram-web-app.js`** | Script oficial (cero dependencias) para el demo |
| Componentes UI | `@telegram-apps/telegram-ui` (React), TGUI | Opcional (estilo Telegram nativo) |
| Hosting local (test) | `python -m http.server`, ngrok/cloudflared, **test server** | Test server + localhost (gratis, sin TLS) |
| Hosting producción | GitHub Pages, Vercel, Netlify, render.com | GitHub Pages / Vercel (gratis, HTTPS) |

### Plantillas que ya existen (ver documento 07)

- `Telegram-Mini-Apps/reactjs-template` (426★) — React + Vite + @tma.js/sdk.
- `zenhtml/telegram-mini-app` — React 19 + mock local en el navegador.
- `aiogram/examples/web_app` y `python-telegram-bot` `webappbot.py` — bot +
  webapp mínimo en Python.
- `tamimattafi/telegram-mini-app` — ejemplo completo bot+app con telegraf+React.

## 4.4 Riesgos / limitaciones honestas

| Riesgo | Mitigación |
|---|---|
| En producción la Mini App **exige HTTPS** | Durante el desarrollo se usa el **test server** (permite `localhost`). Para demo pública: GitHub Pages/Vercel gratis. |
| Bot corre 100% offline en plantel | La app se puede servir desde una laptop local con el **entorno de test**; para plantel sin internet no se recomienda fullscreen/sensores. Si hace falta producción offline, evaluar servir HTTPS con certificado local (más complejo). |
| `sendData` solo funciona desde keyboard button y sin datos del usuario | Usar inline button cuando se necesite identidad del usuario (treo `answerWebAppQuery`). |
| Datos de `initData` manipulables | Validar SIEMPRE con HMAC en el backend (documento 08). |
| No hay App Store "oficial" garantizada | El Mini App Store es por invitación/feature; no bloquea usar Mini Apps normales. |

## 4.5 ¿Qué se ajusta mejor a las necesidades? — Resumen

1. **Corto plazo (demostración):** Mini App informativa + quiz de 5 preguntas
   con `sendData`, abierta desde botón de teclado y menú.
2. **Mediano plazo:** Navegador de apuntes con fórmulas (KaTeX) que llama al
   RAG existente y muestra la respuesta con la fuente citada.
3. **Presentación profesional:** Main Mini App con "Launch App" y previews en
   el perfil del bot para que los profesores lo prueben en 1 tap.