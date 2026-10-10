"""ordenar.py — Minijuego 7: Ordena la Secuencia (Algorithm Sort).

Mecanica (Minijuegos.md #7): aparecen los pasos logicos de un metodo
teorico completamente desordenados y hay que reacomodarlos en la secuencia
correcta arrastrando los bloques.

Los pasos son de procedimiento (no de calculo): "comprobar, calcular el
factor integrante, integrar, aplicar la condicion inicial"...

CONTENIDO: `data/minijuegos/ordenar.json` con "secuencias":
{"titulo","pasos","d"} (los "pasos" ya vienen en el orden correcto).
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "ordenar",
    "titulo": "Ordena la Secuencia",
    "icono": "\U0001F524",
    "resumen": "Reacomoda los pasos de un metodo en el orden logico correcto.",
    "mecanica": "Arrastra los bloques hasta que hagan sentido de principio a fin.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["procedimiento", "metodos"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Toma secuencias del JSON y desordena los pasos para mostrarlos."""
    limite = base.nivel_limite(nivel)
    secuencias = base.contenido("ordenar").get("secuencias", [])
    pool = [s for s in secuencias if s.get("d", 1) <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, secuencia in enumerate(elegidos):
        pasos = secuencia["pasos"]
        indices = list(range(len(pasos)))
        salida.append({
            "id": f"o{i}",
            "titulo": secuencia["titulo"],
            "pasos": pasos,
            "orden_mostrado": base.barajar(azar, indices),
            "solucion": list(range(len(pasos))),
            "pista": f"Son {len(pasos)} pasos.",
        })
    return salida


def publico(ronda: dict) -> dict:
    """Muestra los pasos ya barajados; `solucion` se queda en el servidor."""
    return {
        "id": ronda["id"],
        "titulo": ronda["titulo"],
        "pasos": [ronda["pasos"][i] for i in ronda["orden_mostrado"]],
        "total": len(ronda["pasos"]),
        "pista": ronda["pista"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = lista con el indice (en el orden mostrado) de cada paso,
    ya en el orden que quedo en pantalla."""
    if not isinstance(respuesta, (list, tuple)):
        respuesta = []
    orden = ronda["orden_mostrado"]
    elegido = [int(v) for v in respuesta if str(v).lstrip("-").isdigit()]
    correctas = 0
    for posicion, paso in enumerate(ronda["solucion"]):
        if posicion < len(elegido):
            indice_real = orden[elegido[posicion]]
            if indice_real == paso:
                correctas += 1
    total = len(ronda["solucion"])
    detalle = "La secuencia quedo perfecta." if correctas == total else \
        f"{correctas} de {total} pasos en su lugar. El orden correcto es: " + \
        " ".join(f"{i + 1}) {ronda['pasos'][p]}" for i, p in enumerate(ronda["solucion"]))
    return {
        "correcto": correctas == total,
        "puntaje": base.puntos(correctas / total if total else 0),
        "detalle": detalle,
        "correctas": correctas,
        "total": total,
    }
