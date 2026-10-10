"""main.py — Arranque para hosting externo (Render, Koyeb, etc.).

En un servidor externo se corre UN solo proceso, asi que aqui se levantan
las dos cosas a la vez:

  1) el servidor HTTP de la Mini App + la API (en un hilo), y
  2) el bot de Telegram con long polling (en el hilo principal).

La URL publica se deduce sola en Render (`RENDER_EXTERNAL_URL`) para que el
boton del bot apunte al sitio correcto sin configurar nada. Si se define
`WEBAPP_URL` a mano, esa manda.

Uso local para probar:
    $env:BOT_TOKEN = "..."; python main.py
"""

import os
import sys
import threading

# Este archivo vive en lanzamiento/, pero importa el paquete "app" y el modulo
# "bot". Aseguramos que esten en sys.path sin importar como se invoque (a mano
# con "python lanzamiento/main.py" o desde Render con la misma ruta).
_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_AQUI)
for _ruta in (_AQUI, _RAIZ):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)


def _url_publica() -> str:
    """Devuelve la URL HTTPS publica y deja WEBAPP_URL lista para bot.py."""
    url = (os.environ.get("WEBAPP_URL")
           or os.environ.get("RENDER_EXTERNAL_URL")
           or "").strip()
    if url:
        url = url.rstrip("/")
        os.environ["WEBAPP_URL"] = url
        return url
    puerto = os.environ.get("PORT") or os.environ.get("PUERTO") or "8080"
    return f"http://localhost:{puerto}"


def _servir_web() -> None:
    """Levanta el servidor HTTP de la Mini App (bloquea el hilo)."""
    from app.nucleo import principal

    servidor = principal.construir_app()
    print(f"Mini App sirviendo (puerto {servidor.server_address[1]}).", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()


def main() -> None:
    url = _url_publica()
    print(f"URL publica de la Mini App: {url}", flush=True)

    hilo = threading.Thread(target=_servir_web, name="webapp", daemon=True)
    hilo.start()

    if not (os.environ.get("BOT_TOKEN") or "").strip():
        print("Sin BOT_TOKEN: la Mini App queda publicada, pero el bot no "
              "arranca. Configura el secreto BOT_TOKEN para que responda.",
              flush=True)
        threading.Event().wait()
        return

    import bot

    bot.main()


if __name__ == "__main__":
    main()
