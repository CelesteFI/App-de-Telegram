"""base.py — Contrato comun de un minijuego + utilidades de azar.

Un minijuego es un modulo `.py` de esta carpeta que expone:

    JUEGO = {
        "id": "deslizador",         # mismo nombre del archivo, sin .py
        "titulo": "Desliza el Atributo",
        "icono": "\U0001F504",
        "resumen": "...",
        "mecanica": "que hace el jugador (una frase)",
        "niveles": ["facil", "medio", "dificil"],
    }

    def rondas(azar, nivel, cantidad, tema=None) -> list[dict]
        Arma N rondas YA RESUELTAS (cada una con su solucion dentro).

    def publico(ronda) -> dict
        Lo que se manda al navegador (nunca debe incluir la solucion).

    def califica(ronda, respuesta) -> dict
        {"correcto": bool, "puntaje": 0..100, "detalle": "...", ...}

Regla de oro: la respuesta correcta se decide aqui, en Python, y se califica
en el servidor. El navegador solo manda lo que el jugador eligio.

El CONTENIDO (casos, pares, pasos...) ya no vive en el .py: cada minijuego lo
lee de `data/minijuegos/<id>.json` con `contenido("<id>")`.
"""

import os
import random

PUNTAJE_MAX = 100

NIVELES = {
    "facil": {"indice": 0, "rondas": 6},
    "medio": {"indice": 1, "rondas": 8},
    "dificil": {"indice": 2, "rondas": 10},
}


def normalizar_nivel(nivel: str) -> str:
    return nivel if nivel in NIVELES else "medio"


def config_nivel(nivel: str) -> dict:
    return NIVELES[normalizar_nivel(nivel)]


def nivel_limite(nivel: str) -> int:
    """1 = facil, 2 = medio, 3 = dificil.

    Los items de cada minijuego llevan `d: 1|2|3` (dificultad propia) y se
    filtran con `item["d"] <= nivel_limite(nivel)`.
    """
    return config_nivel(nivel)["indice"] + 1


def nuevas_azar(semilla: int | None = None) -> random.Random:
    return random.Random(semilla)


def barajar(azar: random.Random, lista: list) -> list:
    copia = list(lista)
    azar.shuffle(copia)
    return copia


def tomar(azar: random.Random, lista: list, n: int) -> list:
    return barajar(azar, lista)[:max(0, min(n, len(lista)))]


def puntos(fraccion: float) -> int:
    """Convierte una fraccion 0..1 en puntos 0..PUNTAJE_MAX."""
    return max(0, min(PUNTAJE_MAX, round(PUNTAJE_MAX * max(0.0, min(1.0, fraccion)))))


def contenido(juego_id: str) -> dict:
    """Contenido del minijuego, leido de `data/minijuegos/<juego_id>.json`.

    Cada juego guarda sus casos/pares/pasos en su propio JSON, asi que agregar
    contenido nuevo no toca el codigo: solo se edita el archivo. La cache de
    `nucleo/almacen.py` se invalida sola cuando cambia la fecha del archivo.
    Devuelve {} si el archivo no existe o esta roto (el juego avisara).
    """
    from ..nucleo import config
    from ..nucleo.almacen import leer_json

    datos = leer_json(os.path.join(config.MINIJUEGOS_DIR, f"{juego_id}.json"), {})
    return datos if isinstance(datos, dict) else {}
