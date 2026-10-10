"""columnas.py — Minijuego 3: Relacion de Columnas (Method Match).

Mecanica (Minijuegos.md #3): dos columnas fijas. A la izquierda, formas de
ecuaciones diferenciales; a la derecha, el metodo analitico que las resuelve.
Se unen arrastrando (o tocando) un nodo con otro.

El servidor mezcla ambas columnas y guarda el emparejamiento correcto; el
navegador nunca recibe la solucion.
"""

from . import base

JUEGO = {
    "id": "columnas",
    "titulo": "Relacion de Columnas",
    "icono": "\U0001F517",
    "resumen": "Une cada forma de ecuacion diferencial con el metodo que la resuelve.",
    "mecanica": "Toca una ecuacion y despues el metodo que le corresponde. Une todas.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["metodos", "emparejar"],
}

# (columna izquierda, columna derecha, explicacion, dificultad)
TABLEROS = [
    [
        (r"M\,dx + N\,dy = 0 \;\text{ con }\; \partial M/\partial y = \partial N/\partial x",
         "Integracion directa (ya es exacta)",
         "Si la ecuacion es exacta, la solucion es $F(x,y) = C$ integrating $M dx + N dy$ directo.", 1),
        (r"y' + P(x)\,y = f(x)",
         r"Factor integrante \mu(x) = e^{\int P(x)dx}",
         r"Es la ED lineal de primer orden: se multiplica por el factor integrante.", 1),
        (r"\dfrac{dy}{dx} = f(x)\,g(y)",
         "Separar variables e integrar",
         r"El lado derecho ya es producto: se separa $\frac{dy}{g(y)} = f(x)dx$.", 1),
    ],
    [
        (r"y' + P(x)\,y = Q(x)\,y^{n}",
         r"Sustitucion y = v^{1-n} (Bernoulli)",
         r"La transformacion $y = v^{1-n}$ convierte la ED en lineal.", 2),
        (r"\dfrac{dy}{dx} = F\!\left(\dfrac{y}{x}\right)",
         "Sustitucion y = vx (homogenea)",
         r"Al poner $y = vx$ la ED se separa en $v$ y $x$.", 2),
        (r"y'' + a_{1}y' + a_{0}y = 0",
         "Polinomio caracteristico",
         r"Las raices $\\lambda$ del polinomio dan la solucion complementaria.", 1),
    ],
    [
        (r"y' = a(x)y^{2} + b(x)y + c(x)",
         "Riccati (o reduccion a lineal si se conoce una solucion)",
         r"Es el unico caso no lineal de primer orden que se reduce a una lineal.", 2),
        (r"y'' + p(x)y' + q(x)y = f(x)",
         "Variacion de parametros o reduccion de orden",
         r"Lineal de segundo orden con coeficientes variables.", 3),
        (r"\dfrac{\partial u}{\partial t} = \alpha\,\dfrac{\partial^{2}u}{\partial x^{2}}",
         "Separacion de variables (o Fourier)",
         r"Problema de difusion: se separa $u(x,t) = X(x)T(t)$ o se aplica Fourier.", 2),
    ],
    [
        (r"\partial M/\partial y - \partial N/\partial x = h(x)",
         r"Factor integrante multiplicando solo por x: \mu(x) = e^{\int h(x)dx}",
         r"Cuando la diferencia depende solo de $x$, el factor integrante es funcion de $x$ y se integra directo.", 3),
        (r"\partial M/\partial y - \partial N/\partial x = g(y)",
         r"Factor integrante multiplicando solo por y: \mu(y) = e^{\int -g(y)dy}",
         r"Cuando la diferencia depende solo de $y$, se busca $\\mu(y)$.", 3),
        (r"\int f(x)\,dx = x^{2} + C",
         "Constante de integracion",
         r"Toda integral indefinida lleva su constante $C$.", 1),
    ],
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    salida = []
    for i in range(cantidad):
        candidatos = [t for t in TABLEROS if max(fila[3] for fila in t) <= limite]
        tablero = (azar.choice(candidatos) if candidatos
                   else azar.choice(TABLEROS))
        izquierda = [fila[0] for fila in tablero]
        derecha = [fila[1] for fila in tablero]
        solucion = {str(j): derecha.index(fila[1]) for j, fila in enumerate(tablero)}
        salida.append({
            "id": f"c{i}",
            "izquierda": izquierda,
            "derecha": base.barajar(azar, derecha),
            "solucion": solucion,
            "porque": [fila[2] for fila in tablero],
        })
    return salida


def publico(ronda: dict) -> dict:
    return {
        "id": ronda["id"],
        "izquierda": ronda["izquierda"],
        "derecha": ronda["derecha"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = lista con el indice de la derecha que elegiste por cada
    fila de la izquierda (en el mismo orden)."""
    if not isinstance(respuesta, (list, tuple)):
        respuesta = []
    aciertos = 0
    fallados = []
    for j in range(len(ronda["izquierda"])):
        elegido = respuesta[j] if j < len(respuesta) else None
        if elegido is None:
            continue
        try:
            elegido = int(elegido)
        except (TypeError, ValueError):
            continue
        if elegido == ronda["solucion"][str(j)]:
            aciertos += 1
        else:
            fallados.append(j)
    total = len(ronda["izquierda"])
    detalle = "Perfecto: cada ecuacion quedo con su metodo." if aciertos == total else \
        (f"{aciertos} de {total} pares correctos. " +
         " ".join(f"El metodo de la ecuacion {j + 1} era: {ronda['derecha'][ronda['solucion'][str(j)]]}."
                  for j in fallados[:3]))
    return {
        "correcto": aciertos == total,
        "puntaje": base.puntos(aciertos / total if total else 0),
        "detalle": detalle,
        "aciertos": aciertos,
        "total": total,
    }
