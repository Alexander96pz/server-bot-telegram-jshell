from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
# varuiables de entorno
load_dotenv('.env')
#motor de conexion            user:password
engine = create_engine('mysql+pymysql://'+os.getenv('DB_KEYL'))
Base=declarative_base()