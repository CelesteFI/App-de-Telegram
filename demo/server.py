"""Backend de la Mini App de Examenes (estilo Kahoot) para Telegram.

Roles:
  - SERVIR los archivos estaticos de demo/webapp  (la propia Mini App)
  - API REST para las sesiones de examen de 30-40 estudiantes:
      GET  /api/config                   -> requiere PIN de profesor?
      GET  /api/examenes                 -> catalogo de examenes (sin respuestas)
      GET  /api/practica/<examen_id>     -> quiz individual COMPLETO (incluye correcta)
      POST /api/crear                    -> el profesor crea una sesion con codigo
      POST /api/unirse                   -> el alumno se une con el codigo
      GET  /api/estado?code&uid          -> estado para el alumno (sin claves)
      POST /api/responder                -> el alumno responde la pregunta actual
      POST /api/siguiente                -> el profesor avanza pregunta / cierra
      GET  /api/profesor/estado?code&uid -> estado completo para el profesor
      GET  /api/reporte[.csv|.html] -> reporte de resultados (profesor)

Seguridad: toda peticion lleva initData firmado por Telegram (HMAC-SHA256).
Identidad: uid = id de usuario de Telegram (media inicial via boton inline/menu).

Uso:
  $env:BOT_TOKEN     = "123456789:AAABBB..."
  $env:WEBAPP_DIR    = "demo/webapp"
  $env:BANCO_DIR    = "demo/data/banco"   (un archivo .json por tema)
  $env:PIN_PROFESOR  = "2026"          # opcional: exige PIN al profesor
  $env:RESULTADOS_DIR= "demo/data/resultados"
  python demo/server.py                  # puerto por defecto 8080 (PORT=...)
"""

import csv
import html
import hashlib
import hmac
import io
import json
import os
import random
import threading
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_DIR = os.environ.get("WEBAPP_DIR", os.path.join(os.path.dirname(__file__), "webapp"))
BANCO_DIR = os.environ.get(
    "BANCO_DIR", os.path.join(os.path.dirname(__file__), "data", "banco")
)
RESULTADOS_DIR = os.environ.get(
    "RESULTADOS_DIR", os.path.join(os.path.dirname(__file__), "data", "resultados")
)
PIN_PROFESOR = os.environ.get("PIN_PROFESOR", "")
DEV_AUTHPASS = os.environ.get("DEV_AUTHPASS", "") == "1"

LETRAS = "ABCDEFGHIJ"

# ---------------------------------------------------------------------------
# Seguridad / initData
# ---------------------------------------------------------------------------

def parse_init_data(init_data: str) -> dict:
    return dict(urllib.parse.parse_qsl(init_data or ""))


def validate_init_data(init_data: str, max_age: int = 3600):
    """Valida que initData venga firmado por Telegram y devuelve los parametros."""
    if not BOT_TOKEN or not init_data:
        return None
    params = parse_init_data(init_data)
    received = params.pop("hash", None)
    if not received:
        return None
    data_check_string = "\n".join(f"{k}={params[k]}" for k in sorted(params))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, received):
        return None
    try:
        if int(params.get("auth_date", "0")) < time.time() - max_age:
            return None
    except ValueError:
        return None
    params["hash"] = received
    return params


def user_from_params(params: dict):
    """Extrae {uid, nombre} del usuario de Telegram en initData."""
    if not params:
        return None
    try:
        user = json.loads(params.get("user", "null"))
    except (TypeError, ValueError):
        user = None
    if not user or not user.get("id"):
        return None
    nombre = " ".join(str(x) for x in (user.get("first_name"), user.get("last_name", "")) if x)
    return {"uid": str(user["id"]), "nombre": nombre or "Estudiante"}


# ---------------------------------------------------------------------------
# Banco de preguntas
# ---------------------------------------------------------------------------

