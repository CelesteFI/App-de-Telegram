"""Bot de PRUEBA de Telegram Mini Apps (tonto: sin chatbot, solo botones).

Abre la Mini App de Examenes (2 areas: Teoria y Quizzes).
Los botones son INLINE para que la app reciba la identidad (initData).

Comandos:
  /start -> botones para abrir las areas de Teoria y Quizzes
  /menu  -> configura el boton de menu del chat para abrir la Mini App
  /ayuda -> un texto corto

Uso:
  $env:BOT_TOKEN  = "TOKEN_DE_BOTFATHER"
  $env:WEBAPP_URL = "https://<ngrok>.ngrok.app"   (HTTPS en produccion)
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
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://localhost")

URL_TEORIA = f"{WEBAPP_URL}/?area=teoria"
URL_QUIZZES = f"{WEBAPP_URL}/?area=quizzes"
URL_APP = f"{WEBAPP_URL}/"


def teclado_areas() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Area de Teoria", web_app=WebAppInfo(url=URL_TEORIA))],
        [InlineKeyboardButton("📝 Area de Quizzes", web_app=WebAppInfo(url=URL_QUIZZES))],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🧪 Bot de prueba de Mini Apps (sin chatbot).\n\n"
        "Selecciona un area para abrir la aplicacion:\n"
        "📖 Teoria: apuntes y formulas del curso.\n"
        "📝 Quizzes: examenes en vivo tipo Kahoot.\n\n"
        "Prueba tambien /menu y /ayuda.",
        reply_markup=teclado_areas(),
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp(text="Abrir app", web_app=WebAppInfo(url=URL_APP)),
    )
    await update.message.reply_text("✅ Listo, abajo tienes el boton 'Abrir app'.")


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Como se usa:\n"
        "1) El profesor pulsa '📝 Area de Quizzes' y elige un examen para crear una sesion.\n"
        "2) Aparece un codigo de 4 digitos; lo comparte con el grupo.\n"
        "3) Los alumnos abren la MISMA app, tocan 'Soy alumno', escriben el codigo y responden.\n"
        "4) El profesor ve los resultados por pregunta en vivo y puede descargar el reporte.\n\n"
        "Mientras tanto, en '📖 Area de Teoria' estan los apuntes con formulas."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Este bot es tonto (no es un chatbot). Usa /start para abrir las areas."
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot en linea. Presiona Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()