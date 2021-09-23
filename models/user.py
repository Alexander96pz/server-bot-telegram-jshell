from sqlalchemy import Column,Integer,String,Table,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# from message import Message
# 
Base=declarative_base()
class User(Base):
    __tablename__ = 'user'
    id_user = Column(Integer,primary_key=True,unique=True)
    first_name = Column(String(50),nullable=False)
    is_bot = Column(Boolean, nullable=True)
    username = Column(String(50),nullable=False)
    lenguaje_code = Column(String(50),nullable=True)
    id_message = relationship("Message")