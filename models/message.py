from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
import datetime
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine

Session = sessionmaker(bind=engine)
class Message(Base):
    __tablename__ = 'message'
    id_message = Column(Integer,primary_key=True,unique=True)
    date = Column(DateTime,default=datetime.datetime.utcnow)
    text= Column(String(1000),nullable=False)
    fk_id_user=Column(Integer,ForeignKey('user.id_user'))

    def addMessage(update,id_user):
        session = Session()
        message=Message(id_message=update._effective_message.message_id,text=update._effective_message.text,fk_id_user=id_user)
        session.add(message)
        session.commit()
        id_message=message.id_message
        session.close()
        return message
    def updateMessage(edited_message):
        # Session= sessionmaker(bind=engine)
        session = Session()
        message = session.query(Message).filter(Message.id_message==edited_message.message_id).update({
            # Message.date:datetime.datetime.utcnow,
            Message.text:edited_message.text
        })
        session.commit()
        session.close()
        session = Session()
        if message:
            message=session.query(Message).filter(Message.id_message==edited_message.message_id).first()
        session.close()
        return message