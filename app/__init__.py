"""app — Backend de la Mini App (Python puro, sin frameworks).

Estructura:

    app/nucleo/           http, seguridad, almacen, config, arranque
    app/minijuegos/       un archivo .py por minijuego + registro automatico
    app/minijuegos/quiz/  catalogo de materias, intentos, calificacion, reportes

Arranque:  python -m app.nucleo.principal
"""

__all__ = ["nucleo", "minijuegos"]
