import logging

from models.user import User
from models.message import Message

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