"""app — Backend de la Mini App (Python puro, sin frameworks).

Estructura:

    app/nucleo/       http, seguridad, almacen, config, arranque
    app/quiz/         catalogo de materias, intentos, calificacion, reportes
    app/minijuegos/   un archivo .py por minijuego + registro automatico

Arranque:  python -m app.nucleo.principal
"""

__all__ = ["nucleo", "quiz", "minijuegos"]
