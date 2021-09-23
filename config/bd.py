from sqlalchemy import create_engine
#motor de conexion            user:password
# (url,echo=True) INFO sqlalchemic
engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/practicas')