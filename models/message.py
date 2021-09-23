from sqlalchemy import Column,Integer,String,Table,relationship,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import text
# from user import User 
# 
Base=declarative_base()
class Message(Base):
    __tablename__ = 'message'
    id_message = Column(Integer,primary_key=True,unique=True)
    date = Column(String(50),nullable=False)
    username = Column(String(50),nullable=False)
    text= Column(String(1000),nullable=False)
    fk_id_user=Column(Integer,ForeignKey('user.id_user'))
