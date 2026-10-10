# 11. Mini Apps listas para integrar: catálogo de librerías ya hechas

> Material nuevo para la presentación. Muestra que **no hay que programar todo
> desde cero**: la Mini App es una página web, y existen librerías maduras,
> gratuitas y de código abierto que ya resuelven calculadoras, quizzes,
> flashcards, gráficas, fórmulas LaTeX, diagramas y más.
> Complementa `04_comparativa_y_recomendaciones.md` y `06_propuesta_para_profesores.md`.

---

## Diapositiva 1 — La idea central

**No partimos de cero: la Mini App es una página web.**

- Cualquier librería JS que funcione en un navegador funciona dentro de Telegram.
- La mayoría es **gratuita, MIT y de código abierto**.
- Se puede cargar por CDN con una sola línea `<script>` (sin instalar nada, sin Node).
- El chatbot RAG en Python no se toca: la app solo es la nueva cara.

> Mensaje: *"Cada módulo que proponemos —examen, calculadora, gráfica—
> ya tiene una librería probada por miles de proyectos."*

## Diapositiva 2 — Kit base (lo que toda Mini App necesita)

| Componente | Qué resuelve | Librería |
|---|---|---|
| SDK oficial | Botón, tema claro/oscuro, vibración, compartir | `telegram-web-app.js` · `@telegram-apps/sdk` (TypeScript) |
| UI con estética Telegram | Botones, listas, chips ya hechos con el look de la app | `@telegram-apps/telegram-ui` (React, MIT) |
| Plantillas para empezar | Proyecto listo con build y ngrok incluido | `vanilla-js-boilerplate` · `vite-boilerplate` · `webpack-boilerplate` (React+TS) |

> Estas tres piezas son lo único "nuevo" que aporta Telegram; el resto son
> librerías web normales que ya dominamos o son fáciles de usar.

## Diapositiva 3 — Mapa general de módulos listos

| Módulo | Librería lista | Licencia | Esfuerzo | Ejemplo en Análisis Numérico |
|---|---|---|---|---|
| Fórmulas LaTeX | **KaTeX** / MathJax | MIT / Apache 2.0 | Bajo | Apuntes y exámenes con fórmulas perfectas, sin depender de Telegram |
| Gráficas 2D/3D | **Chart.js**, **Plotly.js**, Recharts, ECharts | MIT | Bajo | Convergencia de bisección, error, datos de interpolación |
| Graficador interactivo | **Desmos API**, GeoGebra, JSXGraph | Gratis (educativo) | Bajo | Localizar raíces, ver el método de Newton paso a paso |
| Calculadora numérica | **math.js**, math-expression-evaluator | Apache 2.0 / MIT | Bajo | Evaluar funciones e iterar fórmulas al instante |
| Quiz / exámenes | **react-quiz-component**, react-quiz-ui | MIT / ISC | Bajo–Medio | Examen tipo con puntaje, temporizador y retroalimentación |
| Flashcards | HTML/CSS + localStorage (SRS) | — | Bajo | Barajar definiciones de 666 apuntes |
| Diagramas / flujo | **Mermaid**, vis.js | MIT | Bajo | Diagrama de flujo de cada algoritmo numérico |
| Mini competencia | Backend Python + tabla de puntos (o Firebase/Supabase) | — | Medio | Retos semanales con ranking |
| Dibujo / práctica | Excalidraw embed o `<canvas>` nativo | MIT | Medio | El estudiante resuelve ejercicios a mano alzada |

## Diapositiva 4 — Gráficas y graficadores (el más visual)

- **Chart.js**: la más usada (~65k ⭐), línea/barra/pastel, ligera y rápida.
  → Ejemplo: curva de convergencia de cada método numérico.
- **Plotly.js**: científica, con 3D; ideal si alguien quiso una gráfica bonita.
- **Desmos API**: calculadora gráfica funcional integrable en la app (gratis para educación).
  → Ejemplo: el alumno mueve un deslizador y ve cómo bisección "abreza" la raíz.
- Se integran con **<script src="https://cdn.jsdelivr.net/npm/chart.js">** y listo.

