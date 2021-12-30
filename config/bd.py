from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
#motor de conexion            user:password
# (url,echo=True) INFO sqlalchemic
engine = create_engine('mysql+pymysql://u0hzf4t3vypi4gaa:8KoYYAznhQXfnXpR8Kv6@bm1uk41dbgwcar5uvd9e-mysql.services.clever-cloud.com:3306/bm1uk41dbgwcar5uvd9e')
# Session = sessionmaker(bind=engine)
# from message import Message
# 
Base=declarative_base()