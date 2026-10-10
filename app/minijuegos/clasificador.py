"""clasificador.py — Minijuego 6: Clasificador Rapido (Category Bin).

Mecanica (Minijuegos.md #6): abajo hay 2 o 3 canastas fijas (las categorias
de ED). Van apareciendo ecuaciones y hay que arrastrar cada una a la canasta
correcta antes de que se acabe el tiempo de la ronda.

Solo hay que RECONOCER la estructura de la ecuacion: separarla, ver si es
exacta por derivadas parciales, etc. Ninguna ronda pide integrar ni despejar.

Cuidado con las ecuaciones que son de dos tipos a la vez (`y' = y/x` es
homogenea Y separable): esas quedaron fuera del pozo a proposito, para que
una ronda nunca tenga una respuesta ambigua.

CONTENIDO: `data/minijuegos/clasificador.json` con:
  - "pozo": {categoria: [ecuaciones en LaTeX]}.
  - "etiquetas": {categoria: nombre visible}.
  - "rondas": [{"categorias","por_categoria","segundos","d"}].
  - "explicar": {categoria: por que pertenece ahi}.
"""

from . import base

# Metadatos del juego (que muestra el menu).
JUEGO = {
    "id": "clasificador",
    "titulo": "Clasificador Rapido",
    "icono": "\U0001F9EA",
    "resumen": "Arrastra cada ecuacion a la canasta del tipo que le corresponde.",
    "mecanica": "Canastas abajo, ecuaciones en el centro. Sueltala antes de que se acabe el tiempo.",
    "niveles": ["facil", "medio", "dificil"],
    "etiquetas": ["clasificacion", "contrarreloj"],
}


def rondas(azar, nivel: str, cantidad: int, tema=None) -> list[dict]:
    """Elige `cantidad` configuraciones de canastas y reparte sus ecuaciones."""
    limite = base.nivel_limite(nivel)
    datos = base.contenido("clasificador")
    pozo = datos.get("pozo", {})
    etiquetas = datos.get("etiquetas", {})
    definiciones = datos.get("rondas", [])
    candidatos = [r for r in definiciones if r.get("d", 1) <= limite] or definiciones[:1]
    salida = []
    for i in range(cantidad):
        ronda_def = azar.choice(candidatos)
        categorias = ronda_def["categorias"]
        por_cat = int(ronda_def.get("por_categoria", 6))
        segundos = int(ronda_def.get("segundos", 40))
        elegidas = []
        for cat in categorias:
            for tex in base.tomar(azar, pozo.get(cat, []), max(2, por_cat // 2)):
                elegidas.append({"id": f"{i}-{len(elegidas)}", "tex": tex, "cat": cat})
        base.barajar(azar, elegidas)
        salida.append({
            "id": f"k{i}",
            "canastas": [{"clave": c, "nombre": etiquetas.get(c, c)} for c in categorias],
            "items": elegidas,
            "segundos": segundos,
        })
    return salida


def publico(ronda: dict) -> dict:
    """Sin `cat`: a que canasta va cada item lo decide el servidor."""
    return {
        "id": ronda["id"],
        "canastas": ronda["canastas"],
        "items": [{"id": it["id"], "tex": it["tex"]} for it in ronda["items"]],
        "segundos": ronda["segundos"],
    }


def califica(ronda: dict, respuesta) -> dict:
    """`respuesta` = lista con la clave de la canasta elegida por cada item,
    en el mismo orden en que los recibiste."""
    datos = base.contenido("clasificador")
    etiquetas = datos.get("etiquetas", {})
    explicar = datos.get("explicar", {})
    if isinstance(respuesta, dict):
        elegido_por_id = {str(k): str(v) for k, v in respuesta.items()}
    elif isinstance(respuesta, (list, tuple)):
        elegido_por_id = {it["id"]: str(respuesta[i]) for i, it in enumerate(ronda["items"])
                          if i < len(respuesta)}
    else:
        elegido_por_id = {}
    acertados = [it for it in ronda["items"] if elegido_por_id.get(it["id"]) == it["cat"]]
    fallados = [it for it in ronda["items"] if elegido_por_id.get(it["id"]) != it["cat"]]
    total = len(ronda["items"])
    ejemplos = "; ".join(f"`{it['tex']}` era {etiquetas.get(it['cat'], it['cat'])} "
                         f"({explicar.get(it['cat'], '')})" for it in fallados[:3])
    detalle = (f"Las {total} ecuaciones quedaron en su canasta." if not fallados
               else f"{len(acertados)} de {total} bien clasificadas. {ejemplos}")
    return {
        "correcto": not fallados,
        "puntaje": base.puntos(len(acertados) / total if total else 0),
        "detalle": detalle,
        "aciertos": len(acertados),
        "total": total,
        "fallados": [{"id": it["id"], "cat": etiquetas.get(it["cat"], it["cat"])} for it in fallados],
    }
