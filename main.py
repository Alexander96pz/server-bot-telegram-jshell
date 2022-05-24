from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode
from telegram.ext import *
from dotenv import load_dotenv
import logging
import sys
# import re
import os

# BASE DE DATOS
from config.bd import *
from models.user import  User
from models.question import Question
from models.message import Message
from models.questionnaire import Questionnaire

import repl

# Controladores de Comandos
# comand /start
def start(update, context):
    # Establecemos el modo = 0
    if "mode" not in context.chat_data:
        # chat_data: {'mode': 0}
        context.chat_data["mode"] = 0
    # Añadir user 
    try:
        # find if user exists in the database
        user=User.findUser(update._effective_user.id)
        # if the user no exists in the database/primera interaccion
        if user is None:
            # add user
            User.addUser(update)
            # add message 
            Message.addMessage(update,update._effective_user.id)
            logging.info('user add success') 
        else:
            try:
                Message.addMessage(update,user.id_user)
                logging.info('message add success') 
            except Exception as err:
                logging.err("message no add user to the database: ",err) 
    except Exception as err:   
        logging.err("message no add user to the database: ",err) 
    update.message.reply_text("Hola Amigo Programador!")
    update.message.reply_text("Te ayudare a poner practica tus habilidades de programación.")
    update.message.reply_text("Para iniciar el entorno de programación usa el comando /mode.")
    update.message.reply_text("Para salir del entorno de programación usa el comando /exit.")

def mode(update, context):
    # En un mensaje válido, borra los datos existentes y establece un nuevo mode    .
    # args = drop_command(update.message.text, "/mode")
    # 1. REPL mode
    drop_data(update, context)
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
        question=Question.getQuestion(questionnaire.id_question+1)
        if question is None:
            options = [
                    InlineKeyboardButton("SI", callback_data="si"),
                    InlineKeyboardButton("NO", callback_data="no"),
                    ]
            update.message.reply_text("La última vez ya completaste el cuestionario.\nDeseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
        else:

            context.chat_data["mode"] = 1
            update.message.reply_text("Selecciona el lenguaje de programación \nRecuerda que para salir del entorno usa el comando /exit",reply_markup=InlineKeyboardMarkup.from_column(options))
    
def exit(update, context):
    # Elimina cualquier instancia de contenedor que se esté ejecutando actualmente
    if "container" in context.chat_data:
        if context.chat_data["mode"] == 1:
            repl.kill(context.chat_data["container"])
        # if context.chat_data["mode"] == 2:
        #     batch.kill(context.chat_data["container"])
        update.message.reply_text("Entorno Finalizado, recuerda /mode para volver a iniciar")
    else:
        update.message.reply_text("Entorno no Inicializado, usa /mode para inicializar")

# Message handlers

def default(update, context):
    # Llamado en cualquier mensaje de texto que no sea de orden
    #  En el modo 1, canaliza el mensaje al contenedor si existe.
    # if mode se encuentra in the context.chat_data[] y tiene el valor de 1 en referencia de iniciar entorno
    if "mode" in context.chat_data and context.chat_data["mode"] == 1:
        if "container" in context.chat_data:
            # reemplazar cadenas \t iniciales
            if update.edited_message:
                message=Message.updateMessage(update.edited_message)
                raw_input = update.edited_message.text
            else:
                message=Message.addMessage(update,update._effective_user.id)
                raw_input = update.message.text
            stdin = raw_input.strip().replace('\n',"")
            repl.pipein(context.chat_data["container"], stdin + "\n", message)
        else:
            update.message.reply_text("Primero inicia el entorno para comenzar a programar /mode")
    else:
        update.message.reply_text("Recuerda que para iniciar el entorno usa el comando /mode")

# Callback handlers //seleccion del interprete button
# mode 1
def button(update, context):
    # Si el usuario no desea repetir el cuestionario de preguntas
    if update.callback_query.data == "no":
        update.callback_query.message.edit_reply_markup()
        update.callback_query.message.reply_text("Espero que regreses, nunca dejes de aprender. Recuerda /mode para iniciar el entorno")
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
                    question=Question.getQuestion(questionnaire.id_question+1)
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
                        logging.error('Error save questionnaire in BD')
                    finally:
                        for o in out:
                            message.reply_text("<code>"+o+"</code>",parse_mode=ParseMode.HTML)
                        if not answer.analysis_dynamic and not answer.analysis_static:
                            message.reply_text("<b>Correcto! bien echo</b>",parse_mode=ParseMode.HTML)
                            question = Question.getQuestion(id_question+1)
                            repl.next(context.chat_data["container"])
                            if question is not None:
                                q="<b>RESUELVE: "+question.text_question+"</b>"
                                message.reply_text(q,parse_mode=ParseMode.HTML)
                            else:
                                repl.kill(context.chat_data["container"])
                                options = [
                                    InlineKeyboardButton("SI", callback_data="si"),
                                    InlineKeyboardButton("NO", callback_data="no"),
                                ]
                                message.reply_text("FELICIDADES! terminaste con exito. Deseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
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
                container = repl.launch(lang, pipeout, on_close,question.id_question,nro_tried)
                message.reply_text("<b>RESUELVE: "+question.text_question+"</b>",parse_mode=ParseMode.HTML)
                context.chat_data["container"] = container

# mezcla de funciones
def drop_data(update, context):
    # Limpia todos los chatdatas y resetea los stados del bot.
    if "container" in context.chat_data:
        repl.kill(context.chat_data["container"])
    context.user_data["mode"] = 0
    # update.message.reply_text("Datos existentes limpios!")

# Initializacion del bot
def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    try:
        # Conexion BD
        Base.metadata.create_all(engine)
        logging.info('BD funcionando correctamente') 
    except Exception:
        logging.error('Error in the conexion to the DB')
    finally:
        # configuracion de los entornos de variables
        load_dotenv('.env')
        # actualizaciones provenientes de telegram
        updater = Updater(token=os.getenv('API_KEY'), use_context=True)
        # despachador nos permite clasificar las actualizaciones 
        dp = updater.dispatcher
        # Add handlers//controladores
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("mode", mode))
        dp.add_handler(CommandHandler("exit", exit))
        dp.add_handler(MessageHandler(Filters.text, default))
        dp.add_handler(CallbackQueryHandler(button))
        #Comienza a sondear las actualizaciones de telegram 
        updater.start_polling()
        updater.idle()
if __name__ == '__main__':
    main()