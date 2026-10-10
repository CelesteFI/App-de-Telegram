# Fuente para NotebookLM — Mejora del Chatbot con Telegram Mini Apps

> Documento de investigación depurado para generar la presentación.
> Subirlo completo (o en partes) a NotebookLM: notebooklm.google.com → Crear notebook → Añadir fuentes.

---

## 1. Contexto del proyecto

- Se tiene un **chatbot RAG para Análisis Numérico UNAM** desarrollado en
  Python y que corre 100 % local en una laptop sin internet.
- Componentes: 666 fragmentos de apuntes LaTeX, embeddings
  `all-MiniLM-L6-v2`, índice FAISS y el modelo LLM local `Qwen2.5-0.5B`
  como generador de respuestas.
- Flujo: la pregunta del estudiante se convierte en vector → FAISS recupera
  los 10 fragmentos más parecidos → el LLM genera la respuesta citando la
  fuente.
- Limitaciones actuales: la interacción es 100 % por texto, las fórmulas
  dependen del renderizado de Telegram y no hay formas visuales de navegar
  los 666 fragmentos ni de guiar al estudiante.

## 2. Qué se investigó

- Telegram permite que sus bots abran **Mini Apps**: aplicaciones web
  (HTML + CSS + JavaScript) que se ejecutan **dentro de la propia app de
  Telegram** sin instalar nada.
- La documentación oficial las describe como capaces de **"reemplazar por
  completo un sitio web"** (core.telegram.org/bots#replace-entire-websites),
  con una guía dedicada en core.telegram.org/bots/webapps.
- **Mini App = Web App**: son lo mismo; solo cambió el nombre con el tiempo.
- Ventajas frente a un sitio web normal:
  - Autenticación **ya resuelta** (Telegram te entrega la identidad del
    usuario validada; no hay registro ni contraseña).
  - Notificaciones integradas (el bot puede escribirle al usuario).
  - Alcance: el usuario ya vive en Telegram; un tap y entra.
  - Pagos integrados (Telegram Stars, Google Pay / Apple Pay).
  - Temas claro/oscuro automáticos mediante variables CSS
    (`--tg-theme-*`) que Telegram inyecta.

## 3. Lo que puede hacer una Mini App hoy

- Pantalla completa (fullscreen) vertical y horizontal.
- Accesos directos al home del teléfono (como app instalada).
- GPS y sensores: acelerómetro, giroscopio, orientación.
- Almacenamiento en la nube, en el dispositivo y seguro + biometría.
- Compartir mensajes, historias y descargar archivos.
- Pagos y suscripciones con Telegram Stars.
- Botones nativos (MainButton, BackButton), popups, lector QR,
  vibración (haptics).
- Validación segura de datos con HMAC-SHA256 y firma Ed25519.

## 4. Cómo se abre una Mini App (formas principales)

1. **Botón de teclado (KeyboardButton)**: botón en el teclado de respuesta;
   la app devuelve datos con `sendData()` (máx. 4096 bytes) en un mensaje de
   servicio. Ideal para formularios y selectores.
2. **Botón inline (InlineKeyboardButton)**: botón bajo un mensaje; recibe la
   identidad del usuario y el bot puede responder con `answerWebAppQuery`.
3. **Botón de menú del chat (Menu Button)**: acceso permanente del bot a la
   app (configurado en BotFather o por API).
4. **Main Mini App (perfil)**: botón "Launch App" + previews en el perfil del
   bot; aspecto de producto terminado.
5. **Enlace directo**: `https://t.me/mibot?startapp=temaX` se comparte en
   cualquier chat.
6. **Modo inline** y **menú de adjuntos** (este último solo para cuentas
   grandes en producción, pero gratis en el entorno de test).

## 5. Comparativa: bot de texto vs con Mini App

