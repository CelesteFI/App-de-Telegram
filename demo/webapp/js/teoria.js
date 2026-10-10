// teoria.js — contenido del Area de Teoria (bloques: p=parrafo, f=formula, li=lista)
window.TEORIA = {
  biseccion: {
    titulo: 'Metodo de biseccion',
    icono: '📐',
    resumen: 'Parte el intervalo a la mitad hasta encerrar la raiz.',
    bloques: [
      { tipo: 'p', texto: 'Se usa cuando $f(x)$ es continua y hay cambio de signo en $[a,b]$, es decir $f(a) \\cdot f(b) < 0$. Esta condicion garantiza que existe al menos una raiz en el intervalo.' },
      { tipo: 'f', tex: 'x_c = \\dfrac{a+b}{2}' },
      { tipo: 'p', texto: 'Se evalua $f(x_c)$ y se reemplaza el extremo que tenga el mismo signo. Con cada paso el error se reduce a la mitad.' },
      { tipo: 'f', tex: '\\dfrac{b-a}{2^n} \\le \\epsilon' },
      { tipo: 'li', items: ['Siempre converge', 'No necesita derivadas', 'Convergencia lenta pero segura'] },
    ],
  },
  newton: {
    titulo: 'Newton-Raphson',
    icono: '🚀',
    resumen: 'Usa la recta tangente para acercarse a la raiz rapidamente.',
    bloques: [
      { tipo: 'p', texto: 'Parte de una aproximacion inicial $x_0$ y traza la tangente a $f$ en ese punto; la interseccion con el eje $x$ es la nueva aproximacion.' },
      { tipo: 'f', tex: "x_{n+1} = x_n - \\dfrac{f(x_n)}{f'(x_n)}" },
      { tipo: 'p', texto: "Convergencia cuadratica cuando la raiz es simple y $x_0$ esta cerca. Puede diverger si $f'(x_n)$ es muy pequena (division entre casi cero)." },
      { tipo: 'li', items: ['Muy rapido cerca de la raiz', "Exige calcular $f'(x)$", 'Puede fallar con raices multiples'] },
    ],
  },
  falsaPosicion: {
    titulo: 'Falsa posicion (regula falsi)',
    icono: '⚖️',
    resumen: 'Combina biseccion con interpolacion lineal.',
    bloques: [
      { tipo: 'p', texto: 'Igual que biseccion, mantiene un intervalo que encierra la raiz, pero en vez de partir a la mitad, usa la recta que une los extremos.' },
      { tipo: 'f', tex: 'x_c = b - \\dfrac{f(b)(b-a)}{f(b)-f(a)}' },
      { tipo: 'p', texto: 'Garantiza convergencia (el intervalo se reduce) y suele ser mas rapida que biseccion en funciones casi lineales.' },
    ],
  },
  puntoFijo: {
    titulo: 'Punto fijo',
    icono: '🎯',
    resumen: 'Reescribe $f(x)=0$ como $x=g(x)$ e itera.',
    bloques: [
      { tipo: 'p', texto: 'Se despeja la ecuacion hasta tener la forma $x = g(x)$ y se aplica la iteracion repetidamente.' },
      { tipo: 'f', tex: 'x_{n+1} = g(x_n)' },
      { tipo: 'p', texto: 'Condicion suficiente de convergencia (en un entorno de la raiz):' },
      { tipo: 'f', tex: "|g'(x)| < 1" },
      { tipo: 'li', items: ['Muy simple de programar', 'Convergencia lineal', 'La eleccion de $g$ decide si converge'] },
    ],
  },
  lagrange: {
    titulo: 'Interpolacion de Lagrange',
    icono: '🌉',
    resumen: 'Construye un polinomio que pasa por todos los puntos dados.',
    bloques: [
      { tipo: 'p', texto: 'Dados $n+1$ puntos $(x_i, y_i)$ existe un unico polinomio de grado a lo mas $n$ que los interpola.' },
      { tipo: 'f', tex: 'P(x) = \\sum_{i=0}^{n} y_i \\, L_i(x)' },
      { tipo: 'f', tex: 'L_i(x) = \\prod_{j \\neq i} \\dfrac{x - x_j}{x_i - x_j}' },
      { tipo: 'p', texto: 'Las bases $L_i$ valen 1 en su nodo y 0 en los demas.' },
    ],
  },
  diferenciasDivididas: {
    titulo: 'Diferencias divididas',
    icono: '➗',
    resumen: 'Forma estable y tabular del polinomio interpolante.',
    bloques: [
      { tipo: 'p', texto: 'El polinomio se escribe en forma de Newton usando diferencias divididas.' },
      { tipo: 'f', tex: 'P(x) = f[x_0] + f[x_0,x_1](x-x_0) + \\cdots + f[x_0,\\dots,x_n]\\prod_{i=0}^{n-1}(x-x_i)' },
      { tipo: 'f', tex: 'f[x_i,x_{i+1}] = \\dfrac{f(x_{i+1})-f(x_i)}{x_{i+1}-x_i}' },
      { tipo: 'p', texto: 'Ventaja: agregar un punto nuevo no obliga a recalcular todo.' },
    ],
  },
  trapecio: {
    titulo: 'Regla del trapecio',
    icono: '📏',
    resumen: 'Aproxima el area bajo la curva con trapecios.',
    bloques: [
      { tipo: 'p', texto: 'Sustituye la curva por rectas. La version simple usa un solo trapecio.' },
      { tipo: 'f', tex: '\\int_a^b f(x)\\,dx \\approx \\dfrac{h}{2}\\left[f(a)+f(b)\\right]' },
      { tipo: 'p', texto: 'La compuesta divide $[a,b]$ en $n$ subintervalos de paso $h$.' },
      { tipo: 'f', tex: '\\int_a^b f(x)\\,dx \\approx \\dfrac{h}{2}\\left[f(x_0)+2\\sum_{i=1}^{n-1} f(x_i)+f(x_n)\\right]' },
      { tipo: 'p', texto: 'Error proporcional a $O(h^2)$: al duplicar $n$ el error baja a la cuarta parte (aprox).' },
    ],
  },
  simpson: {
    titulo: 'Regla de Simpson 1/3',
    icono: '🌗',
    resumen: 'Aproxima la curva con parabolas.',
    bloques: [
      { tipo: 'p', texto: 'Usa parabolas (polinomios de grado 2) sobre pares de subintervalos. Requiere un numero par de subintervalos.' },
      { tipo: 'f', tex: '\\int_a^b f(x)\\,dx \\approx \\dfrac{h}{3}\\left[f(x_0)+4\\sum_{\\text{impar}} f + 2\\sum_{\\text{par}} f + f(x_n)\\right]' },
      { tipo: 'p', texto: 'Error proporcional a $O(h^4)$: mas exacta que el trapecio para el mismo paso.' },
      { tipo: 'li', items: ['Simpson 1/3: parabolas (grado 2)', 'Simpson 3/8: cubicas (grado 3)', 'Si aparece numeros impares de franjas, combinar 3/8 con 1/3'] },
    ],
  },
  derivadas: {
    titulo: 'Derivacion numerica',
    icono: '📈',
    resumen: 'Diferencias finitas para estimar derivadas.',
    bloques: [
      { tipo: 'f', tex: "f'(x) \\approx \\dfrac{f(x+h)-f(x)}{h} \\qquad \\text{(adelantada)}" },
      { tipo: 'f', tex: "f'(x) \\approx \\dfrac{f(x)-f(x-h)}{h} \\qquad \\text{(regresiva)}" },
      { tipo: 'f', tex: "f'(x) \\approx \\dfrac{f(x+h)-f(x-h)}{2h} \\qquad \\text{(centrada, error } O(h^2) \\text{)}" },
      { tipo: 'f', tex: "f''(x) \\approx \\dfrac{f(x+h)-2f(x)+f(x-h)}{h^2}" },
      { tipo: 'p', texto: 'La centrada es la mejor opcion cuando es posible, y la de $h$ muy pequeno introduce error de redondeo.' },
    ],
  },
};