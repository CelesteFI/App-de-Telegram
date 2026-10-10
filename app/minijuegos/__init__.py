"""minijuegos — Registro automatico + rutas HTTP de las partidas.

    GET  /api/minijuegos              catalogo de los juegos y sus niveles
    POST /api/minijuegos/iniciar      {juego, nivel, cantidad} -> ronda publica
    POST /api/minijuegos/responder    {intento, ronda, respuesta} -> veredicto
    GET  /api/minijuegos/estado?intento=   estado de la partida en curso
    GET  /api/minijuegos/historial    ultimas partidas del usuario
    GET  /api/minijuegos/records      mejores marcas por juego
    POST /api/minijuegos/pareja       {intento, ronda, a, b} -> el memorama pregunta
"""

from ..nucleo.http import ErrorApi, ruta
from . import registro, servicio


@ruta("GET", "/api/minijuegos")
def catalogo(peticion):
    usuario = peticion.exige_usuario()
    juegos = registro.catalogo()
    return {
        "ok": True,
        "juegos": juegos,
        "records": servicio.records(usuario["uid"]),
        "cantidades": list(servicio.CANTIDADES),
        "problemas": registro.problemas(),
    }


@ruta("POST", "/api/minijuegos/iniciar")
def iniciar(peticion):
    usuario = peticion.exige_usuario()
    cuerpo = peticion.cuerpo
    datos = servicio.iniciar(usuario, peticion.texto("juego"),
                             cuerpo.get("nivel", "medio"), cuerpo.get("cantidad"),
                             peticion.texto("tema") or None)
    return {"ok": True, **datos}


@ruta("POST", "/api/minijuegos/responder")
def responder(peticion):
    usuario = peticion.exige_usuario()
    cuerpo = peticion.cuerpo
    if "respuesta" not in cuerpo:
        raise ErrorApi("falta la respuesta")
    return {"ok": True, **servicio.responder(
        peticion.texto("intento"), usuario["uid"], peticion.entero("ronda", -1),
        cuerpo["respuesta"])}


@ruta("GET", "/api/minijuegos/estado")
def estado(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, **servicio.estado(peticion.texto("intento"), usuario["uid"])}


@ruta("POST", "/api/minijuegos/pareja")
def pareja(peticion):
    usuario = peticion.exige_usuario()
    cuerpo = peticion.cuerpo
    return servicio.comprobar_pareja(
        peticion.texto("intento"), usuario["uid"], peticion.entero("ronda", -1),
        cuerpo.get("a"), cuerpo.get("b"))


@ruta("GET", "/api/minijuegos/historial")
def historial(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, "historial": servicio.historial(usuario["uid"])}


@ruta("GET", "/api/minijuegos/records")
def records(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, "records": servicio.records(usuario["uid"])}
