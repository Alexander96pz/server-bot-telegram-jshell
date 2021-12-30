from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
#motor de conexion            user:password
# (url,echo=True) INFO sqlalchemic
engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/practicas')
Base=declarative_base()