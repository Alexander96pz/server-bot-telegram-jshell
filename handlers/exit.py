from handlers.drop import drop_data
import asyncio
# BASE DE DATOS
from settings.bd import *

def exit(update, context):
    # Elimina cualquier instancia de contenedor que se esté ejecutando actualmente
    if "container" in context.chat_data:
        if context.chat_data["mode"] == 1 or context.chat_data["mode"] == 2 :
            update.message.reply_text("Haz finalizado el entorno, recuerda /mode para volver a iniciar")
            context.chat_data.pop("mode")
            asyncio.run(drop_data(update, context))
    else:
        update.message.reply_text("Aun no has inicializado el entorno, primero usa /mode")