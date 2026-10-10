# 10. Diapositivas para presentar + guion de apertura + Q&A

> Listo para copiar a Google Slides / PowerPoint. 10 diapositivas.
> Se agregó un guion hablado de apertura y preguntas frecuentes con respuesta.

---

## Diapositiva 1 — Título
**Mejora del Chatbot de Telegram con Mini Apps**
*Proyecto de Análisis Numérico · UNAM · Servicio Social*

- Nombre completo · fecha
- "De un bot que responde texto a una app de estudio dentro de Telegram"

## Diapositiva 2 — Contexto
**El chatbot actual**

- RAG en Python, 100 % local, sin internet ni GPU.
- 666 fragmentos de apuntes LaTeX · embeddings all-MiniLM · índice FAISS.
- LLM local Qwen (0.5B) genera respuestas citando la fuente.
- Funciona — pero la experiencia es 100 % texto.

## Diapositiva 3 — El problema
**Tres limitaciones del bot de texto**

1. Fórmulas: el renderizado depende de Telegram (frágil).
2. Entrada del usuario: texto libre, sin botones ni guía.
3. Navegación: 666 apuntes sin buscador visual.

## Diapositiva 4 — La oportunidad
**¿Qué son las Telegram Mini Apps?**

- Páginas web (HTML/CSS/JS) que corren **dentro de Telegram**, sin instalar nada.
- Documentación oficial: pueden **"reemplazar por completo un sitio web"**.
- Ventajas sobre un sitio normal: login ya hecho, notificaciones, pagos y llegada al usuario ya resueltos.
- (Mini App = Web App; solo cambió el nombre.)

## Diapositiva 5 — Demo oficial (en vivo si hay internet)
**Ejemplo real: @DurgerKingBot**

- Bot oficial de Telegram que muestra el menú, botones y mini app.
- Enlace de documentación: core.telegram.org/bots/webapps
- *[Capitulo: mostrar el bot un momento]*

## Diapositiva 6 — Cómo se abre una Mini App
**Formas de lanzamiento**

- Botón de teclado (*sendData*, formularios) — la más simple.
- Botón inline (con identidad del usuario).
- Botón de menú del chat (acceso permanente).
- Main Mini App en el perfil ("Launch App").
- Enlace directo `t.me/mibot?startapp=temaX`.

## Diapositiva 7 — Comparativa
**Bot de texto vs con Mini App** (tabla corta)

| | Texto | Mini App |
|---|---|---|
| Fórmulas LaTeX | Frágil | KaTeX, siempre perfectas |
| Entrada | Texto libre | Formularios/botones |
| Exámenes | Tedioso | Con pasos y progreso |
| Tema claro/oscuro | Manual | Automático |

> El motor RAG sigue igual en Python; la Mini App es solo la nueva cara.

## Diapositiva 8 — Propuesta
**4 propuestas, 1 se implementa**

- A) Selector de tema visual — esfuerzo bajo
- B) Quiz interactivo con retroalimentación — bajo/medio
- C) Navegador de apuntes con fórmulas renderizadas — medio, mayor impacto
- D) Perfil profesional del bot (Launch App) — muy bajo

**Recomendación:** B para demostrar rápido; C para el valor de fondo.

## Diapositiva 9 — Plan y recursos
**Cronograma y costo**

- 0) Prueba técnica con bot de prueba: 1–2 h ✅ (ya hecha)
- 1) Decidir propuesta con profesores
- 2) Prototipo: 4–8 h
- 3) Integración con el RAG (si es C): 4–6 h
- 4) Publicación demo gratuita (GitHub Pages/ngrok)
- **Costo: $0** · Total: 2–3 semanas parciales

## Diapositiva 10 — Riesgos y cierre
**Riesgos controlados**

- HTTPS obligatorio en producción → ngrok / GitHub Pages gratis; test server acepta localhost.
- Datos manipulables → validación HMAC siempre en backend.
- Token del bot secreto → solo en el servidor, nunca en la web.

**Mensaje final:** *"El chatbot ya entiende las preguntas; le faltaba una cara.
Las Mini Apps la dan — dentro de Telegram, sin registro, sin costo."*

---

## Guion hablado — apertura (1 minuto)

> *"Buenos días. El proyecto tiene un chatbot que contesta preguntas de
> Análisis Numérico usando 666 apuntes de la clase, todo en una laptop sin
> internet: recupera fragmentos con embeddings y FAISS, y un modelo local
> genera la respuesta. Hoy el bot solo habla por texto: las fórmulas se ven
> mal, el estudiante no tiene botones y no hay cómo navegar 666 apuntes.
> Investigué la forma oficial de resolverlo: las Telegram Mini Apps, páginas
> que se abren dentro de Telegram y que la propia documentación dice que
> pueden reemplazar un sitio web completo. Lo bueno: se probaron en minutos
> con un bot de prueba y sin costo. En esta presentación muestro qué son,
> qué se propone y cómo se implementaría."*

---

## Preguntas frecuentes (para el Q&A)

**1. ¿Localhost funciona sin internet? ¿Por qué usaste ngrok?**
En producción Telegram exige HTTPS y una URL pública. Por eso ngrok expone
`http://localhost:8080` como una URL `https`. En el **entorno de test** de
Telegram se permite usar localhost directo, lo que simplifica las pruebas.

**2. ¿De verdad reemplaza el RAG en Python?**
No. El RAG (embeddings + FAISS + Qwen) se mantiene. La Mini App es la
interfaz: recibe al usuario, arma la pregunta y muestra la respuesta con
herramientas visuales. El backend Python hace la magia de siempre.

**3. ¿Por qué JavaScript si todo es Python?**
Porque son dos piezas: el bot (Python) habla con la API de Telegram; la Mini
App es una página web que corre en el navegador de Telegram, y los navegadores
solo ejecutan JavaScript. Es como una app de teléfono: interfaz en JS, lógica
en el servidor Python.

**4. ¿Qué pasa si el plantel no tiene internet?**
El bot offline ya existe. Para la Mini App se puede usar el entorno de test
de Telegram (acepta localhost) o servir la web en una red local. En
producción pública se necesita HTTPS, que es gratis con GitHub Pages.

**5. ¿Los datos del usuario se pueden falsificar?**
Se pueden, si no se valida. Por eso la documentación exige validar `initData`
con HMAC-SHA256 en el servidor: así el backend solo confía en datos firmados
por Telegram. Es el paso obligado antes de usar identidad o pagos.