| Criterio | Bot de texto (actual) | Con Mini App |
|---|---|---|
| Fórmulas LaTeX | Depende del render en Telegram | Se renderizan con KaTeX dentro de la app: siempre perfectas |
| Entrada del usuario | Texto libre (errores) | Botones y formularios guiados |
| Flujos largos (exámenes) | Conversación tediosa | Página con pasos, barra de progreso, botón nativo |
| Tema claro/oscuro | Manual | Automático |
| Login / identidad | ID del chat | ID validado de Telegram sin registro |
| Desarrollo | Baja complejidad | Media (web + hosting) |
| Sin internet (plantel) | Funciona 100% local | Requiere servir la web (con test server se usa localhost) |

**Conclusión:** la Mini App no reemplaza al motor RAG (embeddings + FAISS +
Qwen, que sigue en Python). Es la **capa de interfaz** que mejora cómo el
estudiante le pregunta y consume respuestas.

## 6. Recomendación para este proyecto

- **Corto plazo (demostración):** Mini App informativa + quiz de 5 preguntas
  abierta desde botón de teclado y menú.
- **Mediano plazo:** navegador de apuntes con fórmulas renderizadas conectado
  al RAG.
- **Presentación profesional:** Main Mini App con "Launch App" en el perfil.
- Método de apertura recomendado para empezar: **botón de teclado** (selector
  de tema con `sendData`) + **menú button** + **main mini app** (igual que el
  bot oficial de ejemplo @DurgerKingBot).

## 7. Propuesta concreta

| Propuesta | Esfuerzo | Impacto |
|---|---|---|
| A) Selector visual de tema (formulario) | Bajo | Medio |
| B) Quiz interactivo con retroalimentación | Bajo–Medio | Medio |
| C) Navegador de apuntes con fórmulas renderizadas | Medio | Alto |
| D) Perfil profesional (Main Mini App + previews) | Muy bajo | Profesional |

**Cronograma sugerido:** prueba técnica (1–2 h) → decidir propuesta → prototipo
(4–8 h) → integración con RAG (4–6 h, solo si es C) → publicación demo +
documentación (3–4 h). Total: **2–3 semanas** de trabajo parcial.

**Recursos:** sin costo monetario (BotFather, ngrok, GitHub Pages son gratis).
Hosting HTTPS solo para producción (GitHub Pages gratuito). Python + librerías
anteriores + `python-telegram-bot`.

## 8. Pruebas (cómo se validó el concepto)

- Se creó un **bot de prueba mínimo sin lógica de chatbot**: solo sirve para
  abrir Mini Apps (comandos `/start`, `/inline`, `/menu`, `/data`).
- La Mini App de ejemplo muestra: datos del usuario (`initDataUnsafe`),
  tema claro/oscuro, plataforma, un formulario de ejemplo y devuelve datos al
  bot con `sendData()`.
- Flujo de prueba: `python -m http.server 8080` → `ngrok http 8080` →
  el bot usa la URL HTTPS pública; en el entorno **test server** de Telegram
  se puede usar `http://localhost` sin HTTPS.

## 9. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Producción exige HTTPS | Demo con ngrok o GitHub Pages (gratis); test server permite localhost |
| Datos manipulables por el usuario | Validar SIEMPRE `initData` con HMAC-SHA256 en el backend |
| `sendData` solo desde botón de teclado y sin identidad | Usar botón inline cuando se requiera identidad |
| Plantel sin internet | Test server con localhost para demostración; evaluar hosting local |
| Token del bot expuesto | Nunca poner el token en el frontend; usar variables de entorno |

## 10. Mensaje de cierre sugerido

> "El chatbot ya entiende las preguntas de Análisis Numérico; lo que le falta
> es una cara. Las Mini Apps de Telegram dan esa cara —formularios, quiz,
> fórmulas y navegación de apuntes— dentro de la misma app, sin registro, sin
> costo y con autenticación ya resuelta. Ya validamos el concepto con un bot
> de prueba en minutos; la siguiente fase es convertir la propuesta elegida en
> la interfaz oficial del bot."