"""palabra.py — Minijuego 9: La Palabra Oculta (ED Crossword Lite).

Mecanica (Minijuegos.md #9): se da una pista conceptual estricta y los
espacios vacios de una palabra. Abajo hay un teclado virtual con SOLO las
letras que componen la palabra mas tres letras trampa.

El navegador recibe la pista, el largo y las letras disponibles, pero nunca la
palabra: esa se queda en el servidor y se compara al enviar la respuesta.

CONTENIDO: `data/minijuegos/palabra.json` con:
  - "letras_trampa": letras de relleno para el teclado.
  - "casos": [{"pista","palabra","porque","d"}].
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "palabra",
    "titulo": "La Palabra Oculta",
    "icono": "\U0001F9ED",
    "resumen": "Pista conceptual + huecos. Adivina el termino de ED.",
    "mecanica": "Teclea con el teclado virtual. Tres fallos y se acaba la ronda.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["vocabulario", "pistas"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Toma casos del JSON y arma el teclado (letras reales + trampas)."""
    limite = base.nivel_limite(nivel)
    datos = base.contenido("palabra")
    casos = datos.get("casos", [])
    trampas_pool = datos.get("letras_trampa", "ZQJXKW")
    pool = [c for c in casos if c.get("d", 1) <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, caso in enumerate(elegidos):
        palabra = caso["palabra"]
        letras = sorted(set(palabra))
        trampos = [c for c in trampas_pool if c not in letras][:3]
        teclado = sorted(letras + trampos)
        salida.append({
            "id": f"w{i}",
            "pista": caso["pista"],
            "palabra": palabra,
            "longitud": len(palabra),
            "letras": letras,
            "teclado": teclado,
            "trampas": trampos,
            "intentos": 3,
            "porque": caso["porque"],
        })
    return salida


def publico(ronda: dict) -> dict:
    """Sin `palabra` ni `porque`: la respuesta se queda en el servidor."""
    return {
        "id": ronda["id"],
        "pista": ronda["pista"],
        "longitud": ronda["longitud"],
        "letras": ronda["letras"],
        "teclado": ronda["teclado"],
        "intentos": ronda["intentos"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = la palabra tecleada (o "" si se acabaron los intentos)."""
    palabra = ronda["palabra"].upper()
    if isinstance(respuesta, dict):
        respuesta = respuesta.get("palabra", "")
    tecleada = str(respuesta or "").strip().upper().replace(" ", "")
    ok = bool(tecleada) and tecleada == palabra
    return {
        "correcto": ok,
        "puntaje": 100 if ok else 0,
        "detalle": (f"¡Correcto! {ronda['porque']}" if ok
                    else f"La palabra era {palabra}. {ronda['porque']}"),
        "palabra": palabra,
    }
