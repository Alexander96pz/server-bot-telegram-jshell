import asyncio

from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode
import logging

# BASE DE DATOS
from config.bd import *
from models.question import Question
from models.questionnaire import Questionnaire
from service import repl
from components.mode import entorno

def button(update, context):
    if update.callback_query.data == "no":
        context.chat_data["mode"] = 0
        update.callback_query.message.edit_reply_markup()
        update.callback_query.message.reply_text("Espero que regreses, nunca dejes de aprender. Recuerda /mode para iniciar el entorno")
        if "container" in context.chat_data:
            asyncio.run(repl.kill(context.chat_data["container"]))
    else:
        query=update.callback_query
        message = query.message
        message.edit_reply_markup()
        context.chat_data["mode"] = 1
        entorno(update,context)