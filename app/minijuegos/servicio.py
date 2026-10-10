"""servicio.py — Intentos de minijuegos: armar rondas, calificar y reportar.

El navegador recibe las rondas YA SIN SOLUCION. Cada vez que el jugador
contesta, el servidor llama a `califica()` de ese minijuego y guarda el
puntaje. Al terminar se arma el reporte y se guarda en
`data/resultados/minijuegos/`.
"""

import os
import secrets
import threading
import time
import uuid

from ..nucleo import config
from ..nucleo.almacen import escribir_json, leer_json, marca_de_tiempo
from ..nucleo.http import ErrorApi
from . import base, registro

_lock = threading.Lock()
_intentos: dict[str, dict] = {}

CANTIDADES = (5, 8, 10, 15)
LIMITE_CANTIDAD = 15


def _limpiar() -> None:
    ahora = time.time()
    for clave in [k for k, v in _intentos.items()
                  if ahora - v["creado"] > config.CADUCIDAD_INTENTO]:
        _intentos.pop(clave, None)
    while len(_intentos) > config.MAX_INTENTOS_VIVOS:
        _intentos.pop(min(_intentos, key=lambda k: _intentos[k]["creado"]), None)


def _archivos_de(uid: str) -> list[str]:
    carpeta = os.path.join(config.RESULTADOS_DIR, "minijuegos")
    try:
        return sorted((f for f in os.listdir(carpeta)
                       if f.startswith(f"{uid}_") and f.endswith(".json")),
                      reverse=True)
    except OSError:
        return []


def records(uid: str) -> dict:
    datos = leer_json(os.path.join(config.RESULTADOS_DIR, "records.json"), {}) or {}
    return {k.split(":", 1)[1]: v for k, v in (datos.get(uid, {}) or {}).items()
            if k.startswith("mj:")}


def _guardar_record(uid: str, juego_id: str, datos: dict) -> None:
    archivo = os.path.join(config.RESULTADOS_DIR, "records.json")
    todo = leer_json(archivo, {}) or {}
    por_usuario = todo.setdefault(uid, {})
    clave = f"mj:{juego_id}"
    previo = por_usuario.get(clave)
    if not previo or datos["pct"] > previo.get("pct", -1):
        por_usuario[clave] = datos
    escribir_json(archivo, todo)


def _guardar_reporte(uid: str, reporte: dict) -> str | None:
    carpeta = os.path.join(config.RESULTADOS_DIR, "minijuegos")
    try:
        os.makedirs(carpeta, exist_ok=True)
    except OSError:
        return None
    nombre = f"{uid}_{marca_de_tiempo()}_{secrets.token_hex(3)}.json"
    return nombre if escribir_json(os.path.join(carpeta, nombre), reporte) else None


def historial(uid: str, limite: int = 15) -> list[dict]:
    salida = []
    for nombre in _archivos_de(uid)[:limite]:
        datos = leer_json(os.path.join(config.RESULTADOS_DIR, "minijuegos", nombre))
        if isinstance(datos, dict) and "puntos" in datos:
            salida.append({k: datos.get(k) for k in
                           ("juego_id", "titulo", "puntos", "max", "pct", "n_rondas", "fecha")})
    return salida


def iniciar(usuario: dict, juego_id: str, nivel: str, cantidad, tema: str | None) -> dict:
    try:
        juego = registro.obtener(juego_id)
    except KeyError:
        raise ErrorApi("ese minijuego no existe", 404)
    modulo = juego["modulo"]
    nivel = base.normalizar_nivel(nivel)
    try:
        pedidas = int(cantidad or 0)
    except (TypeError, ValueError):
        pedidas = 0
    if pedidas <= 0:
        pedidas = base.config_nivel(nivel)["rondas"]
    pedidas = max(3, min(LIMITE_CANTIDAD, pedidas))

    azar = base.nuevas_azar()
    rondas = modulo.rondas(azar, nivel, pedidas, tema or None)
    if not rondas:
        raise ErrorApi("no hay contenido suficiente para armar las rondas", 409)

    intento_id = uuid.uuid4().hex[:12]
    with _lock:
        _limpiar()
        _intentos[intento_id] = {
            "id": intento_id,
            "uid": usuario["uid"],
            "nombre": usuario["nombre"],
            "juego_id": juego["id"],
            "titulo": juego["titulo"],
            "nivel": nivel,
            "tema": tema or "",
            "rondas": rondas,
            "pos": 0,
            "puntos": [],
            "creado": time.time(),
            "iniciado": time.time(),
            "terminado": None,
        }
    return _vista(intento_id)


def _obtener(intento_id: str, uid: str) -> dict:
    intento = _intentos.get(str(intento_id))
    if not intento:
        raise ErrorApi("la partida ya no esta en el servidor: vuelve a empezar", 404)
    if intento["uid"] != uid:
        raise ErrorApi("esa partida es de otra persona", 403)
    return intento


