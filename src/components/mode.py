from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode,ChatAction

import asyncio

# BASE DE DATOS
from config.bd import *
from models.question import Question
from models.questionnaire import Questionnaire

def mode(update, context):
    # En un mensaje válido, borra los datos existentes y establece un nuevo mode    .
    # args = drop_command(update.message.text, "/mode")
    # 1. REPL mode
    async def typing():
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING,timeout=10)
    asyncio.run(typing())
    if "mode" in context.chat_data and context.chat_data["mode"] == 1 and "container" in context.chat_data:
        update.message.reply_text("El entorno ya se encuentra iniciado")
    else:
        # drop_data(update, context)
        options = [#                     nombre en el boton, value = "python"
                    InlineKeyboardButton("Java (jshell bot)", callback_data="java"),
                    ]
        questionnaire=Questionnaire.find_Questionnaire(update._effective_user.id)
        # Si es la primera vez que va a iniciar el entorno
        if questionnaire is None:
            context.chat_data["mode"] = 1
            update.message.reply_text("Selecciona el lenguaje de programación",reply_markup=InlineKeyboardMarkup.from_column(options))
        else:
            # obtengo la ultima pregunta respondida correctamente
            question = Question.nextQuestion(questionnaire.id_question)
            # print(q)
            # question=Question.getQuestion(questionnaire.id_question+1)
            if question is None:
                options = [
                        InlineKeyboardButton("SI", callback_data="si"),
                        InlineKeyboardButton("NO", callback_data="no"),
                        ]
                update.message.reply_text("La última vez ya completaste el cuestionario.\nDeseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
            else:
                context.chat_data["mode"] = 1
                update.message.reply_text("Selecciona el lenguaje de programación \nRecuerda que para salir del entorno usa el comando /exit",reply_markup=InlineKeyboardMarkup.from_column(options))