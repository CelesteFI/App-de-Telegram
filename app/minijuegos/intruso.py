"""intruso.py — Minijuego 5: El Intruso (Odd One Out).

Mecanica (Minijuegos.md #5): cuatro tarjetas, tres comparten una caracteristica
teorica estricta y una no pertenece al grupo. Hay que tocar al intruso.

Cada conjunto esta construido para que SOLO una tarjeta se salga de la
propiedad que anuncia la pista (por ejemplo: "casi todas son exactas" revisa
las derivadas parciales de las cuatro).
"""

from . import base

JUEGO = {
    "id": "intruso",
    "titulo": "El Intruso",
    "icono": "\U0001F50E",
    "resumen": "Cuatro ecuaciones, una se sale de la regla. ¿Cual?",
    "mecanica": "Lee la pista, revisa las cuatro tarjetas y toca la que no cumple.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["clasificacion", "rapidito"],
}

# (pista, [4 tarjetas], indice del intruso, explicacion, dificultad)
CONJUNTOS = [
    ("Tres son lineales homogeneas de primer orden",
     [r"y' + 3y = 0", r"y' - 5y = 0", r"y' + x\,y = 0", r"y'' + y = 0"], 3,
     r"La cuarta es de segundo orden.", 1),

    ("Tres son separables",
     [r"y' = x\,y", r"y' = \sin y", r"y' = x + y", r"y' = x\,y^{2}"], 2,
     r"$y' = x + y$ no se puede escribir como producto $f(x)g(y)$.", 1),

    ("Tres son lineales de primer orden",
     [r"y' + y = 0", r"y' + 2y = x", r"y' + y\tan y = 0", r"y' + x\,y = e^{x}"], 2,
     r"$\tan y$ depende de la incognita.", 2),

    ("Tres son exactas",
     [r"y\,dx + x\,dy = 0", r"(1+y^{2})\,dx + 2xy\,dy = 0", r"(2xy + e^{x})\,dx + x^{2}\,dy = 0",
      r"-y\,dx + x\,dy = 0"], 3,
     r"En la ultima $\partial M/\partial y = -1 \ne 1 = \partial N/\partial x$.", 2),

    ("Tres son de segundo orden",
     [r"y'' + y' + y = 0", r"y'' - y = x", r"y''' - y = 0", r"y^{(4)} + y = 0"], 2,
     r"$y'''$ es de tercer orden.", 1),

    ("Tres son homogeneas de tipo no lineal ($y' = F(y/x)$)",
     [r"y' = \dfrac{y}{x}", r"y' = 1 + \dfrac{y}{x}", r"y' = x + y",
      r"y' = \dfrac{x^{2} + y^{2}}{xy}"], 2,
     r"$x$ y $y$ no se pueden agrupar como $F(y/x)$.", 3),

    ("Tres son ED parciales",
     [r"\partial u/\partial t = \alpha\,\partial^{2}u/\partial x^{2}",
      r"\partial^{2}u/\partial x^{2} + \partial^{2}u/\partial y^{2} = 0",
      r"dy/dx = y", r"\partial u/\partial t = u"], 2,
     r"$dy/dx$ son derivadas ordinarias: es una EDO.", 1),

    ("Tres son autonomas (no aparece $x$)",
     [r"y' = y^{2} - 1", r"y' = \sin y", r"y' = x\,y", r"y' = -y + 3"], 2,
     r"$x$ aparece de forma explicita.", 1),

    ("Tres son de tipo Bernoulli",
     [r"y' + y = x\,y^{2}", r"y' + 2y = e^{x}\,y^{3}", r"y' + y\ln y = 0",
      r"y' + \frac{1}{x}y = x^{2}\,y^{4}"], 2,
     r"$y\ln y$ no tiene la forma $Q(x)y^{n}$.", 2),

    ("Tres son lineales de segundo orden con coeficientes constantes",
     [r"y'' + 3y' + 2y = 0", r"y'' - y = 0", r"y'' + p(x)y' + q(x)y = f(x)", r"y'' + y' + y = x"], 2,
     r"Los coeficientes dependen de $x$, no son constantes.", 3),

    ("Tres son de tipo Riccati",
     [r"y' = y^{2} + y + x", r"y' = y^{2} - 1", r"y' = y^{3} + y", r"y' = x\,y^{2} + x"], 2,
     r"El grado 3 en $y$ no es Riccati.", 2),

    ("Tres son lineales homogeneas (con segundo miembro 0)",
     [r"y' + 3y = 0", r"y' - y = 0", r"y' + y = x", r"y' + 5y = 0"], 2,
     r"$x \ne 0$ como segundo miembro la hace no homogenea.", 1),
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [c for c in CONJUNTOS if c[4] <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, (pista, tarjetas, intruso, porque, _d) in enumerate(elegidos):
        orden = list(range(len(tarjetas)))
        azar.shuffle(orden)
        salida.append({
            "id": f"i{i}",
            "pista": pista,
            "tarjetas": [{"id": f"t{k}", "tex": tarjetas[k]} for k in orden],
            "solucion": orden.index(intruso),
            "porque": porque,
        })
    return salida


def publico(ronda: dict) -> dict:
    return {"id": ronda["id"], "pista": ronda["pista"], "tarjetas": ronda["tarjetas"]}


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = indice (0..3) de la tarjeta tocada."""
    try:
        elegido = int(respuesta)
    except (TypeError, ValueError):
        elegido = -1
    ok = elegido == ronda["solucion"]
    return {
        "correcto": ok,
        "puntaje": 100 if ok else 0,
        "detalle": "Correcto: " + ronda["porque"] if ok else "Ese no era el intruso. " + ronda["porque"],
        "intrusa": ronda["tarjetas"][ronda["solucion"]]["tex"],
    }
