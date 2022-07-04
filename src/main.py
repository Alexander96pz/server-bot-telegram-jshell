# from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode,ChatAction
from telegram.ext import *
import logging
import sys

# BASE DE DATOS
from config.bd import *

from components.start import start
from components.exit import exit
from components.mode import mode
from components.default import default
from components.button import button

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
        load_dotenv('../.env')
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