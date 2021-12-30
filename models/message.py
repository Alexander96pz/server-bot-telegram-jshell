from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
import datetime
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine

class Message(Base):
    __tablename__ = 'message'
    id_message = Column(Integer,primary_key=True,unique=True)
    date = Column(DateTime,default=datetime.datetime.utcnow)
    text= Column(String(1000),nullable=False)
    fk_id_user=Column(Integer,ForeignKey('user.id_user'))

    def addMessage(update,id_user):
        Session = sessionmaker(bind=engine)
        session = Session()
        message=Message(id_message=update._effective_message.message_id,text=update._effective_message.text,fk_id_user=id_user)
        session.add(message)
        session.commit()
        print(message.id_message)
        session.close()
        return message