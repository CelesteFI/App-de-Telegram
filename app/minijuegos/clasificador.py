"""clasificador.py — Minijuego 6: Clasificador Rapido (Category Bin).

Mecanica (Minijuegos.md #6): abajo hay 2 o 3 canastas fijas (las categorias
de ED). Van apareciendo ecuaciones y hay que arrastrar cada una a la canasta
correcta antes de que se acabe el tiempo de la ronda.

Solo hay que RECONOCER la estructura de la ecuacion: separarla, ver si es
exacta por derivadas parciales, etc. Ninguna ronda pide integrate ni despejar.

Cuidado con las ecuaciones que son de dos tipos a la vez (`y' = y/x` es
homogenea Y separable): esas quedaron fuera del pozo a proposito, para que
una ronda nunca tenga una respuesta ambigua.
"""

from . import base

JUEGO = {
    "id": "clasificador",
    "titulo": "Clasificador Rapido",
    "icono": "\U0001F9EA",
    "resumen": "Arrastra cada ecuacion a la canasta del tipo que le corresponde.",
    "mecanica": "Canastas abajo, ecuaciones en el centro. Sueltala antes de que se acabe el tiempo.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["clasificacion", "contrarreloj"],
}

# ecuacion -> categoria
POZO = {
    "separable": [
        r"y' = x^{2}y", r"y' = \sin y", r"y' = e^{y}", r"y' = \dfrac{y}{1+x}",
        r"y' = y^{2}\cos x", r"y' = \dfrac{1+y^{2}}{e^{x}}", r"y' = \dfrac{y}{\sqrt{1+x^{2}}}",
    ],
    "homogenea": [
        r"y' = 1 + \dfrac{y}{x}", r"y' = \dfrac{x^{2}+y^{2}}{xy}",
        r"y' = \dfrac{y^{2}-x^{2}}{xy}", r"y' = \tan\!\left(\dfrac{y}{x}\right)",
        r"y' = \dfrac{x^{2}}{y} + y",
    ],
    "exacta": [
        r"y\,dx + x\,dy = 0", r"(1+y^{2})\,dx + 2xy\,dy = 0",
        r"(2xy + e^{x})\,dx + x^{2}\,dy = 0",
        r"-\sin x\,dx + \cos y\,dy = 0",
        r"x^{2}\,dx + y^{2}\,dy = 0",
    ],
    "lineal1": [
        r"y' + 3y = x", r"y' - y = e^{x}", r"y' + x\,y = 1", r"y' + 2y = 5",
        r"y' + \frac{y}{x} = \ln x", r"y' + y = e^{x}\cos x",
    ],
    "nolineal": [
        r"y' = y\tan y", r"y' = \frac{x}{y}", r"y' = y^{3} + 1", r"y' + y\ln y = 0",
        r"y'' = y'^{2}", r"y' = \sqrt{1+y^{2}}",
    ],
    "bernoulli": [
        r"y' + y = x\,y^{2}", r"y' + 2y = e^{x}\,y^{3}",
        r"y' + \frac{1}{x}y = x^{2}\,y^{4}", r"y' + y = x\,y^{-1}",
    ],
    "orden1": [
        r"y' + y = e^{x}", r"y' = x\,y", r"x\,y' = y^{2}", r"y' + y\ln y = 0",
    ],
    "orden2": [
        r"y'' + y' + y = 0", r"y'' - 4y = 0", r"(y')^{2} + y'' = 0",
        r"y'' + p(x)y' + q(x)y = f(x)", r"y'' = y\,y'",
    ],
    "orden3": [
        r"y''' - y = 0", r"y''' + y' = x", r"\frac{d^{3}y}{dx^{3}} = y^{2}",
        r"y^{(4)} + y = 0",
    ],
}