# Un quiz por tema (igual que el Area de Teoria). Los ids coinciden con los
# temas de la app para organizar el catalogo.
TEMAS_QUIZ = [
    ("biseccion", "Metodo de biseccion"),
    ("newton", "Metodo de Newton-Raphson"),
    ("falsaPosicion", "Falsa posicion"),
    ("puntoFijo", "Metodo de punto fijo"),
    ("lagrange", "Interpolacion de Lagrange"),
    ("diferenciasDivididas", "Diferencias divididas"),
    ("trapecio", "Regla del trapecio"),
    ("simpson", "Regla de Simpson"),
    ("derivadas", "Derivacion numerica"),
]

_examenes_lock = threading.Lock()
_CACHE_EXAMENES = None
_CACHE_MTIME = 0


def _plantilla_preguntas(n: int = 5) -> list:
    """Plantilla basica: 'Pregunta 1..N' con Correcta/Incorrecta.
    La profesora reemplazara estas preguntas por el banco real despues."""
    return [
        {"p": f"Pregunta {i + 1}", "f": "",
         "opciones": ["Correcta", "Incorrecta", "Incorrecta", "Incorrecta"],
         "correcta": 0}
        for i in range(n)
    ]


def _examen_fabrica(tema_id: str, nombre: str) -> dict:
    return {
        "id": f"quiz_{tema_id}",
        "tema": tema_id,
        "titulo": f"Quiz de {nombre}",
        "descripcion": "Plantilla basica. Reemplaza las preguntas por el banco real.",
        "preguntas": _plantilla_preguntas(),
    }


def _examenes_por_defecto() -> dict:
    """Quizzes de plantilla por tema (usados si el banco esta vacio)."""
    return {f"quiz_{t}": _examen_fabrica(t, n) for t, n in TEMAS_QUIZ}


