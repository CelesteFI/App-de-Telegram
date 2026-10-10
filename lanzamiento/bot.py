"""bot.py — Bot de Telegram para la Mini App de Repaso de ED.

Todo el repaso vive en una sola pantalla "Practicar": el quiz por tema y los
10 minijuegos juntos (el quiz es un juego más, no una sección aparte).

Comandos:
    /start  -> botón para abrir la app
    /menu   -> deja el botón de menú del chat apuntando a la app
    /ayuda  -> cómo se usa

Uso:
    $env:BOT_TOKEN  = "TOKEN_DE_BOTFATHER"
    $env:WEBAPP_URL = "https://<ngrok>.ngrok.app"   (HTTPS obligatorio)
    python bot.py
"""

import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://localhost").rstrip("/")

URL_APP = f"{WEBAPP_URL}/"
URL_PRACTICAR = f"{WEBAPP_URL}/#/juegos"

SALUDO = (
    "\U0001f4d0 Repaso de Ecuaciones Diferenciales\n\n"
    "Abre la app para practicar por tu cuenta:\n"
    "\U0001f3aa Todo en un solo lugar: quiz por tema + 10 minijuegos de teoría.\n"
    "\U0001f4c8 Cada quien tiene sus marcas y su historial: no hace falta código.\n\n"
    "Prueba también /menu y /ayuda."
)


def teclado() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f3aa Abrir Practicar", web_app=WebAppInfo(url=URL_PRACTICAR))],
        [InlineKeyboardButton("\U0001f3e0 Inicio", web_app=WebAppInfo(url=URL_APP))],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(SALUDO, reply_markup=teclado())


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp(text="Repaso ED", web_app=WebAppInfo(url=URL_APP)),
    )
    await update.message.reply_text("Listo: abajo tienes el botón 'Repaso ED'.")


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Cómo se usa:\n"
        "1) Pulsa 'Abrir Practicar'. Telegram te identifica solo.\n"
        "2) Arriba tienes el Quiz por tema (8 temas, con explicación al instante).\n"
        "3) Abajo los 10 minijuegos: memoria, cestas, globos, intruso y más.\n"
        "4) Al terminar verás tu porcentaje y la revisión.\n\n"
        "Tu progreso se guarda en este dispositivo y en el servidor bajo tu usuario."
    )


async def cualquier_texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Aquí solo hay repaso: pulsa /start para abrir la app.",
        reply_markup=teclado(),
    )


async def al_arrancar(app: Application) -> None:
    """Fija el botón de menú global a la URL de ESTA corrida.

    El botón de menú es persistente: si no se actualiza, sigue apuntando a la
    URL del túnel anterior (ya muerta) y la Mini App abre en blanco. Por eso se
    reconfigura cada vez que arranca el bot.
    """
    try:
        await app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Repaso ED", web_app=WebAppInfo(url=URL_APP)),
        )
        print(f"Botón de menú 'Repaso ED' -> {URL_APP}")
    except Exception as exc:  # noqa: BLE001 - no queremos tumbar el bot por esto
        print(f"No pude fijar el botón de menú: {exc}")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).post_init(al_arrancar).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cualquier_texto))

    print("Bot en línea. Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
