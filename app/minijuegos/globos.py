"""globos.py — Minijuego 10: Tiro al Blanco Teorico (Target Pop).

Mecanica (Minijuegos.md #10): arriba hay una instruccion fija
("Explota las funciones que sean soluciones de y'' + y = 0") y suben globos
con funciones escritas. Hay que explotar SOLO los que cumplen, antes de que
salgan de la pantalla.

Detalle importante: NO se verifica por computadora si cada funcion es
solución (eso seria calcular, y este juego es de teoria). Cada globo trae
declarado si cumple o no, y el servidor guarda la lista de los correctos
para calificar. Asi el jugador decide leyendo la ED, no resolviendo.
"""

from . import base

JUEGO = {
    "id": "globos",
    "titulo": "Tiro al Blanco Teorico",
    "icono": "\U0001F3AF",
    "resumen": "Lee la instruccion y explota solo las funciones que son soluciones de la ED.",
    "mecanica": "Toca los globos que cumplen. Los demas te restan puntos.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["visual", "reaccion"],
}

# (instruccion, [(funcion, cumple)], explicacion, dificultad)
RONDAS = [
    (r"Explota las funciones que sean soluciones de $y'' + y = 0$",
     [(r"\sin x", True), (r"\cos x", True), (r"e^{x}", False), (r"x^{2}", False)],
     r"El polinomio $\lambda^{2}+1=0$ tiene raices $\pm i$: las soluciones son combinaciones de $\sin x$ y $\cos x$.",
     1),

    (r"Explota las funciones que sean soluciones de $y' = y$",
     [(r"e^{x}", True), (r"x", False), (r"\sin x", False), (r"x^{2}", False)],
     r"Para $y'=y$ la unica familia de soluciones es $Ce^{x}$.", 1),

    (r"Explota las funciones que sean soluciones de $y' = 0$",
     [(r"5", True), (r"-3", True), (r"x", False), (r"x^{2}", False)],
     r"$y'=0$ significa pendiente cero: las soluciones son constantes $y = C$.", 1),

    (r"Explota las funciones que sean soluciones de $y'' - 2y' + y = 0$",
     [(r"x\,e^{x}", True), (r"e^{x}", True), (r"e^{2x}", False), (r"x", False)],
     r"Raiz doble $\lambda = 1$: las soluciones son $(C_1 + C_2x)e^{x}$.", 2),

    (r"Explota las funciones que sean soluciones de $y'' + 4y = 0$",
     [(r"\sin 2x", True), (r"\cos 2x", True), (r"e^{x}", False), (r"x", False)],
     r"$\lambda^{2}+4=0$ da $\lambda = \pm 2i$: aparecen $\sin 2x$ y $\cos 2x$.", 2),

    (r"Explota las funciones que sean soluciones de $y' = \cos x$",
     [(r"\sin x", True), (r"-\cos x", False), (r"\cos x", False), (r"x", False)],
     r"Hay que derivar cada globo y ver cual da exactamente $\cos x$.", 2),

    (r"Explota las funciones que sean soluciones de $y'' + y' = 0$",
     [(r"1", True), (r"e^{-x}", True), (r"x", False), (r"e^{x}", False)],
     r"$\lambda(\lambda + 1) = 0$: raices 0 y -1, o sea $C_1 + C_2 e^{-x}$.", 3),

    (r"Explota las funciones que sean soluciones de $y'' = 0$",
     [(r"3x + 2", True), (r"x^{2}", False), (r"e^{x}", False), (r"\sin x", False)],
     r"$y''=0$ integrated da rectas $y = ax + b$.", 3),
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [r for r in RONDAS if r[3] <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, (instruccion, globos, porque, _d) in enumerate(elegidos):
        salida.append({
            "id": f"b{i}",
            "instruccion": instruccion,
            "globos": [{"id": f"g{i}-{k}", "tex": tex}
                       for k, (tex, _cumple) in enumerate(globos)],
            "correctos": [f"g{i}-{k}" for k, (_tex, cumple) in enumerate(globos) if cumple],
            "porque": porque,
            "segundos": 12,
        })
    return salida


def publico(ronda: dict) -> dict:
    return {
        "id": ronda["id"],
        "instruccion": ronda["instruccion"],
        "globos": ronda["globos"],
        "segundos": ronda["segundos"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = lista de ids de globos explotados (en cualquier orden)."""
    if isinstance(respuesta, dict):
        respuesta = respuesta.get("ids", [])
    if not isinstance(respuesta, (list, tuple)):
        respuesta = []
    explotados = {str(x) for x in respuesta}
    correctos = set(ronda["correctos"])
    aciertos = len(explotados & correctos)
    falsos = len(explotados - correctos)
    perdidos = len(correctos - explotados)
    total = len(correctos)
    precision = aciertos / len(explotados) if explotados else 0.0
    recall = aciertos / total if total else 0.0
    valor = 0.55 * precision + 0.45 * recall
    if not explotados:
        detalle = f"No explotaste nada: la instruccion pedia las soluciones de la ED. {ronda['porque']}"
    elif falsos:
        detalle = f"{aciertos} correctos, {falsos} falsos positivos y {perdidos} sin explotar. {ronda['porque']}"
    elif perdidos:
        detalle = f"Acertaste {aciertos} de {total}. {ronda['porque']}"
    else:
        detalle = f"¡Todas las soluciones de la ED! {ronda['porque']}"
    return {
        "correcto": not falsos and not perdidos,
        "puntaje": base.puntos(valor),
        "detalle": detalle,
        "aciertos": aciertos,
        "falsos": falsos,
        "perdidos": perdidos,
        "total": total,
    }
