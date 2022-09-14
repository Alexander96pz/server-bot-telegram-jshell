# from telegram import InlineKeyboardButton,InlineKeyboardMarkup,ParseMode,ChatAction
from telegram.ext import *
import logging
import sys

# BASE DE DATOS
from settings.bd import *

from handlers.start import start
from handlers.exit import exit
from handlers.mode import mode
from handlers.default import default
from handlers.button import button

def setup_dispatcher(dp):
    """
        Adding handlers for events from Telegram
    """
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("mode", mode))
    dp.add_handler(CommandHandler("exit", exit))
    dp.add_handler(MessageHandler(Filters.text, default))
    dp.add_handler(CallbackQueryHandler(button))
    return dp


def run_polling():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    load_dotenv('../.env')
    try:
        # Conexion BD
        Base.metadata.create_all(engine)
        logging.info('BD funcionando correctamente')
    except Exception:
        logging.error('Error in the connection to the DB')
    finally:
        # configuracion de los entornos de variables
        # actualizaciones provenientes de telegram
        updater = Updater(token=os.getenv('API_KEY'), use_context=True)
        # despachador nos permite clasificar las actualizaciones
        dp = updater.dispatcher
        # Add handlers//controladores
        dp = setup_dispatcher(dp)
        # Comienza a sondear las actualizaciones de telegram
        updater.start_polling()
        updater.idle()