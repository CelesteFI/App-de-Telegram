"""completar.py — Minijuego 4: Completa la Forma Estandar (Fill the Blank).

Mecanica (Minijuegos.md #4): se muestra la estructura teorica de un
teorema o de una ecuacion clasica con una pieza faltante, y abajo hay tres
opciones para arrastrar (o tocar) en el hueco.

En el enunciado el hueco se escribe como `___` y las opciones son de una
palabra o de un simbolo: no hay que calcular nada, hay que recordar la
estructura correcta.

CONTENIDO: `data/minijuegos/completar.json` con "casos":
{"enunciado","opciones","correcta","porque","d"} (correcta = indice).
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "completar",
    "titulo": "Completa la Forma Estandar",
    "icono": "\U0001F4D6",
    "resumen": "Elige el pedazo que falta en la estructura de la teoria.",
    "mecanica": "Lee el enunciado con el hueco, elige una de las 3 piezas y suelta en el hueco.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["teoria", "estructuras"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Toma casos del JSON y vuelve a barajar las opciones en cada ronda."""
    limite = base.nivel_limite(nivel)
    casos = base.contenido("completar").get("casos", [])
    pool = [c for c in casos if c.get("d", 1) <= limite]
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
    """Sin `solucion`: el indice correcto se queda en el servidor."""
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
