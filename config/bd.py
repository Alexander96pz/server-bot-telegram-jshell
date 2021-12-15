from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column,Integer,String,Table,Boolean,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
#motor de conexion            user:password
# (url,echo=True) INFO sqlalchemic
engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/practicas')
Session = sessionmaker(bind=engine)
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

class Message(Base):
    __tablename__ = 'message'
    id_message = Column(Integer,primary_key=True,unique=True)
    date = Column(DateTime,default=datetime.datetime.utcnow)
    text= Column(String(1000),nullable=False)
    fk_id_user=Column(Integer,ForeignKey('user.id_user'))

class Question(Base):
    __tablename__= 'question'
    id_question = Column(Integer,primary_key=True,autoincrement=True)
    text_question = Column(String(3000),nullable=False)

class Answer(Base):
    __tablename__= 'answer'
    id_question = Column(ForeignKey("question.id_question"),primary_key=True)
    id_message = Column(ForeignKey("message.id_message"),primary_key=True)
    # nos permitira conocer si la respuesta es correcta o no
    status= Column(Boolean,nullable=False)

# Add new user
def addUser(update):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = User(id_user=update._effective_user.id,
        first_name=update._effective_user.first_name,
        is_bot=update._effective_user.is_bot,
        username=update._effective_user.username,
        lenguaje_code=update._effective_user.language_code)
    session.add(user)
    session.commit()
    session.close()

def addMessage(update,id_user):
    Session = sessionmaker(bind=engine)
    session = Session()
    message=Message(id_message=update._effective_message.message_id,text=update._effective_message.text,fk_id_user=id_user)
    session.add(message)
    session.commit()
    session.close()

def findUser(id_user):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.id_user == id_user).first()
    session.close()
    return user

def getQuestion(number):
    Session = sessionmaker(bind=engine)
    session = Session()
    question = session.query(Question).filter(Question.id_question == number).first()
    session.close()
    return question
    