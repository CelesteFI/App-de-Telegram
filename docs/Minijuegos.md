# Minijuegos para App de Teoría de Ecuaciones Diferenciales

### 1. Desliza el Atributo (ED Tinder)
* **Mecánica:** Aparece una ecuación diferencial en el centro y una propiedad arriba (ej: "Es Lineal"). El usuario desliza a la derecha (**Verdadero**) o a la izquierda (**Falso**).
* **Ejemplo en ED:** 
  * Propiedad en pantalla: **¿Es Lineal?**
  * Ecuación: $y'' + 3yy' = 0$
  * *Acción:* Deslizar a la izquierda (**Falso**, porque el término $yy'$ no es lineal).

### 2. Memorama de Conceptos (ED Memory)
* **Mecánica:** Un tablero clásico de cartas boca abajo. El usuario debe voltear parejas que correspondan a un concepto teórico y su contraparte o definición matemática.
* **Ejemplo en ED:** 
  * Carta A: *"Ecuación Diferencial Ordinaria (EDO)"* ── Carta B: *$\frac{dy}{dx} + 5y = e^x$*
  * Carta C: *"Ecuación en Derivadas Parciales (EDP)"* ── Carta D: *$\frac{\partial u}{\partial t} = \alpha \frac{\partial^2 u}{\partial x^2}$*

### 3. Relación de Columnas (Method Match)
* **Mecánica:** Dos columnas fijas en pantalla. A la izquierda se listan formas estándar de ecuaciones y a la derecha el método analítico exacto para resolverlas. Se unen arrastrando el dedo de un nodo a otro.
* **Ejemplo en ED:**
  * **Columna Izquierda (Ecuación):**
    1. $M(x,y)dx + N(x,y)dy = 0$ donde $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x}$
    2. $\frac{dy}{dx} + P(x)y = f(x)$
  * **Columna Derecha (Método):**
    A. Factor Integrante $\mu(x) = e^{\int P(x)dx}$
    B. Ecuación Exacta (Integración directa)

### 4. Completa la Forma Estándar (Fill the Blank)
* **Mecánica:** Se muestra la estructura teórica de un teorema o una ecuación clásica con una pieza faltante. Abajo se muestran 3 opciones y el usuario debe arrastrar la correcta al espacio vacío.
* **Ejemplo en ED:**
  * Enunciado: *"La forma general de una ecuación de Bernoulli es: $y' + P(x)y = Q(x)y^{[ \quad ]}$"*
  * Opciones: $[ \ 2 \ ]$ , $[ \ n \ ]$ , $[ \ 0 \ ]$
  * *Respuesta correcta:* $[ \ n \ ]$

### 5. El Intruso (Odd One Out)
* **Mecánica:** Se presentan 4 tarjetas con ecuaciones o términos. 3 de ellos comparten una característica teórica estricta y uno no pertenece al grupo. El usuario debe tocar al "intruso".
* **Ejemplo en ED:**
  * Tarjetas en pantalla:
    1. $y'' + y = 0$ (Orden 2)
    2. $(y')^2 + x = 0$ (Orden 1, Grado 2)
    3. $\frac{d^2y}{dx^2} - 5y = e^x$ (Orden 2)
    4. $y^{(2)} - y' = x$ (Orden 2)
  * *Acción:* El usuario selecciona la opción **2** porque es la única que no es de Segundo Orden.

### 6. Clasificador Rápido (Category Bin)
* **Mecánica:** En la parte inferior de la pantalla hay 2 o 3 "canastas" o contenedores fijos que representan categorías de ED. En el centro van apareciendo ecuaciones de forma secuencial y el usuario debe arrastrar cada ecuación a la canasta correcta antes de que se agote el tiempo de la ronda.
* **Ejemplo en ED:** 
  * Contenedores estáticos: **[ Separable ]** | **[ Homogénea ]** | **[ Exacta ]**
  * Ecuación flotante: \(\frac{dy}{dx} = \frac{x^2 + y^2}{xy}\)
  * *Acción:* El usuario debe arrastrarla a la canasta de **Homogénea** (las funciones son de grado 2).

### 7. Ordena la Secuencia (Algorithm Sort)
* **Mecánica:** Para resolver ciertos tipos de ED o aplicar teoremas se requiere un orden analítico estricto. El juego presenta los pasos lógicos de un método teórico completamente desordenados. El usuario debe arrastrarlos verticalmente para ordenarlos secuencialmente del 1 al 4.
* **Ejemplo en ED (Método de Coeficientes Indeterminados):**
  * Bloques desordenados en pantalla:
    * *[ ] Proponer la forma de la solución particular \(y_p\).*
    * *[ ] Resolver la ecuación homogénea asociada para hallar \(y_c\).*
    * *[ ] Sumar ambas soluciones para obtener la solución general \(y = y_c + y_p\).*
    * *[ ] Derivar \(y_p\) y sustituir en la ED original para hallar los coeficientes.*
  * *Acción:* El usuario reordena los bloques en la secuencia lógica correcta para ganar puntos.

### 8. El Gráfico Falso (Direction Field Spy)
* **Mecánica:** Un minijuego visual de opción múltiple. Se muestra una ecuación diferencial lineal de primer orden muy simple o autónoma (ej: \(y' = y\)) y se presentan 3 campos de direcciones (campos de pendientes) diferentes. El usuario debe tocar el gráfico que representa teóricamente el comportamiento de las soluciones de esa ED.
* **Ejemplo en ED:**
  * Ecuación: \(\frac{dy}{dx} = 0\)
  * Opciones visuales: 
    * Gráfico A: Flechas completamente horizontales independientes de \(x\) y \(y\).
    * Gráfico B: Flechas con pendientes que aumentan exponencialmente.
    * Gráfico C: Flechas concéntricas en forma de círculo.
  * *Acción:* El usuario selecciona el **Gráfico A**, demostrando que entiende el significado geométrico de la derivada.

### 9. La Palabra Oculta (ED Crossword Lite)
* **Mecánica:** Estilo crucigrama de una sola palabra o juego del ahorcado modificado. Se da una pista conceptual estricta y espacios vacíos para las letras. Abajo hay un teclado virtual simplificado (solo con las letras que componen la palabra y 3 letras trampa).
* **Ejemplo en ED:**
  * Pista teórica: *"Tipo de solución de una ED que se obtiene al asignar valores específicos a las constantes de la solución general."*
  * Espacios en pantalla: `_ _ _ _ _ _ _ _ _ _ _`
  * *Solución esperada:* El usuario debe teclear ordenadamente la palabra **PARTICULAR**.

### 10. Tiro al Blanco Teórico (Target Pop)
* **Mecánica:** Aparecen globos o burbujas flotando por la pantalla, cada uno con una función matemática escrita dentro. En la parte superior hay una instrucción fija. El usuario debe "explotar" únicamente los globos que cumplan con la condición matemática teórica antes de que salgan de la pantalla.
* **Ejemplo en ED:**
  * Instrucción fija: **"Explota las funciones que sean Soluciones de: \(y'' + y = 0\)"**
  * Globos flotando: 
    * Balloon 1: \(\sin(x)\) (Correcto)
    * Balloon 2: \(\cos(x)\) (Correcto)
    * Balloon 3: \(e^x\) (Incorrecto)
    * Balloon 4: \(x^2\) (Incorrecto)
  * *Acción:* El usuario toca rápidamente los globos 1 y 2 para sumar combo de puntos, evitando los demás.

