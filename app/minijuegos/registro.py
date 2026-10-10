"""registro.py — Descubre los minijuegos automaticamente.

No hay que registrar nada a mano: se lee esta carpeta, se importa cada `.py`
y se usa su diccionario `JUEGO` + sus funciones `rondas/publico/califica`.
Un modulo roto se avisa pero no tumba la app.

Para agregar un minijuego nuevo:
  1) copia `plantilla.py` como `<id>.py` en esta carpeta
  2) defines JUEGO, rondas, publico y califica
  3) crea `webapp/js/minijuegos/<id>.js` (logica) y
     `webapp/css/minijuegos/<id>.css` (estilos)
Listo: aparece solo en el catalogo.
"""

import importlib
import os
import pkgutil
import traceback

from . import base

_registro: dict[str, dict] = {}
_problemas: list[str] = []
_CARPETA = os.path.dirname(os.path.abspath(__file__))

REQUERIDO = ("rondas", "publico", "califica")

# Modulos de infraestructura: no son juegos.
NO_ES_JUEGO = {"base", "registro", "servicio", "plantilla"}


def _cargar_modulo(nombre: str):
    return importlib.import_module(f"{__package__}.{nombre}")


def registrar(modulo, origen: str = "") -> None:
    juego = getattr(modulo, "JUEGO", None)
    if not isinstance(juego, dict):
        raise ValueError("falta el diccionario JUEGO")
    faltan = [n for n in REQUERIDO if not callable(getattr(modulo, n, None))]
    if faltan:
        raise ValueError("faltan funciones: " + ", ".join(faltan))
    jid = str(juego.get("id") or modulo.__name__.rsplit(".", 1)[-1])
    _registro[jid] = {
        "id": jid,
        "titulo": str(juego.get("titulo", jid)),
        "icono": str(juego.get("icono", "🎮")),
        "resumen": str(juego.get("resumen", "")),
        "mecanica": str(juego.get("mecanica", "")),
        "niveles": list(juego.get("niveles", base.NIVELES.keys())),
        "etiquetas": list(juego.get("etiquetas", [])),
        "modulo": modulo,
        "archivo": origen or getattr(modulo, "__file__", jid),
    }


def cargar() -> dict:
    """Importa todos los modulos de la carpeta. Idempotente."""
    if _registro:
        return _registro
    for info in pkgutil.iter_modules([_CARPETA]):
        if info.name.startswith("_") or info.name in NO_ES_JUEGO:
            continue
        try:
            registrar(_cargar_modulo(info.name), info.name + ".py")
        except Exception as exc:  # noqa: BLE001 - un juego roto no debe tumbar la app
            _problemas.append(f"{info.name}: {exc}")
            traceback.print_exc()
    if not _registro:
        raise RuntimeError("no se encontro ningun minijuego en app/minijuegos/")
    return _registro


def catalogo() -> list[dict]:
    salida = []
    for jid, juego in sorted(cargar().items()):
        salida.append({k: v for k, v in juego.items() if k != "modulo"})
    return salida


def obtener(juego_id: str) -> dict:
    cargar()
    juego = _registro.get(str(juego_id))
    if not juego:
        raise KeyError(juego_id)
    return juego


def problemas() -> list[str]:
    return list(_problemas)


def _solo(juego_id: str):
    try:
        return obtener(juego_id)["modulo"]
    except KeyError:
        raise KeyError(juego_id)