# nombre visible de cadaroticidad
ETIQUETAS = {
    "separable": "Separable",
    "homogenea": "Homogenea",
    "exacta": "Exacta",
    "lineal1": "Lineal 1er orden",
    "nolineal": "No lineal",
    "bernoulli": "Bernoulli",
    "orden1": "Orden 1",
    "orden2": "Orden 2",
    "orden3": "Orden 3",
}

# canastas -> (categorias, cuantas ecuaciones por ronda, segundos, dificultad)
RONDAS = [
    (["separable", "homogenea", "exacta"], 6, 45, 1),
    (["lineal1", "nolineal"], 6, 35, 1),
    (["orden1", "orden2", "orden3"], 6, 35, 2),
    (["separable", "bernoulli"], 6, 40, 2),
    (["lineal1", "separable", "homogenea", "exacta"], 8, 45, 3),
    (["bernoulli", "nolineal"], 6, 40, 3),
]

EXPLICAR = {
    "separable": r"$y' = f(x)\,g(y)$: se separan las variables.",
    "homogenea": r"$y' = F(y/x)$: el lado derecho solo depende de $y/x$.",
    "exacta": r"$\partial M/\partial y = \partial N/\partial x$.",
    "lineal1": r"$y' + P(x)y = f(x)$.",
    "nolineal": r"La incognita aparece de otra forma (logaritmo, raiz, potencia > 1, producto).",
    "bernoulli": r"$y' + P(x)y = Q(x)y^{n}$ con $n \ne 1$.",
    "orden1": r"Mayor derivada: $y'$.",
    "orden2": r"Mayor derivada: $y''$.",
    "orden3": r"Mayor derivada: $y'''$.",
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    candidatos = [r for r in RONDAS if r[3] <= limite] or RONDAS[:1]
    salida = []
    for i in range(cantidad):
        categorias, por_cat, segundos, _d = azar.choice(candidatos)
        elegidas = []
        for cat in categorias:
            for tex in base.tomar(azar, POZO[cat], max(2, por_cat // 2)):
                elegidas.append({"id": f"{i}-{len(elegidas)}", "tex": tex, "cat": cat})
        base.barajar(azar, elegidas)
        salida.append({
            "id": f"k{i}",
            "canastas": [{"clave": c, "nombre": ETIQUETAS[c]} for c in categorias],
            "items": elegidas,
            "segundos": segundos,
        })
    return salida


def publico(ronda: dict) -> dict:
    return {
        "id": ronda["id"],
        "canastas": ronda["canastas"],
        "items": [{"id": it["id"], "tex": it["tex"]} for it in ronda["items"]],
        "segundos": ronda["segundos"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = lista con la clave de la canasta elegida por cada item,
    en el mismo orden en que los recibiste."""
    if isinstance(respuesta, dict):
        elegido_por_id = {str(k): str(v) for k, v in respuesta.items()}
    elif isinstance(respuesta, (list, tuple)):
        elegido_por_id = {it["id"]: str(respuesta[i]) for i, it in enumerate(ronda["items"])
                          if i < len(respuesta)}
    else:
        elegido_por_id = {}
    acertados = [it for it in ronda["items"] if elegido_por_id.get(it["id"]) == it["cat"]]
    fallados = [it for it in ronda["items"] if elegido_por_id.get(it["id"]) != it["cat"]]
    total = len(ronda["items"])
    ejemplos = "; ".join(f"`{it['tex']}` era {ETIQUETAS[it['cat']]} ({EXPLICAR[it['cat']]})"
                         for it in fallados[:3])
    detalle = (f"Las {total} ecuaciones quedaron en su canasta." if not fallados
               else f"{len(acertados)} de {total} bien clasificadas. {ejemplos}")
    return {
        "correcto": not fallados,
        "puntaje": base.puntos(len(acertados) / total if total else 0),
        "detalle": detalle,
        "aciertos": len(acertados),
        "total": total,
        "fallados": [{"id": it["id"], "cat": ETIQUETAS[it["cat"]]} for it in fallados],
    }