## Diapositiva 5 — Fórmulas (clave para la materia)

- **KaTeX**: renderiza LaTeX en milisegundos, tan ligero que es el preferido de Telegram/X/Tumblr.
- **MathJax**: más completo (escribe fórmulas a mano), pero más pesado.
- Resuelve el problema #1 detectado: fórmulas que Telegram muestra mal en texto plano.
- Escribes en Markdown/LaTeX → sale perfecto en el chat de estudio.

## Diapositiva 6 — Quiz y tarjetas (exámenes y repaso)

- **react-quiz-component**: se define el examen en **JSON**, y ya trae:
  puntaje, contador de tiempo, mezclar preguntas/respuestas, retroalimentación por pregunta y resultados.
- Compatible con la propuesta "B: Quiz interactivo" del documento 06.
- **Flashcards**: voltear tarjeta = CSS (3 líneas); repaso espaciado = localStorage.
- Ventaja sobre un PDF: el bot **guarda la identidad** (initData) y puede llevar progreso de cada alumno.

## Diapositiva 7 — Mini competencias y retos

- No necesita librería especial: el bot Python ya entrega identidad segura (HMAC).
- Se suma una **tabla de puntos** en el backend y se difunde ranking con `sendMessage`.
- Sensación de juego lista con lo que Telegram ya da: MainButton + HapticFeedback (vibración).
- Opción opcional: base en tiempo real (Supabase/Firebase) para ranking en vivo.
- Pequeño costo moral: "competencia" ≠ "calificación"; se presenta como repaso gamificado.

## Diapositiva 8 — Esfuerzo vs impacto (qué conviene)

| Propuesta | Esfuerzo | Impacto para el alumno | Librería |
|---|---|---|---|
| Fórmulas LaTeX en apuntes | Bajo | Alto | KaTeX |
| Quiz con retroalimentación | Bajo–Medio | Alto | react-quiz-component |
| Gráficas de convergencia | Bajo | Alto | Chart.js / Plotly |
| Graficador interactivo | Bajo–Medio | Muy alto | Desmos API / GeoGebra |
| Flashcards | Bajo | Medio | CSS + localStorage |
| Mini competencia | Medio | Alto | Backend propio |

> Recomendación para 1 semestre: **Fórmulas + Gráficas + Quiz**. Las tres
> juntas cubren repasar, visualizar y evaluar.

## Diapositiva 9 — Notas rápidas para el profesor (Q&A corto)

1. **¿Se instala algo en la escuela?** No. Todo corre en el navegador de Telegram; el RAG sigue en la laptop.
2. **¿Son libres?** Casi todas MIT/Apache (uso comercial gratis). Desmos/GeoGebra gratis para educación.
3. **¿Solo con internet?** La app necesita internet, igual que el bot actual cuando está en línea.
4. **¿En qué idioma se programa?** Interfaz en HTML/CSS/JS (el navegador solo ejecuta JS); la lógica sigue en Python.
5. **¿Se puede romper el RAG?** No se toca; la Mini App consulta al mismo backend.

---

## Documentos relacionados

- `04_comparativa_y_recomendaciones.md` — por qué Mini App sobre bot de texto.
- `06_propuesta_para_profesores.md` — plan A/B/C/D y cronograma.
- `07_recursos_y_referencias.md` — todos los enlaces, plantillas y repositorios de ejemplo.
- `demo/` — bot de prueba ya funcional para repetir la demo en vivo.

## Referencias clave

- SDK y UI kit: https://github.com/telegram-mini-apps-dev/TelegramUI · https://docs.telegram-mini-apps.com
- Chart.js: https://www.chartjs.org · Plotly: https://plotly.com/javascript
- Desmos API: https://www.desmos.com/api · GeoGebra: https://www.geogebra.org
- KaTeX: https://katex.org · MathJax: https://www.mathjax.org
- Quiz: https://www.npmjs.com/package/react-quiz-component
- math.js: https://mathjs.org · Mermaid: https://mermaid.js.org
- Plantillas vanilla/vite/webpack: https://github.com/telegram-mini-apps-dev (boilerplates)