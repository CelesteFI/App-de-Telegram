"""test_api.py — Prueba de extremo a extremo de la API por HTTP real.

Levanta el servidor de la app en un puerto libre y recorre el flujo completo:
identidad, catalogo, quiz (iniciar, responder, saltar, reporte, historial,
records) y los diez minijuegos (iniciar, responder todas las rondas, reporte).

Uso:
    python pruebas/test_api.py

Debe terminar con `todo correcto` y salir con codigo 0.
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

os.environ["DEV_AUTHPASS"] = "1"
# Los resultados van a una carpeta temporal: la prueba no debe dejar basura en
# data/resultados ni pisar las marcas de un usuario real.
RESULTADOS = tempfile.mkdtemp(prefix="repaso-ed-prueba-")
os.environ["RESULTADOS_DIR"] = RESULTADOS

from app.nucleo import config
from app.nucleo.principal import construir_app

UID = "999000111"
puerto = 0
fallos = []


def revisar(condicion, mensaje):
    if condicion:
        print("  [ok ] " + mensaje)
    else:
        print("  [FALLA] " + mensaje)
        fallos.append(mensaje)
    return bool(condicion)


def pedir(metodo, camino, cuerpo=None, dev=True):
    """Como lo haria el navegador: en GET la identidad va en la query."""
    if metodo == "GET":
        if dev:
            sep = "&" if "?" in camino else "?"
            camino = camino + sep + "dev_uid=" + UID + "&dev_nombre=Prueba"
        datos = None
    else:
        base = dict(cuerpo or {})
        if dev:
            base["dev"] = {"uid": UID, "nombre": "Prueba"}
        datos = json.dumps(base).encode()
    peticion = urllib.request.Request(
        "http://127.0.0.1:%d%s" % (puerto, camino), data=datos, method=metodo)
    if datos is not None:
        peticion.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(peticion, timeout=20) as respuesta:
            crudo = respuesta.read().decode("utf-8")
            return respuesta.status, _json(crudo)
    except urllib.error.HTTPError as error:
        crudo = error.read().decode("utf-8")
        return error.code, _json(crudo)


def _json(crudo):
    try:
        return json.loads(crudo)
    except ValueError:
        return {}


def main():
    global puerto
    servidor = construir_app(puerto=0)
    puerto = servidor.server_address[1]
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    print("servidor escuchando en el puerto %d (DEV_AUTHPASS=1)\n" % puerto)

    try:
        probar_identidad()
        probar_catalogo()
        probar_quiz()
        probar_quiz_repaso()
        probar_minijuegos()
    finally:
        servidor.shutdown()
        servidor.server_close()

    print()
    if fallos:
        print("%d comprobaciones fallaron" % len(fallos))
        return 1
    print("todo correcto")
    return 0


def probar_identidad():
    print("identidad")
    codigo, datos = pedir("GET", "/api/config")
    revisar(codigo == 200 and datos.get("app") == config.NOMBRE_APP,
            "GET /api/config responde 200 (%s)" % datos.get("app"))
    revisar("cantidades" in datos and "modos" in datos and "ordenes" in datos,
            "GET /api/config anuncia cantidades, modos y ordenes")
    revisar(datos.get("dev") is True, "el servidor avisa que esta en modo dev")
    revisar(isinstance(datos.get("usuario"), dict) and datos["usuario"].get("uid") == UID,
            "GET /api/config reconoce la identidad de la query")

    codigo, datos = pedir("GET", "/api/config?initData=basura", dev=False)
    revisar(codigo == 200 and datos.get("usuario") is None,
            "una initData invalida deja al usuario como anonimo")

    codigo, datos = pedir("GET", "/api/materias", dev=False)
    revisar(codigo == 403, "sin identidad la API se cierra (codigo %d)" % codigo)

    codigo, datos = pedir("GET", "/api/materias")
    revisar(codigo == 200 and isinstance(datos.get("materias"), list),
            "GET /api/materias responde con el catalogo (identidad por query)")


def probar_catalogo():
    print("catalogo de materias")
    _, datos = pedir("GET", "/api/materias")
    temas = []
    for materia in datos["materias"]:
        for tema in materia.get("temas", []):
            temas.append((materia["id"], tema["id"], tema.get("total", 0),
                          tema.get("disponible")))
    revisar(len(datos["materias"]) >= 1, "hay %d materia(s)" % len(datos["materias"]))
    revisar(len(temas) == 8, "hay %d temas en total" % len(temas))
    vacios = ["%s/%s" % (m, t) for m, t, n, disp in temas if not disp or n <= 0]
    revisar(not vacios, "los 8 temas tienen preguntas (sin preguntas: %s)" % vacios)
    revisar("records" in datos and "historial" in datos,
            "el catalogo trae records e historial del usuario")


def probar_quiz():
    print("quiz individual")
    codigo, datos = pedir("POST", "/api/quiz/iniciar", {
        "materia": "ed", "tema": "exactas", "n": 5,
        "orden": "original", "modo": "normal"})
    if not revisar(codigo == 200, "POST /api/quiz/iniciar responde 200 (%s)"
                   % datos.get("error")):
        return
    intento = datos["intento"]
    revisar(datos["total"] == 5, "pide 5 preguntas (llegan %d)" % datos["total"])
    pregunta = datos["pregunta"]
    revisar(len(pregunta["opciones"]) == 4, "la pregunta llega con 4 opciones")
    revisar("correcta" not in pregunta,
            "la pregunta NO viaja la respuesta correcta")

    codigo, datos = pedir("GET", "/api/quiz/estado?intento=" + intento)
    revisar(codigo == 200 and datos.get("pregunta", {}).get("p") == pregunta["p"],
            "GET /api/quiz/estado devuelve la pregunta que toca")

    codigo, datos = pedir("POST", "/api/quiz/responder",
                          {"intento": intento, "pos": 0, "opcion": 2})
    revisar(codigo == 200 and "acierto" in datos,
            "POST /api/quiz/responder califica (%s)" % datos.get("error"))
    revisar(isinstance(datos.get("explicacion"), str) and datos["explicacion"] != "",
            "la respuesta trae explicacion")

    codigo, datos = pedir("POST", "/api/quiz/responder",
                          {"intento": intento, "pos": 0, "opcion": 1})
    revisar(codigo == 409, "no se puede volver a responder la misma (codigo %d)" % codigo)

    codigo, datos = pedir("POST", "/api/quiz/saltar",
                          {"intento": intento, "pos": 1})
    revisar(codigo == 200 and datos.get("saltada") is True,
            "POST /api/quiz/saltar marca la pregunta como fallada")

    codigo, datos = pedir("POST", "/api/quiz/saltar",
                          {"intento": intento, "pos": 5})
    revisar(codigo == 400, "un pos fuera de rango se rechaza (codigo %d)" % codigo)

    ultima = {}
    for pos in range(2, 5):
        codigo, datos = pedir("POST", "/api/quiz/responder",
                              {"intento": intento, "pos": pos, "opcion": 0})
        revisar(codigo == 200, "responde la pregunta %d" % (pos + 1))
        ultima = datos
    revisar(ultima.get("ultima") is True, "la ultima respuesta cierra el intento")
    reporte = ultima.get("reporte") or {}
    revisar(reporte.get("n_preguntas") == 5, "el reporte cuenta las 5 preguntas")
    revisar(0 <= reporte.get("aciertos", -1) <= 5,
            "el reporte suma %s aciertos" % reporte.get("aciertos"))
    revisar(len(reporte.get("detalle", [])) == 5, "el reporte trae detalle de las 5")
    revisar(any(d.get("saltada") for d in reporte.get("detalle", [])),
            "el detalle recuerda la pregunta saltada")
    revisar(all("explicacion" in d and "correcta" in d for d in reporte.get("detalle", [])),
            "el detalle final si trae la correcta y la explicacion")

    codigo, datos = pedir("GET", "/api/quiz/reporte?intento=" + intento)
    revisar(codigo == 200 and datos["reporte"]["intento"] == intento,
            "GET /api/quiz/reporte devuelve el intento terminado")

    codigo, datos = pedir("GET", "/api/quiz/historial")
    revisar(codigo == 200 and len(datos["historial"]) >= 1,
            "GET /api/quiz/historial lista intentos")

    codigo, datos = pedir("GET", "/api/quiz/records")
    revisar(codigo == 200 and "exactas" in datos["records"],
            "GET /api/quiz/records guarda la marca de exactas")

    codigo, datos = pedir("POST", "/api/quiz/iniciar",
                          {"materia": "ed", "tema": "no-existe", "n": 5})
    revisar(codigo == 404, "un tema inexistente da 404 (codigo %d)" % codigo)

    codigo, datos = pedir("POST", "/api/quiz/iniciar",
                          {"materia": "ed", "tema": "exactas", "n": 7})
    revisar(codigo == 400, "una cantidad no permitida da 400 (codigo %d)" % codigo)

    codigo, datos = pedir("POST", "/api/quiz/responder",
                          {"intento": intento, "pos": 0, "opcion": 99})
    revisar(codigo in (404, 409), "responder a un intento ajeno/cerrado se rechaza (%d)" % codigo)


def probar_quiz_repaso():
    print("modos de repaso")
    for modo in ("normal", "falladas", "pendientes"):
        codigo, datos = pedir("POST", "/api/quiz/iniciar", {
            "materia": "ed", "tema": "laplace", "n": 5, "modo": modo})
        revisar(codigo == 200 and datos.get("total", 0) > 0,
                "modo %s arma un intento" % modo)

    codigo, datos = pedir("POST", "/api/quiz/iniciar", {
        "materia": "ed", "tema": "clasificacion", "n": 0, "orden": "original"})
    revisar(codigo == 200 and datos.get("total", 0) == 12,
            "con n=0 salen todas las preguntas (%d)" % datos.get("total"))

    for tema in ("clasificacion", "exactas", "lineales1", "separable",
                 "bernoulli", "segundo_orden", "laplace", "series_edp"):
        codigo, datos = pedir("POST", "/api/quiz/iniciar", {
            "materia": "ed", "tema": tema, "n": 5})
        revisar(codigo == 200 and datos.get("total") == 5,
                "el tema %s sirve su quiz" % tema)


def probar_minijuegos():
    print("minijuegos")
    codigo, datos = pedir("GET", "/api/minijuegos")
    if not revisar(codigo == 200, "GET /api/minijuegos responde 200 (%s)"
                   % datos.get("error")):
        return
    juegos = datos["juegos"]
    revisar(len(juegos) == 10, "el catalogo anuncia %d juegos" % len(juegos))
    revisar(not datos.get("problemas"),
            "ningun juego reporta problemas: %s" % datos.get("problemas"))

    for juego in juegos:
        juego_id = juego["id"]
        for nivel in juego.get("niveles", ["facil"]):
            codigo, partida = pedir("POST", "/api/minijuegos/iniciar", {
                "juego": juego_id, "nivel": nivel, "cantidad": 3})
            if not revisar(codigo == 200, "%s/%s: iniciar responde 200 (%s)"
                           % (juego_id, nivel, partida.get("error"))):
                continue
            revisar("correcta" not in json.dumps(partida.get("ronda", {}), default=str),
                    "%s/%s: la ronda no filtra la solucion" % (juego_id, nivel))
            intento = partida["intento"]
            total = partida["total"]
            ultima = {}
            for numero in range(total):
                codigo, veredicto = pedir("POST", "/api/minijuegos/responder", {
                    "intento": intento, "ronda": numero,
                    "respuesta": respuesta_en_juego(juego_id, partida["ronda"])})
                if codigo != 200:
                    revisar(False, "%s/%s: ronda %d -> %s"
                            % (juego_id, nivel, numero + 1, veredicto.get("error")))
                    break
                ultima = veredicto
            if not ultima:
                continue
            revisar(ultima.get("ultima") is True,
                    "%s/%s: termina tras %d rondas" % (juego_id, nivel, total))
            revisar(isinstance(ultima.get("reporte", {}).get("pct"), (int, float)),
                    "%s/%s: el reporte trae porcentaje" % (juego_id, nivel))

    codigo, datos = pedir("POST", "/api/minijuegos/iniciar", {"juego": "no-existe"})
    revisar(codigo == 404, "un juego inexistente da 404 (codigo %d)" % codigo)

    codigo, datos = pedir("GET", "/api/minijuegos/historial")
    revisar(codigo == 200 and len(datos.get("historial", [])) >= 1,
            "GET /api/minijuegos/historial lista partidas")

    codigo, datos = pedir("GET", "/api/minijuegos/records")
    revisar(codigo == 200 and len(datos.get("records", {})) >= 1,
            "GET /api/minijuegos/records guarda marcas")

    probar_memorama()


def probar_memorama():
    """El tablero llega mezclado y sin solucion: el servidor debe decir si dos
    cartas forman pareja, y nunca aceptar una ronda que no sea de memoria."""
    print("memorama: el servidor juzga las parejas")
    codigo, partida = pedir("POST", "/api/minijuegos/iniciar",
                            {"juego": "memoria", "nivel": "facil", "cantidad": 3})
    if not revisar(codigo == 200, "memoria: iniciar responde 200"):
        return
    cartas = partida["ronda"]["cartas"]
    revisar(len(cartas) >= 4, "memoria: el tablero trae %d cartas" % len(cartas))
    revisar(all(set(c) == {"id", "cara", "texto"} for c in cartas),
            "memoria: cada carta solo lleva id, cara y texto")
    revisar("solucion" not in partida["ronda"],
            "memoria: el tablero no viaja con la solucion")

    intento, ronda = partida["intento"], 0
    primera, segunda = cartas[0]["id"], cartas[1]["id"]
    codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                          {"intento": intento, "ronda": ronda, "a": primera, "b": segunda})
    revisar(codigo == 200 and datos.get("pareja") is False,
            "memoria: dos cartas distintas se rechazan como pareja")

    codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                          {"intento": intento, "ronda": ronda, "a": primera, "b": primera})
    revisar(codigo == 200 and datos.get("pareja") is False,
            "memoria: una carta no hace pareja consigo misma")

    codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                          {"intento": intento, "ronda": ronda + 5, "a": primera, "b": segunda})
    revisar(codigo == 409, "memoria: preguntar por otra ronda da 409 (%d)" % codigo)

    codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                          {"intento": intento, "ronda": ronda, "a": "r9a99", "b": "r9b99"})
    revisar(codigo == 200 and datos.get("pareja") is False,
            "memoria: inventar dos cartas no da pareja gratis")

    encontrada = None
    for a in cartas:
        for b in cartas:
            if a["id"] == b["id"]:
                continue
            codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                                  {"intento": intento, "ronda": ronda, "a": a["id"], "b": b["id"]})
            if datos.get("pareja"):
                encontrada = (a["id"], b["id"])
                break
        if encontrada:
            break
    revisar(encontrada is not None, "memoria: existe una pareja real en el tablero")
    if not encontrada:
        return

    codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                          {"intento": intento, "ronda": ronda,
                           "a": encontrada[1], "b": encontrada[0]})
    revisar(datos.get("pareja") is True,
            "memoria: el orden en que se voltean las cartas no importa")

    codigo, datos = pedir("POST", "/api/minijuegos/pareja",
                          {"intento": intento, "ronda": ronda, "a": encontrada[0]})
    revisar(codigo == 400, "memoria: mandar una sola carta da 400 (%d)" % codigo)


def respuesta_en_juego(juego_id, ronda):
    """Arma una respuesta con el formato que cada `califica()` espera.

    No conoce la solucion correcta a proposito: asi la prueba verifica el
    formato del viaje completo, no el acierto.
    """
    if juego_id == "deslizador":
        return True
    if juego_id == "memoria":
        return {"completas": ronda.get("pares", 2), "errores": 0}
    if juego_id == "columnas":
        return [0] * len(ronda.get("izquierda", []))
    if juego_id == "completar":
        return 0
    if juego_id == "intruso":
        return 0
    if juego_id == "clasificador":
        canastera = (ronda.get("canastas") or [{"clave": "separable"}])[0]["clave"]
        return dict((item["id"], canastera) for item in ronda.get("items", []))
    if juego_id == "ordenar":
        return [0] * len(ronda.get("pasos", []))
    if juego_id == "grafico":
        return 0
    if juego_id == "palabra":
        return ""
    if juego_id == "globos":
        return {"ids": [globo["id"] for globo in ronda.get("globos", [])]}
    return {}


if __name__ == "__main__":
    try:
        codigo = main()
    finally:
        shutil.rmtree(RESULTADOS, ignore_errors=True)
    sys.exit(codigo)