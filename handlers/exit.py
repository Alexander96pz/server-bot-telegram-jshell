from handlers.drop import drop_data
from telegram import Update
from telegram.ext import CallbackContext
import asyncio

def exit(update: Update, context: CallbackContext):
    # Elimina cualquier instancia de contenedor que se esté ejecutando actualmente
    if "container" in context.chat_data:
        if context.chat_data["mode"] == 1 or context.chat_data["mode"] == 2 :
            update.message.reply_text("Haz finalizado el entorno, recuerda /mode para volver a iniciar")
            context.chat_data.pop("mode")
            asyncio.run(drop_data(update, context))
    else:
        update.message.reply_text("Aun no has inicializado el entorno, primero usa /mode")