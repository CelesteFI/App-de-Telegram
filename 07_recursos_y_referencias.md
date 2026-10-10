# 07. Recursos y referencias

## Documentación oficial (fuentes primarias)

| Recurso | URL |
|---|---|
| Guía de Bots para desarrolladores | https://core.telegram.org/bots |
| "Replace Entire Websites" (sección de Mini Apps) | https://core.telegram.org/bots#replace-entire-websites |
| Telegram Mini Apps (documentación completa) | https://core.telegram.org/bots/webapps |
| Telegram Bot API (referencia) | https://core.telegram.org/bots/api |
| Bot API changelog (8.0+, 9.x, 10.x) | https://core.telegram.org/bots/api-changelog |
| Bot Features (guía extendida) | https://core.telegram.org/bots/features |
| Payments con Telegram Stars | https://core.telegram.org/bots/payments-stars |
| Blog "Fullscreen, Home Screen Shortcuts & More" (Bot API 8.0) | https://telegram.org/blog/fullscreen-miniapps-and-more |
| Ejemplos y códigos oficiales | https://core.telegram.org/bots/samples |

## Bots de ejemplo para probar

- **@DurgerKingBot** — la Mini App demo oficial (hamburguesería: menú, carrito,
  pagos). Referencia de todo lo posible.
- **@GMailBot**, **@GitHubBot**, **@Bing**, **@YouTube**, **@wiki** — bots con
  integración de servicios.
- **@PremiumBot** — comprar Stars (para probar pagos).

## Librerías de bots (Python / JS)

- **python-telegram-bot** (Python) — ejemplo oficial `webappbot.py`
  https://docs.python-telegram-bot.org/en/v21.6/examples.webappbot.html
- **aiogram** (Python asyncio) — ejemplo WebApp
  https://github.com/aiogram/aiogram/blob/dev-3.x/examples/web_app/main.py
  y utilidad `check_webapp_signature`
  https://docs.aiogram.dev/en/dev-3.x/utils/web_app.html
- **telegraf** (Node.js) — https://telegraf.js.org
- **Telegram.Bot** (C#) — ejemplo MiniApp completo con webapp demo y
  DurgerKing https://github.com/TelegramBots/Telegram.Bot.Examples

## SDK / plantillas para la Mini App

- **Script oficial** (cero dependencias):
  `https://telegram.org/js/telegram-web-app.js`
- **@tma.js/sdk** (TypeScript, oficial de la comunidad):
  https://docs.telegram-mini-apps.com/ · https://github.com/Telegram-Mini-Apps
- **Plantilla oficial de la comunidad React + Vite + TMA.js** (426★):
  https://github.com/Telegram-Mini-Apps/reactjs-template
- **zenhtml/telegram-mini-app** — React 19 + mock en navegador (prueba sin
  Telegram) https://github.com/zenhtml/telegram-mini-app
- **Imolatte/telegram-miniapp** — demo con Tailwind + REST API
  https://github.com/Imolatte/telegram-miniapp
- **tamimattafi/telegram-mini-app** — Graz completo bot + app (telegraf+React)
  https://github.com/tamimattafi/telegram-mini-app
- **nikandr-surkov/telegram-miniapp-quickstart** — Next.js + Stars payments
  https://github.com/nikandr-surkov/telegram-miniapp-quickstart
- **TelegramUI** — componentes React con estilo Telegram nativo
  https://github.com/telegram-mini-apps-dev/TelegramUI
- **Parzibyte (español)** — tutorial bot + mini app con `sendData`
  https://parzibyte.me/blog/posts/bot-telegram-mini-app

## Testing / herramientas

- **Test server de Telegram** (cómo acceder) — ver documento 05 y
  https://docs.telegram-mini-apps.com/platform/test-environment
- **ngrok** — https://ngrok.com
- **cloudflared** — https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads
- **GitHub Pages** (hosting estático gratis) — https://pages.github.com
- **Vercel / Netlify** — https://vercel.com · https://www.netlify.com
- **Debug en Android** (`chrome://inspect`), **iOS (Safari Develop)**,
  **Telegram Desktop Beta** (webview inspection) — detalles en documento 05.

## Conceptos clave que conviene citar

- `WebAppInfo` (objeto del Bot API): https://core.telegram.org/bots/api#webappinfo
- `WebAppInitData` / `WebAppUser`: https://core.telegram.org/bots/api#webappinitdata
- `setChatMenuButton`: https://core.telegram.org/bots/api#setchatmenubutton
- `answerWebAppQuery`: https://core.telegram.org/bots/api#answerwebappquery
- Telegram Stars (monetización): https://core.telegram.org/bots/payments-stars