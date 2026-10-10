"""quiz — Rutas HTTP del quiz individual (sin profesor, sin alumnos, sin salas).

    GET  /api/config                 nombre de la app y si exige identidad
    GET  /api/materias               catalogo: materias, temas y cuantos hay
    POST /api/quiz/iniciar           {materia, tema, n, orden, modo} -> intento
    POST /api/quiz/responder         {intento, pos, opcion} -> acierto + explicacion
POST /api/quiz/saltar            {intento, pos} -> cuenta como fallada
    GET  /api/quiz/estado?intento=   la pregunta que toca ahora
    GET  /api/quiz/reporte?intento=   reporte ya terminado
    GET  /api/quiz/historial         ultimos intentos de la persona
    GET  /api/quiz/records           mejor marca por tema
"""

from ...nucleo import config
from ...nucleo.http import ErrorApi, ruta
from . import banco, servicio


@ruta("GET", "/api/config")
def config_app(peticion):
    return {
        "ok": True,
        "app": config.NOMBRE_APP,
        "version": config.VERSION,
        "dev": config.DEV_AUTHPASS,
        "usuario": peticion.usuario,
        "cantidades": list(servicio.CANTIDADES),
        "modos": list(servicio.MODOS),
        "ordenes": list(servicio.ORDENES),
    }


@ruta("GET", "/api/materias")
def listar_materias(peticion):
    usuario = peticion.exige_usuario()
    materias = banco.materias()
    if not materias:
        raise ErrorApi("no hay materias configuradas en data/minijuegos/quiz/materias.json", 404)
    return {
        "ok": True,
        "materias": materias,
        "records": servicio.records(usuario["uid"]),
        "historial": servicio.historial(usuario["uid"], limite=10),
    }


@ruta("GET", "/api/temas")
def listar_temas(peticion):
    peticion.exige_usuario()
    return {"ok": True, "temas": banco.temas_de_contenido()}


@ruta("POST", "/api/quiz/iniciar")
def iniciar(peticion):
    usuario = peticion.exige_usuario()
    cuerpo = peticion.cuerpo
    opciones = {
        "n": cuerpo.get("n", 5),
        "orden": cuerpo.get("orden", "mezclado"),
        "modo": cuerpo.get("modo", "normal"),
    }
    datos = servicio.iniciar(usuario, peticion.texto("materia"), peticion.texto("tema"), opciones)
    return {"ok": True, **datos}


@ruta("POST", "/api/quiz/responder")
def responder(peticion):
    usuario = peticion.exige_usuario()
    cuerpo = peticion.cuerpo
    if "opcion" not in cuerpo:
        raise ErrorApi("falta la opcion")
    return {"ok": True, **servicio.responder(
        peticion.texto("intento"), usuario["uid"],
        peticion.entero("pos", -1), peticion.entero("opcion", -1))}


@ruta("POST", "/api/quiz/saltar")
def saltar(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, **servicio.saltar(
        peticion.texto("intento"), usuario["uid"], peticion.entero("pos", -1))}


@ruta("GET", "/api/quiz/estado")
def estado(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, **servicio.estado_de(
        peticion.texto("intento"), usuario["uid"])}


@ruta("GET", "/api/quiz/reporte")
def reporte(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, "reporte": servicio.reporte_de(
        peticion.texto("intento"), usuario["uid"])}


@ruta("GET", "/api/quiz/historial")
def historial(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, "historial": servicio.historial(usuario["uid"], limite=25)}


@ruta("GET", "/api/quiz/records")
def records(peticion):
    usuario = peticion.exige_usuario()
    return {"ok": True, "records": servicio.records(usuario["uid"])}
