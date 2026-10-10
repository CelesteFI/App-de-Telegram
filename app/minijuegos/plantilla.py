"""plantilla.py — Molde para crear un minijuego nuevo. NO se carga como juego.

Copia este archivo como `<id>.py` en `app/minijuegos/`, cambia la clave `id`
por el mismo nombre y rellena las cuatro piezas. No hay que registrar nada:
`app/minijuegos/registro.py` descubre los `.py` de la carpeta al arrancar.

Las tres funciones son obligatorias:

    rondas(azar, nivel, cantidad, tema) -> list[dict]
        Aqui pones la informacion (preguntas, pares, palabras...). Cada ronda
        debe llevar su solucion, porque `califica` la necesita.

    publico(ronda) -> dict
        Lo que viaja al navegador. Si no lo declaras aqui, la solucion se
        regalaria: revisa que no devuelvas el campo solucion.

    califica(ronda, respuesta) -> dict
        {"correcto": bool, "puntaje": 0..100, "detalle": "texto para el jugador"}

Ademas puedes exponer `pista(ronda)` con una pista que el jugador pide si se
equivoca, y `niveles` dentro de JUEGO para limitar los niveles validos.
"""

JUEGO = {
    "id": "plantilla",
    "titulo": "Minijuego de ejemplo",
    "icono": "\U0001F9EA",
    "resumen": "Una frase para el catalogo de la app.",
    "mecanica": "El jugador hace esto, con estos controles.",
    "niveles": ["facil", "medio", "dificil"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    return [
        {
            "id": "r1",
            "texto": "Primera ronda",
            "opciones": ["A", "B", "C"],
            "solucion": 1,
        }
    ]


def publico(ronda: dict) -> dict:
    return {"id": ronda["id"], "texto": ronda["texto"], "opciones": ronda["opciones"]}


def califica(ronda: dict, respuesta) -> dict:
    elegida = int(respuesta) if str(respuesta).lstrip("-").isdigit() else -1
    ok = elegida == ronda["solucion"]
    return {
        "correcto": ok,
        "puntaje": 100 if ok else 0,
        "detalle": "Correcto." if ok else f"La respuesta era {ronda['opciones'][ronda['solucion']]}.",
    }
