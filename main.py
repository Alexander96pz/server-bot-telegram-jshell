from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode
from telegram.ext import *
import logging
import sys
import re
import os
# BASE DE DATOS
from config.bd import *
from models.user import  User
from models.question import Question
from models.message import Message
from models.answer import Answer

from api_key import API_KEY
import repl

# Controladores de Comandos
# comand /start
def start(update, context):
    # Mensaje Inicial
    if "mode" not in context.chat_data:
        context.chat_data["mode"] = 0
    # Añadir user 
    try:
        # find if user exists in the database
        user=User.findUser(update._effective_user.id)
        # if the user no exists in the database
        if user is None:
            # add user
            User.addUser(update)
            # add message 
            message=Message.addMessage(update,update._effective_user.id)
        else:
            try:
                message=Message.addMessage(update,user.id_user)
            except Exception as err:
                print("message no add to the database: ",err)
    except Exception as err:   
        print("error add user in the database!: ",err)
    update.message.reply_text("Hola que tal!")
    # update.message.reply_text("<b> Hola que tal! </b>",parse_mode=ParseMode.HTML)
    update.message.reply_text("Este es un espació dedicado para poner en practica tus habilidades de programacion")
    update.message.reply_text("Para iniciar, por favor usa /mode.")

def mode(update, context):
    # En un mensaje válido, borra los datos existentes y establece un nuevo mode    .
    # args = drop_command(update.message.text, "/mode")
    # 1. REPL mode
    drop_data(update, context)
    options = [
                #                     nombre en el boton, value = "python"   
                InlineKeyboardButton("Iniciar entono jshell (Java)", callback_data="java"),
                ]
    answer=Answer.find_Answer(update._effective_user.id)
    if answer is None:
        context.chat_data["mode"] = 1
        update.message.reply_text("Para iniciar selecciona el entorno",reply_markup=InlineKeyboardMarkup.from_column(options))
    else:    
        question=Question.getQuestion(answer.id_question+1)
        if question is None:
            options = [
                    InlineKeyboardButton("SI", callback_data="si"),
                    InlineKeyboardButton("NO", callback_data="no"),
                    ]
            update.message.reply_text("Felicidades amigo!..Ya has finalizado el cuestionario, deseas repetir?:",reply_markup=InlineKeyboardMarkup.from_column(options))
        else:
            context.chat_data["mode"] = 1
            update.message.reply_text("Para iniciar selecciona el entorno. \nRecuerda que para salir del entorno usa el comando /exit",reply_markup=InlineKeyboardMarkup.from_column(options))
    
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
    print(context)
    # Llamado en cualquier mensaje de texto que no sea de orden
    #  En el modo 1, canaliza el mensaje al contenedor si existe.
    print(update)
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
            print(context.chat_data["container"])
            repl.pipein(context.chat_data["container"], stdin + "\n", message)
        else:
            update.message.reply_text("Error: Entorno no iniciada")
    else:
        update.message.reply_text("Recuerda que para iniciar el entorno usa el comando /mode")

# Callback handlers //seleccion del interprete button
# mode 1
def button(update, context):
    # print("imprime el contexto.chat_data: ",context.chat_data)
    # print(update.callback_query.data)
    if update.callback_query.data == "no":
        update.callback_query.message.edit_reply_markup()
        update.callback_query.message.reply_text("Nunca dejes de aprender. Sigue Formandote /mode")
    else:
        if "mode" in context.chat_data and context.chat_data["mode"] == 1 and "container" not in context.chat_data or update.callback_query.data == "si":
            query = update.callback_query
            message = query.message
            lang = ''
            if update.callback_query.data == "si":
                # else:
                question=Question.getQuestion(1)
                lang="java"
                context.chat_data["mode"] = 1
            else:
                answer=Answer.find_Answer(update._effective_user.id)
                if answer is None:
                    question=Question.getQuestion(1)
                else: 
                    question=Question.getQuestion(answer.id_question+1) 
                lang = query.data
            message.edit_reply_markup()  # remueve los botones
            shell = {
                "java": "jshell (Java)"
            }[lang]

            # salida del interprete
            def pipeout(out,isError,text,id_user,id_message,id_question):
                if isError:
                    color="red"
                else:
                    color="green"
                # si la lista esta vacia?
                if not out:
                    pass
                else:
                    try:
                        Answer.addAnswer(id_question,id_message,id_user,isError)
                    except Exception  as err:
                        print("Error adding Answer",err)
                    finally:
                        for o in out:
                            message.reply_text("<code>"+o+"</code>",parse_mode=ParseMode.HTML)
                        if not isError:
                            question=Question.getQuestion(id_question+1)
                            repl.next(context.chat_data["container"])
                            if question is not None:
                                q="<b>"+question.text_question+"</b>"
                                message.reply_text(q,parse_mode=ParseMode.HTML)
                                # message.reply_text(question.text_question)
                            else:
                                repl.kill(context.chat_data["container"])
                                options = [
                                    InlineKeyboardButton("SI", callback_data="si"),
                                    InlineKeyboardButton("NO", callback_data="no"),
                                ]
                                message.reply_text("Felicidades! terminaste con exito, deseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
                        else:
                            message.reply_text("<b>Intentalo de nuevo amigo</b>",parse_mode=ParseMode.HTML)        
                    # controlamos que la cadena no contengan espacios en blanco para reenviar texto
            # elimina del item chat_data la identificacion contenedor
            def on_close():
                context.chat_data.pop("container", None)

            if(question is None):
                options = [
                                    InlineKeyboardButton("SI", callback_data="si"),
                                    InlineKeyboardButton("NO", callback_data="no"),
                                ]
                message.reply_text("Has finalizado el cuestionario correctamente, deseas repetir?",reply_markup=InlineKeyboardMarkup.from_column(options))
                # message.reply_text("Has finalizado el cuestionario correctamente, deseas repetir?:",reply_markup=InlineKeyboardMarkup.from_column(options))
            else:
                container = repl.launch(lang, pipeout, on_close,question.id_question)
                q="<b>"+question.text_question+"</b>"
                message.reply_text(q,parse_mode=ParseMode.HTML)
                # update.message.reply_text("<b> Hola que tal! </b>",parse_mode=ParseMode.HTML)
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
    try:
        Base.metadata.create_all(engine)
        print("connection DataBase sucessfully")
    except Exception:
        print("Error in the conexion to the DB")
    finally:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
        # actualizaciones provenientes de telegram
        updater = Updater(API_KEY, use_context=True)
        # despachador nos permite clasificar las actualizaciones 
        dp = updater.dispatcher
        # Add handlers//controladores
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("mode", mode))
        dp.add_handler(CommandHandler("exit", exit))
        dp.add_handler(MessageHandler(Filters.text, default))
        dp.add_handler(CallbackQueryHandler(button))

        updater.start_polling()
        updater.idle()
    # Log stdout //nos ayudara a saber cuando y porque no funcionan las cosas

if __name__ == '__main__':
    main()
