"""columnas.py — Minijuego 3: Relacion de Columnas (Method Match).

Mecanica (Minijuegos.md #3): dos columnas fijas. A la izquierda, formas de
ecuaciones diferenciales; a la derecha, el metodo analitico que las resuelve.
Se unen arrastrando (o tocando) un nodo con otro.

El servidor mezcla ambas columnas y guarda el emparejamiento correcto; el
navegador nunca recibe la solucion.

CONTENIDO: `data/minijuegos/columnas.json` con "tableros": una lista de
tableros y, dentro, filas {"izq","der","porque","d"}.
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "columnas",
    "titulo": "Relacion de Columnas",
    "icono": "\U0001F517",
    "resumen": "Une cada forma de ecuacion diferencial con el metodo que la resuelve.",
    "mecanica": "Toca una ecuacion y despues el metodo que le corresponde. Une todas.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["metodos", "emparejar"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Elige `cantidad` tableros cuyo peor caso no pase la dificultad pedida."""
    limite = base.nivel_limite(nivel)
    tableros = base.contenido("columnas").get("tableros", [])
    salida = []
    for i in range(cantidad):
        candidatos = [t for t in tableros if max(f.get("d", 1) for f in t) <= limite]
        tablero = azar.choice(candidatos) if candidatos else azar.choice(tableros)
        izquierda = [f["izq"] for f in tablero]
        derecha = [f["der"] for f in tablero]
        solucion = {str(j): derecha.index(f["der"]) for j, f in enumerate(tablero)}
        salida.append({
            "id": f"c{i}",
            "izquierda": izquierda,
            "derecha": base.barajar(azar, derecha),
            "solucion": solucion,
            "porque": [f["porque"] for f in tablero],
        })
    return salida


def publico(ronda: dict) -> dict:
    """La columna derecha va mezclada y sin `solucion`."""
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
