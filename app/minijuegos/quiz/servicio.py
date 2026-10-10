"""servicio.py — Intentos de quiz individuales: armar, calificar y reportar.

Ya no hay sesiones ni roles: cada persona abre su propio intento, contesta y
al terminar ve su reporte. El servidor guarda la respuesta correcta y la
explicacion, asi el cliente nunca las tiene hasta que contesta (el reporte
final si las incluye para poder repasar).

Un intento vive en memoria con caducidad; el reporte terminado se guarda en
`data/resultados/` como JSON.
"""

import os
import secrets
import threading
import time
import uuid

from ...nucleo import config
from ...nucleo.almacen import escribir_json, leer_json, marca_de_tiempo
from ...nucleo.http import ErrorApi
from . import banco

_lock = threading.Lock()
_intentos: dict[str, dict] = {}

CANTIDADES = (5, 10, 15, 0)
MODOS = ("normal", "falladas", "pendientes")
ORDENES = ("mezclado", "original")


def _archivo_registros() -> str:
    return os.path.join(config.RESULTADOS_DIR, "records.json")


def _limpiar_intentos() -> None:
    ahora = time.time()
    muertos = [k for k, v in _intentos.items()
               if ahora - v["creado"] > config.CADUCIDAD_INTENTO]
    for clave in muertos:
        _intentos.pop(clave, None)
    while len(_intentos) > config.MAX_INTENTOS_VIVOS:
        mas_viejo = min(_intentos, key=lambda k: _intentos[k]["creado"])
        _intentos.pop(mas_viejo, None)


def _archivo_historial(uid: str) -> str:
    return os.path.join(config.RESULTADOS_DIR, f"{uid}_{marca_de_tiempo()}_{secrets.token_hex(3)}.json")


def _guardar_reporte(uid: str, reporte: dict) -> str | None:
    try:
        os.makedirs(config.RESULTADOS_DIR, exist_ok=True)
    except OSError:
        return None
    ruta = _archivo_historial(uid)
    if escribir_json(ruta, reporte):
        return os.path.basename(ruta)
    return None


def _actualizar_record(uid: str, tema: str, reporte: dict) -> None:
    archivo = _archivo_registros()
    datos = leer_json(archivo, {}) or {}
    por_usuario = datos.setdefault(uid, {})
    previo = por_usuario.get(tema)
    if not previo or reporte["pct"] > previo.get("pct", -1):
        por_usuario[tema] = {
            "aciertos": reporte["aciertos"],
            "total": reporte["n_preguntas"],
            "pct": reporte["pct"],
            "fecha": reporte["fecha"],
        }
    escribir_json(archivo, datos)


def records(uid: str) -> dict:
    datos = leer_json(_archivo_registros(), {}) or {}
    return datos.get(uid, {}) if isinstance(datos.get(uid), dict) else {}


def historial(uid: str, limite: int = 20) -> list[dict]:
    """Ultimos intentos guardados de esta persona (sin el detalle completo)."""
    try:
        archivos = [f for f in os.listdir(config.RESULTADOS_DIR)
                    if f.startswith(f"{uid}_") and f.endswith(".json")]
    except OSError:
        return []
    archivos.sort(reverse=True)
    salida = []
    for nombre in archivos[:limite]:
        datos = leer_json(os.path.join(config.RESULTADOS_DIR, nombre))
        if isinstance(datos, dict) and "aciertos" in datos:
            salida.append({
                "fecha": datos.get("fecha"),
                "titulo": datos.get("titulo"),
                "tema": datos.get("tema"),
                "aciertos": datos.get("aciertos"),
                "n_preguntas": datos.get("n_preguntas"),
                "pct": datos.get("pct"),
                "duracion": datos.get("duracion"),
            })
    return salida


def _ultimo_reporte(uid: str) -> dict | None:
    """El reporte guardado mas reciente de esta persona, o None."""
    try:
        archivos = sorted((f for f in os.listdir(config.RESULTADOS_DIR)
                           if f.startswith(f"{uid}_") and f.endswith(".json")),
                          reverse=True)
    except OSError:
        return None
    for nombre in archivos:
        datos = leer_json(os.path.join(config.RESULTADOS_DIR, nombre))
        if isinstance(datos, dict) and "detalle" in datos:
            return datos
    return None


