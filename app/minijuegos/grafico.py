"""grafico.py — Minijuego 8: El Grafico Falso (Direction Field Spy).

Mecanica (Minijuegos.md #8): se muestra una ED lineal de primer orden muy
simple o autonoma y tres campos de direcciones (campos de pendientes). Hay
que tocar el campo que representa el comportamiento teorico de las soluciones.

Aqui no se resuelve NADA: cada campo es un "tipo" declarado (horizontal, en
bandas, circular...) y el navegador sabe pintarlo en un canvas. El servidor
solo dice cual tipo es el correcto.

Los tipos que el navegador sabe dibujar (deben coincidir con `CAMPOS` de
webapp/js/minijuegos/grafico.js):

    todo_horizontal  pendientes 0 en todas partes              (y' = 0)
    constante        todas las pendientes iguales               (y' = 1)
    bandas_y         la pendiente depende de y                  (y' = y)
    bandas_y_neg     la pendiente depende de y, con signo opuesto (y' = -y)
    verticales_x     la pendiente depende de x                  (y' = x)
    creciente_x      crece con |x| y pasa por cero              (y' = x^2 - 1)
    circular         tangentes a las circunferencias             (y' = -x/y)
    seno             oscila con x                               (y' = cos x)
    pendiente_alta   casi vertical en un lado del eje            (y' = 5x)
    divergente       patron asimetrico                          (y' = x + 2y)
"""

from . import base

JUEGO = {
    "id": "grafico",
    "titulo": "El Grafico Falso",
    "icono": "\U0001F5A5",
    "resumen": "Mira los campos de pendientes y elige el que corresponde a la ED.",
    "mecanica": "Tres campos de pendientes, una ED. Toca el campo correcto.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["visual", "intuicion"],
}

# (ecuacion, tipo correcto, distractores, explicacion, dificultad)
CASOS = [
    (r"\dfrac{dy}{dx} = 0", "todo_horizontal", ["circular", "seno"],
     r"La derivada es 0 en todo punto: las soluciones son rectas horizontales $y = C$.", 1),
    (r"\dfrac{dy}{dx} = y", "bandas_y", ["todo_horizontal", "verticales_x"],
     r"La pendiente depende de $y$: horizontal sobre el eje $x$, positiva arriba y negativa abajo.", 1),
    (r"\dfrac{dy}{dx} = -y", "bandas_y_neg", ["todo_horizontal", "bandas_y"],
     r"La pendiente se opone al valor de $y$: hacia abajo por encima del eje y hacia abajo... (hacia el eje) por debajo.", 1),
    (r"\dfrac{dy}{dx} = x", "verticales_x", ["bandas_y", "circulo"],
     r"Aqui la pendiente depende de $x$: las flechas son constantes en cada columna vertical.", 2),
    (r"\dfrac{dy}{dx} = \dfrac{-x}{y}", "circular", ["bandas_y", "verticales_x"],
     r"Es la ED de las circunferencias centradas en el origen: $x^2 + y^2 = C$.", 2),
    (r"\dfrac{dy}{dx} = \cos x", "seno", ["todo_horizontal", "verticales_x"],
     r"La pendiente solo depende de $x$ y oscila entre -1 y 1.", 2),
    (r"\dfrac{dy}{dx} = 1", "constante", ["verticales_x", "seno"],
     r"Todas las pendientes valen 1: rectas de pendiente 1.", 1),
    (r"\dfrac{dy}{dx} = x^{2} - 1", "creciente_x", ["todo_horizontal", "bandas_y"],
     r"La pendiente depende de $x$ y se anula en $x = \pm 1$.", 3),
    (r"\dfrac{dy}{dx} = x + 2y", "divergente", ["todo_horizontal", "constante"],
     r"Depende de $x$ y de $y$: el patron no es ni de columnas ni de bandas.", 3),
    (r"\dfrac{dy}{dx} = 5x", "pendiente_alta", ["todo_horizontal", "constante"],
     r"La pendiente se hace muy grande en valor absoluto: el campo se ve casi vertical lejos del eje $y$.", 3),
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [c for c in CASOS if c[4] <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, (ecuacion, correcto, distractores, porque, _d) in enumerate(elegidos):
        tipos = base.barajar(azar, [correcto] + list(distractores))
        salida.append({
            "id": f"g{i}",
            "ecuacion": ecuacion,
            "tipos": tipos,
            "solucion": tipos.index(correcto),
            "porque": porque,
        })
    return salida


def publico(ronda: dict) -> dict:
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
