# 06. Propuesta para profesores — Plan completo

> Documento listo para presentar: contexto, propuestas, alcance, cronograma,
> entregables, riesgos y métricas. Puede adaptarse a la presentación.

## 0. Contexto del proyecto

- Se tiene un chatbot RAG para Análisis Numérico UNAM (Python, 100% local en
  CPU): 666 fragmentos de apuntes LaTeX, embeddings `all-MiniLM-L6-v2`,
  índice FAISS y LLM `Qwen2.5-0.5B`/`1.5B` como generador.
- Hoy la interacción es 100% por texto. Limitaciones:
  - Las fórmulas dependen del renderizado de Telegram.
  - No hay formularios ni botones para guiar al estudiante.
  - No hay manera visual de navegar los 666 fragmentos.
  - El bot Telegram aún no está conectado (fase F4.2 del plan de mejoras).
- **Investigación realizada:** las **Telegram Mini Apps** (web apps embebidas
  en Telegram) resuelven exactamente esos tres puntos, con login ya integrado
  y costo cero. Fuentes oficiales: `core.telegram.org/bots` y
  `core.telegram.org/bots/webapps`.

## 1. Objetivos

**Objetivo general:** integrar una o más Mini Apps al chatbot para pasar de
una experiencia texto-planо a una experiencia **educativa visual** dentro de
Telegram, manteniendo el motor RAG local como backend.

**Objetivos específicos:**
1. Validar técnicamente las Mini Apps con un bot de prueba (sin lógica de
   chatbot) en el entorno de test de Telegram.
2. Construir una Mini App mínima de "panel del usuario" (demo) que muestre
   identidad, tema y envíe datos de vuelta.
3. Construir el prototipo de **quiz interactivo** de 5 preguntas con
   retroalimentación (elige la que mejor demuestre).
4. Construir el prototipo de **navegador de apuntes** con fórmulas renderizadas
   conectado al RAG.
5. Elegir (con las profesoras/es) una propuesta para implementar en
   producción y entregarla documentada.

## 2. Propuestas (de menor a mayor alcance)

### Propuesta A — "Selector de tema visual" (prototipo)
- Mini App con botones de los temas del temario.
- Al tocar, `sendData` al bot → el bot responde con la información del tema
  (llama al RAG).

### Propuesta B — "Quiz interactivo" (prototipo)
- Mini App de 5 preguntas de opción múltiple (fórmulas LaTeX con KaTeX).
- Retroalimentación visual inmediata + botón nativo "Ver resultado".
- Resultado devuelto al bot para registro.

### Propuesta C — "Navegador de apuntes" (prototipo + RAG)
- Buscador visual + filtros por tema.
- Resultados con fuentes (archivo/seccion), fórmulas renderizadas.
- Llama al backend del RAG (FastAPI + `QueryEngine`) desde la Mini App.

### Propuesta D — "Presentación profesional del bot" (muy barato)
- Main Mini App: botón "Launch App" en el perfil + previews de video.
- Menú button permanente "Inicio" → abre la Mini App.
- Da aspecto de producto terminado para las presentaciones.

## 3. Plan de trabajo (cronograma sugerido)

| Etapa | Entregable | Tiempo |
|---|---|---|
| 0. Prueba técnica (este paquete) | Bot tonto + Mini App demo funcionando en test | 1–2 h |
| 1. Decidir propuesta A/B/C con profesores | Acta de selección | 1 sesión |
| 2. Implementar prototipo | Mini App + integración al bot Python | 4–8 h |
| 3. Integrar con RAG (si C) | Endpoint FastAPI + CORS + validación initData | 4–6 h |
| 4. Publicación demo (GitHub Pages / ngrok) | Enlace HTTPS para presentar | 1–2 h |
| 5. Documentación y presentación | Doc + demo en vivo | 2 h |

Total estimado: **2–3 semanas** de trabajo parcial si se elige la B,
3–4 semanas si se elige la C.

## 4. Entregables finales

- Código del bot + Mini App (repositorio).
- Guía de instalación y prueba (este paquete).
- Documento técnico (seguridad/validación, arquitectura).
- Video/demo de 3 minutos para presentación.

## 5. Recursos necesarios

- Sin costo monetario (herramientas gratis: BotFather, test server, ngrok,
  GitHub Pages).
- Hosting HTTPS solo para producción (GitHub Pages gratuito sirve).
- Python 3 + bibliotecas ya en uso + `python-telegram-bot`.

## 6. Riesgos y mitigación (resumido)

| Riesgo | Mitigación |
|---|---|
| Complement edge: producción requiere HTTPS | demo en test server; GitHub Pages gratis |
| `sendData` limitado a botón de teclado | usar inline button cuando se requiera identidad |
| Datos manipulados por el usuario | validación HMAC-SHA256 (documento 08) siempre en backend |
| El plantel puede no tener internet | entorno de test con localhost; evaluar servir la web localmente solo para demo |
| Alcance demasiado grande | priorizar UNA propuesta al primer ciclo |

## 7. Métricas para evaluar la mejora

- **Diste**: encuesta de 5 preguntas a estudiantes (¿más fácil? ¿más claro?).
- **Técnica**: % de respuestas del RAG con fuente correcta; tiempo de respuesta
  con la app vs sin ella; datos recibidos correctamente (`web_app_data`).
- **Adopción**: usuarios que abren la app vs usuarios que solo escriben texto
  (dato que te da Telegram: número de opens de la main mini app).

## 8. Mensaje de cierre (para la presentación)

> "El chatbot ya entiende las preguntas de Análisis Numérico; le falta una
> cara. Las Mini Apps de Telegram dan esa cara — formularios, quiz, fórmulas y
> navegación de apuntes — dentro de la misma app, sin registro, sin costo y
> con autenticación ya resuelta por Telegram. Ya validamos que se puede probar
> en minutos; elegimos la propuesta ___ y la siguiente fase es convertirla en
> la interfaz oficial del bot."