def _seleccionar_preguntas(preguntas: list[dict], opciones: dict, uid: str) -> list[int]:
    """Devuelve los indices (en el banco) de las preguntas de este intento.

    modo:
      normal      -> cualquier pregunta del tema
      falladas    -> solo las que fallaste en tu ultimo intento de ese tema
      pendientes  -> solo las que aun no has acertado nunca
    orden:
      mezclado    -> al azar (default)
      original    -> en el orden del archivo
    """
    modo = str(opciones.get("modo", "normal"))
    orden = str(opciones.get("orden", "mezclado"))
    n = int(opciones.get("n", 5) or 0)
    pool = list(range(len(preguntas)))

    if modo in ("falladas", "pendientes"):
        ultimo = _ultimo_reporte(uid)
        if ultimo and ultimo.get("tema") == opciones.get("tema_id"):
            falladas = {str(d.get("id", "")) for d in ultimo.get("detalle", [])
                        if not d.get("ok") and d.get("id")}
            if modo == "falladas" and falladas:
                pool = [i for i in pool if preguntas[i].get("id") in falladas]
            elif modo == "pendientes":
                acertadas = {str(d.get("id", "")) for d in ultimo.get("detalle", [])
                             if d.get("ok") and d.get("id")}
                pool = [i for i in pool if str(preguntas[i].get("id", "")) not in acertadas]
        if not pool:
            pool = list(range(len(preguntas)))

    if orden == "mezclado":
        pool.sort(key=lambda _i: secrets.randbelow(1 << 30))
    if n > 0:
        pool = pool[:min(n, len(pool))]
    return pool


def iniciar(usuario: dict, materia_id: str, tema_id: str, opciones: dict) -> dict:
    try:
        encontrado = banco.buscar_tema(materia_id, tema_id)
    except KeyError:
        raise ErrorApi("ese tema no existe en el catalogo", 404)
    quiz = encontrado["quiz"]
    if not quiz:
        raise ErrorApi(f"el tema {encontrado['tema']['nombre']} todavia no tiene preguntas", 409)

    modo = str(opciones.get("modo", "normal"))
    orden = str(opciones.get("orden", "mezclado"))
    if modo not in MODOS:
        raise ErrorApi("modo de repaso no valido")
    if orden not in ORDENES:
        raise ErrorApi("orden no valido")
    try:
        n = int(opciones.get("n", 5) or 0)
    except (TypeError, ValueError):
        raise ErrorApi("cantidad de preguntas no valida")
    if n not in CANTIDADES:
        raise ErrorApi("cantidad de preguntas no valida")

    preguntas = quiz["preguntas"]
    elegidas = _seleccionar_preguntas(
        preguntas, {"n": n, "modo": modo, "orden": orden, "tema_id": tema_id},
        usuario["uid"])
    if not elegidas:
        raise ErrorApi("no hay preguntas disponibles para este repaso", 409)

    intento_id = uuid.uuid4().hex[:12]
    with _lock:
        _limpiar_intentos()
        _intentos[intento_id] = {
            "id": intento_id,
            "uid": usuario["uid"],
            "nombre": usuario["nombre"],
            "materia_id": materia_id,
            "materia_nombre": encontrado["materia"]["nombre"],
            "tema_id": tema_id,
            "tema_nombre": encontrado["tema"]["nombre"],
            "titulo": quiz["titulo"],
            "descripcion": quiz.get("descripcion", ""),
            "banco": preguntas,
            "orden": elegidas,
            "pos": 0,
            "respuestas": {},
            "creado": time.time(),
            "iniciado": time.time(),
            "terminado": None,
            "guardado": None,
        }
    return _vista_publica(_intentos[intento_id])


def _vista_publica(intento: dict) -> dict:
    """Lo que el cliente ve mientras responde: nunca incluye la correcta."""
    if intento["terminado"] is not None:
        return {"intento": intento["id"], "terminado": True, "reporte": _reporte(intento)}
    indice = intento["orden"][intento["pos"]]
    pregunta = intento["banco"][indice]
    return {
        "intento": intento["id"],
        "terminado": False,
        "materia": intento["materia_nombre"],
        "tema": intento["tema_nombre"],
        "titulo": intento["titulo"],
        "pos": intento["pos"],
        "total": len(intento["orden"]),
        "pregunta": {
            "p": pregunta["p"],
            "f": pregunta["f"],
            "opciones": pregunta["opciones"],
        },
        "respondidas": len(intento["respuestas"]),
    }


def _obtener(intento_id: str, uid: str) -> dict:
    intento = _intentos.get(str(intento_id))
    if not intento:
        raise ErrorApi("el intento ya no existe: vuelve a empezar el quiz", 404)
    if intento["uid"] != uid:
        raise ErrorApi("ese intento es de otra persona", 403)
    return intento