def _cargar_banco_dir() -> dict:
    """Lee todos los *.json de BANCO_DIR. Cada archivo = 1 quiz (o wrapper {"examenes": [...]}).
    Sin preguntas/corrupto se ignora ese archivo. Un quiz sin id se omite."""
    index = {}
    if not os.path.isdir(BANCO_DIR):
        return index
    for nombre in sorted(os.listdir(BANCO_DIR)):
        if not nombre.lower().endswith(".json"):
            continue
        try:
            with open(os.path.join(BANCO_DIR, nombre), encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        items = data.get("examenes", [data]) if isinstance(data, dict) else []
        for ex in items:
            if not isinstance(ex, dict) or not ex.get("id"):
                continue
            ex = dict(ex)
            ex["preguntas"] = list(ex.get("preguntas", []))
            ex.setdefault("tema", "miscelaneo")
            if ex["preguntas"]:
                index[ex["id"]] = ex
    return index


def cargar_examenes() -> dict:
    """Carga el banco por temas (un archivo por tema) en memoria con cache.
    Se invalida si cambia la fecha de los archivos o aparece/desaparece alguno.
    Si el banco no existe o esta vacio usa las plantillas por defecto."""
    global _CACHE_EXAMENES, _CACHE_MTIME
    try:
        firma = (os.path.getmtime(BANCO_DIR),
                 tuple((f, os.path.getmtime(os.path.join(BANCO_DIR, f)))
                       for f in sorted(os.listdir(BANCO_DIR))))
    except OSError:
        return dict(_examenes_por_defecto())
    if _CACHE_EXAMENES is None or firma != _CACHE_MTIME:
        index = _cargar_banco_dir()
        _CACHE_EXAMENES = index if index else dict(_examenes_por_defecto())
        _CACHE_MTIME = firma
    return _CACHE_EXAMENES


def examen_publico(ex):
    """Catalogo para GET /api/examenes (sin preguntas/correctas)."""
    return {"id": ex["id"], "tema": ex.get("tema", "miscelaneo"),
            "titulo": ex["titulo"], "descripcion": ex.get("descripcion", ""),
            "total": len(ex["preguntas"])}


# ---------------------------------------------------------------------------
# Estado de las sesiones
# ---------------------------------------------------------------------------

_sesiones_lock = threading.Lock()
SESIONES = {}


def nuevo_codigo() -> str:
    while True:
        code = f"{random.randint(1000, 9999)}"
        if code not in SESIONES:
            return code


def crear_sesion(uid: str, nombre: str, examen_id: str) -> dict:
    examenes = cargar_examenes()
    if examen_id not in examenes:
        raise ValueError("examen no encontrado")
    ex = examenes[examen_id]
    with _sesiones_lock:
        code = nuevo_codigo()
        SESIONES[code] = {
            "code": code,
            "examen_id": examen_id,
            "titulo": ex["titulo"],
            "descripcion": ex.get("descripcion", ""),
            "preguntas": [{k: q[k] for k in ("p", "f", "opciones", "correcta") if k in q}
                          for q in ex["preguntas"]],
            "current": -1,                 # -1 = espera; n = pregunta actual
            "status": "espera",            # espera | activa | final | cerrada
            "creador": {"uid": uid, "nombre": nombre},
            "alumnos": {},                 # uid -> {nombre, unido_at}
            "respuestas": {},              # uid -> [ {q, opcion, t} ... ]
            "creado_at": time.time(),
            "inicio_at": None,
        }
        return SESIONES[code]


def alumno_estado(sesion: dict, uid: str | None = None) -> dict:
    """Vista para el alumno (oculta la clave correcta salvo en el repaso final)."""
    preg = []
    show_correcta = sesion["status"] in ("final", "cerrada")
    if sesion["status"] in ("activa", "final", "cerrada"):
        total = len(sesion["preguntas"])
        for i, q in enumerate(sesion["preguntas"]):
            if sesion["status"] == "activa" and i != sesion["current"]:
                continue
            item = {"q": i, "p": q["p"], "f": q.get("f", ""),
                    "opciones": q["opciones"]}
            if show_correcta:
                item["correcta"] = q["correcta"]
            preg.append(item)
    resumen = {
        "code": sesion["code"],
        "titulo": sesion["titulo"],
        "total": len(sesion["preguntas"]),
        "status": sesion["status"],
        "current": sesion["current"],
        "unidos": len(sesion["alumnos"]),
        "preguntas": preg,
        "inicio_at": sesion["inicio_at"],
    }
    if uid:
        resumen["mis_respuestas"] = sesion["respuestas"].get(uid, [])
    return resumen


def conteo_pregunta(sesion: dict, idx: int) -> dict:
    """Contador de opciones para la pregunta idx."""
    if not (0 <= idx < len(sesion["preguntas"])):
        return {}
    opciones = sesion["preguntas"][idx]["opciones"]
    cuenta = {i: 0 for i in range(len(opciones))}
    for uid, arr in sesion["respuestas"].items():
        for r in arr:
            if r["q"] == idx:
                opcion = int(r["opcion"])
                if opcion in cuenta:
                    cuenta[opcion] += 1
                break
    return cuenta


def reporte(sesion: dict) -> dict:
    """Reporte completo: por alumno y por pregunta."""
    preguntas = sesion["preguntas"]
    filas = []
    for uid, arr in sesion["respuestas"].items():
        info = sesion["alumnos"].get(uid, {"nombre": "Desconocido"})
        aciertos = 0
        detalle = []
        for i, q in enumerate(preguntas):
            resp = next((r for r in arr if r["q"] == i), None)
            if resp is None:
                detalle.append({"q": i, "opcion": None, "ok": None})
                continue
            ok = resp["opcion"] == q["correcta"]
            if ok:
                aciertos += 1
            detalle.append({"q": i, "opcion": resp["opcion"], "ok": ok,
                            "t": resp.get("t")})
        filas.append({
            "uid": uid,
            "nombre": info.get("nombre", "Desconocido"),
            "aciertos": aciertos,
            "total": len(preguntas),
            "pct": round(100.0 * aciertos / len(preguntas), 1) if preguntas else 0.0,
            "detalle": detalle,
        })
    filas.sort(key=lambda r: (-r["aciertos"], r["nombre"].lower()))

    por_pregunta = []
    for i, q in enumerate(preguntas):
        cuenta = conteo_pregunta(sesion, i)
        por_pregunta.append({
            "q": i,
            "p": q["p"],
            "f": q.get("f", ""),
            "opciones": q["opciones"],
            "correcta": q["correcta"],
            "cuenta": cuenta,
            "respondidas": sum(cuenta.values()),
            "aciertos": cuenta.get(q["correcta"], 0),
        })

    return {
        "code": sesion["code"],
        "titulo": sesion["titulo"],
        "n_preguntas": len(preguntas),
        "n_alumnos": len(filas),
        "creado_at": sesion["creado_at"],
        "inicio_at": sesion["inicio_at"],
        "fin_at": time.time(),
        "filas": filas,
        "por_pregunta": por_pregunta,
    }


def guardar_reporte(sesion: dict, incl_csv: bool = True):
    """Persiste el reporte en data/resultados/<code>_<timestamp>.{json,csv}."""
    try:
        os.makedirs(RESULTADOS_DIR, exist_ok=True)
    except OSError:
        return
    stamp = time.strftime("%Y%m%d_%H%M%S")
    base = os.path.join(RESULTADOS_DIR, f"{sesion['code']}_{stamp}")
    try:
        with open(base + ".json", "w", encoding="utf-8") as fh:
            json.dump(reporte(sesion), fh, ensure_ascii=False, indent=2)
    except OSError:
        pass
    if not incl_csv:
        return
    buf = io.StringIO()
    writer = csv.writer(buf)
    filas = reporte(sesion)["filas"]
    headers = ["Nombre", "Aciertos", "Total", "Pct"]
    headers += [f"P{i+1}" for i in range(len(sesion["preguntas"]))]
    writer.writerow(headers)
    for f in filas:
        row = [f["nombre"], f["aciertos"], f["total"], f["pct"]]
        for d in f["detalle"]:
            row.append(LETRAS[d["opcion"]] + ("*" if d["ok"] else ""))
        writer.writerow(row)
    try:
        with open(base + ".csv", "w", encoding="utf-8-sig", newline="") as fh:
            fh.write(buf.getvalue())
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------

class Handler(SimpleHTTPRequestHandler):
    server_version = "QuizMiniApp/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBAPP_DIR, **kwargs)

    def log_message(self, fmt, *args):
        pass

    # ---- utilidades -------------------------------------------------------
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _text(self, code: int, body: str, ctype: str = "text/plain; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > 1_000_000:
            raise ValueError("peticion demasiado grande")
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw or b"{}")

    def _query(self) -> dict:
        return dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(self.path).query or ""))

    def _auth(self, payload: dict) -> dict | None:
        """Devuelve {uid, nombre} autenticado o None a partir del body.
        Solo para desarrollo local: si DEV_AUTHPASS=1 acepta un dev {uid,nombre}."""
        if DEV_AUTHPASS:
            dev = payload.get("dev")
            if isinstance(dev, dict) and dev.get("uid"):
                nombre = str(dev.get("nombre", "")) or "Dev"
                return {"uid": str(dev["uid"]), "nombre": nombre}
        params = validate_init_data(str(payload.get("initData", "")))
        return user_from_params(params)

    # ---- enrutado ---------------------------------------------------------
    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path.startswith("/api/"):
            self.handle_api_get(path)
        else:
            try:
                super().do_GET()
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        if path.startswith("/api/"):
            self.handle_api_post(path)
        else:
            self._json(404, {"ok": False, "error": "no encontrado"})

    def handle_api_get(self, path: str):
        try:
            self._route_get(path)
        except ValueError as exc:
            self._json(400, {"ok": False, "error": str(exc)})
        except Exception:
            self._json(500, {"ok": False, "error": "error interno"})

    def handle_api_post(self, path: str):
        try:
            self._route_post(path)
        except ValueError as exc:
            self._json(400, {"ok": False, "error": str(exc)})
        except Exception:
            self._json(500, {"ok": False, "error": "error interno"})

    # ---- GET --------------------------------------------------------------
    def _route_get(self, path: str):
        q = self._query()
        if path == "/api/config":
            self._json(200, {"ok": True, "pin": bool(PIN_PROFESOR),
                             "nombre": "Examenes de Analisis Numerico"})
        elif path == "/api/examenes":
            examenes = [examen_publico(e) for e in cargar_examenes().values()]
            self._json(200, {"ok": True, "examenes": examenes})
        elif path.startswith("/api/practica/"):
            # Quiz individual: devuelve el examen COMPLETO (incluye correcta)
            # para que el alumno practique solo y vea retroalimentacion.
            ex_id = path[len("/api/practica/"):]
            ex = cargar_examenes().get(ex_id)
            if not ex:
                self._json(404, {"ok": False, "error": "quiz no encontrado"})
                return
            self._json(200, {"ok": True, "examen": {
                "id": ex["id"], "tema": ex.get("tema", "miscelaneo"),
                "titulo": ex["titulo"], "descripcion": ex.get("descripcion", ""),
                "preguntas": [{k: q[k] for k in ("p", "f", "opciones", "correcta") if k in q}
                              for q in ex["preguntas"]],
            }})
        elif path == "/api/estado":
            sesion = self._get_sesion_alumno(q)
            self._json(200, {"ok": True, **alumno_estado(sesion, uid=q.get("uid"))})
        elif path == "/api/profesor/estado":
            sesion = self._get_sesion_profe(q)
            self._json(200, {"ok": True, **self._profesor_estado(sesion)})
        elif path == "/api/reporte":
            sesion = self._get_sesion_profe(q)
            self._json(200, {"ok": True, "reporte": reporte(sesion)})
        elif path == "/api/reporte.csv":
            sesion = self._get_sesion_profe(q)
            inf = reporte(sesion)
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["Nombre", "Aciertos", "Total", "Pct"] +
                            [f"P{i+1}" for i in range(inf["n_preguntas"])])
            for f in inf["filas"]:
                row = [f["nombre"], f["aciertos"], f["total"], f["pct"]]
                for d in f["detalle"]:
                    row.append(LETRAS[d["opcion"]] + ("*" if d["ok"] else ""))
                writer.writerow(row)
            self._text(200, buf.getvalue(), "text/csv; charset=utf-8")
        elif path == "/api/reporte.html":
            sesion = self._get_sesion_profe(q)
            self._text(200, self._render_reporte_html(reporte(sesion)),
                       "text/html; charset=utf-8")
        else:
            self._json(404, {"ok": False, "error": "ruta no encontrada"})

    def _get_sesion_alumno(self, q: dict) -> dict:
        code = q.get("code", "")
        if code not in SESIONES:
            raise ValueError("sesion no encontrada")
        sesion = SESIONES[code]
        if sesion["status"] == "cerrada":
            raise ValueError("esta sesion ya se cerro")
        return sesion

    def _get_sesion_profe(self, q: dict) -> dict:
        code = q.get("code", "")
        uid = q.get("uid", "")
        if code not in SESIONES:
            raise ValueError("sesion no encontrada")
        sesion = SESIONES[code]
        if uid != sesion["creador"]["uid"]:
            raise ValueError("permiso denegado")
        return sesion

    def _profesor_estado(self, sesion: dict) -> dict:
        current = sesion["current"]
        respuestas_avance = {uid: len(arr) for uid, arr in sesion["respuestas"].items()}
        return {
            "code": sesion["code"],
            "titulo": sesion["titulo"],
            "status": sesion["status"],
            "current": current,
            "total": len(sesion["preguntas"]),
            "unidos": list(sesion["alumnos"].values()),
            "n_unidos": len(sesion["alumnos"]),
            "respondidos": len(sesion["respuestas"]),
            "conteo": conteo_pregunta(sesion, current),
            "correcta": sesion["preguntas"][current]["correcta"] if 0 <= current < len(sesion["preguntas"]) else None,
            "avance": respuestas_avance,
            "creador": sesion["creador"],
            "inicio_at": sesion["inicio_at"],
        }

    def _render_reporte_html(self, inf: dict) -> str:
        filas_html = ""
        for f in inf["filas"]:
            celdas = "".join(
                f"<td class='{'ok' if d['ok'] else 'mal'}'>"
                f"{LETRAS[d['opcion']] if d['opcion'] is not None else '—'}</td>"
                for d in f["detalle"]
            )
            filas_html += (
                "<tr>"
                f"<td>{html.escape(f['nombre'])}</td>"
                f"<td>{f['aciertos']}/{f['total']}</td>"
                f"<td>{f['pct']}%</td>{celdas}</tr>"
            )
        cab = "".join(f"<th>P{i+1}</th>" for i in range(inf["n_preguntas"]))
        por_preg = ""
        for pp in inf["por_pregunta"]:
            barras = "".join(
                f"<li><b>{LETRAS[i]}:</b> {cnt}"
                f"{' <span class=ok>✔ (correcta)</span>' if i == pp['correcta'] else ''}"
                f" — {'▰' * cnt}</li>"
                for i, cnt in pp["cuenta"].items()
            )
            por_preg += (
                "<h3>" + html.escape(pp["p"]) + "</h3>"
                + (("<div class='f'><code>" + html.escape(pp["f"]) + "</code></div>") if pp["f"] else "")
                + "<ul>" + barras + f"</ul><p class='mal'>Aciertos: {pp['aciertos']}/{pp['respondidas']}</p>"
            )
        return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Reporte {html.escape(inf['titulo'])}</title>
