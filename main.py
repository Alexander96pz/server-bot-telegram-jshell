from telegram import InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import *
import logging
import sys
import re
import os
# BASE DE DATOS

# from sqlalchemy.exc import NoResultFound
from config.bd import *
# from models.user import User,Base
# from models.message import Message
from config.bd import engine,Base,User,Message
# Session = sessionmaker(bind=engine)

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
        user=findUser(update._effective_user.id)
        # if the user no exists in the database
        if user is None:
            # add user
            addUser(update)
            # add message 
            message=addMessage(update,update._effective_user.id)
        else:
            try:
                message=addMessage(update,user.id_user)
                print("message add to the database")
            except:
                print("message no add to the database")
    except Exception as err:   
        print("error add user in the database!: ",err)
    update.message.reply_text("Hola que tal!")
    update.message.reply_text("Este es un espació dedicado para poner en practica tus habilidades de programacion")
    update.message.reply_text("Para iniciar, por favor usa /mode.")

def mode(update, context):
    # En un mensaje válido, borra los datos existentes y establece un nuevo mode    .
    # args = drop_command(update.message.text, "/mode")
    # 1. REPL mode
    drop_data(update, context)
    context.chat_data["mode"] = 1
    options = [
            #                     nombre en el boton, value = "python"   
            # InlineKeyboardButton("python (Python)", callback_data="python"),
            InlineKeyboardButton("jshell (Java)", callback_data="java"),
            ]
    update.message.reply_text("Por favor seleccione el tipo de interprete:",reply_markup=InlineKeyboardMarkup.from_column(options))
    
def exit(update, context):
    # Elimina cualquier instancia de contenedor que se esté ejecutando actualmente
    if "container" in context.chat_data:
        if context.chat_data["mode"] == 1:
            repl.kill(context.chat_data["container"])
        # if context.chat_data["mode"] == 2:
        #     batch.kill(context.chat_data["container"])
        update.message.reply_text("Contenedor Finalizado")
    else:
        update.message.reply_text("Error: Interpreter not started or already terminated")

# Message handlers
def default(update, context):
    # Llamado en cualquier mensaje de texto que no sea de orden
    #  En el modo 1, canaliza el mensaje al contenedor si existe.
    if "mode" in context.chat_data and context.chat_data["mode"] == 1:
        if "container" in context.chat_data:
            # reemplazar cadenas \t iniciales
            raw_input = update.message.text
            indent = 0 #sangrìa
            while raw_input[:2] == "\\t":
                indent += 1
                raw_input = raw_input[2:]
            # literal \n string sent - send blank line
            if raw_input == "\\n":
                raw_input = ""
            stdin = indent * "\t" + raw_input
            repl.pipein(context.chat_data["container"], stdin + "\n")
        else:
            update.message.reply_text("Error: Intérprete no iniciada o aun finalizada")
    else:
        pass  # no defined behaviour in other modes

# Callback handlers //seleccion del interprete button
# mode 1
def button(update, context):
    # print("imprime el contexto.chat_data: ",context.chat_data)
    if "mode" in context.chat_data and context.chat_data["mode"] == 1 and "container" not in context.chat_data:
        query = update.callback_query
        message = query.message
        lang = query.data
        message.edit_reply_markup()  # remueve los botones
        shell = {
            # "python": "python (Python)",
            "java": "jshell (Java)"
        }[lang]
        # message.reply_text("Ahora iniciando " + shell + " interprete...")
        question=getQuestion(1)
        # salida del interprete
        def pipeout(out,isError):
            # expresion regular
            print(isError)
            # si la lista esta vacia?
            if not out:
                pass
            else:
                for o in out:
                    # if re.match("\S", o):
                        message.reply_text(o)
                # controlamos que la cadena no contengan espacios en blanco para reenviar texto
        # elimina del item chat_data la identificacion contenedor
        def on_close():
            context.chat_data.pop("container", None)

        container = repl.launch(lang, pipeout, on_close)
        message.reply_text(question.text_question)
        context.chat_data["container"] = container  
    # else:
    #     print("Esto imprime",context.chat_data["mode"])  # debug statement


# mezcla de funciones
def drop_data(update, context):
    # Limpia todos los chatdatas y resetea los stados del bot.
    if "container" in context.chat_data:
        repl.kill(context.chat_data["container"])
    # chat_id = str(update.effective_chat.id)
    # for ext in KNOWN_FILE_TYPES:
    #     path = "user_files/" + chat_id + ext
    #     if os.path.exists(path):
    #         os.remove(path)
    context.user_data["mode"] = 0
    update.message.reply_text("Datos existentes limpios!")


def drop_command(message, command):
    """
    Given a message text, drops the command prefix from the string.
    """
    return message[len(command) + 1:]


# Initializacion del bot
def main():
    try:
        Base.metadata.create_all(engine)
        print("connection DataBase sucessfully")
    except Exception:
        print("Error in the conexion in the DB")
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
