"""seguridad.py — Identidad del usuario de Telegram (initData firmada).

Reglas:
  - Fuera de Telegram (navegador normal) no se puede entrar a la API.
  - Dentro de Telegram, `initData` viene firmada con el token del bot y se
    valida con HMAC-SHA256. Si no cuadra, el usuario es anonimo.
  - `initData` puede llegar en el cuerpo (POST), en la query (GET) o en la
    cabecera `X-Telegram-Init-Data`, porque un GET no lleva cuerpo.
  - Con DEV_AUTHPASS=1 se acepta una identidad de prueba para trabajar local.
"""

import hashlib
import hmac
import json
import time
import urllib.parse

from . import config


def firmar_initdata_para_pruebas(token: str, uid: int = 1,
                                 nombre: str = "Chequeo") -> str:
    """Arma un `initData` de mentira firmado con el token dado.

    Reproduce el mismo HMAC que valida `validar_init_data`, asi que las
    pruebas pueden verificar el camino completo de la identidad sin Telegram
    ni un celular.
    """
    params = {
        "auth_date": str(int(time.time())),
        "user": json.dumps({"id": uid, "first_name": nombre}),
    }
    orden = "\n".join(f"{clave}={params[clave]}" for clave in sorted(params))
    secreto = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    firma = hmac.new(secreto, orden.encode(), hashlib.sha256).hexdigest()
    return urllib.parse.urlencode(params) + "&hash=" + firma


def parse_init_data(init_data: str) -> dict:
    return dict(urllib.parse.parse_qsl(init_data or ""))


def validar_init_data(init_data: str, max_age: int | None = None) -> dict | None:
    """Devuelve los parametros de initData si la firma es valida, o None."""
    if not config.BOT_TOKEN or not init_data:
        return None
    params = parse_init_data(init_data)
    recibido = params.pop("hash", None)
    if not recibido:
        return None
    orden = "\n".join(f"{clave}={params[clave]}" for clave in sorted(params))
    secreto = hmac.new(b"WebAppData", config.BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculado = hmac.new(secreto, orden.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculado, recibido):
        return None
    limite = config.MAX_AGE_INITDATA if max_age is None else max_age
    try:
        if int(params.get("auth_date", "0")) < time.time() - limite:
            return None
    except (TypeError, ValueError):
        return None
    params["hash"] = recibido
    return params


def usuario_de_params(params: dict | None) -> dict | None:
    """Saca {uid, nombre, username} del usuario de Telegram."""
    if not params:
        return None
    try:
        user = json.loads(params.get("user", "null"))
    except (TypeError, ValueError):
        return None
    if not isinstance(user, dict) or user.get("id") is None:
        return None
    nombre = " ".join(
        str(x) for x in (user.get("first_name"), user.get("last_name")) if x
    ).strip()
    return {
        "uid": str(user["id"]),
        "nombre": nombre or "Estudiante",
        "username": str(user.get("username", "") or ""),
    }


def identidad_dev(uid, nombre="") -> dict | None:
    """Identidad de pruebas para trabajar en el navegador sin Telegram."""
    if not uid:
        return None
    return {
        "uid": str(uid),
        "nombre": str(nombre or "") or "Dev",
        "username": "",
    }


def identificar(cuerpo: dict | None = None, consulta: dict | None = None,
                cabeceras=None) -> dict | None:
    """Identidad de quien hace la peticion, o None si no se puede probar.

    `initData` se busca en los tres sitios posibles porque un GET no lleva
    cuerpo: llega en la query o en la cabecera `X-Telegram-Init-Data`. Con
    DEV_AUTHPASS=1 tambien vale `dev` en el cuerpo, o `dev_uid` en la query.
    """
    cuerpo = cuerpo or {}
    consulta = consulta or {}

    if config.DEV_AUTHPASS:
        dev = cuerpo.get("dev")
        if isinstance(dev, dict):
            encontrada = identidad_dev(dev.get("uid"), dev.get("nombre"))
            if encontrada:
                return encontrada
        uid = consulta.get("dev_uid")
        nombre = consulta.get("dev_nombre")
        if cabeceras is not None:
            uid = uid or cabeceras.get("X-Dev-Uid")
            nombre = nombre or cabeceras.get("X-Dev-Nombre")
        if uid:
            return identidad_dev(uid, nombre)

    init_data = cuerpo.get("initData") or consulta.get("initData")
    if not init_data and cabeceras is not None:
        init_data = cabeceras.get("X-Telegram-Init-Data")
    return usuario_de_params(validar_init_data(str(init_data or "")))