<style>
 body{{font-family:system-ui,sans-serif;margin:24px;color:#222}}
 table{{border-collapse:collapse;width:100%;margin-top:8px}}
 th,td{{border:1px solid #ccc;padding:4px 8px;text-align:center}}
 .ok{{color:#16a34a}} .mal{{color:#dc2626}}
 ul{{list-style:none;padding:0}} li{{padding:2px 0}}
 .f{{color:#555}} h3{{margin-bottom:2px}}
</style></head><body>
<h1>{html.escape(inf['titulo'])}</h1>
<p>Codigo: <b>{inf['code']}</b> · Alumnos: <b>{inf['n_alumnos']}</b> · Preguntas: <b>{inf['n_preguntas']}</b></p>
<h2>Por alumno</h2>
<table><tr><th>Nombre</th><th>Puntaje</th><th>%</th>{cab}</tr>{filas_html}</table>
<h2>Por pregunta</h2>{por_preg}
</body></html>"""

    # ---- POST -------------------------------------------------------------
    def _route_post(self, path: str):
        if path == "/api/crear":
            self._post_crear()
            return
        if path == "/api/unirse":
            self._post_unirse()
            return
        if path == "/api/responder":
            self._post_responder()
            return
        if path == "/api/siguiente":
            self._post_siguiente()
            return
        self._json(404, {"ok": False, "error": "ruta no encontrada"})

    def _post_crear(self):
        data = self._read_json()
        auth = self._auth(data)
        if not auth:
            self._json(403, {"ok": False, "error": "initData invalido o vencido"})
            return
        if PIN_PROFESOR:
            pin = str(data.get("pin", "")).strip()
            if not hmac.compare_digest(pin, PIN_PROFESOR):
                self._json(403, {"ok": False, "error": "PIN de profesor incorrecto"})
                return
        examen_id = str(data.get("examen_id", ""))
        if not examen_id:
            self._json(400, {"ok": False, "error": "falta examen_id"})
            return
        try:
            sesion = crear_sesion(auth["uid"], auth["nombre"], examen_id)
        except ValueError as exc:
            self._json(404, {"ok": False, "error": str(exc)})
            return
        self._json(200, {"ok": True, "code": sesion["code"], "titulo": sesion["titulo"],
                         "total": len(sesion["preguntas"]),
                         "creador": sesion["creador"]})

    def _post_unirse(self):
        payload = self._read_json()
        auth = self._auth(payload)
        if not auth:
            self._json(403, {"ok": False, "error": "initData invalido o vencido"})
            return
        code = str(payload.get("code", "")).strip()
        if code not in SESIONES:
            self._json(404, {"ok": False, "error": "codigo inexistente"})
            return
        sesion = SESIONES[code]
        if sesion["status"] == "cerrada":
            self._json(409, {"ok": False, "error": "sesion ya cerrada"})
            return
        with _sesiones_lock:
            if auth["uid"] not in sesion["alumnos"]:
                sesion["alumnos"][auth["uid"]] = {
                    "nombre": auth["nombre"], "unido_at": time.time()}
            if auth["uid"] not in sesion["respuestas"]:
                sesion["respuestas"][auth["uid"]] = []
            sesion["alumnos"][auth["uid"]]["nombre"] = auth["nombre"]
        self._json(200, {"ok": True, "uid": auth["uid"], **alumno_estado(sesion, uid=auth["uid"])})

    def _post_responder(self):
        payload = self._read_json()
        auth = self._auth(payload)
        if not auth:
            self._json(403, {"ok": False, "error": "initData invalido o vencido"})
            return
        code = str(payload.get("code", "")).strip()
        if code not in SESIONES:
            self._json(404, {"ok": False, "error": "sesion no encontrada"})
            return
        sesion = SESIONES[code]
        if sesion["status"] != "activa":
            self._json(409, {"ok": False, "error": "no hay pregunta activa"})
            return
        try:
            pregunta = int(payload.get("pregunta", -1))
            opcion = int(payload.get("opcion", -1))
        except (TypeError, ValueError):
            self._json(400, {"ok": False, "error": "datos invalidos"})
            return
        if pregunta != sesion["current"]:
            self._json(409, {"ok": False, "error": "pregunta fuera de turno"})
            return
        if not (0 <= opcion < len(sesion["preguntas"][pregunta]["opciones"])):
            self._json(400, {"ok": False, "error": "opcion invalida"})
            return
        if auth["uid"] not in sesion["alumnos"]:
            sesion["alumnos"][auth["uid"]] = {"nombre": auth["nombre"], "unido_at": time.time()}
        base = sesion["inicio_at"] or time.time()
        with _sesiones_lock:
            arr = sesion["respuestas"].setdefault(auth["uid"], [])
            arr = [r for r in arr if r["q"] != pregunta] + [
                {"q": pregunta, "opcion": opcion, "t": round(time.time() - base, 1)}]
            sesion["respuestas"][auth["uid"]] = arr
        self._json(200, {"ok": True, "opcion": opcion})

    def _post_siguiente(self):
        payload = self._read_json()
        auth = self._auth(payload)
        if not auth:
            self._json(403, {"ok": False, "error": "initData invalido o vencido"})
            return
        code = str(payload.get("code", "")).strip()
        accion = str(payload.get("accion", ""))
        if code not in SESIONES:
            self._json(404, {"ok": False, "error": "sesion no encontrada"})
            return
        sesion = SESIONES[code]
        if auth["uid"] != sesion["creador"]["uid"]:
            self._json(403, {"ok": False, "error": "solo el profesor controla la sesion"})
            return
        total = len(sesion["preguntas"])
        with _sesiones_lock:
            if accion in ("empezar", "siguiente"):
                if sesion["status"] == "espera":
                    sesion["current"] = 0
                    sesion["status"] = "activa"
                    sesion["inicio_at"] = time.time()
                elif sesion["status"] == "activa":
                    if sesion["current"] + 1 >= total:
                        sesion["status"] = "final"
                    else:
                        sesion["current"] += 1
                elif sesion["status"] == "final":
                    sesion["status"] = "cerrada"
                    guardar_reporte(sesion)
            elif accion == "ver_resultados":
                sesion["status"] = "final"
            elif accion == "reiniciar":
                sesion["current"] = -1
                sesion["status"] = "espera"
                sesion["inicio_at"] = None
                sesion["respuestas"] = {}
            elif accion == "cerrar":
                if sesion["status"] != "cerrada":
                    guardar_reporte(sesion)
                sesion["status"] = "cerrada"
            else:
                self._json(400, {"ok": False, "error": "accion invalida"})
                return
        self._json(200, {"ok": True, "status": sesion["status"], "current": sesion["current"]})


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    n = len(cargar_examenes())
    print(
        f"Backend de Examenes listo en http://localhost:{PORT}\n"
        f"  - Mini App: {WEBAPP_DIR}\n"
        f"  - Banco de preguntas: {n} examenes ({BANCO_DIR})\n"
        f"  - PIN profesor: {'si' if PIN_PROFESOR else 'desactivado'}\n"
        "Presiona Ctrl+C para detener."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")


if __name__ == "__main__":
    main()