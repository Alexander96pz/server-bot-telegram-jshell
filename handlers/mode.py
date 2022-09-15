from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ChatAction,Update
from telegram.ext import CallbackContext
import asyncio

def mode(update: Update, context: CallbackContext):
    # En un mensaje válido, borra los datos existentes y establece un nuevo mode    .
    # args = drop_command(update.message.text, "/mode")
    # 1. REPL mode
    async def typing():
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING,timeout=10)
    asyncio.run(typing())
    if "mode" in context.chat_data and (context.chat_data["mode"] == 1 or context.chat_data["mode"]==2) and "container" in context.chat_data:
        update.message.reply_text("El entorno ya se encuentra iniciado")
    else:
        options = [#                     nombre en el boton, value = "python"
                    InlineKeyboardButton("Preguntas y Respuestas", callback_data="opcion1"),
                    InlineKeyboardButton("Libre", callback_data="opcion2"),
                    ]
        update.message.reply_text("Selecciona el modo de interaccion",
                        reply_markup=InlineKeyboardMarkup.from_column(options))