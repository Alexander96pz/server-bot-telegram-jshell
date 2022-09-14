import asyncio

from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode
import logging

# BASE DE DATOS
from models.question import Question
from models.questionnaire import Questionnaire
from services import repl, repl2


def button(update, context):
    update.callback_query.message.edit_reply_markup()
    if update.callback_query.data == "no":
        update.callback_query.message.reply_text("Espero que regreses, nunca dejes de aprender. Recuerda /mode para iniciar el entorno")
        if "container" in context.chat_data:
            temp=context.chat_data["container"]
            context.chat_data.pop("container")
            asyncio.run(repl.kill(temp))

        if "mode" in context.chat_data:
            context.chat_data.pop("mode")
    elif update.callback_query.data == "si":
        if "mode" not in context.chat_data:
            context.chat_data["mode"]=1
            methodQuestion(update,context)
        elif "mode" in context.chat_data:
            if context.chat_data["mode"] == 1:
                if "container" not in context.chat_data:
                    methodQuestion(update, context)
                else:
                    questionnaire = Questionnaire.find_Questionnaire(update._effective_user.id)
                    question = Question.nextQuestion(questionnaire.id_question)
                    if question is None:
                        question = Question.getQuestion(1)
                        context.bot.send_message(update.effective_message.chat_id, "<b>"+question.text_question+"</b>", parse_mode=ParseMode.HTML)
                    else:
                        pass
    elif update.callback_query.data == "opcion1":
        if ("mode" in context.chat_data and context.chat_data["mode"]!=0):
            print("Opcion1")
            print(context.chat_data["mode"])
            pass
            # update.message.reply_text("Primero cierra el entorno /exit")
        else:
            context.chat_data["mode"] = 1
            methodQuestion(update,context)
    elif update.callback_query.data == "opcion2":
        if"mode" in context.chat_data and context.chat_data["mode"]!=0:
            pass
            # update.message.reply_text("Primero cierra el entorno /exit")
        else:
            context.chat_data["mode"] = 2
            if "mode" in context.chat_data and context.chat_data["mode"] == 2 and "container" not in context.chat_data:
                query = update.callback_query
                message = query.message
                lang = query.data
                # message.edit_reply_markup()  # remove the buttons
                lan="java"

                def pipeout2(out):
                    message.reply_text(out)

                def on_close2():
                    context.chat_data.pop("container", None)

                container = repl2.launch2(lan, pipeout2, on_close2)
                context.chat_data["container"] = container
        # Cuando el usuario si desea repetir el cuestionario de preguntas
def methodQuestion(update,context):
    if ("mode" in context.chat_data and context.chat_data["mode"] == 1 and "container" not in context.chat_data):
        query = update.callback_query
        message = query.message
        lang = "java"
        # Si selecciona de la opcion SI, de repetir el cuestionario
        if update.callback_query.data == "si":
            question = Question.getQuestion(1)
            # context.chat_data["mode"] = 1
            questionnaire = Questionnaire.find_Questionnaire(update._effective_user.id)
            # obtener el nro de intento actual+1,de esta forma se el numero del cuestionario
            nro_tried = questionnaire.tried + 1
        else:
            questionnaire = Questionnaire.find_Questionnaire(update._effective_user.id)
            # Permite verificar si es la primera interaccion en modo entorno
            if questionnaire is None:
                question = Question.getQuestion(1)
                nro_tried = 1
            else:
                nro_tried = questionnaire.tried
                question = Question.nextQuestion(questionnaire.id_question)
        # message.edit_reply_markup()  # remueve los botones

        # salida del interprete
        def pipeout(out, id_user, id_message, id_question, nro_tried, answer):
            # si no hay respuesta
            if answer == None:
                pass
            else:
                try:
                    Questionnaire.addQuestionnaire(id_question, id_message, id_user, answer.id_answer, nro_tried)
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
                            message.reply_text("<b>No hay errores de sintaxis, pero la solución es incorrecta</b>",
                                               parse_mode=ParseMode.HTML)
                # controlamos que la cadena no contengan espacios en blanco para reenviar texto

        # elimina del item chat_data la identificacion contenedor
        def on_close():
            context.chat_data.pop("container", None)

        # Si has respondido todas las preguntas
        if (question is None):
            context.chat_data.pop("mode")
            options = [
                InlineKeyboardButton("SI", callback_data="si"),
                InlineKeyboardButton("NO", callback_data="no"),
            ]
            message.reply_text("Ya has finalizado el cuestionario correctamente. Deseas repetir?",
                               reply_markup=InlineKeyboardMarkup.from_column(options))
            if "container" in context.chat_data:
                temp=context.chat_data["container"]
                context.chat_data.pop("container")
                asyncio.run(repl.kill(temp))

        else:
            container = repl.launch(lang, pipeout, on_close, question, nro_tried)
            message.reply_text("<b>RESUELVE: " + question.text_question + "</b>", parse_mode=ParseMode.HTML)
            if "container" in context.chat_data:
                asyncio.run(repl.kill(context.chat_data["container"]))
            context.chat_data["container"] = container