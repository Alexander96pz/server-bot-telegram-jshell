from sqlalchemy import Column,ForeignKey,Boolean,Integer
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine
from models.message import Message
from sqlalchemy import desc

class Answer(Base):
    __tablename__= 'answer'
    id_answer = Column(Integer,primary_key=True,unique=True,autoincrement=True)
    id_question = Column(ForeignKey("question.id_question"))
    id_message = Column(ForeignKey("message.id_message"))
    id_user = Column(ForeignKey("user.id_user"))
    # nos permitira conocer si la respuesta es correcta o no
    isError= Column(Boolean,nullable=False)

    def find_Answer(id_user):
        # me extrae la ultima respuesta respondida correctamente
        Session = sessionmaker(bind=engine)
        session = Session()
        answer = session.query(Answer).join(Message
        ).filter(Answer.id_message == Message.id_message
        ).filter(Answer.id_user == id_user
        ).filter(Answer.isError == False
        ).order_by(desc(Message.date)).first()
        session.close()
        return answer

    def addAnswer(id_question,id_message,id_user,isError):
        Session = sessionmaker(bind=engine)
        session = Session()
        answer = Answer(id_question=id_question,
                id_message=id_message,
                id_user=id_user,
                isError=isError)
        session.add(answer)
        session.commit()
        session.close()