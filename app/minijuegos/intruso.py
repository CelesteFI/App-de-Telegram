"""intruso.py — Minijuego 5: El Intruso (Odd One Out).

Mecanica (Minijuegos.md #5): cuatro tarjetas, tres comparten una caracteristica
teorica estricta y una no pertenece al grupo. Hay que tocar al intruso.

Cada conjunto esta construido para que SOLO una tarjeta se salga de la
propiedad que anuncia la pista (por ejemplo: "casi todas son exactas" revisa
las derivadas parciales de las cuatro).

CONTENIDO: `data/minijuegos/intruso.json` con "conjuntos":
{"pista","tarjetas","intruso","porque","d"} (intruso = indice 0..3).
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "intruso",
    "titulo": "El Intruso",
    "icono": "\U0001F50E",
    "resumen": "Cuatro ecuaciones, una se sale de la regla. ¿Cual?",
    "mecanica": "Lee la pista, revisa las cuatro tarjetas y toca la que no cumple.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["clasificacion", "rapidito"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Toma conjuntos del JSON y mezcla las tarjetas de cada uno."""
    limite = base.nivel_limite(nivel)
    conjuntos = base.contenido("intruso").get("conjuntos", [])
    pool = [c for c in conjuntos if c.get("d", 1) <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, conjunto in enumerate(elegidos):
        tarjetas = conjunto["tarjetas"]
        intruso = int(conjunto["intruso"])
        orden = list(range(len(tarjetas)))
        azar.shuffle(orden)
        salida.append({
            "id": f"i{i}",
            "pista": conjunto["pista"],
            "tarjetas": [{"id": f"t{k}", "tex": tarjetas[k]} for k in orden],
            "solucion": orden.index(intruso),
            "porque": conjunto["porque"],
        })
    return salida


def publico(ronda: dict) -> dict:
    """Sin `solucion`: la posicion del intruso se queda en el servidor."""
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
