"""config.py — Rutas y opciones del backend en un solo lugar.

Todo lo que se puede cambiar sin tocar logica se cambia aqui (o por variable
de entorno). Si mueves archivos, ajusta las variables de entorno:

    $env:PUERTO         = "8080"
    $env:BOT_TOKEN      = "123456:AAE..."
    $env:WEBAPP_DIR     = "webapp"
    $env:MINIJUEGOS_DIR = "data/minijuegos"
    $env:MATERIAS_FILE  = "data/minijuegos/quiz/materias.json"
    $env:QUIZZ_DIR      = "data/minijuegos/quiz"
    $env:RESULTADOS_DIR = "data/resultados"
    $env:DEV_AUTHPASS   = "1"   # solo desarrollo: acepta identidad falsa
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ruta(*partes: str) -> str:
    return os.path.join(RAIZ, *partes)


def ruta_env(nombre: str, por_defecto: str) -> str:
    valor = os.environ.get(nombre, "")
    return os.path.abspath(valor) if valor else por_defecto


PUERTO = int(os.environ.get("PUERTO") or os.environ.get("PORT") or 8080)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP_DIR = ruta_env("WEBAPP_DIR", ruta("webapp"))
# Contenido: un JSON por minijuego en data/minijuegos/ y, dentro, la carpeta
# quiz/ con el catalogo (materias.json) y un quiz_tema_<tema>.json por tema.
MINIJUEGOS_DIR = ruta_env("MINIJUEGOS_DIR", ruta("data", "minijuegos"))
MATERIAS_FILE = ruta_env("MATERIAS_FILE", ruta("data", "minijuegos", "quiz", "materias.json"))
QUIZZ_DIR = ruta_env("QUIZZ_DIR", ruta("data", "minijuegos", "quiz"))
RESULTADOS_DIR = ruta_env("RESULTADOS_DIR", ruta("data", "resultados"))
DEV_AUTHPASS = os.environ.get("DEV_AUTHPASS", "") == "1"

MAX_AGE_INITDATA = int(os.environ.get("MAX_AGE_INITDATA", "3600"))
MAX_INTENTOS_VIVOS = int(os.environ.get("MAX_INTENTOS_VIVOS", "400"))
CADUCIDAD_INTENTO = float(os.environ.get("CADUCIDAD_INTENTO", "14400"))

NOMBRE_APP = os.environ.get("NOMBRE_APP", "Repaso de Ecuaciones Diferenciales")
VERSION = "2.0"