def _vista(intento_id: str) -> dict:
    intento = _intentos[intento_id]
    modulo = registro.obtener(intento["juego_id"])["modulo"]
    total = len(intento["rondas"])
    return {
        "intento": intento["id"],
        "titulo": intento["titulo"],
        "juego_id": intento["juego_id"],
        "nivel": intento["nivel"],
        "total": total,
        "terminado": intento["terminado"] is not None,
        "puntos": sum(intento["puntos"]),
        "pos": intento["pos"],
        "ronda": modulo.publico(intento["rondas"][min(intento["pos"], total - 1)]),
        "reporte": _reporte(intento) if intento["terminado"] is not None else None,
    }


def _reporte(intento: dict) -> dict:
    total = len(intento["rondas"])
    puntos = sum(intento["puntos"])
    maximo = base.PUNTAJE_MAX * total
    detalle = []
    for pos, valor in enumerate(intento["puntos"]):
        detalle.append({
            "pos": pos,
            "puntaje": valor,
            "correcto": valor >= base.PUNTAJE_MAX,
            "detalle": intento["resultados"][pos]["detalle"] if pos in intento.get("resultados", {}) else "",
        })
    return {
        "intento": intento["id"],
        "nombre": intento["nombre"],
        "juego_id": intento["juego_id"],
        "titulo": intento["titulo"],
        "nivel": intento["nivel"],
        "tema": intento["tema"],
        "n_rondas": total,
        "puntos": puntos,
        "max": maximo,
        "pct": round(100.0 * puntos / maximo, 1) if maximo else 0.0,
        "perfectas": sum(1 for v in intento["puntos"] if v >= base.PUNTAJE_MAX),
        "duracion": round((intento["terminado"] or time.time()) - intento["iniciado"], 1),
        "fecha": time.strftime("%Y-%m-%d %H:%M"),
        "detalle": detalle,
        "record": records(intento["uid"]).get(intento["juego_id"]),
    }


def responder(intento_id: str, uid: str, ronda: int, respuesta) -> dict:
    with _lock:
        intento = _obtener(intento_id, uid)
        if intento["terminado"] is not None:
            raise ErrorApi("la partida ya termino", 409)
        if ronda != intento["pos"]:
            raise ErrorApi("esa ronda ya no es la actual")
        modulo = registro.obtener(intento["juego_id"])["modulo"]
        try:
            veredicto = modulo.califica(intento["rondas"][ronda], respuesta)
        except (TypeError, ValueError, KeyError, IndexError):
            raise ErrorApi("respuesta con formato inesperado")
        if not isinstance(veredicto, dict):
            raise ErrorApi("el minijuego no devolvio un veredicto valido")

        ganados = int(veredicto.get("puntaje", 0))
        intento["puntos"].append(max(0, min(base.PUNTAJE_MAX, ganados)))
        intento.setdefault("resultados", {})[ronda] = {
            "detalle": str(veredicto.get("detalle", ""))[:600],
        }
        intento["pos"] = ronda + 1
        ultima = intento["pos"] >= len(intento["rondas"])
        if ultima:
            intento["terminado"] = time.time()
            reporte = _reporte(intento)
            reporte["guardado"] = _guardar_reporte(uid, reporte)
            _guardar_record(uid, intento["juego_id"], {
                "puntos": reporte["puntos"], "max": reporte["max"],
                "pct": reporte["pct"], "nivel": intento["nivel"],
                "fecha": reporte["fecha"],
            })

    salida = {"ok": True, "pos": ronda, "ultima": ultima,
              "puntos": sum(intento["puntos"])}
    salida.update({k: v for k, v in veredicto.items() if k != "puntaje"})
    if ultima:
        salida["reporte"] = _reporte(intento)
    return salida


def estado(intento_id: str, uid: str) -> dict:
    with _lock:
        return _vista(_obtener(intento_id, uid)["id"])


def comprobar_pareja(intento_id: str, uid: str, ronda: int, id_a, id_b) -> dict:
    """Solo para el memorama: el tablero llega mezclado y sin solucion, asi que
    el servidor es quien dice si dos cartas cartas son la misma pareja."""
    with _lock:
        intento = _obtener(intento_id, uid)
        if intento["terminado"] is not None:
            raise ErrorApi("la partida ya termino", 409)
        if ronda != intento["pos"]:
            raise ErrorApi("esa ronda ya no es la actual", 409)
        if not isinstance(id_a, str) or not isinstance(id_b, str):
            raise ErrorApi("faltan las dos cartas")
        modulo = registro.obtener(intento["juego_id"])["modulo"]
        revisar = getattr(modulo, "es_pareja", None)
        if revisar is None:
            raise ErrorApi("este juego no usa parejas", 400)
        actual = intento["rondas"][ronda]
        return {"ok": True, "pareja": bool(revisar(actual, id_a, id_b))}
