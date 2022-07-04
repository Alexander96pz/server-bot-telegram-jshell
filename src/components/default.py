# BASE DE DATOS
from config.bd import *
from models.message import Message

from service import repl

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
            repl.pipein(context.chat_data["container"], stdin, message)
        else:
            update.message.reply_text("Primero inicia el entorno para comenzar a programar /mode")
    else:
        update.message.reply_text("Recuerda que para iniciar el entorno usa el comando /mode")