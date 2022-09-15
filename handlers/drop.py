import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from services import repl
# mezcla de funciones

async def drop_data(update : Update, context:CallbackContext):
    # Limpia todos los chatdatas y resetea los stados del bot.
    if "container" in context.chat_data:
         asyncio.create_task(repl.kill(context.chat_data["container"]))
