"""principal.py — Arranque del backend.

    python -m app.nucleo.principal

Levanta el servidor estatico de `webapp` mas la API de quiz y minijuegos.
Los comandos `--comprobar` y `--juego <id>` validan los datos sin abrir
puertos, que es lo que corre la prueba de humo.
"""

import argparse
import json
import sys
import time

from . import config
from .http import construir_servidor


def _cargar_modulos() -> None:
    """Importa los minijuegos y el quiz para que se registren sus rutas."""
    from .. import minijuegos  # noqa: F401
    from ..minijuegos import quiz  # noqa: F401


def comprobar() -> int:
    """Valida configuracion, catalogo y contenido de los minijuegos."""
    from ..minijuegos import registro, servicio
    from ..minijuegos.quiz import banco, servicio as quiz_servicio  # noqa: F401

    fallos = 0
    print(f"app        : {config.NOMBRE_APP} v{config.VERSION}")
    print(f"webapp     : {config.WEBAPP_DIR}")
    print(f"materias   : {config.MATERIAS_FILE}")
    print(f"quizzes    : {config.QUIZZ_DIR}")
    print(f"resultados : {config.RESULTADOS_DIR}")

    materias = banco.materias()
    if not materias:
        print("  [FALLO] no se leyo ninguna materia")
        fallos += 1
    for materia in materias:
        for tema in materia["temas"]:
            marca = "ok " if tema["disponible"] else "sin"
            print(f"  [{marca}] {materia['id']}/{tema['id']}: "
                  f"{tema['total']} preguntas - {tema['nombre']}")

    try:
        juegos = registro.catalogo()
    except RuntimeError as exc:
        print(f"  [FALLO] {exc}")
        return 1
    for juego in juegos:
        total_rondas = 0
        for nivel in juego["niveles"]:
            rondas = servicio.iniciar({"uid": "smoke", "nombre": "Smoke"},
                                     juego["id"], nivel, 3, None)["total"]
            total_rondas += rondas
        print(f"  [ok] {juego['id']}: {juego['titulo']} "
              f"({len(juego['niveles'])} niveles, {total_rondas} rondas probadas)")
    for problema in registro.problemas():
        print(f"  [FALLO] {problema}")
        fallos += 1

    print("todo correcto" if not fallos else f"{fallos} problema(s)")
    return 1 if fallos else 0


def construir_app(puerto: int | None = None):
    """Carga modulos y devuelve un servidor listo para `serve_forever`.

    Lo usan `main()` y las pruebas de extremo a extremo, para no depender de
    que el servidor este corriendo por fuera.
    """
    from ..minijuegos import registro

    _cargar_modulos()
    try:
        registro.cargar()
    except RuntimeError as exc:
        raise RuntimeError(f"No puedo arrancar sin minijuegos: {exc}") from exc
    return construir_servidor(puerto=puerto)


def _chequear_identidad(puerto: int) -> int:
    """Pregunta al servidor local si logra validar una identidad firmada.

    Es el fallo que dio el token perdido: el bot arrancaba bien pero el
    servidor respondia 403 a todos. Aqui se ve de una vez, en la consola.
    """
    import urllib.parse
    import urllib.request

    from .seguridad import firmar_initdata_para_pruebas

    if not config.BOT_TOKEN:
        print("  [AVISO] BOT_TOKEN no esta en el entorno: NADIE podra entrar "
              "desde Telegram (la API respondera 403).")
        print("          Ponlo en $env:BOT_TOKEN o en $TOKEN_FIJO de run.ps1.")
        return 1

    url = (f"http://localhost:{puerto}/api/config?"
           + urllib.parse.urlencode({"initData": firmar_initdata_para_pruebas(config.BOT_TOKEN)}))
    try:
        with urllib.request.urlopen(url, timeout=5) as respuesta:
            datos = json.load(respuesta)
    except Exception as exc:  # noqa: BLE001 - aqui solo informamos
        print(f"  [AVISO] No se pudo consultar /api/config: {exc}")
        return 1

    usuario = datos.get("usuario")
    if usuario:
        print(f"  [ok] El servidor valida la identidad de Telegram "
              f"(usuario {usuario.get('uid')}).")
        return 0
    print("  [FALLO] El servidor NO logra validar initData aunque el token este "
          "en el entorno.")
    print("          Revisa que BOT_TOKEN sea el mismo para el servidor y para el bot.")
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Backend de la Mini App")
    parser.add_argument("--comprobar", action="store_true",
                        help="valida los datos y sale")
    parser.add_argument("--chequeo-identidad", action="store_true",
                        help="comprueba que el servidor valida la identidad y sale")
    parser.add_argument("--puerto", type=int, default=config.PUERTO)
    args = parser.parse_args()

    _cargar_modulos()
    if args.comprobar:
        sys.exit(comprobar())

    config.PUERTO = args.puerto

    if args.chequeo_identidad:
        # No levanta otro servidor en el mismo puerto (eso competia con el que
        # ya corre): solo pregunta al servidor activo si logra validar la firma.
        sys.exit(_chequear_identidad(args.puerto))

    from ..minijuegos import registro
    from ..minijuegos.quiz import banco

    try:
        registro.cargar()
    except RuntimeError as exc:
        print(f"No puedo arrancar sin minijuegos: {exc}")
        sys.exit(1)

    servidor = construir_servidor()
    print(f"\n{config.NOMBRE_APP} v{config.VERSION}")
    print(f"  Mini App   http://localhost:{args.puerto}")
    print(f"  Modo dev   {'si (identidad falsa permitida)' if config.DEV_AUTHPASS else 'no'}")
    print(f"  Identidad  {'lista (puede validar initData)' if config.BOT_TOKEN else 'NO: sin BOT_TOKEN, todos sera 403'}")
    print(f"  Materias   {len(banco.materias())}")
    print(f"  Quizzes    {len(banco.quizzes())} temas con preguntas")
    print(f"  Minijuegos {len(registro.catalogo())}")
    print("Ctrl+C para detener.\n")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