def responder(intento_id: str, uid: str, pos: int, opcion: int) -> dict:
    """Califica una respuesta y devuelve si acerto + (al final) el reporte."""
    with _lock:
        intento = _obtener(intento_id, uid)
        if intento["terminado"] is not None:
            raise ErrorApi("este quiz ya termino", 409)
        if not 0 <= pos < len(intento["orden"]):
            raise ErrorApi("numero de pregunta fuera de rango")
        if pos != intento["pos"]:
            raise ErrorApi("responde en orden", 409)
        indice = intento["orden"][pos]
        pregunta = intento["banco"][indice]
        if not 0 <= opcion < len(pregunta["opciones"]):
            raise ErrorApi("opcion no valida")

        correcto = opcion == pregunta["correcta"]
        intento["respuestas"][pos] = {
            "opcion": opcion,
            "t": round(time.time() - intento["iniciado"], 1),
        }
        intento["pos"] = pos + 1
        ultima = intento["pos"] >= len(intento["orden"])
        if ultima:
            intento["terminado"] = time.time()
            intento["guardado"] = _guardar_reporte(uid, _reporte(intento))
            try:
                _actualizar_record(uid, intento["tema_id"], _reporte(intento))
            except OSError:
                pass

    salida = {
        "ok": True,
        "acierto": correcto,
        "correcta": pregunta["correcta"],
        "elige": opcion,
        "explicacion": pregunta.get("explicacion", ""),
        "pos": pos,
        "ultima": ultima,
    }
    if ultima:
        salida["reporte"] = _reporte(intento)
    return salida


def saltar(intento_id: str, uid: str, pos: int) -> dict:
    """Marca la pregunta actual como fallada y avanza (sin ver la correcta)."""
    with _lock:
        intento = _obtener(intento_id, uid)
        if intento["terminado"] is not None:
            raise ErrorApi("este quiz ya termino", 409)
        if not 0 <= pos < len(intento["orden"]):
            raise ErrorApi("numero de pregunta fuera de rango")
        if pos != intento["pos"]:
            raise ErrorApi("responde en orden", 409)
        indice = intento["orden"][pos]
        pregunta = intento["banco"][indice]
        intento["respuestas"][pos] = {
            "opcion": -1,
            "t": round(time.time() - intento["iniciado"], 1),
        }
        intento["pos"] = pos + 1
        ultima = intento["pos"] >= len(intento["orden"])
        if ultima:
            intento["terminado"] = time.time()
            intento["guardado"] = _guardar_reporte(uid, _reporte(intento))
        salida = {
            "ok": True,
            "acierto": False,
            "correcta": pregunta["correcta"],
            "saltada": True,
            "explicacion": pregunta.get("explicacion", ""),
            "pos": pos,
            "ultima": ultima,
        }
        if ultima:
            salida["reporte"] = _reporte(intento)
        return salida


def estado_de(intento_id: str, uid: str) -> dict:
    """La pregunta actual (o el reporte si ya termino), sin la solucion."""
    return _vista_publica(_obtener(intento_id, uid))


def reporte_de(intento_id: str, uid: str) -> dict:
    intento = _obtener(intento_id, uid)
    if intento["terminado"] is None:
        raise ErrorApi("el quiz no ha terminado todavia", 409)
    return _reporte(intento)


def _reporte(intento: dict) -> dict:
    """Reporte completo: aciertos, detalle pregunta por pregunta y resumas."""
    detalle = []
    aciertos = 0
    for pos, indice in enumerate(intento["orden"]):
        pregunta = intento["banco"][indice]
        elegida = intento["respuestas"].get(pos, {}).get("opcion", -1)
        ok = elegida == pregunta["correcta"]
        if ok:
            aciertos += 1
        detalle.append({
            "pos": pos,
            "id": pregunta.get("id", ""),
            "p": pregunta["p"],
            "f": pregunta["f"],
            "opciones": pregunta["opciones"],
            "correcta": pregunta["correcta"],
            "elige": elegida,
            "ok": ok,
            "saltada": elegida < 0,
            "explicacion": pregunta.get("explicacion", ""),
            "t": intento["respuestas"].get(pos, {}).get("t", 0),
        })
    total = len(intento["orden"])
    duracion = round((intento["terminado"] or time.time()) - intento["iniciado"], 1)
    return {
        "intento": intento["id"],
        "nombre": intento["nombre"],
        "materia": intento["materia_nombre"],
        "tema": intento["tema_id"],
        "tema_nombre": intento["tema_nombre"],
        "titulo": intento["titulo"],
        "n_preguntas": total,
        "aciertos": aciertos,
        "pct": round(100.0 * aciertos / total, 1) if total else 0.0,
        "duracion": duracion,
        "fecha": time.strftime("%Y-%m-%d %H:%M"),
        "detalle": detalle,
        "guardado": intento["guardado"],
        "record": records(intento["uid"]).get(intento["tema_id"]),
    }
