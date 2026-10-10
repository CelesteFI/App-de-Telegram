"""memoria.py — Minijuego 2: Memorama de Conceptos (ED Memory).

Mecanica (Minijuegos.md #2): tablero de cartas boca abajo. Hay que emparejar
un concepto teorico con su contraparte matematica (o al reves).

El servidor reparte las cartas mezcladas y se guarda cual es la pareja de
cada una. El navegador solo ve el texto de las cartas, nunca el emparejamiento.

CONTENIDO: `data/minijuegos/memoria.json` con:
  - "pares": [{"concepto","mate","d"}], una pareja por elemento.
  - "cantidad_por_nivel": {"facil": n, "medio": n, "dificil": n}.
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "memoria",
    "titulo": "Memorama de Conceptos",
    "icono": "\U0001F0CF",
    "resumen": "Empareja cada concepto teorico con su formula o definicion.",
    "mecanica": "Voltea dos cartas: si hacen pareja, se quedan. Todas las cartas al final.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["conceptos", "memoria"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Reparte `cantidad` tableros de `cuantos` parejas, cartas ya mezcladas."""
    limite = base.nivel_limite(nivel)
    datos = base.contenido("memoria")
    pares = datos.get("pares", [])
    cantidades = datos.get("cantidad_por_nivel", {})
    pool = [p for p in pares if p.get("d", 1) <= limite]
    cuantos = min(int(cantidades.get(base.normalizar_nivel(nivel), 4)), len(pool))
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
    """Sin `solucion`: el emparejamiento se queda en el servidor."""
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
    # Cada error de memoria cuesta 15 puntos (con tope, para no llegar a 0).
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
