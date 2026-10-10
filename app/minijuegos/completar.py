"""completar.py — Minijuego 4: Completa la Forma Estandar (Fill the Blank).

Mecanica (Minijuegos.md #4): se muestra la estructura teorica de un
teorema o de una ecuacion clasica con una pieza faltante, y abajo hay tres
opciones para arrastrar (o tocar) en el hueco.

En el enunciado el hueco se escribe como `___` y las opciones son de una
palabra o de un simbolo: no hay que calcular nada, hay que recordar la
estructura correcta.
"""

from . import base

JUEGO = {
    "id": "completar",
    "titulo": "Completa la Forma Estandar",
    "icono": "\U0001F4D6",
    "resumen": "Elige el pedazo que falta en la estructura de la teoria.",
    "mecanica": "Lee el enunciado con el hueco, elige una de las 3 piezas y suelta en el hueco.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["teoria", "estructuras"],
}

CASOS = [
    {"enunciado": r"La forma general de una ecuacion de Bernoulli es $y' + P(x)y = Q(x)\,y^{\,\_\_\_}$",
     "opciones": [r"n", "2", "0"], "correcta": 0,
     "porque": r"El exponente $n$ es el que caracteriza a Bernoulli (y $n=1$ la reduce a lineal).", "d": 1},
    {"enunciado": r"El orden de una ED es el grado de la derivada mas alta que aparece: $y^{(\_\_\_)}$",
     "opciones": ["n", "2", "0"], "correcta": 0,
     "porque": r"Se escribe $y^{(m)}$ y $m$ es el orden; no siempre vale 2.", "d": 1},
    {"enunciado": r"El factor integrante de $y' + P(x)y = f(x)$ es $\mu(x) = e^{\int \_\_\_\, dx}$",
     "opciones": [r"P(x)", "f(x)", "1"], "correcta": 0,
     "porque": r"Depende del coeficiente de $y$, que es $P(x)$; el segundo miembro $f(x)$ no entra.", "d": 1},
    {"enunciado": r"La ED $y' = F\!\left(\frac{y}{x}\right)$ se linealiza con la sustitucion $y = \_\_\_\, x$",
     "opciones": ["v", "u", "w"], "correcta": 0,
     "porque": r"La variable nueva se llama comunmente $v = y/x$, de modo que $y = vx$.", "d": 1},
    {"enunciado": r"La transformada de Laplace cumple $\mathcal{L}\{y''\} = s^{2}Y(s) - s\,y(0) - \_\_\_$",
     "opciones": [r"y'(0)", "y''(0)", "0"], "correcta": 0,
     "porque": r"Cada derivada resta la siguiente condicion inicial: por eso aparece $y'(0)$.", "d": 2},
    {"enunciado": r"La solucion complementaria de una ED lineal homogenea de segundo orden sale de las raices del polinomio $\lambda^{\_\_\_} + a_{1}\lambda + a_{0} = 0$",
     "opciones": ["2", "3", "1"], "correcta": 0,
     "porque": r"El polinomio caracteristico de una ED de segundo orden es cuadratico.", "d": 1},
    {"enunciado": r"La solucion general de una ED lineal de primer orden contiene exactamente \_\_\_ constante(s) de integracion",
     "opciones": ["1", "2", "0"], "correcta": 0,
     "porque": r"Se integra una sola vez, asi que aparece una sola $C$ (mas el dato inicial).", "d": 2},
    {"enunciado": r"La ED $y' + y = e^{x}$ es lineal de primer orden y, por tanto, su factor integrante es $\mu(x) = e^{\int 1\,dx} = \_\_\_$",
     "opciones": [r"e^{x}", "x", r"\ln x"], "correcta": 0,
     "porque": r"$P(x) = 1$, luego $\mu(x) = e^{x}$.", "d": 2},
    {"enunciado": r"Una ED es lineal si la incognita y sus derivadas aparecen con potencia exactamente \_\_\_",
     "opciones": ["1", "2", "0"], "correcta": 0,
     "porque": r"Lineal significa grado 1 en $y, y', y''\dots$; cualquier otro grado ya no lo es.", "d": 1},
    {"enunciado": r"El error de la aproximacion de $\mathcal{L}\{y''\}$ solo desaparece si se conocen las condiciones iniciales en $t = \_\_\_$",
     "opciones": ["0", "1", r"\infty"], "correcta": 0,
     "porque": r"La transformada introduce $y(0)$ y $y'(0)$: las condiciones iniciales en el origen.", "d": 2},
    {"enunciado": r"La ED $M\,dx + N\,dy = 0$ es exacta cuando $\frac{\partial M}{\partial y} - \frac{\partial N}{\partial x} = \_\_\_$",
     "opciones": ["0", r"P(x)", "1"], "correcta": 0,
     "porque": r"La diferencia debe ser identicamente cero en todo el dominio.", "d": 2},
    {"enunciado": r"La ED de Riccati $y' = a(x)y^{2} + b(x)y + c(x)$ se puede reducir a lineal cuando se conoce una solucion particular $y_p$ con la sustitucion $y = y_p + v$ y $v = z^{\_\_\_}$",
     "opciones": ["-1", "1", "0"], "correcta": 0,
     "porque": r"Con $v = 1/z$ la Riccati se vuelve lineal: de ahi el exponente $-1$.", "d": 3},
    {"enunciado": r"El teorema de existencia y unicidad para $y' = f(x,y)$ con dato inicial exige que $f$ y $\frac{\partial f}{\partial y}$ sean continuas, es decir que se cumpla la hipotesis de \_\_\_",
     "opciones": ["Lipschitz", "periodicidad", "convexa"], "correcta": 0,
     "porque": r"La hipotesis de Lipschitz (o $\partial f/\partial y$ continua) garantiza la unicidad.", "d": 3},
    {"enunciado": r"Una ED parcial homogenea con condiciones iniciales $u(x,0) = f(x)$ se ataca, en el caso mas simple, por \_\_\_\_\_\_\_\_\_\_\_",
     "opciones": ["separacion de variables", "variacion de parametros", "biseccion"], "correcta": 0,
     "porque": r"Se escribe $u(x,t) = X(x)T(t)$ y cada factor se resuelve por separado.", "d": 3},
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [c for c in CASOS if c["d"] <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, caso in enumerate(elegidos):
        opciones = list(caso["opciones"])
        correcta = caso["correcta"]
        texto_correcto = opciones.pop(correcta)
        barajadas = base.barajar(azar, opciones)
        barajadas.insert(azar.randrange(len(barajadas) + 1), texto_correcto)
        salida.append({
            "id": f"h{i}",
            "enunciado": caso["enunciado"],
            "opciones": barajadas,
            "solucion": barajadas.index(texto_correcto),
            "porque": caso["porque"],
        })
    return salida


def publico(ronda: dict) -> dict:
    return {"id": ronda["id"], "enunciado": ronda["enunciado"], "opciones": ronda["opciones"]}


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = indice de la opcion elegida (o el texto de la pieza)."""
    elegido = None
    if isinstance(respuesta, bool):
        elegido = None
    elif isinstance(respuesta, int):
        elegido = respuesta
    elif isinstance(respuesta, str):
        if respuesta.strip().lstrip("-").isdigit():
            elegido = int(respuesta.strip())
        else:
            limpio = respuesta.strip()
            elegido = ronda["opciones"].index(limpio) if limpio in ronda["opciones"] else None
    ok = elegido == ronda["solucion"]
    if ok:
        detalle = "Exacto: " + ronda["porque"]
    elif elegido is not None and 0 <= elegido < len(ronda["opciones"]):
        detalle = f"No. La pieza correcta era `{ronda['opciones'][ronda['solucion']]}`. {ronda['porque']}"
    else:
        detalle = "No. " + ronda["porque"]
    return {
        "correcto": ok,
        "puntaje": 100 if ok else 0,
        "detalle": detalle,
        "correcta": ronda["opciones"][ronda["solucion"]],
    }
