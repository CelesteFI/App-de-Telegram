"""banco.py — Catalogo de materias, temas y preguntas.

De donde sale la informacion (todo junto en data/minijuegos/quiz/):

    data/minijuegos/quiz/materias.json              -> materias y temas
    data/minijuegos/quiz/quiz_tema_<tema>.json      -> preguntas de ese tema

Formato de una pregunta (los campos extra son opcionales):

    {
      "p": "enunciado (admite LaTeX entre $...$)",
      "f": "formula o dato que se muestra aparte (opcional)",
      "opciones": ["a", "b", "c", "d"],
      "correcta": 0,
      "explicacion": "por que esa es la correcta (opcional pero recomendado)"
    }

Un tema sin archivo de preguntas aparece en el catalogo marcado como
`disponible: false` y la app lo avisa en vez de fallar.
"""

from ...nucleo import config
from ...nucleo.almacen import leer_carpeta_json, leer_json

_CLAVES = ("p", "f", "opciones", "correcta")


def _limpiar_pregunta(q: dict) -> dict | None:
    """Deja la pregunta en un formato seguro y completo, o None si no sirve."""
    if not isinstance(q, dict):
        return None
    p = str(q.get("p", "") or "").strip()
    opciones = q.get("opciones")
    if not p or not isinstance(opciones, (list, tuple)) or len(opciones) < 2:
        return None
    try:
        correcta = int(q.get("correcta", -1))
    except (TypeError, ValueError):
        return None
    if not 0 <= correcta < len(opciones):
        return None
    limpia = {
        "p": p[:1500],
        "f": str(q.get("f", "") or "")[:1500],
        "opciones": [str(o)[:600] for o in opciones],
        "correcta": correcta,
        "explicacion": str(q.get("explicacion", "") or "")[:1200],
    }
    for extra in ("id", "tipo", "tag"):
        if q.get(extra):
            limpia[extra] = str(q[extra])[:80]
    return limpia


def _leer_quizzes() -> dict:
    """{tema: {id, titulo, descripcion, preguntas[]}} con preguntas ya limpiadas."""
    indice: dict[str, dict] = {}
    for nombre, datos in leer_carpeta_json(config.QUIZZ_DIR):
        items = datos.get("preguntas") if isinstance(datos, dict) else datos
        if not isinstance(items, list):
            continue
        preguntas = [limpia for limpia in (_limpiar_pregunta(q) for q in items) if limpia]
        if not preguntas:
            continue
        # El tema sale del campo "tema" del JSON; si falta, del nombre del
        # archivo quitando el prefijo "quiz_tema_" (p. ej. quiz_tema_exactas).
        tema = str(datos.get("tema") or "").strip()
        if not tema:
            base = nombre[:-5] if nombre.lower().endswith(".json") else nombre
            tema = base[len("quiz_tema_"):] if base.startswith("quiz_tema_") else base
            tema = tema.strip()
        if not tema:
            continue
        indice[tema] = {
            "id": str(datos.get("id") or f"quiz_{tema}"),
            "tema": tema,
            "titulo": str(datos.get("titulo") or f"Quiz de {tema}"),
            "descripcion": str(datos.get("descripcion", "") or ""),
            "preguntas": preguntas,
        }
    return indice


def quizzes() -> dict:
    return _leer_quizzes()


def materias() -> list[dict]:
    """Materias del config con, por tema: si hay quiz y cuantas preguntas tiene."""
    datos = leer_json(config.MATERIAS_FILE, {}) or {}
    lista = datos.get("materias") if isinstance(datos, dict) else None
    if not isinstance(lista, list):
        return []
    indice = _leer_quizzes()
    salida = []
    for materia in lista:
        if not isinstance(materia, dict) or not materia.get("id"):
            continue
        temas = []
        for tema in materia.get("temas", []) or []:
            if not isinstance(tema, dict) or not tema.get("id"):
                continue
            quiz = indice.get(str(tema["id"]))
            temas.append({
                "id": str(tema["id"]),
                "nombre": str(tema.get("nombre", tema["id"])),
                "resumen": str(tema.get("resumen", "")),
                "disponible": bool(quiz),
                "total": len(quiz["preguntas"]) if quiz else 0,
            })
        if not temas:
            continue
        salida.append({
            "id": str(materia["id"]),
            "nombre": str(materia.get("nombre", materia["id"])),
            "icono": str(materia.get("icono", "📘")),
            "descripcion": str(materia.get("descripcion", "")),
            "temas": temas,
            "total_preguntas": sum(t["total"] for t in temas),
            "total_disponibles": sum(1 for t in temas if t["disponible"]),
        })
    return salida


def buscar_tema(materia_id: str, tema_id: str) -> dict:
    """Devuelve {materia, tema, quiz} o lanza KeyError."""
    for materia in materias():
        if materia["id"] != materia_id:
            continue
        for tema in materia["temas"]:
            if tema["id"] == tema_id:
                return {"materia": materia, "tema": tema, "quiz": _leer_quizzes().get(tema_id)}
    raise KeyError(f"tema {materia_id}/{tema_id} no encontrado")


def preguntas(materia_id: str, tema_id: str) -> list[dict]:
    datos = buscar_tema(materia_id, tema_id)["quiz"]
    return list(datos["preguntas"]) if datos else []


def temas_de_contenido() -> list[dict]:
    """Temas que tienen preguntas, con su materia (lo usan los minijuegos)."""
    indice = _leer_quizzes()
    salida = []
    for materia in materias():
        for tema in materia["temas"]:
            if indice.get(tema["id"]):
                salida.append({
                    "materia": materia["id"],
                    "materia_nombre": materia["nombre"],
                    "tema": tema["id"],
                    "tema_nombre": tema["nombre"],
                })
    return salida
