"""grafico.py — Minijuego 8: El Grafico Falso (Direction Field Spy).

Mecanica (Minijuegos.md #8): se muestra una ED lineal de primer orden muy
simple o autonoma y tres campos de direcciones (campos de pendientes). Hay
que tocar el campo que representa el comportamiento teorico de las soluciones.

Aqui no se resuelve NADA: cada campo es un "tipo" declarado (horizontal, en
bandas, circular...) y el navegador sabe pintarlo en un canvas. El servidor
solo dice cual tipo es el correcto.

Los tipos que el navegador sabe dibujar (deben coincidir con `CAMPOS` de
webapp/js/juegos/grafico.js):

    todo_horizontal  pendientes 0 en todas partes               (y' = 0)
    constante        todas las pendientes iguales               (y' = 1)
    bandas_y         la pendiente depende de y                  (y' = y)
    bandas_y_neg     la pendiente depende de y, con signo opuesto (y' = -y)
    verticales_x     la pendiente depende de x                  (y' = x)
    creciente_x      crece con |x| y pasa por cero              (y' = x^2 - 1)
    circular         tangentes a las circunferencias            (y' = -x/y)
    seno             oscila con x                               (y' = cos x)
    pendiente_alta   casi vertical en un lado del eje           (y' = 5x)
    divergente       patron asimetrico                          (y' = x + 2y)

CONTENIDO: `data/minijuegos/grafico.json` con "casos":
{"ecuacion","correcto","distractores","porque","d"}.
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "grafico",
    "titulo": "El Grafico Falso",
    "icono": "\U0001F5A5",
    "resumen": "Mira los campos de pendientes y elige el que corresponde a la ED.",
    "mecanica": "Tres campos de pendientes, una ED. Toca el campo correcto.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["visual", "intuicion"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Toma casos del JSON y baraja el tipo correcto con sus distractores."""
    limite = base.nivel_limite(nivel)
    casos = base.contenido("grafico").get("casos", [])
    pool = [c for c in casos if c.get("d", 1) <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, caso in enumerate(elegidos):
        correcto = caso["correcto"]
        tipos = base.barajar(azar, [correcto] + list(caso.get("distractores", [])))
        salida.append({
            "id": f"g{i}",
            "ecuacion": caso["ecuacion"],
            "tipos": tipos,
            "solucion": tipos.index(correcto),
            "porque": caso["porque"],
        })
    return salida


def publico(ronda: dict) -> dict:
    """Sin `solucion`: el tipo correcto se queda en el servidor."""
    return {"id": ronda["id"], "ecuacion": ronda["ecuacion"], "tipos": ronda["tipos"]}


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = indice del campo tocado."""
    try:
        elegido = int(respuesta)
    except (TypeError, ValueError):
        elegido = -1
    ok = elegido == ronda["solucion"]
    return {
        "correcto": ok,
        "puntaje": 100 if ok else 0,
        "detalle": ("Correcto: " if ok else "Ese campo no corresponde. ") + ronda["porque"],
        "tipo_real": ronda["tipos"][ronda["solucion"]],
    }
