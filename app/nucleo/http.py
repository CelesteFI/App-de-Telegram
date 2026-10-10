"""http.py — Servidor HTTP minimo con ruteo por tabla.

No usa frameworks: solo `http.server` de la libreria estandar, que es lo que
ya usaba la version anterior. Cada modulo de la app registra sus rutas aqui:

    from ..nucleo.http import ruta
    @ruta("GET", "/api/quiz/intentos")
    def listar(peticion): ...

Un manejador recibe un `Peticion` y devuelve un `Responde` (o un dict, que se
convierte solo en JSON 200).
"""

import json
import re
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from . import config
from .seguridad import identificar


class ErrorApi(Exception):
    """Error que se convierte en {ok: false, error: ...} con su codigo HTTP."""

    def __init__(self, mensaje: str, codigo: int = 400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


class Responde:
    """Respuesta HTTP ya construida (texto plano, HTML, CSV o binario)."""

    def __init__(self, cuerpo: bytes | str, codigo: int = 200, tipo: str = "text/plain; charset=utf-8"):
        self.cuerpo = cuerpo.encode("utf-8") if isinstance(cuerpo, str) else cuerpo
        self.codigo = codigo
        self.tipo = tipo


def json_texto(datos: Any, codigo: int = 200) -> Responde:
    return Responde(json.dumps(datos, ensure_ascii=False), codigo, "application/json; charset=utf-8")


def texto(cuerpo: str, tipo: str = "text/plain; charset=utf-8", codigo: int = 200) -> Responde:
    return Responde(cuerpo, codigo, tipo)


class Peticion:
    """Lo que un manejador necesita saber de la llamada."""

    def __init__(self, metodo: str, camino: str, consulta: dict, cuerpo: dict,
                 parametros: dict, usuario: dict | None):
        self.metodo = metodo
        self.camino = camino
        self.consulta = consulta
        self.cuerpo = cuerpo
        self.parametros = parametros
        self.usuario = usuario

    def get(self, nombre: str, por_defecto: Any = "") -> Any:
        valor = self.cuerpo.get(nombre, self.consulta.get(nombre, por_defecto))
        return por_defecto if valor is None else valor

    def entero(self, nombre: str, por_defecto: int = 0, minimo: int | None = None,
               maximo: int | None = None) -> int:
        try:
            valor = int(self.get(nombre, por_defecto))
        except (TypeError, ValueError):
            valor = por_defecto
        if minimo is not None:
            valor = max(minimo, valor)
        if maximo is not None:
            valor = min(maximo, valor)
        return valor

    def texto(self, nombre: str, por_defecto: str = "", largo: int = 4000) -> str:
        return str(self.get(nombre, por_defecto))[:largo]

    def exige_usuario(self) -> dict:
        if not self.usuario:
            raise ErrorApi("identidad no valida: abre la app desde Telegram", 403)
        return self.usuario


class _Ruta:
    def __init__(self, metodo: str, patron: str, manejador: Callable):
        self.metodo = metodo
        self.patron = patron
        self.re = re.compile("^" + patron + "$")
        self.manejador = manejador


class Router:
    def __init__(self):
        self.rutas: list[_Ruta] = []

    def agregar(self, metodo: str, patron: str, manejador: Callable) -> None:
        self.rutas.append(_Ruta(metodo.upper(), patron, manejador))

    def buscar(self, metodo: str, camino: str):
        permitido = False
        for ruta in self.rutas:
            coincidencias = ruta.re.match(camino)
            if not coincidencias:
                continue
            if ruta.metodo != metodo.upper():
                permitido = True
                continue
            return ruta.manejador, dict(coincidencias.groupdict())
        if permitido:
            raise ErrorApi("metodo no permitido para esta ruta", 405)
        return None, None


_router = Router()


class Manejador(SimpleHTTPRequestHandler):
    """Sirve los archivos de `webapp` y delega `/api/...` al Router."""

    server_version = f"QuizED/{config.VERSION}"
    router: Router = _router

    # Tipos MIME explicitos: algunos WebView (iOS/WKWebView) rechazan fuentes
    # servidas como application/octet-stream, y entonces KaTeX no pinta. El
    # resto son para que ningun navegador adivine mal JavaScript o CSS.
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".woff2": "font/woff2",
        ".woff": "font/woff",
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".json": "application/json",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=config.WEBAPP_DIR, **kwargs)

    def log_message(self, formato, *args):
        pass

    def log_error(self, formato, *args):
        pass

    def end_headers(self):
        if getattr(self, "_estatico", False):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        partes = urllib.parse.urlsplit(self.path)
        if partes.path.startswith("/api/"):
            self._despachar("GET", partes.path, dict(urllib.parse.parse_qsl(partes.query or "")))
            return
        self._estatico = True
        try:
            super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self._estatico = False

    def do_HEAD(self):
        partes = urllib.parse.urlsplit(self.path)
        if partes.path.startswith("/api/"):
            self._despachar("HEAD", partes.path, dict(urllib.parse.parse_qsl(partes.query or "")))
            return
        self._estatico = True
        try:
            super().do_HEAD()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self._estatico = False

    def do_POST(self):
        partes = urllib.parse.urlsplit(self.path)
        if partes.path.startswith("/api/"):
            self._despachar("POST", partes.path, dict(urllib.parse.parse_qsl(partes.query or "")))
            return
        self._enviar(json_texto({"ok": False, "error": "ruta no encontrada"}, 404))

    def _leer_cuerpo(self) -> dict:
        largo = int(self.headers.get("Content-Length") or 0)
        if largo <= 0:
            return {}
        if largo > 2_000_000:
            raise ErrorApi("peticion demasiado grande", 413)
        crudo = self.rfile.read(largo)
        try:
            datos = json.loads(crudo or b"{}")
        except ValueError:
            raise ErrorApi("cuerpo JSON invalido", 400)
        return datos if isinstance(datos, dict) else {}

    def _despachar(self, metodo: str, camino: str, consulta: dict):
        try:
            manejador, parametros = self.router.buscar(metodo, camino)
            if manejador is None:
                raise ErrorApi("ruta no encontrada", 404)
            cuerpo = self._leer_cuerpo() if metodo == "POST" else {}
            peticion = Peticion(metodo, camino, consulta, cuerpo, parametros,
                                 identificar(cuerpo, consulta, self.headers))
            respuesta = manejador(peticion)
            if isinstance(respuesta, Responde):
                self._enviar(respuesta)
            elif isinstance(respuesta, dict):
                self._enviar(json_texto(respuesta))
            elif respuesta is None:
                self._enviar(json_texto({"ok": True}))
            else:
                raise ErrorApi("el manejador no devolvio una respuesta valida", 500)
        except ErrorApi as exc:
            self._enviar(json_texto({"ok": False, "error": exc.mensaje}, exc.codigo))
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            self._enviar(json_texto({"ok": False, "error": "error interno del servidor"}, 500))

    def _enviar(self, respuesta: Responde):
        self.send_response(respuesta.codigo)
        self.send_header("Content-Type", respuesta.tipo)
        self.send_header("Content-Length", str(len(respuesta.cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(respuesta.cuerpo)
        except (BrokenPipeError, ConnectionResetError):
            pass


def ruta(metodo: str, patron: str):
    """Decorador para registrar un manejador en el router global."""

    def envoltorio(manejador: Callable):
        _router.agregar(metodo, patron, manejador)
        return manejador

    return envoltorio


def construir_servidor(router: Router | None = None, puerto: int | None = None):
    activo = router if router is not None else _router
    clase = type("ManejadorApp", (Manejador,), {"router": activo})
    servidor = ThreadingHTTPServer(("0.0.0.0", puerto if puerto is not None else config.PUERTO), clase)
    servidor.daemon_threads = True
    return servidor
