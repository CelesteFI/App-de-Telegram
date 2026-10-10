"""Prueba de humo del flujo completo de la API de examenes (dev).

Usa DEV_AUTHPASS=1 para no depender de initData real.
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DEV_AUTHPASS", "1")

BASE = "http://127.0.0.1:8099"
ok = 0
fail = 0

def call(method, path, body=None):
    data = json.dumps(body or {}).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def check(nombre, cond, extra=None):
    global ok, fail
    if cond:
        ok += 1
        print(f"  [OK] {nombre}")
    else:
        fail += 1
        print(f"  [FAIL] {nombre} {extra if extra else ''}")

print("== config/examenes ==")
st, j = call("GET", "/api/config")
check("config", st == 200 and j.get("pin") is False, j)
st, j = call("GET", "/api/examenes")
check("examenes (9 por tema)", st == 200 and len(j.get("examenes", [])) == 9, j)
check("todos con tema", st == 200 and all(e.get("tema") for e in j.get("examenes", [])), j)

print("== practica individual ==")
st, j = call("GET", "/api/practica/quiz_biseccion")
check("practica ok", st == 200 and j.get("ok"), j)
ex = j.get("examen", {})
check("practica 5 preguntas con correcta", len(ex.get("preguntas", [])) == 5 and
      all("correcta" in q and "opciones" in q for q in ex.get("preguntas", [])), ex)
check("practica tema biseccion", ex.get("tema") == "biseccion", ex)
st, j = call("GET", "/api/practica/no_existe")
check("practica 404", st == 404, j)

print("== sesion del profesor ==")
st, j = call("POST", "/api/crear", {"dev": {"uid": "profe1", "nombre": "Profe"}, "examen_id": "quiz_biseccion"})
check("crear", st == 200 and j.get("ok"), j)
code = j["code"]
print(f"   codigo generado: {code}")

print("== alumnos se unen ==")
st, j = call("POST", "/api/unirse", {"dev": {"uid": "a1", "nombre": "Ana"}, "code": code})
check("unirse a1", st == 200 and j.get("status") == "espera", j)
st, j = call("POST", "/api/unirse", {"dev": {"uid": "a2", "nombre": "Beto"}, "code": code})
check("unirse a2", st == 200, j)

def responder_actual():
    st, e = call("GET", f"/api/profesor/estado?code={code}&uid=profe1")
    if e.get("status") != "activa":
        return e
    c = e["correcta"]
    nopts = len(e.get("conteo", {}))
    call("POST", "/api/responder", {"dev": {"uid": "a1"}, "code": code, "pregunta": e["current"], "opcion": c})
    call("POST", "/api/responder", {"dev": {"uid": "a2"}, "code": code, "pregunta": e["current"], "opcion": (c + 1) % max(2, nopts)})
    return e

print("== empieza la sesion ==")
st, j = call("POST", "/api/siguiente", {"dev": {"uid": "profe1"}, "code": code, "accion": "empezar"})
check("empezar -> activa", st == 200 and j.get("status") == "activa", j)
responder_actual()

print("== estado alumno (pregunta activa, sin correcta) ==")
st, j = call("GET", f"/api/estado?code={code}&uid=a1")
check("estado alumno activa", st == 200 and j.get("current") == 0 and len(j.get("preguntas", [])) == 1, j)
check("oculta correcta en activa", "correcta" not in j["preguntas"][0], j["preguntas"][0])

print("== avanza las 5 preguntas respondiendo en cada una ==")
st, e = call("GET", f"/api/profesor/estado?code={code}&uid=profe1")
check("conteo pregunta 0", st == 200 and e.get("conteo", {}).get("0") == 1, e)
check("correcta pregunta 0 = 0", e.get("correcta") == 0, e)
for _ in range(4):
    st, j = call("POST", "/api/siguiente", {"dev": {"uid": "profe1"}, "code": code, "accion": "siguiente"})
    responder_actual()
st, j = call("GET", f"/api/profesor/estado?code={code}&uid=profe1")
check("aun activa en pregunta 4", j.get("status") == "activa" and j.get("current") == 4, j)

print("== ver resultados finales ==")
st, j = call("POST", "/api/siguiente", {"dev": {"uid": "profe1"}, "code": code, "accion": "ver_resultados"})
check("final", st == 200 and j.get("status") == "final", j)

print("== estado alumno final (con correcta y mis respuestas) ==")
st, j = call("GET", f"/api/estado?code={code}&uid=a1")
check("final con correcta", st == 200 and "correcta" in j["preguntas"][0], j)
check("mis_respuestas len 5", len(j.get("mis_respuestas", [])) == 5, j)

print("== reporte ==")
st, j = call("GET", f"/api/reporte?code={code}&uid=profe1")
check("reporte ok", st == 200 and j.get("ok"), j)
r = j.get("reporte", {})
check("2 filas de alumnos", len(r.get("filas", [])) == 2, r)
check("5 preguntas analizadas", len(r.get("por_pregunta", [])) == 5, r)
filas = r.get("filas", [])
a1 = next((f for f in filas if f["nombre"] == "Ana"), None)
check("Ana acierto las 5", a1 and a1["aciertos"] == 5, a1)
check("Beto acierto 0", next((f for f in filas if f["nombre"] == "Beto"))["aciertos"] == 0, filas)

print("== cerrar guarda reporte ==")
st, j = call("POST", "/api/siguiente", {"dev": {"uid": "profe1"}, "code": code, "accion": "cerrar"})
check("cerrar", st == 200 and j.get("status") == "cerrada", j)
import glob
archs = glob.glob(os.path.join(os.path.dirname(__file__), "data", "resultados", f"{code}_*.csv"))
check("csv guardado", len(archs) == 1, archs)

print("== permisos ==")
code2 = call("POST", "/api/crear", {"dev": {"uid": "profe1"}, "examen_id": "quiz_biseccion"})[1]["code"]
call("POST", "/api/unirse", {"dev": {"uid": "a1"}, "code": code2})
st, j = call("POST", "/api/siguiente", {"dev": {"uid": "a1"}, "code": code2, "accion": "empezar"})
check("alumno no controla", st == 403, j)
st, j = call("GET", f"/api/reporte?code={code2}&uid=a1")
check("alumno no ve reporte", st != 200, j)

print("== fallback plantillas por defecto ==")
import importlib
srv = importlib.import_module("server")
orig = srv.BANCO_DIR
srv.BANCO_DIR = os.path.join(os.path.dirname(__file__), "data", "no_existe")
srv._CACHE_EXAMENES = None
por_def = srv.cargar_examenes()
srv.BANCO_DIR = orig
check("fallback 9 por tema", len(por_def) == 9 and
      set(por_def) == {"quiz_" + t for t, _ in srv.TEMAS_QUIZ})
q0 = por_def["quiz_biseccion"]["preguntas"][0]
check("plantilla Correcta=0", q0["opciones"][0] == "Correcta" and q0["correcta"] == 0, q0)

print("== banco por tema (un archivo por quiz) ==")
banco_dir = orig
archivos_json = [f for f in os.listdir(banco_dir) if f.lower().endswith(".json")]
check("9 archivos en data/banco", len(archivos_json) == 9, archivos_json)
for t, _ in srv.TEMAS_QUIZ:
    with open(os.path.join(banco_dir, t + ".json"), encoding="utf-8") as fh:
        ex = json.load(fh)
    check(f"archivo {t}.json con id quiz_{t}", ex.get("id") == f"quiz_{t}" and
          ex.get("tema") == t and len(ex.get("preguntas", [])) == 5, ex.get("id"))

print(f"\nRESULTADO: {ok} ok, {fail} fallos")
sys.exit(1 if fail else 0)