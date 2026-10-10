"""memoria.py — Minijuego 2: Memorama de Conceptos (ED Memory).

Mecanica (Minijuegos.md #2): tablero de cartas boca abajo. Hay que emparejar
un concepto teorico con su contraparte matematica (o al reves).

El servidor reparte las cartas mezcladas y se guarda cual es la pareja de
cada una. El navegador solo ve el texto de las cartas, nunca el emparejamiento.
"""

from . import base

JUEGO = {
    "id": "memoria",
    "titulo": "Memorama de Conceptos",
    "icono": "\U0001F0CF",
    "resumen": "Empareja cada concepto teorico con su formula o definicion.",
    "mecanica": "Voltea dos cartas: si hacen pareja, se quedan. Todas las cartas al final.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["conceptos", "memoria"],
}

PARES = [
    {"concepto": "EDO lineal de primer orden", "mate": r"y' + P(x)\,y = f(x)", "d": 1},
    {"concepto": "Ecuacion exacta", "mate": r"M\,dx + N\,dy = 0 \;\text{ con }\; \partial M/\partial y = \partial N/\partial x", "d": 1},
    {"concepto": "Factor integrante", "mate": r"\mu(x) = e^{\int P(x)\,dx}", "d": 1},
    {"concepto": "Forma separable", "mate": r"\dfrac{dy}{dx} = f(x)\,g(y)", "d": 1},
    {"concepto": "ED homogenea (no lineal)", "mate": r"\dfrac{dy}{dx} = F\!\left(\dfrac{y}{x}\right)", "d": 2},
    {"concepto": "Ecuacion de Bernoulli", "mate": r"y' + P(x)\,y = Q(x)\,y^{n}", "d": 1},
    {"concepto": "Ecuacion de Riccati", "mate": r"y' = a(x)y^{2} + b(x)y + c(x)", "d": 2},
    {"concepto": "Polinomio caracteristico", "mate": r"\lambda^{2} + a_{1}\lambda + a_{0} = 0", "d": 1},
    {"concepto": "ED parcial del calor (difusion)", "mate": r"\dfrac{\partial u}{\partial t} = \alpha\,\dfrac{\partial^{2}u}{\partial x^{2}}", "d": 2},
    {"concepto": "Autonoma", "mate": r"\dfrac{dy}{dx} = g(y) \quad (\text{sin } x \text{ expli\u0301cita})", "d": 2},
    {"concepto": "Orden de la ED", "mate": r"\text{grado de la derivada m\u00e1s alta presente}", "d": 1},
    {"concepto": "ED de Euler (Cauchy)", "mate": r"x^{2}y'' + a\,x\,y' + b\,y = 0", "d": 3},
    {"concepto": "Coeficiente de un sistema lineal", "mate": r"m = \det(A - \lambda I)", "d": 3},
    {"concepto": "Existencia y unicidad", "mate": r"|g'(x)| < 1 \quad \text{cerca de la ra\u00edz (punto fijo)}", "d": 3},
]

CANTIDAD_DE_PARES = {"facil": 4, "medio": 5, "dificil": 6}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [p for p in PARES if p["d"] <= limite]
    cuantos = min(CANTIDAD_DE_PARES[base.normalizar_nivel(nivel)], len(pool))
    salida = []
    for i in range(cantidad):
        elegidos = base.tomar(azar, pool, cuantos)
        cartas = []
        solucion = {}
        for j, par in enumerate(elegidos):
            id_a, id_b = f"r{i}a{j}", f"r{i}b{j}"
            cartas.append({"id": id_a, "cara": "concepto", "texto": par["concepto"]})
            cartas.append({"id": id_b, "cara": "mate", "texto": par["mate"]})
            solucion[id_a] = id_b
            solucion[id_b] = id_a
        salida.append({
            "id": f"r{i}",
            "cartas": base.barajar(azar, cartas),
            "solucion": solucion,
            "pares": cuantos,
            "errores_permitidos": 1 + limite,
        })
    return salida


def publico(ronda: dict) -> dict:
    return {"id": ronda["id"], "cartas": ronda["cartas"], "pares": ronda["pares"]}


def es_pareja(ronda: dict, id_a: str, id_b: str) -> bool:
    """El navegador no recibe la solucion: pregunta si dos cartas hacen pareja."""
    if id_a == id_b:
        return False
    return ronda["solucion"].get(id_a) == id_b


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = {"completas": n, "errores": m, "intentos": k}."""
    datos = respuesta if isinstance(respuesta, dict) else {}
    completas = max(0, min(int(datos.get("completas", 0) or 0), ronda["pares"]))
    errores = max(0, int(datos.get("errores", 0) or 0))
    permitidos = ronda["errores_permitidos"]
    completa = completas == ronda["pares"]
    if not completa:
        faltan = ronda["pares"] - completas
        return {
            "correcto": False,
            "puntaje": 0,
            "detalle": f"Te faltaron {faltan} pareja(s). El tablero se acaba: hay que unir todas.",
        }
    castigo = 15 * min(errores, permitidos + 3)
    detalle = f"Las {ronda['pares']} parejas salieron bien"
    detalle += f" con {errores} error(es) de memoria." if errores else " al primer intento."
    if errores > permitidos:
        detalle += " Demasiados errores para el nivel."
    return {
        "correcto": errores <= permitidos,
        "puntaje": max(20, base.PUNTAJE_MAX - castigo),
        "detalle": detalle,
    }
