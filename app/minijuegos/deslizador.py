"""deslizador.py — Minijuego 1: Desliza el Atributo (ED Tinder).

Mecanica (Minijuegos.md #1): sale una ecuacion diferencial y una propiedad
encima ("Es lineal", "Es autonoma"...). Deslizas a la DERECHA para decir
Verdadero y a la IZQUIERDA para decir Falso.

Se decidio aqui que el veredicto es teorico puro: no se resuelve nada, solo se
reconoce la estructura de la ecuacion (orden, linealidad, homogeneidad,
separabilidad, exactitud...). Por eso se puede jugar sin calculadora.
"""

from . import base

JUEGO = {
    "id": "deslizador",
    "titulo": "Desliza el Atributo",
    "icono": "\U0001F504",
    "resumen": "Desliza a la derecha si la propiedad es verdadera; a la izquierda si es falsa.",
    "mecanica": "Una propiedad y una ecuacion. Desliza: derecha = verdadero, izquierda = falso.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["clasificacion", "teoria"],
}

# dificultad: 1 = glaring, 2 = normal, 3 = trampa de examen
CASOS = [
    # ---- linealidad ----
    {"attr": "Es lineal", "tex": r"y'' + 3y' + 2y = 0", "valor": True, "d": 1,
     "porque": r"$y$, $y'$ y $y''$ aparecen de primer grado y los coeficientes solo dependen de $x$."},
    {"attr": "Es lineal", "tex": r"y' + x\,y = e^{x}", "valor": True, "d": 1,
     "porque": r"Tiene la forma $y' + P(x)y = f(x)$, que es lineal de primer orden."},
    {"attr": "Es lineal", "tex": r"y' + y\,\tan y = 0", "valor": False, "d": 1,
     "porque": r"$\tan y$ depende de la incognita: deja de ser lineal."},
    {"attr": "Es lineal", "tex": r"y'' + 3y\,y' = 0", "valor": False, "d": 1,
     "porque": r"El producto $y\,y'$ es un termino no lineal (quintico grado si se desarrolla)."},
    {"attr": "Es lineal", "tex": r"y' + y = y\sin x", "valor": True, "d": 2,
     "porque": r"Reordenando: $y' + (1 - \sin x)y = 0$. Es lineal (y el producto $y\sin x$ no la rompe: $y$ sale factor)."},
    {"attr": "Es lineal", "tex": r"\dfrac{\partial u}{\partial t} = \alpha\, \dfrac{\partial^2 u}{\partial x^2}", "valor": True, "d": 2,
     "porque": r"Es lineal en $u$ y sus derivadas: es una EDP lineal."},
    {"attr": "Es lineal de primer orden", "tex": r"y'' - x y = 0", "valor": False, "d": 2,
     "porque": r"Lineal, si, pero de SEGUNDO orden."},
    {"attr": "Es lineal", "tex": r"y' = \dfrac{x}{y}", "valor": False, "d": 2,
     "porque": r"La incognita aparece en el denominador: no se puede escribir $y' + P(x)y = f(x)$."},

    # ---- homogeneidad (lineal) ----
    {"attr": "Es lineal homogenea", "tex": r"y' + 4y = 0", "valor": True, "d": 1,
     "porque": r"El segundo miembro es 0: es la ED homogenea."},
    {"attr": "Es lineal homogenea", "tex": r"y' - 2y = t", "valor": False, "d": 1,
     "porque": r"El segundo miembro $t$ no es cero: es NO homogenea."},
    {"attr": "Es lineal homogenea", "tex": r"y' + y = x", "valor": False, "d": 2,
     "porque": r"Lineal, pero con $f(x) = x \neq 0$."},
    {"attr": "Es homogenea de tipo no lineal", "tex": r"\dfrac{dy}{dx} = \dfrac{x^2 + y^2}{xy}", "valor": True, "d": 2,
     "porque": r"El lado derecho es funcion solo de $y/x$: es $F(y/x)$, la forma homogenea clasica (NO es 'lineal homogenea')."},
    {"attr": "Es lineal homogenea", "tex": r"y' = 1 + \dfrac{y}{x}", "valor": False, "d": 3,
     "porque": r"Es homogenea en el sentido no lineal ($F(y/x)$), pero no es lineal."},

    # ---- separabilidad ----
    {"attr": "Es separable", "tex": r"\dfrac{dy}{dx} = x^2 y", "valor": True, "d": 1,
     "porque": r"$y' = f(x)g(y)$ con $f(x)=x^2$ y $g(y)=y$: se separa."},
    {"attr": "Es separable", "tex": r"\dfrac{dy}{dx} = x + y", "valor": False, "d": 1,
     "porque": r"No se puede escribir como producto $f(x)g(y)$: es lineal de primer orden."},
    {"attr": "Es separable", "tex": r"\dfrac{dy}{dx} = \dfrac{1+y^2}{e^{x}}", "valor": True, "d": 3,
     "porque": r"$\dfrac{dy}{dx} = e^{-x}(1+y^2)$: producto de funcion de $x$ por funcion de $y$."},
    {"attr": "Es separable", "tex": r"\dfrac{dy}{dx} = \dfrac{y}{1 + x}", "valor": True, "d": 2,
     "porque": r"$y' = \dfrac{1}{1+x}\,y$, producto de $f(x)$ y $g(y)$."},

    # ---- exactitud ----
    {"attr": "Es exacta", "tex": r"y\,dx + x\,dy = 0", "valor": True, "d": 2,
     "porque": r"$\partial M/\partial y = 1 = \partial N/\partial x$; ademas $M dx + N dy = d(xy)$."},
    {"attr": "Es exacta", "tex": r"-y\,dx + x\,dy = 0", "valor": False, "d": 2,
     "porque": r"$\partial M/\partial y = -1 \neq 1 = \partial N/\partial x$."},
    {"attr": "Es exacta", "tex": r"(1+y^2)\,dx + 2xy\,dy = 0", "valor": True, "d": 2,
     "porque": r"Ambas derivadas parciales valen $2y$."},

    # ---- autonomia ----
    {"attr": "Es autonoma", "tex": r"y' = y^2 - 1", "valor": True, "d": 1,
     "porque": r"La $x$ no aparece: la evolucion depende solo de $y$."},
    {"attr": "Es autonoma", "tex": r"y' = x\,y", "valor": False, "d": 1,
     "porque": r"Aparece $x$ de forma explicita."},
    {"attr": "Es autonoma", "tex": r"y' = -y + 3", "valor": True, "d": 2,
     "porque": r"Autonoma (no aparece $x$) aunque no sea homogenea."},

    # ---- orden ----
    {"attr": "Es de segundo orden", "tex": r"y'' + y' + y = 0", "valor": True, "d": 1,
     "porque": r"La mayor derivada es $y''$."},
    {"attr": "Es de segundo orden", "tex": r"(y')^2 + x = 0", "valor": False, "d": 2,
     "porque": r"Aunque $(y')^2$ parezca de segundo grado, la mayor derivada es $y'$: es de PRIMER orden, y ademas no lineal por el cuadrado."},
    {"attr": "Es de tercer orden", "tex": r"y^{(4)} + y = 0", "valor": False, "d": 2,
     "porque": r"Es de cuarto orden."},
    {"attr": "Es de primer orden", "tex": r"y''' - y = x", "valor": False, "d": 1,
     "porque": r"Es de tercer orden."},

    # ---- tipos con nombre ----
    {"attr": "Es de tipo Bernoulli", "tex": r"y' + y = x\,y^{2}", "valor": True, "d": 1,
     "porque": r"Forma $y' + P(x)y = Q(x)y^{n}$ con $n = 2$."},
    {"attr": "Es de tipo Bernoulli", "tex": r"y' + y\ln y = 0", "valor": False, "d": 3,
     "porque": r"El termino $y\ln y$ no es $Q(x)y^{n}$: es una no lineal (aunque se resuelve separando)."},
    {"attr": "Es de tipo Riccati", "tex": r"y' = y^2 + y + x", "valor": True, "d": 2,
     "porque": r"$y' = a(x)y^2 + b(x)y + c(x)$ es exactamente Riccati."},
    {"attr": "Es de tipo Riccati", "tex": r"y' = y^3 + y", "valor": False, "d": 2,
     "porque": r"El grado en $y$ es 3, no 2: no es Riccati."},
    {"attr": "Es una ecuacion en derivadas parciales", "tex": r"\dfrac{\partial u}{\partial t} = \alpha\,\dfrac{\partial^2 u}{\partial x^2}", "valor": True, "d": 1,
     "porque": r"Aparecen derivadas parciales respecto a dos variables distintas."},
    {"attr": "Es una ecuacion en derivadas parciales", "tex": r"\dfrac{dy}{dx} = y", "valor": False, "d": 1,
     "porque": r"Solo hay derivadas ordinarias: es una EDO."},
    {"attr": "Es una ED lineal de primer orden", "tex": r"x^2 y' + x y = 0", "valor": True, "d": 2,
     "porque": r"Al dividir entre $x^2$: $y' + \dfrac{1}{x}y = 0$, lineal de primer orden."},
    {"attr": "Es una ED lineal de primer orden", "tex": r"\cos y\, y' + x = 0", "valor": False, "d": 3,
     "porque": r"$\cos y$ depende de la incognita: no es lineal."},
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [c for c in CASOS if c["d"] <= limite]
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
    return {
        "id": ronda["id"],
        "attr": ronda["attr"],
        "formula": ronda["formula"],
    }


def califica(ronda: dict, respuesta) -> dict:
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
