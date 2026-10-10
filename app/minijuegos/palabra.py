"""palabra.py — Minijuego 9: La Palabra Oculta (ED Crossword Lite).

Mecanica (Minijuegos.md #9): se da una pista conceptual estricta y los
espacios vacios de una palabra. Abajo hay un teclado virtual con SOLO las
letras que componen la palabra mas tres letras trampa.

El navegador recibe la pista, el largo y las letras disponibles, pero nunca la
palabra: esa se queda en el servidor y se compara al enviar la respuesta.
"""

from . import base

JUEGO = {
    "id": "palabra",
    "titulo": "La Palabra Oculta",
    "icono": "\U0001F9ED",
    "resumen": "Pista conceptual + huecos. Adivina el termino de ED.",
    "mecanica": "Teclea con el teclado virtual. Tres fallos y se acaba la ronda.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["vocabulario", "pistas"],
}

# (pista, palabra, por que)
CASOS = [
    ("Tipo de solucion de una ED que se obtiene al asignar valores especificos a las constantes de la solucion general.",
     "PARTICULAR",
     "La solucion particular es una solucion concreta de la familia general.", 1),
    ("Ecuacion diferencial en la que $M\\,dx + N\\,dy$ es la diferencial total de una funcion de $x$ e $y$.",
     "EXACTA",
     "La condición es $\\partial M/\\partial y = \\partial N/\\partial x$.", 1),
    ("Raíces del polinomio característico que dan la solución complementaria de una ED lineal de segundo orden.",
     "RAICES",
     "Raices reales repetidas, reales distintas o complejas conjugadas.", 1),
    ("Transformada integral que convierte un problema con condición inicial en una ecuación algebraica.",
     "LAPLACE",
     "Su inversa recupera la función original.", 1),
    ("ED de primer orden $y' + P(x)y = Q(x)y^{n}$ que se resuelve con $y = v^{1-n}$.",
     "BERNOULLI",
     "Si $n = 1$ degenera en una ED lineal.", 1),
    ("ED de primer orden $y' = a(x)y^{2} + b(x)y + c(x)$; con una solución conocida se reduce a lineal.",
     "RICCATI",
     "Único caso no lineal de primer orden reducible a lineal.", 2),
    ("Propiedad de una ED separable; aquí $y' = f(x)g(y)$.",
     "SEPARABLE",
     "Se separan las variables y se integra cada lado.", 2),
    ("ED cuyo lado derecho $g(y)$ no contiene $x$ de forma explícita.",
     "AUTONOMA",
     "La evolucion depende solo del valor actual de $y$.", 2),
    ("Propiedad que garantiza que el problema con dato inicial tenga una única solución.",
     "UNICIDAD",
     "Se asegura con hipótesis de Lipschitz o con $\\partial f/\\partial y$ continua.", 3),
    ("Fenómeno que garantiza que exista al menos una solución del problema con dato inicial.",
     "EXISTENCIA",
     "Es la otra mitad del teorema de existencia y unicidad.", 3),
    ("Solución de una ED que incluye la constante de integración sin conocer el dato inicial.",
     "GENERAL",
     "La solución particular es la general con la constante ya determinada.", 3),
    ("Parte de la solución total que corresponde a la ED lineal homogénea asociada.",
     "HOMOGENEA",
     "Se le llama también solución complementaria: la que no ve el término no homogéneo.", 3),
]

LETRAS_TRAMPA = "ZQJXKW"


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [c for c in CASOS if c[3] <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, (pista, palabra, porque, _d) in enumerate(elegidos):
        letras = sorted(set(palabra))
        trampos = [c for c in LETRAS_TRAMPA if c not in letras][:3]
        teclado = sorted(letras + trampos)
        salida.append({
            "id": f"w{i}",
            "pista": pista,
            "palabra": palabra,
            "longitud": len(palabra),
            "letras": letras,
            "teclado": teclado,
            "trampas": trampos,
            "intentos": 3,
            "porque": porque,
        })
    return salida


def publico(ronda: dict) -> dict:
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
