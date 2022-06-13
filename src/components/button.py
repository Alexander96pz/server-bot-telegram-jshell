from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode
import logging

# BASE DE DATOS
from config.bd import *
from models.question import Question
from models.questionnaire import Questionnaire
from service import repl

def button(update, context):
    # Si el usuario no desea repetir el cuestionario de preguntas
    if update.callback_query.data == "no":
        update.callback_query.message.edit_reply_markup()
        update.callback_query.message.reply_text("Espero que regreses, nunca dejes de aprender. Recuerda /mode para iniciar el entorno")
        if "container" in context.chat_data:
            repl.kill(context.chat_data["container"])
    else:
        # Cuando el usuario si desea repetir el cuestionario de preguntas
        if "mode" in context.chat_data and context.chat_data["mode"] == 1 and "container" not in context.chat_data or update.callback_query.data == "si":
            query = update.callback_query
            message = query.message
            lang = "java"
            # Si selecciona de la opcion SI, de repetir el cuestionario
            if update.callback_query.data == "si":
                question=Question.getQuestion(1)
                context.chat_data["mode"] = 1
                questionnaire=Questionnaire.find_Questionnaire(update._effective_user.id)
                # obtener el nro de intento actual+1,de esta forma se el numero del cuestionario
                nro_tried=questionnaire.tried+1
            else:
                questionnaire = Questionnaire.find_Questionnaire(update._effective_user.id)
                # Permite verificar si es la primera interaccion en modo entorno
                if questionnaire is None:
                    question=Question.getQuestion(1)
                    nro_tried=1
                else:
                    nro_tried=questionnaire.tried
                    question=Question.nextQuestion(questionnaire.id_question)
            message.edit_reply_markup()  # remueve los botones

            # salida del interprete
            def pipeout(out,id_user,id_message,id_question, nro_tried, answer):
                # si no hay respuesta
                if answer == None:
                    pass
                else:
                    try:
                        Questionnaire.addQuestionnaire(id_question,id_message,id_user,answer.id_answer,nro_tried)
                    except Exception as err:
                        logging.error('Error save questionnaire in BD: ',err)
                    finally:
                        for o in out:
                            message.reply_text("<code>"+o+"</code>",parse_mode=ParseMode.HTML)
                        if not answer.analysis_dynamic and not answer.analysis_static:
                            message.reply_text("<b>Correcto! bien echo</b>",parse_mode=ParseMode.HTML)
                            question = Question.nextQuestion(id_question)
                            repl.next(context.chat_data["container"], question)
                            if question is not None:
                                q="<b>RESUELVE: "+question.text_question+"</b>"
                                message.reply_text(q,parse_mode=ParseMode.HTML)
                            else:
                                    options = [
                                        InlineKeyboardButton("SI", callback_data="si"),
                                        InlineKeyboardButton("NO", callback_data="no"),
                                    ]
                                    message.reply_text("FELICIDADES! terminaste con exito. Deseas repetir?",
                                                       reply_markup=InlineKeyboardMarkup.from_column(options))
                        else:
                            if answer.analysis_dynamic:
                                message.reply_text("<b>Error en la sintaxis! intentalo de nuevo amigo</b>",parse_mode=ParseMode.HTML)
                            else:
                                message.reply_text("<b>No hay errores de sintaxis, pero la solución es incorrecta</b>",parse_mode=ParseMode.HTML)
                    # controlamos que la cadena no contengan espacios en blanco para reenviar texto
            # elimina del item chat_data la identificacion contenedor
            def on_close():
                context.chat_data.pop("container", None)
            # Si has respondido todas las preguntas
            if(question is None):

                options = [
                            InlineKeyboardButton("SI", callback_data="si"),
                            InlineKeyboardButton("NO", callback_data="no"),
                            ]
                message.reply_text("Has finalizado el cuestionario correctamente. Deseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
            else:
                container = repl.launch(lang, pipeout, on_close, question, nro_tried)
                message.reply_text("<b>RESUELVE: "+question.text_question+"</b>",parse_mode=ParseMode.HTML)
                context.chat_data["container"] = container