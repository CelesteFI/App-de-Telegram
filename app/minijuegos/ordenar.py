"""ordenar.py — Minijuego 7: Ordena la Secuencia (Algorithm Sort).

Mecanica (Minijuegos.md #7): aparecen los pasos logicos de un metodo
teorico completamente desordenados y hay que reacomodarlos en la secuencia
correcta arrastrando los bloques.

Los pasos son de procedimiento (no de calculo): "comprobar, calcular el
factor integrante, integrar, aplicar la condicion inicial"...
"""

from . import base

JUEGO = {
    "id": "ordenar",
    "titulo": "Ordena la Secuencia",
    "icono": "\U0001F524",
    "resumen": "Reacomoda los pasos de un metodo en el orden logico correcto.",
    "mecanica": "Arrastra los bloques hasta que hagan sentido de principio a fin.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["procedimiento", "metodos"],
}

# (titulo, [pasos en orden correcto], dificultad)
SECUENCIAS = [
    ("Metodo de coeficientes indeterminados", [
        r"Proponer la forma de la solucion particular $y_p$.",
        r"Resolver la ED homogenea asociada para obtener $y_c$.",
        r"Derivar $y_p$ y sustituirla en la ED original para armar el sistema de ecuaciones.",
        r"Determinar los coeficientes y escribir $y = y_c + y_p$.",
    ], 1),

    ("Comprobar si una ED es exacta", [
        r"Escribir $M\,dx + N\,dy = 0$ e identificar $M$ y $N$.",
        r"Calcular $\partial M/\partial y$ y $\partial N/\partial x$.",
        r"Comparar: si son iguales, la ED es exacta y se integra directo.",
        r"Si no son iguales, buscar el factor integrante $\mu(x)$ o $\mu(y)$.",
    ], 1),

    ("ED lineal de primer orden", [
        r"Pasar todo a la forma $y' + P(x)y = f(x)$.",
        r"Calcular el factor integrante $\mu(x) = e^{\int P(x)dx}$.",
        r"Multiplicar la ED por $\mu(x)$ para que el lado izquierdo sea una derivada exacta.",
        r"Integrar y usar la condicion inicial para despejar la constante.",
    ], 1),

    ("ED separable", [
        r"Identificar la forma $y' = f(x)g(y)$.",
        r"Despejar: $\dfrac{dy}{g(y)} = f(x)\,dx$.",
        r"Integrar ambos miembros.",
        r"Aplicar la condicion inicial y despejar $y$ en funcion de $x$.",
    ], 1),

    ("Transformada de Laplace en una ED con dato inicial", [
        r"Aplicar $\mathcal{L}$ a los dos miembros usando las propiedades de la transformada.",
        r"Sustituir las condiciones iniciales para obtener la ecuacion algebraica en $Y(s)$.",
        r"Despejar $Y(s)$.",
        r"Aplicar la transformada inversa y recuperar $y(t)$.",
    ], 2),

    ("Coeficientes indeterminados con resonancia", [
        r"Escribir la ED homogenea y hallar sus raices.",
        r"Detectar que el termino no homogeneo coincide con una raiz del polinomio caracteristico.",
        r"Multiplicar $y_p$ por $x^{s}$ con $s$ = veces que se repite la raiz.",
        r"Determinar los coeficientes y sumar $y_c + y_p$.",
    ], 3),

    ("Metodo de variacion de parametros", [
        r"Resolver la ED homogenea asociada $y'' + p(x)y' + q(x)y = 0$ y obtener $y_1, y_2$.",
        r"Calcular el Wronskiano $W = y_1y_2' - y_1'y_2$.",
        r"Proponer $y_p = u(x)y_1 + v(x)y_2$ con la restriccion $u'y_1 + v'y_2 = 0$.",
        r"Integrar $u'$ y $v'$ e imponer las condiciones iniciales.",
        r"Escribir la solucion general $y = y_c + y_p$.",
    ], 3),

    ("Serie de Fourier de una funcion periodica", [
        r"Verificar que $f$ cumple las condiciones de existencia de la serie.",
        r"Calcular los coeficientes $a_n$ y $b_n$ integrando sobre un periodo.",
        r"Escribir la serie con esos coeficientes.",
        r"Evaluar el valor de la serie en los puntos de discontinuidad (promedio de los limites).",
    ], 3),
]


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    limite = base.nivel_limite(nivel)
    pool = [s for s in SECUENCIAS if s[2] <= limite]
    elegidos = base.tomar(azar, pool, cantidad)
    salida = []
    for i, (titulo, pasos, _d) in enumerate(elegidos):
        indices = list(range(len(pasos)))
        salida.append({
            "id": f"o{i}",
            "titulo": titulo,
            "pasos": pasos,
            "orden_mostrado": base.barajar(azar, indices),
            "solucion": list(range(len(pasos))),
            "pista": f"Son {len(pasos)} pasos.",
        })
    return salida


def publico(ronda: dict) -> dict:
    return {
        "id": ronda["id"],
        "titulo": ronda["titulo"],
        "pasos": [ronda["pasos"][i] for i in ronda["orden_mostrado"]],
        "total": len(ronda["pasos"]),
        "pista": ronda["pista"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = lista con el indice (en el orden mostrado) de cada paso,
    ya en el orden que quedo en pantalla."""
    if not isinstance(respuesta, (list, tuple)):
        respuesta = []
    orden = ronda["orden_mostrado"]
    elegido = [int(v) for v in respuesta if str(v).lstrip("-").isdigit()]
    correctas = 0
    for posicion, paso in enumerate(ronda["solucion"]):
        if posicion < len(elegido):
            indice_real = orden[elegido[posicion]]
            if indice_real == paso:
                correctas += 1
    total = len(ronda["solucion"])
    detalle = "La secuencia quedo perfecta." if correctas == total else \
        f"{correctas} de {total} pasos en su lugar. El orden correcto es: " + \
        " ".join(f"{i + 1}) {ronda['pasos'][p]}" for i, p in enumerate(ronda["solucion"]))
    return {
        "correcto": correctas == total,
        "puntaje": base.puntos(correctas / total if total else 0),
        "detalle": detalle,
        "correctas": correctas,
        "total": total,
    }
