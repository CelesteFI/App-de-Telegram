"""deslizador.py — Minijuego 1: Desliza el Atributo (ED Tinder).

Mecanica (Minijuegos.md #1): sale una ecuacion diferencial y una propiedad
encima ("Es lineal", "Es autonoma"...). Deslizas a la DERECHA para decir
Verdadero y a la IZQUIERDA para decir Falso.

Se decidio aqui que el veredicto es teorico puro: no se resuelve nada, solo se
reconoce la estructura de la ecuacion (orden, linealidad, homogeneidad,
separabilidad, exactitud...). Por eso se puede jugar sin calculadora.

CONTENIDO: los casos viven en `data/minijuegos/deslizador.json` (clave "casos").
Cada caso es {"attr", "tex", "valor", "d", "porque"}:
  - attr : la propiedad que se muestra arriba.
  - tex  : la ecuacion en LaTeX.
  - valor: True si la propiedad es verdadera para esa ecuacion.
  - d    : dificultad 1..3.
  - porque: explicacion mostrada al calificar.
"""

from . import base

# Metadatos del juego (que muestra el menu). El contenido NO va aqui.
JUEGO = {
    "id": "deslizador",
    "titulo": "Desliza el Atributo",
    "icono": "\U0001F504",
    "resumen": "Desliza a la derecha si la propiedad es verdadera; a la izquierda si es falsa.",
    "mecanica": "Una propiedad y una ecuacion. Desliza: derecha = verdadero, izquierda = falso.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["clasificacion", "teoria"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Arma `cantidad` rondas con casos del JSON que no pasen la dificultad."""
    limite = base.nivel_limite(nivel)
    casos = base.contenido("deslizador").get("casos", [])
    pool = [c for c in casos if c.get("d", 1) <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, caso in enumerate(elegidos):
        salida.append({
            "id": f"d{i}",
            "attr": caso["attr"],
            "formula": caso["tex"],
            "valor": bool(caso["valor"]),
            "porque": caso["porque"],
        })
    return salida


def publico(ronda: dict) -> dict:
    """Lo que ve el navegador: nunca se manda `valor` (la respuesta)."""
    return {
        "id": ronda["id"],
        "attr": ronda["attr"],
        "formula": ronda["formula"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """Compara el deslizamiento del jugador con el veredicto guardado."""
    if isinstance(respuesta, str):
        dado = respuesta.strip().lower() in ("v", "verdadero", "true", "1")
    else:
        dado = bool(respuesta)
    ok = dado == ronda["valor"]
    veredicto = "verdadero" if ronda["valor"] else "falso"
    return {
        "correcto": ok,
        "puntaje": 100 if ok else 0,
        "detalle": ("Correcto: " if ok else "No: ") + ronda["porque"],
        "marcador": "\u2713" if ok else "\u2717",
        "valor_real": veredicto,
    }
