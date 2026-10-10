"""globos.py — Minijuego 10: Tiro al Blanco Teorico (Target Pop).

Mecanica (Minijuegos.md #10): arriba hay una instruccion fija
("Explota las funciones que sean soluciones de y'' + y = 0") y suben globos
con funciones escritas. Hay que explotar SOLO los que cumplen, antes de que
salgan de la pantalla.

Detalle importante: NO se verifica por computadora si cada funcion es
solucion (eso seria calcular, y este juego es de teoria). Cada globo trae
declarado si cumple o no, y el servidor guarda la lista de los correctos
para calificar. Asi el jugador decide leyendo la ED, no resolviendo.

CONTENIDO: `data/minijuegos/globos.json` con:
  - "segundos": duracion de cada ronda.
  - "rondas": [{"instruccion","globos":[{"tex","cumple"}],"porque","d"}].
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "globos",
    "titulo": "Tiro al Blanco Teorico",
    "icono": "\U0001F3AF",
    "resumen": "Lee la instruccion y explota solo las funciones que son soluciones de la ED.",
    "mecanica": "Toca los globos que cumplen. Los demas te restan puntos.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["visual", "reaccion"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Toma rondas del JSON y guarda que globos son soluciones validas."""
    limite = base.nivel_limite(nivel)
    datos = base.contenido("globos")
    definiciones = datos.get("rondas", [])
    segundos = int(datos.get("segundos", 12))
    pool = [r for r in definiciones if r.get("d", 1) <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, ronda in enumerate(elegidos):
        globos = ronda["globos"]
        salida.append({
            "id": f"b{i}",
            "instruccion": ronda["instruccion"],
            "globos": [{"id": f"g{i}-{k}", "tex": g["tex"]}
                       for k, g in enumerate(globos)],
            "correctos": [f"g{i}-{k}" for k, g in enumerate(globos) if g["cumple"]],
            "porque": ronda["porque"],
            "segundos": segundos,
        })
    return salida


def publico(ronda: dict) -> dict:
    """Sin `correctos`: se manda solo el texto de cada globo."""
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
    # Puntaje combinado: que lo explotado sea bueno (precision) y que no
    # falte ninguno (recall).
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
