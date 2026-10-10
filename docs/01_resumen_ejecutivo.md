# 01. Resumen Ejecutivo (para profesores)

> Versión corta del trabajo: qué se investigó, qué se propone y qué se necesita.

## Qué se investigó

Telegram permite que los bots abran **Mini Apps**: aplicaciones web
(HTML + CSS + JavaScript) que se ejecutan **dentro de la propia app de
Telegram**, con autenticación de usuario "invisible" (sin pedir correo ni
contraseña), temas claros/oscuros automáticos y soporte para pagos,
notificaciones y compartir contenido.

La documentación oficial las describe como capaces de **"reemplazar
completamente un sitio web"** (`core.telegram.org/bots#replace-entire-websites`),
y publica una guía dedicada en `core.telegram.org/bots/webapps`.

## Por qué es relevante para el proyecto

El chatbot actual (Análisis Numérico UNAM) responde por texto con formato
Markdown/LaTeX. Con una Mini App se puede:

- Renderizar **fórmulas matemáticas** bonitas (TeX dentro de la app) sin
  depender del renderizado de Telegram.
- Ofrecer un **formulario de selección de tema** (Botón: "¿De qué tema quieres
  preguntar?") en vez de escribir manualmente.
- Hacer **quizzes/preguntas tipo examen** con selección múltiple y
  retroalimentación visual inmediata.
- Navegar los **666 fragmentos de apuntes** con buscador y filtros visuales.
- Tener **botones nativos de Telegram** (MainButton, BackButton) y temas que
  siguen el modo claro/oscuro del usuario.

## Lo que se puede probar YA, rápido y gratis

Se preparó una guía y un **bot de prueba mínimo** (sin lógica de chatbokg)
para validar las Mini Apps en menos de una hora:

- Entorno **test server** de Telegram → permite usar `http://localhost` (sin
  comprar hosting ni dominio).
- Bot creado con `@BotFather` en 2 minutos.
- Mini App de ejemplo incluida en `demo/` que muestra: datos del usuario,
  tema claro/oscuro, botones, y envío de datos de vuelta al bot
  (`sendData` / `answerWebAppQuery`).

## Propuesta (de un vistazo)

| Propuesta | Esfuerzo | Impacto |
|---|---|---|
| A) Formulario visual de pregunta por tema | Bajo | Medio |
| B) Quiz interactivo con retroalimentación | Bajo–Medio | Medio |
| C) Navegador de apuntes con fórmulas renderizadas | Medio | Alto |
| D) Monitoreo de datos del usuario (Mini App de "información") | Muy bajo | Demostración |
| E) Botón "Abrir app" en el perfil (Main Mini App) | Muy bajo | Visto profesional |

## Qué se necesita (recursos)

- ~4–8 horas de desarrollo para prototipos de prueba (gratis).
- Un servicio de hosting HTTPS **solo para producción** (el entorno de test
  permite `localhost`). Opciones gratuitas: GitHub Pages, Vercel, Netlify,
  ngrok/cloudflared para demos.
- Python (ya se usa) con `python-telegram-bot` o `aiogram`, que ya lo soportan.

---

## Conclusión en una frase

Las Mini Apps de Telegram son la forma oficial, gratuita y de bajo esfuerzo de
convertir el chatbot de texto en una **aplicación educativa visual** dentro de
Telegram, y se puede demostrar en minutos con un bot de prueba sin lógica de
conversación.