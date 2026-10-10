"""almacen.py — Lectura de archivos JSON con cache que se invalida sola.

Sirve para `data/minijuegos/*.json` y `data/minijuegos/quiz/*.json`: puedes
editarlos mientras la app esta corriendo y se recarga sola (compara la
fecha de modificacion, no el contenido).
"""

import json
import os
import threading
import time
from typing import Any

_caches: dict[str, tuple[Any, Any]] = {}
_lock = threading.Lock()


def _firma(archivo: str):
    try:
        return (os.path.getmtime(archivo), os.path.getsize(archivo))
    except OSError:
        return None


def leer_json(archivo: str, por_defecto: Any = None) -> Any:
    """Devuelve el JSON del archivo; `por_defecto` si no existe o esta roto."""
    clave = "file:" + os.path.abspath(archivo)
    firma = _firma(archivo)
    with _lock:
        guardado = _caches.get(clave)
        if firma is not None and guardado is not None and guardado[1] == firma:
            return guardado[0]
    if firma is None:
        with _lock:
            _caches.pop(clave, None)
        return por_defecto
    try:
        with open(archivo, encoding="utf-8") as fh:
            datos = json.load(fh)
    except (OSError, ValueError):
        with _lock:
            _caches.pop(clave, None)
        return por_defecto
    with _lock:
        _caches[clave] = (datos, firma)
    return datos


_cache_dir: tuple | None = None


def _firma_dir(directorio: str):
    if not os.path.isdir(directorio):
        return None
    partes = []
    for nombre in sorted(os.listdir(directorio)):
        if not nombre.lower().endswith(".json"):
            continue
        ruta = os.path.join(directorio, nombre)
        firma = _firma(ruta)
        if firma is not None:
            partes.append((nombre, firma))
    return tuple(partes)


def leer_carpeta_json(directorio: str) -> list[tuple[str, Any]]:
    """Devuelve [(nombre_archivo, contenido)] de todos los *.json validos."""
    clave = "dir:" + os.path.abspath(directorio)
    firma = _firma_dir(directorio)
    with _lock:
        guardado = _caches.get(clave)
        if firma is not None and guardado is not None and guardado[1] == firma:
            return guardado[0]
    if firma is None:
        with _lock:
            _caches.pop(clave, None)
        return []
    salida: list[tuple[str, Any]] = []
    for nombre, _ in firma:
        datos = leer_json(os.path.join(directorio, nombre))
        if datos is not None:
            salida.append((nombre, datos))
    with _lock:
        _caches[clave] = (tuple(salida), firma)
    return salida


def escribir_json(archivo: str, datos: Any) -> bool:
    """Guarda JSON de forma atómica (escribe aparte y reemplaza)."""
    temporal = f"{archivo}.tmp{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(archivo) or ".", exist_ok=True)
        with open(temporal, "w", encoding="utf-8") as fh:
            json.dump(datos, fh, ensure_ascii=False, indent=2)
        os.replace(temporal, archivo)
    except OSError:
        try:
            os.unlink(temporal)
        except OSError:
            pass
        return False
    with _lock:
        _caches.pop("file:" + os.path.abspath(archivo), None)
    return True


def marca_de_tiempo() -> str:
    return time.strftime("%Y%m%d_%H%M%S")
