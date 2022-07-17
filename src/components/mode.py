from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ChatAction,ReplyKeyboardMarkup,ParseMode

import asyncio

# BASE DE DATOS
from config.bd import *
from models.question import Question
from models.questionnaire import Questionnaire
# from models.question import Question
# from models.questionnaire import Questionnaire
from service import repl
import logging

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
        options = [#                     nombre en el boton, value = "python"
                    InlineKeyboardButton("Java (jshell bot)", callback_data="java"),
                    ]
        questionnaire=Questionnaire.find_Questionnaire(update._effective_user.id)
        # Si es la primera vez que van a interactuar con el entorno - to new users
        if questionnaire is None:
            context.chat_data["mode"] = 1
            entorno(update, context)
            # update.message.reply_text("Selecciona el lenguaje de programación",reply_markup=InlineKeyboardMarkup.from_column(options))
        else:
            # obtengo la ultima pregunta respondida correctamente
            question = Question.nextQuestion(questionnaire.id_question)
            if question is None:
                options = [
                        InlineKeyboardButton("SI", callback_data="si"),
                        InlineKeyboardButton("NO", callback_data="no"),
                        ]
                update.message.reply_text("La última vez ya completaste el cuestionario.\nDeseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
            else:
                context.chat_data["mode"] = 1
                entorno(update,context)
                # update.message.reply_text("Selecciona el lenguaje de programación \nRecuerda que para salir del entorno usa el comando /exit",reply_markup=InlineKeyboardMarkup.from_column(options))

def entorno(update,context):
    if "mode" in context.chat_data and context.chat_data["mode"] == 1:
        lang = "java"
        message = update.message
        questionnaire = Questionnaire.find_Questionnaire(update._effective_user.id)
        # Permite verificar si es la primera interaccion en modo entorno
        if questionnaire is None:
            question = Question.getQuestion(1)
            nro_tried = 1
        else:
            nro_tried = questionnaire.tried
            question = Question.nextQuestion(questionnaire.id_question)

        # salida del interprete
        def pipeout(out, id_user, id_message, id_question, nro_tried, answer):
            # si no hay respuesta
            if answer == None:
                pass
            else:
                try:
                    Questionnaire.addQuestionnaire(id_question, id_message, id_user, answer.id_answer,
                                                   nro_tried)
                except Exception as err:
                    logging.error('Error save questionnaire in BD: ', err)
                finally:
                    try:
                        for o in out:
                            message.reply_text(o)
                    except:
                        logging.ERROR("Error al envio respuesta a telegram")
                    if not answer.analysis_dynamic and not answer.analysis_static:
                        message.reply_text("<b>Correcto! bien echo</b>", parse_mode=ParseMode.HTML)
                        question = Question.nextQuestion(id_question)
                        repl.next(context.chat_data["container"], question)
                        if question is not None:
                            q = "<b>RESUELVE: " + question.text_question + "</b>"
                            message.reply_text(q, parse_mode=ParseMode.HTML)
                        else:
                            options = [
                                InlineKeyboardButton("SI", callback_data="si"),
                                InlineKeyboardButton("NO", callback_data="no"),
                            ]
                            message.reply_text("FELICIDADES! terminaste con exito. Deseas repetir?",
                                               reply_markup=InlineKeyboardMarkup.from_column(options))
                    else:
                        if answer.analysis_dynamic:
                            message.reply_text("<b>Error en la sintaxis! intentalo de nuevo amigo</b>",
                                               parse_mode=ParseMode.HTML)
                        else:
                            message.reply_text(
                                "<b>No hay errores de sintaxis, pero la solución es incorrecta</b>",
                                parse_mode=ParseMode.HTML)
                # controlamos que la cadena no contengan espacios en blanco para reenviar texto

        # elimina del item chat_data la identificacion contenedor
        def on_close():
            context.chat_data.pop("container", None)

        # Si has respondido todas las preguntas
        if (question is None):
            query = update.callback_query
            message = query.message
            question = Question.getQuestion(1)
            questionnaire = Questionnaire.find_Questionnaire(update._effective_user.id)
            nro_tried = questionnaire.tried + 1
        container = repl.launch(lang, pipeout, on_close, question, nro_tried)
        message.reply_text("<b>RESUELVE: " + question.text_question + "</b>", parse_mode=ParseMode.HTML)
        if "container" in context.chat_data:
            asyncio.run(repl.kill(context.chat_data["container"]))
        context.chat_data["container"] = container

